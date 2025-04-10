# Predição de Sobrevivência no Titanic

## Introdução

Este projeto tem como objetivo prever quais passageiros do Titanic sobreviveram ao naufrágio, utilizando técnicas de machine learning. Foram utilizados dados históricos dos passageiros para treinar um modelo e realizar previsões.

## Análise dos Dados
Uma análise exploratória dos dados foi realizada para entender as características dos passageiros e como elas se relacionam com a probabilidade de sobrevivência. As principais descobertas incluem:

* **[Descobertas:]**
    * A classe social dos passageiros teve um impacto significativo na taxa de sobrevivência.
    * Mulheres especialmente aquelas com filhos tiveram uma taxa de sobrevivência alta .
    * A presença de parentes a bordo contribuiu para o aumento das chances de salvamento.
    * A distribuição dos passageiros por local de embarque levanta a hipótese de que fatores como a classe social podem ter influenciado a localização dos passageiros no navio, com possíveis implicações para as chances de sobrevivência.

## Modelagem e Resultados
* **Modelo utilizado:** [GradientBoostingClassifier]
* **Métricas de avaliação:**
    * **Acurácia:** 83% (conjunto de treino) e 85% (conjunto de teste)
* **Interpretação dos resultados:**
    * O modelo apresentou um bom desempenho na previsão da sobrevivência dos passageiros, indicando que as features selecionadas são relevantes para a tarefa.
    * **[Durante o processo eu treinei varios modelo e quando eu desligava o computador e ligava novamente acurracy e a diferença entre os modelo mudava então não sei ao certo se esse modelo seria uma boa escolha,por isso decide salva o modelo]**

## Conclusão
Através deste projeto, foi possível desenvolver um modelo de machine learning capaz de prever a sobrevivência dos passageiros do Titanic com uma acurácia satisfatória. A análise dos dados e a escolha das features adequadas foram cruciais para o sucesso do modelo. 

## Como Utilizar
* **[Para utilizar você precisa instalar a biblioteca sklearn,também foi utilizado na analise a biblioteca pandas e matplotlib.]**