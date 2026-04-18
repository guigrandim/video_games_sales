#==================================
# Import Library
#==================================

import pandas as pd
import os
import datetime
import streamlit as st
import folium
from PIL import Image
import plotly.express as px
import re
from utils.data_loader import dataset_clean
from datetime import date

#==================================
# Configuration Page
#==================================

st.set_page_config(page_title = 'Volume e Vendas', page_icon = '📉', layout = 'wide')

#===================================
# Functions
#===================================

@st.cache_data
def get_data():
    return dataset_clean()

def release_game_per_year(df1):
    release_game_year = df1.loc[:, ['title', 'release_date']]
    release_game_year['release_year'] = pd.to_datetime(release_game_year['release_date']).dt.year
    
    release_by_year = release_game_year.groupby('release_year')['title'].count().reset_index()
    release_by_year.columns = ['Ano', 'Qtde de Lançamentos']
    
    fig = px.bar(
        release_by_year, 
        x='Ano', 
        y='Qtde de Lançamentos', 
        title='Lançamentos por Ano', 
        template = 'plotly_dark', 
        color_discrete_sequence=['#00CC96']
    )
    
    return fig

def sales_game_per_year(df1):
    sales_global_year = df1.loc[:, ['total_sales', 'release_date']]
    sales_global_year['release_year'] = pd.to_datetime(sales_global_year['release_date']).dt.year
    
    sales_by_year = sales_global_year.groupby('release_year')['total_sales'].sum().reset_index()
    sales_by_year = sales_by_year[sales_by_year['total_sales'] > 0]
    
    sales_by_year.columns = ['Ano', 'Qtde de Vendas']
    
    fig = px.bar(sales_by_year,
                 x='Ano',
                 y='Qtde de Vendas',
                 title='Vendas Por Ano (Milhões de Unidades)',
                 template = 'plotly_dark',
                 color_discrete_sequence=['#00CC96']
    )
    
    return fig

#-------------------------------------------- Beginning of the logical structure code --------------------- #

#===============================================
# Select Directory - Load Files and Clean Dataset
#===============================================

df1 = get_data()

#======================================
# PHASE 2 - Create a Sidebar
#======================================

#1. Load Logo Page

#2. Configuration Filters
#2.1 - Date
data_minima = date(2024, 12, 31)
data_maxima = date(1970, 1, 1)

#2.2 - Genre
genero = sorted(df1['genre'].unique())

#2.3 - Console
console = df1.groupby('console')['total_sales'].sum().sort_values(ascending = False).reset_index()
console = console['console']

#2.4 - Empresa
manufacture = df1.groupby('manufacture')['total_sales'].sum().sort_values(ascending = False).reset_index()
manufacture = manufacture['manufacture']

#2.5 - Geração
generation = sorted(df1['generation'].unique())

#3. Create a Sidebar
with st.sidebar:
    st.title('BrasCo - Gaming Ltd.')
    st.divider()

    data_minima, data_maxima = st.slider("Filtar por data", data_minima, data_maxima, (data_minima, data_maxima))
    
    with st.expander("Filtros Avançados"):
        filter_genero = st.multiselect("Selecione o Genero", options=genero, default=genero)
        filter_console = st.multiselect("Selecione o Console", options=console, default=console)
        filter_manufacture = st.multiselect("Selecione a Empresa", options=manufacture, default=manufacture)
        filter_generation = st.multiselect("Selecione a Geração", options=generation, default=generation)

    st.divider()
    
    st.sidebar.markdown('#### Powered by GG Solution \nOwner: Guilherme Grandim')

#4. Filter Functions

df1 = df1[df1['release_date'].between(pd.Timestamp(data_minima), pd.Timestamp(data_maxima))]
df1 = df1[df1['genre'].isin(filter_genero)]
df1 = df1[df1['console'].isin(filter_console)]
df1 = df1[df1['manufacture'].isin(filter_manufacture)]
df1 = df1[df1['generation'].isin(filter_generation)]

#=======================================
# PHASE 3 - Create a Body Page
#=======================================

#1. Create a Header

st.title ('Sales & Volume')

#2. Bulletpoins in Page

#3. First Line

#4. Second Line

with st.container():
    fig_release_games_per_year = release_game_per_year(df1)
    fig_sales_games_per_year = sales_game_per_year(df1)
    
    st.plotly_chart(fig_release_games_per_year, use_container_width=True)
    st.plotly_chart(fig_sales_games_per_year, use_container_width=True)
