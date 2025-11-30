# Importar as bibliotecas
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import timedelta
import plotly.express as px
import google.generativeai as genai
import os

# Configurar chave da API Gemini
API_KEY = os.getenv("GEMINI_API_KEY")  # Substitua pela variável de ambiente configurada
if not API_KEY:
    st.error("A chave da API Gemini não foi configurada corretamente. Certifique-se de configurá-la como variável de ambiente.")
else:
    genai.configure(api_key=API_KEY)

# Criar um modelo Gemini
modelo = genai.GenerativeModel("gemini-1.5-pro")

# Funções para carregar dados do yFinance
@st.cache_data
def carregar_dados(empresas):
    texto_tickers = " ".join(empresas)
    try:
        dados_acao = yf.Tickers(texto_tickers)
        cotacoes_acao = dados_acao.history(period="1d", start="2010-01-01", end="2024-07-01")
        cotacoes_acao = cotacoes_acao["Close"]
        cotacoes_acao = cotacoes_acao.dropna(how="all", axis=1)  # Remove ações com todos os valores NaN
        return cotacoes_acao
    except Exception as e:
        st.error(f"Erro ao carregar os dados das ações: {e}")
        return pd.DataFrame()

@st.cache_data
def carregar_tickers_acoes():
    try:
        base_tickers = pd.read_csv("IBOV.csv", sep=";")
        tickers = list(base_tickers["Código"])
        tickers = [item + ".SA" for item in tickers]
        return tickers
    except Exception as e:
        st.error(f"Erro ao carregar os tickers das ações: {e}")
        return []

# Carregar dados com indicador de carregamento
with st.spinner("Carregando os dados, por favor aguarde..."):
    acoes = carregar_tickers_acoes()
    dados = carregar_dados(acoes)

# Verificar se os dados foram carregados
if dados.empty:
    st.warning("Nenhum dado carregado. Verifique se os tickers estão corretos ou se há conexão com a API.")
else:
    # Converter índices para datetime
    try:
        dados.index = pd.to_datetime(dados.index)
    except Exception as e:
        st.error(f"Erro ao converter os índices para datetime: {e}")

    # Verificar valores nulos ou inválidos nos índices
    if dados.index.isnull().any():
        st.error("Os índices contêm valores nulos ou inválidos. Verifique os dados de entrada.")
    else:
        # Verificar se alguma ação foi removida devido a valores NaN
        acoes_removidas = [acao for acao in acoes if acao not in dados.columns]
        if acoes_removidas:
            st.warning(f"As seguintes ações foram ignoradas devido a dados incompletos: {', '.join(acoes_removidas)}")

        # Criar a interface do Streamlit
        st.write("""
        # App Preço de Ações
        O gráfico abaixo representa a evolução do preço das ações ao longo dos anos
        """)

        # Prepara as visualizações - filtros
        st.sidebar.header("Filtros")

        # Filtro de ações
        lista_acoes = st.sidebar.multiselect("Escolha as ações para visualizar", dados.columns)
        if lista_acoes:
            dados = dados[lista_acoes]
            if len(lista_acoes) == 1:
                acao_unica = lista_acoes[0]
                dados = dados.rename(columns={acao_unica: "Close"})

        # Filtro de datas
        # Converta os índices para datetime.datetime
        data_inicial = dados.index.min().to_pydatetime()
        data_final = dados.index.max().to_pydatetime()
        intervalo_data = st.sidebar.slider(
            "Selecione o período",
            min_value=data_inicial,
            max_value=data_final,
            value=(data_inicial, data_final),
            step=timedelta(days=1)
        )

        # Filtrar dados pelo período selecionado
        dados_filtrados = dados.loc[intervalo_data[0]:intervalo_data[1]].dropna()

        # Adicionar interface para perguntas ao Gemini
        st.sidebar.header("Perguntas para o Gemini")
        pergunta_gemini = st.sidebar.text_input("Faça uma pergunta ao Gemini")
        if pergunta_gemini:
            try:
                resposta_gemini = modelo.generate_content(contents=pergunta_gemini)
                st.sidebar.write(resposta_gemini.text)
            except Exception as e:
                st.sidebar.error(f"Erro ao processar a pergunta: {e}")

        # Criar o gráfico com Plotly
        if not dados_filtrados.empty:
            fig = px.line(
                dados_filtrados,
                title="Evolução do Preço das Ações",
                labels={"value": "Preço (R$)", "variable": "Ações"}
            )
            st.plotly_chart(fig, use_container_width=True)

            # Calculo de performance
            texto_performance_ativos = ""

            if len(lista_acoes) == 0:
                lista_acoes = list(dados_filtrados.columns)

            carteira = [1000 for _ in lista_acoes]  # Cada ativo começa com R$ 1.000
            total_inicial_carteira = sum(carteira)

            for i, acao in enumerate(lista_acoes):
                try:
                    # Verificar se existem valores suficientes para cálculo
                    if len(dados_filtrados[acao]) < 2:
                        texto_performance_ativos += f"""<p style="color:gray;">{acao}: Dados insuficientes</p>"""
                        continue

                    # Calcular a performance
                    performance_ativo = dados_filtrados[acao].iloc[-1] / dados_filtrados[acao].iloc[0] - 1
                    performance_ativo = float(performance_ativo)

                    carteira[i] = carteira[i] * (1 + performance_ativo)

                    if performance_ativo > 0:
                        texto_performance_ativos += f"""<p style="color:green;">{acao}: {performance_ativo:.1%} </p>"""
                    elif performance_ativo < 0:
                        texto_performance_ativos += f"""<p style="color:red;">{acao}: {performance_ativo:.1%} </p>"""
                    else:
                        texto_performance_ativos += f"""<p style="color:gray;">{acao}: {performance_ativo:.1%} </p>"""
                except Exception as e:
                    st.warning(f"Erro ao calcular a performance para {acao}: {e}")
                    continue

            # Calcular o valor total da carteira
            total_atual_carteira = sum(carteira)

            # Exibir texto com HTML permitido
            st.markdown(f"""
            ### Performance dos Ativos
            Essa foi a performance de cada ativo no período selecionado:

            {texto_performance_ativos}
            """, unsafe_allow_html=True)

            # Exibir o valor total da carteira
            st.markdown(f"""
            ### Valor Total da Carteira
            O valor total da carteira com base nos rendimentos é: **R$ {total_atual_carteira:,.2f}**
            """)
        else:
            st.warning("Nenhum dado disponível no período selecionado.")











