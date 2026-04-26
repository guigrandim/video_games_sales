import streamlit as st
import os
import pandas as pd
from datetime import date
from utils.data_loader import dataset_clean
from pathlib import Path

def render_sidebar():
    #Load Dataset Principal and Libray Publishers and Developers
    df = dataset_clean()
    df1 = df.copy()
    
    #1. Load Logo Page
    base_dir = Path(__file__).parents[1]
    imagem_path1 = base_dir / "assets" / "img" / "logo1.png"
    imagem_path2 = base_dir / "assets" / "img" / "logo2.png"

    #2. Configuration Filters
    #2.1 - Genre
    genero = sorted(df1['genre'].unique())

    #2.2 - Console
    console = df1.groupby('console')['total_sales'].sum().sort_values(ascending = False).reset_index()
    console = console['console']

    #2.3 - Empresa
    manufacture = ["Todas as Empresas"] + (
        df1.groupby('manufacture')['total_sales']
        .sum()
        .sort_values(ascending = False)
        .reset_index()['manufacture']
        .tolist()
    )
    
    #2.4 - Geração
    generation = ["Todas as Gerações"] + sorted(df1['generation'].unique().tolist())

    #3. Create a Sidebar
    with st.sidebar:
        #Plot Logo BrasCo.
        if imagem_path1.exists():
            st.image(str(imagem_path1))
        else:
            st.warning("Imagem não encontrada")
        
        st.divider()
    
        filter_generation = st.sidebar.selectbox("Selecione a Geração", options=generation, index=0)
        filter_manufacture = st.sidebar.selectbox("Selecione a Empresa", options=manufacture, index=0)
        
        if filter_generation != "Todas as Gerações" : 
            df1 = df1[df1['generation'] == filter_generation]
            
        if filter_manufacture != "Todas as Empresas" : 
            df1 = df1[df1['manufacture'] == filter_manufacture]
    
        with st.expander("Filtros Avançados"):
            
            filter_genero = st.multiselect("Selecione o Genero", options=genero, default=genero)
            filter_console = st.multiselect("Selecione o Console", options=console, default=console)
            
            filter_genero = filter_genero if filter_genero else genero
            filter_console = filter_console if filter_console else console.tolist()
            
        st.divider()
        
        #Plot Logo BrasCo.
        if imagem_path2.exists():
            st.image(str(imagem_path2), width=250)
        else:
            st.warning("Imagem não encontrada")
    
        st.markdown(
    "<p style='text-align: center;'>Owner: Guilherme Grandim </p>",
    unsafe_allow_html=True
)
    
    df1 = df1[df1['genre'].isin(filter_genero)]
    df1 = df1[df1['console'].isin(filter_console)]
    
    return df1, filter_genero, filter_console, filter_manufacture, filter_generation