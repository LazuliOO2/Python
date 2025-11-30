# -*- coding: utf-8 -*-
"""
Versão B (sem Ollama): extrai pedidos de texto usando heurísticas e regex,
mantendo o mesmo schema Pydantic e as funções de salvamento.

Execute:
    python pedido_extractor_no_llm.py
ou importe a função:
    from pedido_extractor_no_llm import extrair_sem_llm
"""

from typing import Optional, List, Tuple, Dict
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime
from pathlib import Path
import json, re, traceback

# ============================================================
# 1) Esquemas (Pydantic)
# ============================================================

class Item(BaseModel):
    produto: str
    tamanho: Optional[str] = None
    quantidade: Optional[int] = None
    observacoes: Optional[List[str]] = None

class PedidoSchema(BaseModel):
    cliente: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    pagamento: Optional[str] = None  # "pix"|"dinheiro"|"cartão crédito"|"cartão débito"|None
    itens: List[Item] = Field(default_factory=list)
    observacoes_gerais: Optional[List[str]] = None
    mensagem_original: str

# ============================================================
# 2) Vocabulários e utilitários
# ============================================================

NUM_PALAVRA = {
    "um": 1, "uma": 1,
    "dois": 2, "duas": 2,
    "três": 3, "tres": 3,
    "quatro": 4, "cinco": 5,
    "seis": 6, "sete": 7,
    "oito": 8, "nove": 9,
    "dez": 10,
    "meia": 0.5, "metade": 0.5,
}

TAMANHOS = {"pequena", "média", "media", "grande", "gg", "g", "m", "p"}

# Mapeia tamanho abreviado para forma descritiva
MAP_TAMANHO = {
    "p": "pequena", "m": "média", "media": "média",
    "g": "grande", "gg": "grande",
}

PAGAMENTOS = {
    "pix": "pix",
    "dinheiro": "dinheiro",
    "cartao credito": "cartão crédito",
    "cartão credito": "cartão crédito",
    "cartao debito": "cartão débito",
    "cartão debito": "cartão débito",
    "cartão crédito": "cartão crédito",
    "cartão débito": "cartão débito",
    "credito": "cartão crédito",
    "débito": "cartão débito",
    "debito": "cartão débito",
}

SABORES_PALAVRAS = [
    # lista não exaustiva; apenas algumas comuns para heurística
    "calabresa", "frango", "catupiry", "mussarela", "marguerita", "portuguesa",
    "pepperoni", "quatro queijos", "bacon", "milho", "tomate", "cebola", "azeitona",
    "chocolate", "brigadeiro"
]

BEBIDAS_VOLUMES = r"(?:(\d+(?:,\d+)?|\d+(?:\.\d+)?)\s?(?:l|ml))"  # 2L, 350ml, 1,5L

# ============================================================
# 3) Funções auxiliares de limpeza e normalização
# ============================================================

def normalizar_txt(s: str) -> str:
    s = s.strip()
    s = s.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    s = re.sub(r"\s+", " ", s)
    return s

def extrair_cliente(s: str) -> Optional[str]:
    # Padrões simples: "aqui é o João", "sou a Maria", "me chamo Lucas"
    m = re.search(r"\b(aqui é o|sou|me chamo|aqui eh o|aqui e o)\s+([A-ZÁÂÃÀÉÊÍÓÔÕÚÇ][\wÁÂÃÀÉÊÍÓÔÕÚÇ]+)", s, flags=re.I)
    if m:
        return m.group(2).strip()
    # "Ass: Nome", "Att: Nome"
    m = re.search(r"\b(ass|att|atenciosamente)\s*[:\-]\s*([A-ZÁÂÃÀÉÊÍÓÔÕÚÇ][\wÁÂÃÀÉÊÍÓÔÕÚÇ ]+)", s, flags=re.I)
    if m:
        return m.group(2).strip()
    return None

def extrair_telefone(s: str) -> Optional[str]:
    # Formatos brasileiros comuns
    m = re.search(r"(\+?55\s*)?\(?\d{2}\)?\s*\d{4,5}[- ]?\d{4}", s)
    return m.group(0).strip() if m else None

def extrair_endereco(s: str) -> Optional[str]:
    # Heurística: procurar por "rua", "avenida", "av.", "rodovia", "travessa", "estrada"
    m = re.search(r"\b(rua|avenida|av\.?|rodovia|travessa|estrada)\b[^.]*", s, flags=re.I)
    if m:
        # cortar até vírgula final plausível
        trecho = m.group(0).strip()
        # tenta pegar número após vírgula ou espaço
        m2 = re.search(r".{0,80}\b\d{1,5}\b", trecho)
        return trecho if not m2 else trecho[:m2.end()].strip()
    return None

def normalizar_pagamento(s: str) -> Optional[str]:
    s = s.lower()
    s = s.replace("ã", "a").replace("á", "a").replace("â", "a").replace("à", "a")
    s = s.replace("é", "e").replace("ê", "e")
    s = s.replace("í", "i").replace("ó", "o").replace("ô", "o").replace("õ", "o").replace("ú", "u")
    s = s.replace("  ", " ")
    for k, v in PAGAMENTOS.items():
        if re.search(rf"\b{k}\b", s):
            return v
    return None

def numero_da_palavra(p: str) -> Optional[int]:
    p = p.lower()
    if p in NUM_PALAVRA and isinstance(NUM_PALAVRA[p], (int, float)):
        n = NUM_PALAVRA[p]
        if isinstance(n, float):
            # não usamos 0.5 como quantidade de unidades de item generalizado
            return None
        return int(n)
    return None

def extrair_quantidade(tokens: List[str]) -> Tuple[Optional[int], int]:
    """
    Retorna (quantidade, idx_consumidos) a partir do início da lista de tokens.
    Aceita números (2, 3) ou palavras (duas, três).
    """
    if not tokens:
        return None, 0
    t0 = tokens[0]
    if t0.isdigit():
        return int(t0), 1
    n = numero_da_palavra(t0)
    if n is not None:
        return n, 1
    return None, 0

def detectar_tamanho(tokens: List[str]) -> Tuple[Optional[str], int]:
    if not tokens:
        return None, 0
    t0 = tokens[0].lower()
    t0_norm = MAP_TAMANHO.get(t0, t0)
    if t0_norm in TAMANHOS:
        return t0_norm, 1
    return None, 0

def extrair_bebida_volume(s: str) -> Optional[str]:
    m = re.search(BEBIDAS_VOLUMES, s, flags=re.I)
    if m:
        vol = m.group(0).lower().replace(" ", "")
        vol = vol.replace(",", ".")
        vol = vol.replace("l", "L").replace("ml", "ml")  # mantém unidade
        return vol.upper() if vol.endswith("l") else vol
    return None

def limpar_observacao(s: str) -> str:
    s = s.strip()
    s = re.sub(r"^\(|\)$", "", s)  # remove parênteses externos
    return s if s else ""

def split_por_itens_brutos(msg: str) -> List[str]:
    """
    Tentativa de segmentar lista de itens por conectivos comuns.
    Ex.: "2 pizzas grandes de calabresa (sem cebola) e uma coca 2L"
    """
    # primeiro separa por " e " só quando faz sentido (entre itens)
    partes = re.split(r"\b(?: e |,|;|\+|\&)\b", msg, flags=re.I)
    # junta partes curtas que parecem continuar o item anterior
    out = []
    buffer = ""
    for p in partes:
        p = p.strip()
        if not p:
            continue
        if buffer:
            # decisão heurística: se p inicia com "de", "com", "sem", "grande/média/..." então é continuação
            if re.match(r"^(de|com|sem|pequena|m[eé]dia|grande|p|m|g|gg|[0-9]+l|[0-9]+ml)\b", p, flags=re.I):
                buffer += " " + p
                continue
            else:
                out.append(buffer.strip())
                buffer = p
        else:
            buffer = p
    if buffer:
        out.append(buffer.strip())
    return out

def gerar_item_de_texto(chunk: str) -> Optional[Dict]:
    """
    Gera um Item a partir de um pedaço de texto.
    Regras simples, priorizando pizza/lanches e bebidas.
    """
    texto = chunk.strip()
    texto_low = texto.lower()

    # Observações entre parênteses
    obs = []
    for m in re.finditer(r"\((.*?)\)", texto):
        o = limpar_observacao(m.group(1))
        if o:
            obs.append(o)
    texto_sem_obs = re.sub(r"\(.*?\)", "", texto).strip()

    # Tokens para detectar quantidade e tamanho
    tokens = texto_sem_obs.split()
    qtd, c1 = extrair_quantidade(tokens)
    tokens = tokens[c1:] if c1 else tokens

    tamanho, c2 = detectar_tamanho(tokens)
    tokens = tokens[c2:] if c2 else tokens

    # Heurística de bebida (coca, refri, água) + volume
    volume = extrair_bebida_volume(texto_low)
    if any(x in texto_low for x in ["coca", "coca-cola", "refrigerante coca"]):
        produto = "coca-cola"
        if not tamanho and volume:
            tamanho = volume.upper()
        return {
            "produto": produto,
            "tamanho": tamanho,
            "quantidade": qtd if qtd is not None else 1,
            "observacoes": obs or None
        }

    # Heurística de pizza/lanches: busca "pizza" e sabor depois de "de ..."
    if "pizza" in texto_low or any(s in texto_low for s in SABORES_PALAVRAS):
        # produto base
        sabor = None
        m = re.search(r"pizza\s*(?:de|c\/|c/)?\s*(.*)", texto_sem_obs, flags=re.I)
        if m:
            sabor = m.group(1).strip()
        else:
            # tenta "de X" mesmo sem a palavra pizza
            m2 = re.search(r"\bde\s+(.+)", texto_sem_obs, flags=re.I)
            sabor = m2.group(1).strip() if m2 else None

        # normaliza sabor e produto
        if sabor:
            sabor = sabor.replace(" c/ ", " com ")
            sabor = re.sub(r"\b c\b", " com", sabor)
            # remove palavras fortes de tamanho que sobraram no sabor
            sabor = re.sub(r"\b(pequena|m[eé]dia|grande|p|m|g|gg)\b", "", sabor, flags=re.I).strip()
            produto = f"pizza de {sabor}".strip()
        else:
            produto = "pizza"

        return {
            "produto": produto,
            "tamanho": tamanho,
            "quantidade": qtd if qtd is not None else 1,
            "observacoes": obs or None
        }

    # Caso genérico: usa o texto restante como produto
    produto = texto_sem_obs.strip()
    if not produto:
        return None
    return {
        "produto": produto,
        "tamanho": tamanho,
        "quantidade": qtd if qtd is not None else 1,
        "observacoes": obs or None
    }

def extrair_observacoes_gerais(msg: str) -> Optional[List[str]]:
    """
    Observações que NÃO são do item: exemplos
    - sem guardanapo; entregar no portão; com talheres
    """
    candidatos = []
    padroes = [
        r"\b(sem guardanapo[s]?)\b",
        r"\b(entregar no port[aã]o)\b",
        r"\b(com talher(?:es)?)\b",
        r"\b(deixar na portaria)\b",
        r"\b(n[ãa]o tocar a campainha)\b",
    ]
    low = msg.lower()
    for p in padroes:
        m = re.search(p, low, flags=re.I)
        if m:
            candidatos.append(m.group(0))
    return candidatos or None

# ============================================================
# 4) Extrator principal (sem LLM)
# ============================================================

def extrair_sem_llm(mensagem: str) -> dict:
    """
    Extrai campos com heurísticas e valida com Pydantic.
    Mantém regras pedidas no projeto original:
      - quantidade default = 1 quando não explícita
      - tamanho só para porte (pizza) ou volume (2L, 350ml)
      - observacoes_gerais não deve repetir pagamento/endereço/etc.
    """
    original = normalizar_txt(mensagem)
    msg = original

    cliente = extrair_cliente(msg)
    telefone = extrair_telefone(msg)
    endereco = extrair_endereco(msg)
    pagamento = normalizar_pagamento(msg)

    # Divide mensagem em "blocos de itens" de maneira aproximada
    # A divisão evita pegar endereço/pagamento. Removemos linhas óbvias antes.
    msg_itens = re.sub(r"(rua|avenida|av\.?|pagamento|pago|pix|dinheiro|d[ée]bito|cr[ée]dito|telefone)[: ]+.*", "", msg, flags=re.I)
    chunks = split_por_itens_brutos(msg_itens)

    itens = []
    for ch in chunks:
        item = gerar_item_de_texto(ch)
        if item and item.get("produto"):
            itens.append(item)

    # Observações gerais (não vinculadas a item)
    observacoes_gerais = extrair_observacoes_gerais(msg)

    data = {
        "cliente": cliente,
        "telefone": telefone,
        "endereco": endereco,
        "pagamento": pagamento,
        "itens": itens,
        "observacoes_gerais": observacoes_gerais,
        "mensagem_original": original
    }

    # Filtra lixo nas observações gerais conforme critérios do projeto
    if isinstance(data.get("observacoes_gerais"), list):
        ban = ["pizza", "coca", "catupiry", "calabresa", "endereço", "endereco", "pago", "pagamento", "telefone"]
        data["observacoes_gerais"] = [
            o for o in data["observacoes_gerais"]
            if isinstance(o, str) and 2 <= len(o) <= 80 and not any(k in o.lower() for k in ban)
        ] or None

    # Validação final
    pedido = PedidoSchema(**data)
    return pedido.model_dump()

# ============================================================
# 5) Salvar (mesmo formato do projeto original)
# ============================================================

def _safe_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def save_pedido_json_unico(pedido: dict, out_dir: str = "out") -> Path:
    ts = datetime.now().isoformat(timespec="seconds").replace(":", "-")
    path = Path(out_dir) / f"pedido-{ts}.json"
    _safe_write_text(path, json.dumps(pedido, ensure_ascii=False, indent=2))
    return path

def append_pedido_jsonl(pedido: dict, out_dir: str = "out", filename: str = "pedidos.jsonl") -> Path:
    path = Path(out_dir) / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(pedido, ensure_ascii=False)
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    return path

# ============================================================
# 6) Demo
# ============================================================

if __name__ == "__main__":
    msg = (
        "Oi! Aqui é o João. Quero 2 pizzas grandes de calabresa (sem cebola) e uma coca 2L. "
        "Entregar na Rua das Flores, 55. Pago em dinheiro. Por favor, deixar na portaria"
    )
    try:
        resultado = extrair_sem_llm(msg)
        print(json.dumps(resultado, ensure_ascii=False, indent=2))

        # Salvar como no original
        json_unico = save_pedido_json_unico(resultado, out_dir="out")
        jsonl_log  = append_pedido_jsonl(resultado, out_dir="out", filename="pedidos.jsonl")
        print(f"\nArquivos salvos:\n- {json_unico}\n- {jsonl_log}")
    except ValidationError as e:
        print("Falha de validação:", e)
    except Exception as e:
        print("Erro geral:", e)
        print("--- TRACEBACK ---")
        print(traceback.format_exc())
