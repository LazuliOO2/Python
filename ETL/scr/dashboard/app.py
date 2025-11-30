import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
import os

load_dotenv(dotenv_path="../transform/.env")

print("HOST:", os.getenv("MYSQL_HOST"))
print("PORT:", os.getenv("MYSQL_PORT"))
print("USER:", os.getenv("MYSQL_USER"))
print("DATABASE:", os.getenv("MYSQL_DATABASE"))
# Variáveis de ambiente
host = os.getenv("MYSQL_HOST")
port = int(os.getenv("MYSQL_PORT"))
user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
database = os.getenv("MYSQL_DATABASE")

engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')

df = pd.read_sql_query("SELECT * FROM produtos", engine)
# cria titulos
st.title('📊 Pesquisa de Mercado - Notebooks no Mercado Livre')
# Cria um subtitulos
st.subheader('💡 KPIs principais')
# Cria três colunas de largura igual na interface.As variáveis col1, col2 e col3 representam cada uma das colunas, permitindo adicionar conteúdo específico em cada uma delas.
col1, col2, col3 = st.columns(3)
# KPI 1: Número total de itens
# O método shape retorna uma tupla com o número de linhas e colunas do DataFrame.[0] acessa primeiro elemento da tupla
total_itens = df.shape[0]
#  método metric é usado para exibir um valor numérico com um rótulo (label) em um painel interativo.
# value=total_itens: Define o valor que será exibido. Nesse caso, é o número total de linhas do DataFrame (total_itens).
col1.metric(label="🖥️ Total de Notebooks", value=total_itens)

# KPI 2: Número de marcas únicas
# Calcula o número de valores únicos na coluna 'brand' do DataFrame 'df'.
unique_brands = df['brand'].nunique()
# Exibe o número de marcas únicas como uma métrica em uma das colunas da interface (col2).
# 'label' define o texto que aparece acima do valor da métrica.
# 'value' define o valor numérico a ser exibido.
col2.metric(label="🏷️ Marcas Únicas", value=unique_brands)

# KPI 3: Preço médio novo (em reais)
# Calcula a média dos valores na coluna 'new_price' do DataFrame 'df'.
average_new_price = df['new_price'].mean()
# Exibe o preço médio como uma métrica em outra coluna da interface (col3).
# 'label' define o texto que aparece acima do valor da métrica.
# 'value' define o valor a ser exibido, formatado para duas casas decimais e precedido por "R$".
f"{average_new_price:.2f}"
col3.metric(label="💰 Preço Médio (R$)", value=f"{average_new_price:.2f}")

# Marcas mais frequentes
# Define um subtítulo para a seção de marcas mais frequentes.
st.subheader('🏆 Marcas mais encontradas até a 10ª página')
# Cria duas colunas com proporções de largura 4:2 na interface.
col1, col2 = st.columns([4, 2])
# Conta a frequência de cada valor único na coluna 'brand' e ordena em ordem decrescente.
top_brands = df['brand'].value_counts().sort_values(ascending=False)
# Exibe um gráfico de barras na primeira coluna (col1) mostrando a frequência das marcas.
col1.bar_chart(top_brands)
# Exibe os dados de frequência das marcas como texto na segunda coluna (col2).
col2.write(top_brands)

# Preço médio por marca
# Define um subtítulo para a seção de preço médio por marca.
st.subheader('💵 Preço médio por marca')
# Cria duas colunas com proporções de largura 4:2 na interface.
col1, col2 = st.columns([4, 2])
# Cria um novo DataFrame contendo apenas as linhas onde o preço ('new_price') é maior que zero.
df_non_zero_prices = df[df['new_price'] > 0]
# Agrupa o DataFrame 'df_non_zero_prices' pela coluna 'brand', calcula a média da coluna 'new_price' para cada grupo e ordena em ordem decrescente.
average_price_by_brand = df_non_zero_prices.groupby('brand')['new_price'].mean().sort_values(ascending=False)
# Exibe um gráfico de barras na primeira coluna (col1) mostrando o preço médio por marca.
col1.bar_chart(average_price_by_brand)
# Exibe os dados do preço médio por marca como texto na segunda coluna (col2).
col2.write(average_price_by_brand)

# Satisfação média por marca
# Define um subtítulo para a seção de satisfação média por marca.
st.subheader('⭐ Satisfação média por marca')
# Cria duas colunas com proporções de largura 4:2 na interface.
col1, col2 = st.columns([4, 2])
# Cria um novo DataFrame contendo apenas as linhas onde o número de avaliações ('reviews_rating_number') é maior que zero.
df_non_zero_reviews = df[df['reviews_rating_number'] > 0]
# Agrupa o DataFrame 'df_non_zero_reviews' pela coluna 'brand', calcula a média da coluna 'reviews_rating_number' para cada grupo e ordena em ordem decrescente.
satisfaction_by_brand = df_non_zero_reviews.groupby('brand')['reviews_rating_number'].mean().sort_values(ascending=False)
# Exibe um gráfico de barras na primeira coluna (col1) mostrando a satisfação média por marca.
col1.bar_chart(satisfaction_by_brand)
# Exibe os dados da satisfação média por marca como texto na segunda coluna (col2).
col2.write(satisfaction_by_brand)