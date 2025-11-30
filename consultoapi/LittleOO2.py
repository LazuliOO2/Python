# -*- coding: utf-8 -*-
import requests
import json
import os
import re
import time
from datetime import datetime

# =========================
# Saída organizada
# =========================
OUTPUT_DIR = "historico_LittleOO2"  # pasta onde vai salvar TXT e JSON
MAX_EXPORTS_PER_CEP = 10              # quantos arquivos TXT manter por CEP (None = sem limite)

def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

HISTORICO_FILE = os.path.join(OUTPUT_DIR, "historico_ceps.json")

# =========================
# Configurações de "robot vibe"
# =========================
HTTP_TIMEOUT = 10
HTTP_HEADERS = {"User-Agent": "LittleOO2/1.0 (+https://viacep.com.br)"}

SLOW_BANNER = True       # True = banner digitando
TYPE_SPEED = 0.01        # Velocidade do banner (s por caractere)

HUMOR_MODE = True        # Deixa as falas engraçadas
THINK_SPEED = 1.2        # Tempo base do "pensar"
PROGRESS_SPEED = 1.6     # Tempo base do "carregando/progresso"

# =========================
# Utilidades visuais
# =========================
def typewrite(line: str, delay: float = TYPE_SPEED):
    """Efeito de digitação para o banner."""
    for ch in line:
        print(ch, end='', flush=True)
        time.sleep(delay)
    print()

def robo_fala(texto: str, delay: float = 0.02):
    """Fala do robozinho com leve efeito de digitação."""
    for ch in texto:
        print(ch, end='', flush=True)
        time.sleep(delay)
    print()

def pensar(segundos: float = THINK_SPEED, msg: str = "🤖 Processando…", dots: int = 3):
    """Mostra uma mensagem e fica 'pensando' por alguns segundos."""
    robo_fala(msg)
    steps = max(1, int(segundos / 0.4))
    for _ in range(steps):
        print("." * dots, flush=True)
        time.sleep(0.4)

def show_progress(titulo: str = "⏳ Carregando módulos secretos",
                  segundos: float = PROGRESS_SPEED,
                  barra_len: int = 22):
    """Mini barra de progresso ASCII."""
    robo_fala(titulo)
    steps = max(3, int(segundos / 0.08))
    for i in range(steps + 1):
        filled = int((i / steps) * barra_len)
        bar = "█" * filled + "░" * (barra_len - filled)
        print(f"[{bar}] {int((i/steps)*100)}%", end="\r", flush=True)
        time.sleep(segundos / steps if steps else 0.05)
    print()  # quebra de linha final

def safe_get(d: dict, key: str, default: str = "N/D"):
    v = d.get(key)
    return v if (v is not None and v != "") else default

def only_digits(s: str) -> str:
    return re.sub(r"\D", "", s or "")

# =========================
# ViaCEP
# =========================
def consulta_cep(cep: str):
    """
    Consulta um CEP na ViaCEP.
    Retorna dict com os campos da ViaCEP ou None se erro/CEP inválido.
    """
    url = f"https://viacep.com.br/ws/{cep}/json/"
    try:
        resp = requests.get(url, headers=HTTP_HEADERS, timeout=HTTP_TIMEOUT)
        data = resp.json()
        if data.get('erro'):
            return None
        return data
    except Exception:
        return None

# =========================
# IBGE (por CÓDIGO do município)
# =========================
def dados_ibge_por_codigo_municipio(codigo_ibge: str):
    """
    Consulta detalhes do município direto pelo ID IBGE (ex: '3106200' para Belo Horizonte).
    Evita ambiguidade de nome.
    Retorna dict com nome, microrregião, estado, uf e região — ou None se falhar.
    """
    codigo_ibge = str(codigo_ibge or "").strip()
    if not codigo_ibge.isdigit():
        return None

    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{codigo_ibge}"
    try:
        resp = requests.get(url, headers=HTTP_HEADERS, timeout=HTTP_TIMEOUT)
        muni = resp.json()
        return {
            'nome': muni['nome'],
            'microrregiao': muni['microrregiao']['nome'],
            'estado': muni['microrregiao']['mesorregiao']['UF']['nome'],
            'uf': muni['microrregiao']['mesorregiao']['UF']['sigla'],
            'regiao': muni['microrregiao']['mesorregiao']['UF']['regiao']['nome'],
        }
    except Exception:
        return None

# =========================
# Histórico
# =========================
def carregar_historico():
    ensure_output_dir()
    if os.path.exists(HISTORICO_FILE):
        with open(HISTORICO_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def salvar_no_historico(dados):
    ensure_output_dir()
    historico = carregar_historico()
    dados = dict(dados)  # copia defensiva
    dados['consulta'] = datetime.now().isoformat()
    historico.append(dados)
    with open(HISTORICO_FILE, 'w', encoding='utf-8') as f:
        json.dump(historico, f, indent=2, ensure_ascii=False)

# =========================
# Exportação
# =========================
def exportar_txt(dados):
    ensure_output_dir()

    # normaliza CEP só com dígitos para padronizar nome do arquivo + limpeza
    cep_norm = only_digits(safe_get(dados, 'cep', 'desconhecido'))
    filename = os.path.join(
        OUTPUT_DIR,
        f"CEP_{cep_norm}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    )

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"CEP: {safe_get(dados,'cep')}\n")
        f.write(f"Logradouro: {safe_get(dados,'logradouro')}\n")
        f.write(f"Bairro: {safe_get(dados,'bairro')}\n")
        f.write(f"Cidade/UF: {safe_get(dados,'localidade')}/{safe_get(dados,'uf')}\n")
    robo_fala(f"📄 Arquivo {os.path.basename(filename)} salvo em {OUTPUT_DIR}! (cheirinho de bytes recém-assados)")

    # Limpeza: mantém no máximo N arquivos TXT por CEP (match por CEP normalizado)
    if MAX_EXPORTS_PER_CEP:
        try:
            arquivos = [
                os.path.join(OUTPUT_DIR, arq)
                for arq in os.listdir(OUTPUT_DIR)
                if arq.startswith(f"CEP_{cep_norm}_") and arq.endswith(".txt")
            ]
            arquivos.sort(key=lambda p: os.path.getmtime(p), reverse=True)
            for velho in arquivos[MAX_EXPORTS_PER_CEP:]:
                os.remove(velho)
                robo_fala(f"🧹 Limpeza preventiva: removi {os.path.basename(velho)} (organização é vida!)", delay=0.005)
        except Exception:
            pass  # não quebra o fluxo se não conseguir limpar

# =========================
# Mapinha ASCII
# =========================
def mapa_regiao(uf):
    mapas = {
        'SP': ['┌───────────┐', '│    SP     │', '│   █████   │', '│   █▓▓▓█   │', '│   █▓★▓█   │', '└───────────┘'],
        'RJ': ['┌───────────┐', '│     RJ    │', '│   █████   │', '│   █▓★▓█   │', '│   █▓▓▓█   │', '└───────────┘'],
        'MG': ['┌───────────┐', '│    MG     │', '│  █▓★▓█    │', '│  █▓▓▓█    │', '│  █████    │', '└───────────┘']
    }
    return mapas.get(uf, ['┌───────────┐', '│    ??     │', '│   █████   │', '│   █▓▓▓█   │', '│   █▓★▓█   │', '└───────────┘'])

# =========================
# Comparador
# =========================
def comparar_ceps(cep1, cep2):
    regioes = {
        'SP':'Sudeste', 'RJ':'Sudeste', 'MG':'Sudeste', 'ES':'Sudeste',
        'PR':'Sul', 'SC':'Sul', 'RS':'Sul',
        'DF':'Centro-Oeste', 'GO':'Centro-Oeste', 'MT':'Centro-Oeste', 'MS':'Centro-Oeste',
        'BA':'Nordeste', 'SE':'Nordeste', 'AL':'Nordeste', 'PE':'Nordeste',
        'PB':'Nordeste', 'RN':'Nordeste', 'CE':'Nordeste', 'PI':'Nordeste', 'MA':'Nordeste',
        'AM':'Norte', 'RR':'Norte', 'AP':'Norte', 'PA':'Norte', 'TO':'Norte', 'RO':'Norte', 'AC':'Norte'
    }
    d1, d2 = consulta_cep(cep1), consulta_cep(cep2)
    if not all([d1, d2]):
        return None

    reg1 = regioes.get(d1['uf'], 'Desconhecida')
    reg2 = regioes.get(d2['uf'], 'Desconhecida')
    mesma = reg1 == reg2

    ibge1 = dados_ibge_por_codigo_municipio(d1.get('ibge',''))
    ibge2 = dados_ibge_por_codigo_municipio(d2.get('ibge',''))

    return {
        'mesma_regiao': mesma,
        'regiao1': reg1,
        'regiao2': reg2,
        'dados1': d1,
        'dados2': d2,
        'ibge1': ibge1,
        'ibge2': ibge2,
    }

# =========================
# Banner / Menu
# =========================
def banner():
    linhas = [
        "="*50,
        "🤖 Olá! Eu sou o Robô LittleOO2 — seu assistente em exploração postal!",
        "   Consulto CEPs, comparo regiões e ainda salvo tudo bonitinho.",
        "="*50,
    ]
    if SLOW_BANNER:
        for line in linhas:
            typewrite(line)
            time.sleep(0.1)
        show_progress("⚙️ Iniciando motores elétricos do humor", 1.2)
    else:
        for line in linhas:
            print(line)

def menu():
    print("\nMenu Principal:")
    print("1. Consultar CEP")
    print("2. Ver histórico")
    print("3. Comparar CEPs")
    print("4. Sair")

# =========================
# App
# =========================
def main():
    banner()
    ensure_output_dir()

    while True:
        menu()
        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == '1':
            cep = input("Digite o CEP (com ou sem hífen): ").strip()
            cep = re.sub(r'\D', '', cep)
            if len(cep) != 8:
                robo_fala("❌ CEP inválido! Meu radar postal detectou dígitos a menos ou a mais…")
                continue

            show_progress("📡 Conectando à CEP.AI…", 1.1)
            pensar(1.0, "🛰️ Trazendo dados do satélite dos Correios…")
            show_progress("🧠 Aplicando inteligência (artificial mesmo) aos dados", 1.1)

            dados = consulta_cep(cep)
            if not dados:
                robo_fala("❌ CEP não encontrado! Ou ele tá de férias, ou eu errei a antena…")
                continue

            print(f"\n📍 CEP {safe_get(dados,'cep')} - {safe_get(dados,'localidade')}/{safe_get(dados,'uf')}")
            print(f"   Rua: {safe_get(dados,'logradouro')}")
            print(f"   Bairro: {safe_get(dados,'bairro')}")
            print(f"   Cidade: {safe_get(dados,'localidade')}")
            print(f"   Estado: {safe_get(dados,'uf')}")

            print("\n🗺  Mapa Simbólico:")
            for linha in mapa_regiao(dados['uf']):
                print(f"    {linha}")
            print("    (★ = Local aproximado — confia no algoritmo 😎)")

            pensar(0.8, "📚 Consultando enciclopédia geográfica do IBGE…")
            info_ibge = dados_ibge_por_codigo_municipio(dados.get('ibge',''))
            if info_ibge:
                print("\n🧠 Curiosidade Geográfica (IBGE):")
                print(f"   - Município: {info_ibge['nome']} ({info_ibge['uf']})")
                print(f"   - Microrregião: {info_ibge['microrregiao']}")
                print(f"   - Estado: {info_ibge['estado']}")
                print(f"   - Região: {info_ibge['regiao']}")
            else:
                robo_fala("ℹ️ Não rolou do IBGE me notar agora, mas sigo confiante. ✨")

            salvar_no_historico(dados)
            show_progress("📝 Salvando evidências desta missão no histórico", 0.9)
            exportar_txt(dados)

        elif opcao == '2':
            show_progress("📂 Abrindo pastas secretas do histórico", 0.9)
            historico = carregar_historico()
            if not historico:
                robo_fala("📭 Nenhuma consulta no histórico! Meu HD está mais vazio que domingo à noite.")
                continue

            robo_fala("\n📜 Últimas Consultas (máx. 5):")
            for i, item in enumerate(historico[-5:], 1):
                robo_fala(f"{i}. {safe_get(item,'cep')} - {safe_get(item,'localidade')}/{safe_get(item,'uf')} - {safe_get(item,'logradouro')}", delay=0.01)

        elif opcao == '3':
            cep1 = input("Primeiro CEP: ").strip()
            cep2 = input("Segundo CEP: ").strip()
            cep1 = re.sub(r'\D', '', cep1)
            cep2 = re.sub(r'\D', '', cep2)

            if len(cep1) != 8 or len(cep2) != 8:
                robo_fala("❌ Preciso de dois CEPs válidos de 8 dígitos. Eu conto nos meus transistores, juro!")
                continue

            show_progress("🧰 Coletando dados dos dois CEPs", 1.1)
            pensar(1.0, "🧮 Comparando latitudes imaginárias e longitudes estilizadas…")
            show_progress("📊 Montando dossiê comparativo", 1.0)

            resultado = comparar_ceps(cep1, cep2)
            if not resultado:
                robo_fala("❌ Erro na comparação! Um dos CEPs se escondeu atrás do roteador.")
                continue

            print(f"\n📊 Comparação entre {cep1} e {cep2}:")
            print(f"   - Mesma região: {'✅' if resultado['mesma_regiao'] else '❌'}")
            print(f"   - Região do {cep1}: {resultado['regiao1']}")
            print(f"   - Região do {cep2}: {resultado['regiao2']}")

            i1, i2 = resultado.get('ibge1'), resultado.get('ibge2')
            if i1 and i2:
                print("\n🧠 Dados IBGE dos municípios:")
                print(f"   - {cep1}: {i1['nome']} ({i1['microrregiao']} - {i1['estado']}/{i1['uf']}) — Região {i1['regiao']}")
                print(f"   - {cep2}: {i2['nome']} ({i2['microrregiao']} - {i2['estado']}/{i2['uf']}) — Região {i2['regiao']}")
            else:
                robo_fala("ℹ️ Não consegui puxar todos os detalhes do IBGE agora. Culpa do cabo de rede? 👀")

        elif opcao == '4':
            pensar(0.7, "💤 Desligando sub-rotinas de fofura robótica…")
            robo_fala("👋 Até logo! O LittleOO2 vai tirar uma soneca elétrica e sonhar com CEPs.")
            break

        else:
            robo_fala("⚠️ Opção inválida. Meu menu não tem DLC escondida… ainda.")

if __name__ == "__main__":
    main()
