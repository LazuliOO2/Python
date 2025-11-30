# ETL Process and Data Dashboard for Mercado Livre Products

## Descrição

Este projeto consiste em um processo ETL (Extração, Transformação e Carga) para coletar dados de produtos do Mercado Livre e um painel de dashboard para visualizá-los. O objetivo é fornecer insights sobre preços, marcas e satisfação do cliente para notebooks.

## Estrutura do Projeto

```

📂 scr
├── 📄 README.md           → Documentação principal
├── 📂 transform/
│   └── 📄 app.ipynb       → Script Jupyter para transformar e carregar os dados
├── 📂 mercadolivre/
│   ├── 📄 data.json       → Dados coletados (saída do Scrapy)
│   ├── 📄 scrapy.cfg      → Configuração do Scrapy
│   ├── 📂 mercadolivre/
│   │   ├── 📄 items.py    → Definição dos itens do Scrapy
│   │   ├── 📄 settings.py → Configurações do Scrapy
│   │   ├── 📂 spiders/
│   │   │   ├── 📄 init.py
│   │   │   └── 📄 notebook.py → Spider do Scrapy para coletar dados de notebooks
│   │   └── 📄 init.py
├── 📂 dashboard/
│   └── 📄 app.py          → Script Streamlit para criar o dashboard

```
## Tecnologias Utilizadas

- **Python**: Linguagem de programação principal
- **Scrapy**: Framework para web scraping (coleta de dados)
- **Pandas**: Biblioteca para manipulação e análise de dados
- **SQLAlchemy**: Toolkit SQL para interagir com bancos de dados
- **Streamlit**: Framework para criar aplicativos web interativos
- **MySQL**: Banco de dados para armazenar os dados
- **dotenv**: Biblioteca para carregar variáveis de ambiente

## Instalação

1.  **Clonar o repositório:**

    ```sh
    git clone <URL_DO_REPOSITORIO>
    cd <NOME_DO_REPOSITORIO>
    ```
2.  **Configurar o ambiente virtual (opcional, mas recomendado):**

    ```sh
    python -m venv env
    source env/bin/activate # ou env\Scripts\activate no Windows
    ```
3.  **Instalar as dependências:**

    ```
    pip install scrapy pandas sqlalchemy python-dotenv streamlit mysql-connector-python
    ```
4.  **Configurar as variáveis de ambiente:**

    Crie um arquivo `.env` na pasta `scr/transform/` com as credenciais do banco de dados MySQL:

    ```env
    MYSQL_HOST=seu_host
    MYSQL_PORT=3306
    MYSQL_USER=seu_usuario
    MYSQL_PASSWORD=sua_senha
    MYSQL_DATABASE=seu_banco_de_dados
    ```

## Execução

```
scrapy startproject mercadolivre
```

```
cd mercadolivre
```


```
scrapy genspider notebook mercadolivre.com.br
```

```
scrapy shell
```


```
use fetch('https://lista.mercadolivre.com.br/computadore#D[A:computadore]')
```

```
Defina o user-agent é so pesquisa meu user agent e pegar e copia ou usar inspecionar 
```

```
Agora usamos o comando response para obter os dado que já estão salvo como response.css('.Mais a class que deseja')
```

```
usamos o comando para salva scrapy crawl notebook -o ../data/data.json
```

## 📌 Observações
Este projeto foi desenvolvido exclusivamente para fins educacionais.
Todos os dados coletados foram utilizados apenas para testes e já foram excluídos do banco de dados.


## Contribuição

Sinta-se à vontade para contribuir com melhorias, correções de bugs ou novas funcionalidades. Basta abrir uma **Pull Request**.

## Licença

Este projeto está sob a licença MIT.