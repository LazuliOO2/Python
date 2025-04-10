def calcular_fibonacci(n):
    # Inicializa a sequência de Fibonacci com os dois primeiros números
    fib_sequence = [0, 1]
    #Índices negativos em Python: Em Python, índices negativos acessam elementos de uma lista a partir do final
    # Continua gerando números da sequência até que o último número seja maior ou igual a n
    while fib_sequence[-1] < n:
        # Adiciona um novo número à sequência somando os dois últimos números
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    
    return fib_sequence

def pertence_a_fibonacci(numero):
    # Gera a sequência de Fibonacci até o número informado
    fib_sequence = calcular_fibonacci(numero)
    
    # Verifica se o número informado pertence à sequência
    if numero in fib_sequence:
        return f"O número {numero} pertence à sequência de Fibonacci.\nSequência gerada: {fib_sequence}"
    else:
        return f"O número {numero} não pertence à sequência de Fibonacci.\nSequência gerada: {fib_sequence}"

# Número a ser verificado
numero = int(input("Informe um número: "))
print(pertence_a_fibonacci(numero))

