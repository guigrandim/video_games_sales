import streamlit as st
import os
import pandas as pd
from datetime import date
from utils.data_loader import dataset_clean

def render_sidebar():
    #Load Dataset Principal and Libray Publishers and Developers
    df = dataset_clean()
    df1 = df.copy()
    
    #1. Load Logo Page

    #2. Configuration Filters
    #2.1 - Date
    data_minima = date(1970, 1, 1)
    data_maxima = date(2024, 12, 31)

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

            filter_genero = filter_genero if filter_genero else genero
            filter_console = filter_console if filter_console else console.tolist()
            filter_manufacture = filter_manufacture if filter_manufacture else manufacture.tolist()
            filter_generation = filter_generation if filter_generation else generation

        st.divider()
    
        st.markdown('#### Powered by GG Solution \nOwner: Guilherme Grandim')
    
    df1 = df1[df1['release_date'].between(pd.Timestamp(data_minima), pd.Timestamp(data_maxima))]
    df1 = df1[df1['genre'].isin(filter_genero)]
    df1 = df1[df1['console'].isin(filter_console)]
    df1 = df1[df1['manufacture'].isin(filter_manufacture)]
    df1 = df1[df1['generation'].isin(filter_generation)]
    
    return df1, filter_genero, filter_console, filter_manufacture, filter_generation