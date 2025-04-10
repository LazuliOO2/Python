# Os desafios 4 e 5 são de lógica. Embora dê para fazer o 4 com programação, vamos fazer só com README a resposta.

Descubra a lógica e complete o próximo elemento:
a) 1, 3, 5, 7, ___
b) 2, 4, 8, 16, 32, 64, ____
c) 0, 1, 4, 9, 16, 25, 36, ____
d) 4, 16, 36, 64, ____
e) 1, 1, 2, 3, 5, 8, ____
f) 2, 10, 12, 16, 17, 18, 19, ____

Vamos descobrir a lógica e completar os próximos elementos:

a) 1, 3, 5, 7, **9**

**Lógica:** Sequência de números ímpares consecutivos.

b) 2, 4, 8, 16, 32, 64, **128**

**Lógica:** Cada número é o dobro do anterior.

c) 0, 1, 4, 9, 16, 25, 36, **49**

**Lógica:** Sequência dos quadrados perfeitos ($$n^2$$).

d) 4, 16, 36, 64, **100**

**Lógica:** Sequência dos quadrados perfeitos ($$n^2$$), começando de $$2^2$$.

e) 1, 1, 2, 3, 5, 8, **13**

**Lógica:** Sequência de Fibonacci, onde cada número é a soma dos dois anteriores.

f) 2, 10, 12, 16, 17, 18, 19, **20**

**Lógica:** Sequência de números que contêm o dígito 2.

# Caso queira criar um programa para resolve isso : 
a) Sequência de números ímpares consecutivos:

Python

def odd_sequence(n):
    return [2 * i + 1 for i in range(n)]

print(odd_sequence(5))  # Saída: [1, 3, 5, 7, 9]
Código gerado por IA. Examine e use com cuidado. Mais informações em perguntas frequentes.
b) Cada número é o dobro do anterior:

Python

def double_sequence(n):
    sequence = [2]
    for i in range(1, n):
        sequence.append(sequence[-1] * 2)
    return sequence

print(double_sequence(7))  # Saída: [2, 4, 8, 16, 32, 64, 128]
Código gerado por IA. Examine e use com cuidado. Mais informações em perguntas frequentes.
c) Sequência dos quadrados perfeitos (n^2):

Python

def perfect_squares(n):
    return [i ** 2 for i in range(n)]

print(perfect_squares(8))  # Saída: [0, 1, 4, 9, 16, 25, 36, 49]
Código gerado por IA. Examine e use com cuidado. Mais informações em perguntas frequentes.
d) Sequência dos quadrados perfeitos (n^2), começando de 2^2:

Python

def perfect_squares_from_2(n):
    return [(i + 2) ** 2 for i in range(n)]

print(perfect_squares_from_2(5))  # Saída: [4, 16, 36, 64, 100]
Código gerado por IA. Examine e use com cuidado. Mais informações em perguntas frequentes.
e) Sequência de Fibonacci:

Python

def fibonacci_sequence(n):
    sequence = [1, 1]
    while len(sequence) < n:
        sequence.append(sequence[-1] + sequence[-2])
    return sequence

print(fibonacci_sequence(7))  # Saída: [1, 1, 2, 3, 5, 8, 13]
Código gerado por IA. Examine e use com cuidado. Mais informações em perguntas frequentes.
f) Sequência de números que contêm o dígito 2:

Python

def contains_digit_2(n):
    sequence = []
    i = 2
    while len(sequence) < n:
        if '2' in str(i):
            sequence.append(i)
        i += 1
    return sequence

print(contains_digit_2(8))  # Saída: [2, 12, 20, 21, 22, 23, 24, 25]

# Você está em uma sala com três interruptores, cada um conectado a uma lâmpada em salas diferentes. Você não pode ver as lâmpadas da sala em que está, mas pode ligar e desligar os interruptores quantas vezes quiser. Seu objetivo é descobrir qual interruptor controla qual lâmpada. Como você faria para descobrir, usando apenas duas idas até uma das salas das lâmpadas, qual interruptor controla cada lâmpada?

Ligue o primeiro interruptor e deixe-o ligado por alguns minutos. Isso fará com que a lâmpada conectada a esse interruptor aqueça.
Desligue o primeiro interruptor e ligue o segundo interruptor. Deixe o segundo interruptor ligado.
Vá até a sala das lâmpadas pela primeira vez.
Agora, você terá três situações possíveis:

A lâmpada que está acesa é controlada pelo segundo interruptor.
Toque nas lâmpadas que estão apagadas:
A lâmpada que está quente é controlada pelo primeiro interruptor.
A lâmpada que está fria é controlada pelo terceiro interruptor.



