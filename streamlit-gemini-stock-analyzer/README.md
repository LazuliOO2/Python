# Streamlit App para Análise de Ações com Gemini

Este aplicativo Streamlit permite que você visualize e analise o desempenho de ações da bolsa brasileira, com a ajuda do chatbot Gemini para responder a perguntas sobre o mercado financeiro.

## Introdução

O aplicativo usa as seguintes bibliotecas:

- **streamlit**: para criar a interface web interativa.
- **pandas**: para manipulação e análise de dados.
- **yfinance**: para baixar dados históricos de ações do Yahoo Finance.
- **plotly.express**: para criar gráficos interativos.
- **google.generativeai**: para interagir com o chatbot Gemini.

## Instalação

### Instale as bibliotecas:

```bash
pip install streamlit pandas yfinance plotly.express google-generativeai
```

### Obtenha a chave da API Gemini:

1. Acesse o [Google AI Studio](https://ai.google/studio) e crie um novo projeto.
2. Gere uma chave de API e copie-a.

### Configure a variável de ambiente:

- **No terminal (PowerShell):**

```bash
$env:GEMINI_API_KEY = "sua_chave_api"
```

- **No Windows:**
  1. Pesquise por "Variáveis de ambiente" no menu Iniciar.
  2. Clique em "Editar as variáveis de ambiente do sistema".
  3. Na aba "Avançado", clique em "Variáveis de Ambiente...".
  4. Em "Variáveis do sistema", clique em "Novo...".
  5. Insira o nome da variável como `GEMINI_API_KEY` e o valor como sua chave de API.
  6. Clique em "OK" em todas as janelas.

## Explicação do Código

Este aplicativo foi criado com base em um tutorial da Hashtag Programação, utilizando o Streamlit para a interface gráfica e o chatbot Gemini para auxiliar na análise.

- **Interface**: A interface do Streamlit permite que você selecione as ações que deseja visualizar, o período de tempo e faça perguntas ao Gemini sobre o mercado financeiro.
- **Gráficos**: Os gráficos são gerados com o Plotly.express, que oferece maior desempenho e interatividade em comparação com os gráficos nativos do Streamlit, especialmente para grandes conjuntos de dados.
- **Dados**: Os dados históricos das ações são baixados do Yahoo Finance usando a biblioteca yfinance.
- **Web Scraping**: Os tickers das ações podem ser obtidos através de web scraping. Um exemplo de como fazer isso está disponível no meu repositório do GitHub.
- **Gemini**: O chatbot Gemini é integrado ao aplicativo para responder a perguntas sobre o mercado financeiro e fornecer insights adicionais.

> **Observação**: Este aplicativo foi desenvolvido com foco na análise de ações da bolsa brasileira.Ele está incompleto e em breve recebera atualizações

## Como Usar

1. Clone o repositório para o seu ambiente local:

```bash
git clone <URL_DO_REPOSITORIO>
cd <NOME_DO_REPOSITORIO>
```

2. Instale as dependências necessárias:

```bash
pip install -r requirements.txt
```

3. Execute o arquivo para iniciar o Streamlit:

```bash
streamlit run app.py
```
