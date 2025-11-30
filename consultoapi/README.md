
# 🤖 LittleOO2 – Consultor de CEP com Humor Robótico

## 📦 Descrição

**LittleOO2** é um assistente de terminal que consulta **CEPs brasileiros** usando a API pública [ViaCEP](https://viacep.com.br) e enriquece os resultados com informações detalhadas do [IBGE](https://servicodados.ibge.gov.br/api/docs/localidades).  

Ele foi desenvolvido com foco em **interatividade e diversão**, simulando um robô que "pensa", digita e até **faz piadinhas enquanto busca os dados**.  
Além disso, o projeto oferece funcionalidades como:

- 📍 Consulta detalhada de qualquer CEP brasileiro.  
- 🧠 Extração de informações geográficas do município pelo IBGE.  
- 🗺️ Exibição simbólica da região com mapa ASCII.  
- 📚 Histórico de consultas e exportação automática para TXT.  
- 📊 Comparação de dois CEPs com dados de região e microrregião.

---

## 📁 Estrutura do Projeto

```
📂 consultoapi/
├── 📁 env/                       → Ambiente virtual (opcional)
├── 📁 historico_LittleOO2/      → Histórico e arquivos TXT exportados
├── 📄 LittleOO2.py              → Script principal (robô consultor)
└── 📄 requirements.txt          → Dependências do projeto
```

---

## 🛠️ Tecnologias Utilizadas

- **Python** – Linguagem principal do projeto.  
- **Requests** – Para chamadas às APIs públicas (ViaCEP e IBGE).  
- **JSON** – Armazenamento do histórico de consultas.  
- **Regex (re)** – Para sanitização e limpeza de dados.  
- **OS / Time / Datetime** – Manipulação de arquivos, diretórios e formatação de datas.  

---

## ⚙️ Instalação

1. **Clonar o repositório:**

```bash
git clone <URL_DO_REPOSITORIO>
cd consultoapi
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

---

## 🚀 Execução

Para iniciar o robô consultor, basta executar o script:

```bash
python LittleOO2.py
```

Ao iniciar, você verá o banner divertido do robô e um menu com as opções:

```
Menu Principal:
1. Consultar CEP
2. Ver histórico
3. Comparar CEPs
4. Sair
```

---

## 🧠 Funcionalidades

### 1. 🔍 Consultar CEP  
Digite um CEP (com ou sem hífen) e veja:

- Logradouro, bairro, cidade e estado.  
- Região geográfica e microrregião do IBGE.  
- Um mini mapa ASCII com a localização simbólica.  
- Exportação automática dos resultados em `.txt`.

---

### 2. 📜 Histórico de Consultas  
Veja as últimas consultas feitas (máximo de 5 exibidas) e mantenha um registro automático em:

```
historico_LittleOO2/historico_ceps.json
```

---

### 3. 📊 Comparar CEPs  
Compare dois CEPs e descubra:

- Se pertencem à mesma região geográfica.  
- As regiões e microrregiões de cada um.  
- Dados detalhados do IBGE para cada município.

---

### 4. 🧪 Exportação Automática  
Cada consulta gera um arquivo TXT:

```
historico_LittleOO2/CEP_<CEP>_YYYYMMDD_HHMM.txt
```

O sistema mantém apenas os últimos `MAX_EXPORTS_PER_CEP` arquivos (padrão: 10), removendo automaticamente os mais antigos.

---

## 📚 Exemplo de Uso

### ✅ Consulta de CEP:

```
Digite o CEP: 01001-000

📍 CEP 01001-000 - São Paulo/SP
   Rua: Praça da Sé
   Bairro: Sé
   Cidade: São Paulo
   Estado: SP

🗺  Mapa Simbólico:
    ┌───────────┐
    │    SP     │
    │   █████   │
    │   █▓▓▓█   │
    │   █▓★▓█   │
    └───────────┘
    (★ = Local aproximado — confia no algoritmo 😎)

🧠 Curiosidade Geográfica (IBGE):
   - Município: São Paulo (SP)
   - Microrregião: São Paulo
   - Estado: São Paulo
   - Região: Sudeste

📄 Arquivo CEP_01001000_20251012_2230.txt salvo!
```

---

## 💡 Dica

Quer comparar rapidamente dois endereços?

```
Menu Principal → 3. Comparar CEPs
```

Você verá se pertencem à mesma região e dados detalhados do IBGE para cada localidade.

---

## 📌 Observações

- O projeto utiliza APIs públicas e não requer autenticação.  
- Funciona 100% no terminal e não necessita de navegador ou interface gráfica.  
- Pode ser facilmente integrado em outras aplicações Python para consultas automáticas de CEP.

---

## 🤝 Contribuição

Contribuições são super bem-vindas!  
Se quiser adicionar novas funcionalidades (como exportação para CSV ou interface web), basta abrir uma **Pull Request**.

---

## 📜 Licença

Este projeto está licenciado sob a **MIT License** – veja o arquivo `LICENSE` para mais detalhes.
