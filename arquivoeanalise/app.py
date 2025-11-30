# app.py
# -*- coding: utf-8 -*-
import io
from datetime import datetime, date  # datetime não é usado diretamente, mas mantive caso você use depois

import pandas as pd
import streamlit as st

from sqlalchemy import create_engine       # MySQL via SQLAlchemy
import os

# =========================
# Configuração da página
# =========================
st.set_page_config(
    page_title="Análise de Usuários",
    page_icon="📊",
    layout="wide",
)

# =========================
# Funções utilitárias
# =========================
EXEMPLO_CSV = """nome,idade,cidade,data_de_cadastro,valor_compras
João,28,Uberlândia,2023-06-01,350.75
Maria,34,Belo Horizonte,2023-05-10,120.50
Paulo,22,Uberlândia,2023-07-12,980.20
Ana,30,São Paulo,2023-03-08,250.00
Carla,27,São Paulo,2024-01-15,820.40
Diego,41,Rio de Janeiro,2024-02-02,145.00
Luiza,36,Curitiba,2023-11-21,410.99
"""

def _padronizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # ? strip() remove espaços em branco no início e fim. lower() deixa tudo minúsculo.
    df.columns = [c.strip().lower() for c in df.columns]
    # Renomear se necessário (tolerância a nomes similares)
    aliases = {
        "data_cadastro": "data_de_cadastro",
        "data": "data_de_cadastro",
        "valor": "valor_compras",
        "compras": "valor_compras",
    }
    for antigo, novo in aliases.items():
        # ? Só renomeia se existe a coluna com o nome alternativo (antigo)
        #   e ainda não existe a coluna com o nome padronizado (novo).
        #   Isso evita sobrescrever/duplicar caso o nome final já exista.
        if antigo in df.columns and novo not in df.columns:
            df.rename(columns={antigo: novo}, inplace=True)
    return df

def _conversoes_robustas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "idade" in df.columns:
        df["idade"] = pd.to_numeric(df["idade"], errors="coerce")

    if "valor_compras" in df.columns:
        df["valor_compras"] = (
            df["valor_compras"]
            .astype(str)
            .str.replace(".", "", regex=False)  # remove milhar '1.234,56'
            .str.replace(",", ".", regex=False) # troca vírgula por ponto
        )
        df["valor_compras"] = pd.to_numeric(df["valor_compras"], errors="coerce")

    if "data_de_cadastro" in df.columns:
        df["data_de_cadastro"] = pd.to_datetime(df["data_de_cadastro"], errors="coerce")

    # ? limpa espaços em strings
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()

    return df

def carregar_qualquer_formato(file) -> pd.DataFrame:
    """Recebe um arquivo do st.file_uploader e retorna um DataFrame."""
    nome = file.name.lower()
    data = file.read()

    if nome.endswith((".csv", ".txt")):
        # ? tenta detectar separador; se falhar, usa vírgula
        try:
            df = pd.read_csv(io.BytesIO(data), sep=None, engine="python")
        except Exception:
            df = pd.read_csv(io.BytesIO(data))
    elif nome.endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(data))
    elif nome.endswith(".json"):
        # ? aceita JSON linha-a-linha (NDJSON) também
        try:
            df = pd.read_json(io.BytesIO(data), lines=True)
        except ValueError:
            df = pd.read_json(io.BytesIO(data))
    elif nome.endswith(".parquet"):
        df = pd.read_parquet(io.BytesIO(data))
    else:
        raise ValueError("Formato não suportado.")

    # ? padroniza nomes + aplica conversões robustas
    df = _padronizar_colunas(df)
    df = _conversoes_robustas(df)
    return df

# ? Decorador do Streamlit que cacheia
@st.cache_data
# ? recebe o conteúdo do arquivo em bytes e devolve o dataframe em pandas
def carregar_csv(conteudo_bytes: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(conteudo_bytes))
    df = _padronizar_colunas(df)
    df = _conversoes_robustas(df)
    return df

@st.cache_data(ttl=300)
def carregar_do_mysql(query: str) -> pd.DataFrame:
    # --- SOMENTE B (st.secrets["mysql"]) + fallback ENV ---
    try:
        user = st.secrets["mysql"]["user"]
        pwd  = st.secrets["mysql"]["password"]
        host = st.secrets["mysql"]["host"]
        port = st.secrets["mysql"].get("port", "3306")
        db   = st.secrets["mysql"]["database"]
        url  = f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}"
    except Exception:
        # ? Fallback por variáveis de ambiente (útil localmente com .env)
        user = os.getenv("MYSQL_USER")
        pwd  = os.getenv("MYSQL_PASSWORD")
        host = os.getenv("MYSQL_HOST", "localhost")
        port = os.getenv("MYSQL_PORT", "3306")
        db   = os.getenv("MYSQL_DATABASE")
        if not (user and pwd and db):
            raise RuntimeError(
                "Defina [mysql] em st.secrets ou variáveis de ambiente "
                "MYSQL_USER/MYSQL_PASSWORD/MYSQL_DATABASE."
            )
        url = f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}"

    engine = create_engine(url)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    df = _padronizar_colunas(df)
    df = _conversoes_robustas(df)
    return df

# ?help_text: opcional; texto do tooltip (aquele ícone de “i” do lado do KPI).
#  formato: opcional; função (callable) para formatar valor antes de mostrar ex.: transformar 1234.5 em "R$ 1.234,50"
def kpi(valor, label, help_text=None, formato=None):
    if formato:
        valor_fmt = formato(valor)
    else:
        valor_fmt = valor
    # ? Chama o componente do Streamlit st.metric para renderizar a métrica na tela
    st.metric(label, valor_fmt, help=help_text)

def gerar_usuarios_top(df_filtrado: pd.DataFrame) -> pd.DataFrame:
    # ? calcula a média
    media = df_filtrado["valor_compras"].mean()
    # ? filtrar os usuarios acima da média em ordem decrescente
    return df_filtrado[df_filtrado["valor_compras"] > media].sort_values(
        by="valor_compras", ascending=False
    )

# =========================
# Sidebar (controles)
# =========================
# ? cria um titulo na barra lateral
st.sidebar.header("⚙️ Controles")

# ? seletor de arquivo (multi-formato)
arquivo = st.sidebar.file_uploader(
    "Faça upload do seu arquivo (CSV, Excel, JSON, Parquet, TXT)",
    type=["csv", "xlsx", "xls", "json", "parquet", "txt"]
)

# ? fornecer um arquivo de exemplo caso não tenha
usar_exemplo = st.sidebar.toggle("Usar CSV de exemplo", value=True if not arquivo else False)

# ? separar visualmente os controles de outras informações.
st.sidebar.markdown("---")
st.sidebar.caption(
    # ? Exibe um texto de rodapé
    "O arquivo deve conter as colunas: **nome, idade, cidade, data_de_cadastro, valor_compras** "
    "(nomes semelhantes são aceitos)."
)

# ? Escolha da fonte de dados: Upload/Exemplo ou Banco
st.sidebar.markdown("---")
fonte_dados = st.sidebar.radio("Fonte de dados", ["Arquivo/Exemplo", "Banco MySQL"], index=0)

# --- Reset inteligente quando a FONTE ou o TOGGLE mudarem ---
if "fonte_atual" not in st.session_state:
    st.session_state.fonte_atual = fonte_dados
if "usar_exemplo_prev" not in st.session_state:
    st.session_state.usar_exemplo_prev = usar_exemplo

fonte_trocou = st.session_state.fonte_atual != fonte_dados
toggle_trocou = st.session_state.usar_exemplo_prev != usar_exemplo

if fonte_trocou or toggle_trocou:
    # limpa cache de dados (CSV/MySQL) para evitar 'fantasmas'
    st.cache_data.clear()

    # reseta filtros dependentes do dataset
    for k in ("cidades_sel", "periodo_filtro"):
        if k in st.session_state:
            del st.session_state[k]

    st.session_state.fonte_atual = fonte_dados
    st.session_state.usar_exemplo_prev = usar_exemplo

# --- Reset quando o ARQUIVO enviado trocar ---
if "nome_arquivo_prev" not in st.session_state:
    st.session_state.nome_arquivo_prev = getattr(arquivo, "name", None)

nome_atual = getattr(arquivo, "name", None)
if nome_atual != st.session_state.nome_arquivo_prev:
    # ? Se trocou o arquivo, limpa cache e zera filtros relacionados
    st.cache_data.clear()
    for k in ("cidades_sel", "periodo_filtro"):
        st.session_state.pop(k, None)
    st.session_state.nome_arquivo_prev = nome_atual

# =========================
# Carregamento de dados
# =========================
if fonte_dados == "Arquivo/Exemplo":
    if usar_exemplo:
        df = carregar_csv(EXEMPLO_CSV.encode("utf-8"))
    elif arquivo is not None:
        df = carregar_qualquer_formato(arquivo)
    else:
        st.info("📥 Envie um arquivo na barra lateral ou ative **Usar CSV de exemplo**.")
        st.stop()
elif fonte_dados == "Banco MySQL":
    try:
        df = carregar_do_mysql(
            # ? usa apenas secrets/env (sem override manual)
            "SELECT nome, idade, cidade, data_de_cadastro, valor_compras FROM usuarios;"
        )
    except Exception as e:
        st.error(f"Erro ao consultar o banco: {e}")
        st.stop()

# =========================
# Filtros
# =========================
# ? cria container que agrupa componentes
col_filtros = st.sidebar.container()
# ? Adiciona um subtítulo dentro do container
col_filtros.subheader("Filtros")

# ? pega os valores únicos da coluna cidade. ❌ Se não tiver: define cidades como uma lista vazia [] para evitar erro.
cidades = sorted(df["cidade"].dropna().unique().tolist()) if "cidade" in df.columns else []

# ? Cria um filtro de seleção múltipla com KEY fixa (permite reset via session_state)
selecionadas = col_filtros.multiselect(
    "Cidade(s)",
    options=cidades,
    default=cidades,
    key="cidades_sel"                # <--- KEY
)

# Filtro por período (com base em data_de_cadastro) com KEY fixa
if "data_de_cadastro" in df.columns:
    datas_validas = df["data_de_cadastro"].dropna()
    if len(datas_validas) > 0:
        dt_min = datas_validas.min().date()
        dt_max = datas_validas.max().date()
    else:
        # fallback se coluna existe mas só tem NaT
        dt_min = date(2000, 1, 1)
        dt_max = date.today()
    periodo = st.sidebar.date_input(
        "Período (data_de_cadastro)",
        (dt_min, dt_max),
        min_value=dt_min,
        max_value=dt_max,
        format="DD/MM/YYYY",
        key="periodo_filtro"          # <--- KEY
    )
else:
    periodo = None

# --- Sidebar: limites de linhas ---
st.sidebar.markdown("### Exibição")
limite_top = st.sidebar.number_input(
    "Limite (⭐ Usuários acima da média)", min_value=1, max_value=10_000, value=10, step=1
)
limite_filtrados = st.sidebar.number_input(
    "Limite (📋 Dados filtrados)", min_value=1, max_value=10_000, value=100, step=10
)

# Aplicar filtros
df_filtrado = df.copy()

if "cidade" in df_filtrado.columns and selecionadas:
    df_filtrado = df_filtrado[df_filtrado["cidade"].isin(selecionadas)]

if periodo and isinstance(periodo, (list, tuple)) and len(periodo) == 2 and "data_de_cadastro" in df_filtrado.columns:
    ini, fim = periodo
    # incluir limite superior (fim do dia)
    mask = (df_filtrado["data_de_cadastro"].dt.date >= ini) & (df_filtrado["data_de_cadastro"].dt.date <= fim)
    df_filtrado = df_filtrado[mask]

# =========================
# Cabeçalho
# =========================
st.title("📊 Dashboard de Usuários")
st.caption(
    "Carregue um CSV, aplique filtros e visualize KPIs, gráficos, tabelas e baixe o arquivo de usuários acima da média de compras."
)

# =========================
# Abas
# =========================
aba_overview, aba_graficos, aba_tabelas, aba_dados = st.tabs(
    ["Visão Geral", "Gráficos", "Tabelas", "Dados brutos"]
)

# =========================
# Aba visão geral (KPIs)
# =========================
# ? Cria 4 colunas lado a lado na interface do Streamlit
col1, col2, col3, col4 = st.columns(4)
# ? conta quantas linhas ele tem
total_registros = len(df_filtrado)
# ? calcula a média de idade se a coluna idade existir
media_idade = df_filtrado["idade"].mean() if "idade" in df_filtrado else None
# ? calcula soma total de compras
valor_total = df_filtrado["valor_compras"].sum() if "valor_compras" in df_filtrado else None
# ? calcula valor médio de compras
valor_medio = df_filtrado["valor_compras"].mean() if "valor_compras" in df_filtrado else None

# ? 1 coluna total de usuarios
with col1:
    kpi(total_registros, "Total de Usuários")
# ? 2 coluna media de idade
with col2:
    if media_idade is not None:
        kpi(media_idade, "Média de Idade", formato=lambda v: f"{v:.2f} anos")
    else:
        st.metric("Média de Idade", "—")
# ? 3 coluna valor total
with col3:
    if valor_total is not None:
        kpi(valor_total, "Valor Total", formato=lambda v: f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    else:
        st.metric("Valor Total", "—")
# ? 4 coluna valor medio
with col4:
    if valor_medio is not None:
        kpi(valor_medio, "Valor Médio", formato=lambda v: f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    else:
        st.metric("Valor Médio", "—")

# =========================
# ABA: Gráficos (Novos usuários, Barras por cidade, Histograma Idade, Dispersão)
# =========================
with aba_graficos:
    st.subheader("📈 Novos usuários ao longo do tempo")

    if "data_de_cadastro" in df_filtrado.columns:
        # ? Escolha de agregação
        agg = st.selectbox("Agregação", options=["Diária", "Mensal"], index=1, help="Como agrupar novos usuários ao longo do tempo.")
        base_tempo = df_filtrado.dropna(subset=["data_de_cadastro"]).copy()
        base_tempo["data"] = base_tempo["data_de_cadastro"].dt.to_period("M" if agg == "Mensal" else "D").dt.start_time
        novos = base_tempo.groupby("data")["nome"].count().rename("novos_usuarios").reset_index()
        novos = novos.sort_values("data")
        st.line_chart(novos.set_index("data"), use_container_width=True)
    else:
        st.info("Coluna **data_de_cadastro** não encontrada no CSV.")

    st.markdown("---")

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("🏙️ Usuários por cidade")
        if "cidade" in df_filtrado.columns:
            contagem = df_filtrado["cidade"].value_counts().sort_values(ascending=False)
            st.bar_chart(contagem, use_container_width=True)
        else:
            st.info("Coluna **cidade** não encontrada no CSV.")

    with col_g2:
        st.subheader("📊 Histograma de idade")
        if "idade" in df_filtrado.columns and df_filtrado["idade"].notna().any():
            # ? bins automáticos com pd.cut
            serie = df_filtrado["idade"].dropna()
            # ? criar ~10 bins (ajusta automaticamente pelo range)
            bins = min(10, max(3, int(serie.nunique() // 2) or 5))
            cats = pd.cut(serie, bins=bins)
            hist = cats.value_counts().sort_index()
            # ? converter Interval para string
            hist.index = hist.index.astype(str)
            st.bar_chart(hist, use_container_width=True)
        else:
            st.info("Coluna **idade** não encontrada ou sem dados válidos.")

    st.markdown("---")

    st.subheader("🟣 Dispersão: Idade × Valor de Compras")
    if all(col in df_filtrado.columns for col in ["idade", "valor_compras"]):
        df_disp = df_filtrado[["idade", "valor_compras", "cidade"]].dropna()
        if len(df_disp) > 0:
            st.scatter_chart(
                df_disp,
                x="idade",
                y="valor_compras",
                color="cidade" if "cidade" in df_disp.columns else None,
                use_container_width=True
            )
        else:
            st.info("Dados insuficientes após limpeza para o gráfico de dispersão.")
    else:
        st.info("São necessárias as colunas **idade** e **valor_compras** para o gráfico de dispersão.")

# =========================
# ABA: Tabelas (Top usuários + Download) e Dados filtrados
# =========================
with aba_tabelas:
    st.subheader("⭐ Usuários acima da média de compras (base: conjunto filtrado)")
    if "valor_compras" in df_filtrado.columns:
        usuarios_top = gerar_usuarios_top(df_filtrado)
        st.dataframe(usuarios_top.head(limite_top), use_container_width=True)

        csv_bytes = usuarios_top.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Baixar usuarios_top.csv", csv_bytes, "usuarios_top.csv", "text/csv")
    else:
        st.info("Coluna **valor_compras** não encontrada no CSV.")

    st.subheader("📋 Dados filtrados")
    st.dataframe(df_filtrado.head(limite_filtrados), use_container_width=True)

# =========================
# ABA: Dados brutos (sem filtros) — opcional para auditoria
# =========================
with aba_dados:
    st.subheader("📄 Dados originais (sem filtros)")
    st.dataframe(df, use_container_width=True)

# =========================
# Rodapé
# =========================
st.markdown("---")
st.caption(
    "Observação: a média e o arquivo **usuarios_top.csv** são calculados com base no conjunto **filtrado** atual."
)
