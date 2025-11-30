import PySimpleGUI as sg
import mysql.connector

# Classe para representar um livro
class Livro:
    def __init__(self, titulo, autor, ano_publicado):
        self.titulo = titulo
        self.autor = autor
        self.ano_publicado = ano_publicado

    def __str__(self):
        return f"{self.titulo} por {self.autor}, Publicado em {self.ano_publicado}"

# Conectar ao banco de dados MySQL
def conectar_banco():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="biblioteca"
    )

# Adicionar um livro ao banco de dados
def adicionar_livro(titulo, autor, ano_publicado):
    conexao = conectar_banco()
# Um cursor no MySQL é como um ponteiro que permite navegar linha a linha dentro do resultado de uma consulta.Você pode usar qualquer tipo de marcador - um pedaço de papel, uma caneta, um clipe - para marcar onde você parou na leitura. O importante é que ele sirva como referência para você voltar ao mesmo ponto.Então por isso eu posso nomeia o curso da maneira que eu queira
    cursor = conexao.cursor()
# Os %s são chamados de placeholders ou marcadores de posição. Eles servem para indicar onde os valores reais serão inseridos na sua consulta SQL durante a execução.Porque usar? Evitam a injeção de SQL, que é uma vulnerabilidade comum em aplicações web. Ao usar placeholders, você garante que os valores inseridos na consulta são tratados como dados e não como código SQL
    cursor.execute("INSERT INTO livros (titulo, autor, ano_publicado) VALUES (%s, %s, %s)", (titulo, autor, ano_publicado))
    conexao.commit()
    conexao.close()
    print(f"{titulo} foi adicionado à biblioteca.")

# Obter todos os livros do banco de dados
def obter_livros():
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("SELECT titulo, autor, ano_publicado FROM livros")
# O método cursor.fetchall() retorna todos os registros encontrados pela consulta em uma lista de tuplas
    livros = cursor.fetchall()
    conexao.close()
    return [Livro(titulo, autor, ano_publicado) for titulo, autor, ano_publicado in livros]

# Pesquisar um livro no banco de dados pelo título
def pesquisar_livro(titulo_pesquisado):
    """Pesquisa um livro no banco de dados pelo título.

    Args:
        titulo_pesquisado (str): O título do livro a ser pesquisado.

    Returns:
        list: Uma lista com os resultados da pesquisa.
    """
    conexao = conectar_banco()
    cursor = conexao.cursor()
# O uso do LIKE permite realizar pesquisas mais flexíveis, como encontrar livros que contenham a palavra "Python" no título, independentemente de ser no início, meio ou fim
    consulta = "SELECT titulo, autor, ano_publicado FROM livros WHERE titulo LIKE %s"
    valores = (f'%{titulo_pesquisado}%',)
    cursor.execute(consulta, valores)
    resultados = cursor.fetchall()
    conexao.close()
    return [Livro(titulo, autor, ano_publicado) for titulo, autor, ano_publicado in resultados]

# Layout da interface gráfica
layout = [
    [sg.Text('Título'), sg.InputText(key='titulo')],
    [sg.Text('Autor'), sg.InputText(key='autor')],
    [sg.Text('Ano Publicado'), sg.InputText(key='ano_publicado')],
    [sg.Button('Adicionar Livro'), sg.Button('Sair')],
    [sg.Text('Pesquisar'), sg.InputText(key='pesquisa')],
    [sg.Button('Pesquisar Livro')],
    [sg.Listbox(values=[], size=(60, 10), key='biblioteca')]
]

# Criar a janela
janela = sg.Window('Biblioteca', layout)

# Iniciar o loop como verdadeiro para que o loop seja infinito, só encerrado com a condição break
while True:
 # Criar duas variáveis para capturar o valor e evento que estão acontecendo
    # O valor que o usuário digitou no input e o evento que seria adicionar ou sair
    # Depois usamos janela.read para ler esses eventos
    evento, valores = janela.read()
 # Especificar os eventos: se o evento for closed (fechar no X) ou Sair (definido no botão ali em cima), ele vai break (quebrar) e encerrar o programa
    if evento == sg.WIN_CLOSED or evento == 'Sair':
        break
# Caso o evento seja adicionar livro, ele vai adicionar e depois exibir um print com as informações
    if evento == 'Adicionar Livro':
        titulo = valores['titulo']
        autor = valores['autor']
        ano_publicado = valores['ano_publicado']
        adicionar_livro(titulo, autor, ano_publicado)
 # Atualizar a Listbox com os livros da biblioteca
        janela['biblioteca'].update([str(livro) for livro in obter_livros()])
# se o evento seja Pesquisar Livro ele vai pesquisar e logo em seguida vai atualizar a listbox
    if evento == 'Pesquisar Livro':
        titulo_pesquisado = valores['pesquisa']
        resultados = pesquisar_livro(titulo_pesquisado)
        janela['biblioteca'].update([str(livro) for livro in resultados])

janela.close()