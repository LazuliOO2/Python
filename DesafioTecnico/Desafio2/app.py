import unicodedata
#A função unicodedata.normalize é usada para decompor os caracteres acentuados em seus componentes básicos. O parâmetro 'NFD' (Normalization Form D) significa “Forma de Normalização D”, que decompõe os caracteres acentuados em caracteres base e marcas de acentuação separadas. Por exemplo, a letra ‘á’ seria decomposta em ‘a’ e uma marca de acento
# Função para remover acentuação
def remover_acentuacao(texto):
    return ''.join(
        caractere for caractere in unicodedata.normalize('NFD', texto)
        if unicodedata.category(caractere) != 'Mn'
    )

# Solicitando a entrada do usuário
string = input("Digite uma string: ")

# Removendo acentuação e transformando a string em maiúscula
string_sem_acentos = remover_acentuacao(string).upper()

# Inicializando o contador
contador = 0

# Iterando sobre cada caractere na string
for caractere in string_sem_acentos:
    # Verificando se o caractere é 'A'
    if caractere == 'A':
        contador += 1

# Verificando se a letra 'A' foi encontrada
if contador > 0:
    print(f"A letra 'A' foi encontrada {contador} vezes na string.")
else:
    print("A letra 'A' não foi encontrada na string.")
