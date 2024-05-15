import pandas as pd
import numpy as np
import streamlit as st
from sqlalchemy import create_engine
import requests
import secrets
import plotly.express as px
import plotly.graph_objects as go
from cria_imagens import *
from datetime import datetime
#setando a configuração da pagina1

#setando a configuração da pagina
st.set_page_config(layout='wide', page_title="Boletins Itajuba")

@st.cache_data
@st.cache
def converte_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def local_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)

local_css("styles.css")

left_co,aux1, cent_co,aux2,last_coco = st.columns([1.6,1.5,2,1.6,1.5])
caminho_imagens_uberlandia = 'logo.jpg'
with cent_co:
    st.image(caminho_imagens_uberlandia, use_column_width=True)


conn = st.connection('mysql', type='sql')

tabela = 'animais_peconhentos_ita'

def query_dados():
    return f'''
SELECT DT_NOTIFIC, idade_anos FROM {tabela} WHERE ID_MUNICIP = 313240
'''


def query_testes():
    return f'''

SELECT be.nome as Escolaridade, bs.Nome as Sexo, br.Nome as Raça FROM animais_peconhentos doenca
INNER JOIN Base_CS_Escolar be ON be.ID = doenca.CS_ESCOL_N
INNER JOIN Base_CS_SEXO bs ON bs.sigla = doenca.CS_SEXO
INNER JOIN Base_CS_Raca br ON br.ID = doenca.CS_RACA
WHERE doenca.ID_MUNICIP = 313240
'''


# Executar a primeira consulta
df = conn.query(query_dados(), ttl=600)
# Executar a segunda consulta

df_testes = conn.query(query_testes(), ttl=600)

rotulos_faixas = ['0-20', '21-30', '31-40', '41-50', '51-60', '60+']
faixas_idade = [0, 20, 30, 40, 50, 60, float('inf')]
# Criando a coluna de faixas de idade
df['Faixa_Idade'] = pd.cut(df['idade_anos'], bins=faixas_idade, labels=rotulos_faixas, right=False)




df['Ano_Mes'] = df['DT_NOTIFIC'].dt.strftime('%Y-%m')

# Agrupando e contando as ocorrências de cada ano/mês
contagem_meses_ano = df.groupby('Ano_Mes').size().reset_index(name='Contagem')
contagem_raca =  df_testes.groupby('Raça').size().reset_index(name='Contagem')
contagem_escolaridade = df_testes.groupby('Escolaridade').size().reset_index(name='Contagem')
contagem_sexo = df_testes.groupby('Sexo').size().reset_index(name='Contagem')
contagem_faixa_idade = df.groupby('Faixa_Idade').size().reset_index(name='Contagem')


quantidade = df.shape[0]
data_maxima = max(df['DT_NOTIFIC'])
data_maxima_formatada = data_maxima.strftime('%d/%m/%Y')


######################################################################################################################################
with last_coco:
    st.metric("Data mais recente identificada no SINAN", data_maxima_formatada)


fig_datas = criar_grafico_linhas(contagem_meses_ano, 'Ano_Mes', 'Contagem', 'Casos por mes e ano', 300)
st.altair_chart(fig_datas, use_container_width=True)

fig_raca = cria_grafico_pizza(contagem_raca,'Contagem', 'Raça', 'Casos por raça', 0.2, 'middle')

fig_faixa_idade = criar_grafico_horizontal(contagem_faixa_idade, 'Contagem', 'Faixa_Idade', "Casos por idade", True, 400)
col1, col2 = st.columns([1,1])

with col1:
    st.altair_chart(fig_faixa_idade, use_container_width=True)
with col2:
    st.altair_chart(fig_raca, use_container_width=True)


fig_sexo = cria_grafico_pizza(contagem_sexo,'Contagem', 'Sexo', 'Casos por sexo', 0.2, 'middle')


col11, col22 = st.columns([1,1])

with col11:
    st.altair_chart(fig_sexo, use_container_width=True)
with col22:
    st.altair_chart(fig_sexo, use_container_width=True)