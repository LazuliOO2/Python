# Tem 2 arquivos: o primeiro seria de aula que eu fiz na faculdade e o segundo, modif.py, seria as modificações que eu fiz no código para que refletisse o que eu estou aprendendo.

# aula.py 
Nesse arquivo seria a aula da faculdade onde você cria a classe Livro utilizando POO, adiciona os livros e cria um gráfico com os livros utilizando matplotlib.

# modif.py
Seria a biblioteca digital Python onde decidi colocar interface e banco de dados para refletir um projeto real, além de, claro, aprimorar as habilidades que estou aprendendo, porque, em uma aplicação real, a biblioteca não teria conhecimento técnico e precisaria de uma interface para ajudar, além de, claro, precisar de um banco de dados para adicionar os livros e pesquisar por eles.

# Biblioteca Digital Python

## Descrição
Aplicação Python para gerenciamento de uma biblioteca, utilizando uma interface gráfica intuitiva e um banco de dados MySQL para armazenar as informações dos livros. A ferramenta permite adicionar novos livros, pesquisar por título e visualizar a coleção completa.

## Funcionalidades
- **Cadastro de livros**: Permite adicionar novos livros ao catálogo, incluindo título, autor e ano de publicação.
- **Pesquisa de livros**: Realiza pesquisas por título, exibindo os resultados de forma clara e organizada.
- **Interface gráfica**: Possui uma interface intuitiva desenvolvida com PySimpleGUI, facilitando a interação do usuário.
- **Integração com banco de dados**: Utiliza MySQL para armazenar as informações dos livros de forma persistente.

## Tecnologias Utilizadas
- **Python**: Linguagem de programação principal.
- **PySimpleGUI**: Biblioteca para criação de interfaces gráficas.
- **MySQL**: Sistema gerenciador de banco de dados relacional.
- **mysql-connector-python**: Conector Python para MySQL.

## Pré-requisitos
- **Python**: Instalar a versão mais recente do Python.
- **PySimpleGUI**: Instalar com `pip install PySimpleGUI`.
- **mysql-connector-python**: Instalar com `pip install mysql-connector-python`.
- **MySQL**: Instalar e configurar o banco de dados MySQL.

## como utilizar:
Clone o repositório: git clone https://[seu_repositorio]
Instale as dependências: pip install -r requirements.txt (crie um arquivo requirements.txt listando as dependências)
Configure o banco de dados: Crie um banco de dados chamado "biblioteca" e uma tabela "livros" com os campos "titulo", "autor" e "ano_publicado".
Execute o script: python sua_aplicacao.py