
# 📊 UserAnalytics – Dashboard de Usuários com Streamlit

## 📦 Descrição

**UserAnalytics** é um aplicativo web interativo desenvolvido com **Streamlit** para analisar e visualizar dados de usuários a partir de arquivos (CSV, Excel, JSON, Parquet, TXT) ou diretamente de um **banco de dados MySQL**.  

O objetivo do projeto é oferecer uma ferramenta prática para análise de dados com foco em **negócios e comportamento de clientes**, permitindo filtrar, visualizar métricas e exportar relatórios em poucos cliques.

O sistema foi projetado para ser **modular e extensível**, com tratamento robusto de dados, detecção automática de formatos, limpeza e padronização de colunas.

---

## 📁 Estrutura do Projeto

```
📂 ARQUIVOEANALISE/
├── 📁 .streamlit/              → Configurações de secrets (MySQL, etc.)
│   └── secrets.toml
├── 📁 env/                     → Ambiente virtual (opcional)
├── 📄 app.py                   → Script principal do Streamlit
├── 📄 requirements.txt         → Dependências do projeto
└── 📄 .gitignore               → Arquivos ignorados pelo Git
```

---

## 🛠️ Tecnologias Utilizadas

- **Python** – Linguagem principal.  
- **Streamlit** – Criação da interface web.  
- **Pandas** – Manipulação e análise de dados.  
- **SQLAlchemy** – Conexão com MySQL.  
- **PyMySQL** – Driver para MySQL.  
- **OpenPyXL / PyArrow** – Suporte a formatos Excel e Parquet.

---

## ⚙️ Instalação

1. **Clonar o repositório:**

```bash
git clone <URL_DO_REPOSITORIO>
cd ARQUIVOEANALISE
```

2. **Criar e ativar um ambiente virtual (opcional):**

```bash
python -m venv env
source env/bin/activate      # Linux/Mac
env\Scripts\activate       # Windows
```

3. **Instalar as dependências:**

```bash
pip install -r requirements.txt
```

4. **Configurar variáveis do banco MySQL (opcional):**  

No arquivo `.streamlit/secrets.toml`:

```toml
[mysql]
user = "usuario"
password = "senha"
host = "localhost"
port = "3306"
database = "meu_banco"
```

Ou configure variáveis de ambiente:

```bash
export MYSQL_USER="usuario"
export MYSQL_PASSWORD="senha"
export MYSQL_DATABASE="meu_banco"
```

---

## 🚀 Execução

Inicie a aplicação com:

```bash
streamlit run app.py
```

Acesse no navegador:

```
http://localhost:8501
```

---

## 🧠 Funcionalidades

### 📥 Importação de Dados  
- Upload de arquivos CSV, Excel, JSON, TXT ou Parquet.  
- Leitura direta de tabelas MySQL.  
- CSV de exemplo incluído para testes rápidos.

### 🧹 Limpeza e Padronização  
- Conversão automática de tipos (datas, números e strings).  
- Padronização de nomes de colunas.  
- Suporte a diferentes formatos e separadores.

### 🔍 Filtros Avançados  
- Filtragem por cidade.  
- Intervalo de datas baseado em `data_de_cadastro`.  
- Limite de registros exibidos.

### 📊 Visão Geral (KPIs)  
- Total de usuários.  
- Média de idade.  
- Valor total e médio de compras.

### 📈 Visualizações  
- Gráfico de novos usuários ao longo do tempo (diário ou mensal).  
- Contagem de usuários por cidade.  
- Histograma de idade.  
- Dispersão entre idade × valor de compras.

### 📋 Tabelas e Exportação  
- Lista dos usuários com compras acima da média.  
- Download direto do CSV com usuários filtrados.  
- Exibição dos dados filtrados e originais.

---

## 📚 Exemplo de Uso

1. Faça upload de um CSV com colunas como:

```csv
nome,idade,cidade,data_de_cadastro,valor_compras
João,28,Uberlândia,2023-06-01,350.75
Maria,34,Belo Horizonte,2023-05-10,120.50
```

2. Aplique filtros na barra lateral:

- ✅ Selecione cidades específicas  
- 📆 Escolha um período de datas  
- 📊 Ajuste o limite de registros exibidos  

3. Explore as abas do dashboard:

- **Visão Geral:** KPIs com dados resumidos.  
- **Gráficos:** Evolução de usuários, histogramas e dispersões.  
- **Tabelas:** Lista dos usuários com compras acima da média e opção de download.  
- **Dados Brutos:** Exibição completa sem filtros.

---

## 💡 Dicas

- Use o modo **“Usar CSV de exemplo”** para testar rapidamente.  
- Configure a conexão com MySQL no `secrets.toml` para análise em tempo real.  
- Utilize os filtros para análises segmentadas e contextualizadas.

---

## 🤝 Contribuição

Contribuições são super bem-vindas!  
Sinta-se livre para abrir **Issues** e **Pull Requests** com melhorias ou novas funcionalidades.

---

## 📜 Licença

Este projeto está licenciado sob a **MIT License** – veja o arquivo `LICENSE` para mais detalhes.
