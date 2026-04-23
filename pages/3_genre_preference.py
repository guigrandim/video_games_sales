#==================================
# Import Library
#==================================

import pandas as pd
import streamlit as st
from PIL import Image
import plotly.express as px
from utils.data_loader import dataset_clean
from utils.sidebar import render_sidebar
from datetime import date
import plotly.graph_objects as go

#==================================
# Configuration Page
#==================================

st.set_page_config(page_title = 'Plataforma e Hardware', page_icon = '🎮', layout = 'wide')

#===================================
# Functions
#===================================

def top_genre_sales_na(df1):
    
    filter_by_sales = df1[df1['total_sales'] >= 0.5]
    
    best_sales_na =(
    filter_by_sales.groupby('genre')['na_sales']
    .mean()
    .sort_values (ascending = False)
    .reset_index (name = 'na_sales')
    .round(2)
    )

    best_genre_sales_na = best_sales_na['genre'].iloc[0]
    best_genre_sales_na_qtd = best_sales_na['na_sales'].iloc[0]

    return best_genre_sales_na, best_genre_sales_na_qtd

def top_genre_sales_jp(df1):
    
    filter_by_sales = df1[df1['total_sales'] >= 0.5]
    
    best_sales_jp =(
    filter_by_sales.groupby('genre')['jp_sales']
    .mean()
    .sort_values (ascending = False)
    .reset_index (name = 'jp_sales')
    .round(2)
    )

    best_genre_sales_jp = best_sales_jp['genre'].iloc[0]
    best_genre_sales_jp_qtd = best_sales_jp['jp_sales'].iloc[0]

    return best_genre_sales_jp, best_genre_sales_jp_qtd

def top_genre_sales_pal(df1):
    
    filter_by_sales = df1[df1['total_sales'] >= 0.5]
    
    best_sales_pal =(
    filter_by_sales.groupby('genre')['pal_sales']
    .mean()
    .sort_values (ascending = False)
    .reset_index (name = 'pal_sales')
    .round(2)
    )

    best_genre_sales_pal = best_sales_pal['genre'].iloc[0]
    best_genre_sales_pal_qtd = best_sales_pal['pal_sales'].iloc[0]

    return best_genre_sales_pal, best_genre_sales_pal_qtd

def genre_sales_global(df1):
    
    filter_by_sales = df1[df1['total_sales'] >= 0.5]
    
    sales_global_per_genre = (
        filter_by_sales.groupby('genre')['total_sales']
        .sum()
        .sort_values(ascending = False)
        .reset_index()
        .round(2)
    )
    
    fig = go.Figure(go.Bar(
        x = sales_global_per_genre['total_sales'],
        y = sales_global_per_genre['genre'],
        orientation = 'h',
        marker_color='#82caff',
        text = sales_global_per_genre['total_sales'],
        textposition='outside',
        cliponaxis = False
    ))
    fig.update_layout(
        title = 'Vendas Globais por Genero em Milhões',
        yaxis=dict(categoryorder = 'total ascending'),
        margin = dict(l=50, r=150, t=50, b=50),
        xaxis = dict(range=[0, sales_global_per_genre['total_sales'].max() * 1])
    )
    
    return fig

def critic_score_per_genre(df1):

    filter_by_sales = df1[df1['total_sales'] >= 0.5].dropna(subset = ['critic_score'])
    
    critic_score_genre = (
        filter_by_sales.groupby('genre')['critic_score']
        .mean()
        .sort_values(ascending = False)
        .reset_index()
        .round(1)
    )
    
    fig = go.Figure(go.Bar(
        x = critic_score_genre['critic_score'],
        y = critic_score_genre['genre'],
        orientation = 'h',
        marker_color='#82caff',
        text = critic_score_genre['critic_score'],
        textposition='outside',
        cliponaxis = False
    ))
    fig.update_layout(
        title = 'Nota da Critica por Genero',
        yaxis=dict(categoryorder = 'total ascending'),
        margin = dict(l=50, r=150, t=50, b=50),
        xaxis = dict(range=[0, critic_score_genre['critic_score'].max() * 1])
    )
    
    return fig

def total_sales_per_critic(df1):
    
    filter_by_sales = df1[df1['total_sales'] >= 0.5].dropna(subset = ['critic_score'])
    
    critic_score_per_genre = (
        filter_by_sales.groupby('genre')
        .agg(
            mean_critic_score=('critic_score', 'mean'),
            total_sales=('total_sales', 'sum')
        )
        .sort_values('total_sales', ascending=False)
        .reset_index()
        .round(2)
    )
    
    fig = px.scatter(
        critic_score_per_genre,
        x = 'mean_critic_score',
        y = 'total_sales',
        text = 'genre',
        title = 'Relação entre Nota da Critica e Vendas por Genero',
        labels={
            'mean_critic_score': 'Nota Média da Crítica',
            'total_sales' : 'Vendas Totais (Milhões)'
        },
        color = 'genre',
        size = 'total_sales'
    )
    fig.update_layout(showlegend=False)
    
    return fig

def sales_by_genre_heatmap(df1):
    
    filter_by_sales = df1[df1['total_sales'] >= 0.5]
    
    heatmap_data = (
        filter_by_sales.groupby('genre')
        .agg(
            na_sales = ('na_sales', 'sum'),
            jp_sales = ('jp_sales', 'sum'),
            pal_sales = ('pal_sales', 'sum'),
            other_sales = ('other_sales', 'sum')
        )
        .round(2)
    )
    
    heatmap_pivot = heatmap_data.T
    
    heatmap_norm = heatmap_pivot.div(heatmap_pivot.max(axis=1), axis=0)
    
    fig = px.imshow(
        heatmap_norm,
        zmin=0, zmax=1,
        title = 'Preferencia de Genero por Região (Escala Relativa por Linha)',
        labels = dict(color='Intensidade', x='Gênero', y='Região'),
        color_continuous_scale='RdYlGn',
        text_auto=True
    )
    fig.update_traces(text=heatmap_pivot.values, texttemplate="%{text}")
    fig.update_layout(height=600)
    
    return fig

def sales_gen_per_generation(df1):
    
    ajust_generation = df1[(df1['generation'] != 'Other/Unknown') & (df1['generation'] != '9th Gen')]

    sales_gen_global_sales = (
        ajust_generation.groupby(['genre', 'generation'])
        .agg(
            total_sales = ('total_sales', 'sum'),
            lancamentos = ('title', 'nunique')
        )
        .sort_values('total_sales', ascending = False)
        .reset_index()
        .round(2)
    )
    
    sales_gen_global_sales_filter = sales_gen_global_sales[sales_gen_global_sales['lancamentos'] >= 1]
    best_genre_per_gen = sales_gen_global_sales_filter.groupby('generation').first().reset_index()
    
    return best_genre_per_gen

def critic_gen_per_generation(df1):
    
    filter_by_sales = df1[df1['total_sales'] >= 0.5]
    ajust_generation = filter_by_sales[(filter_by_sales['generation'] != 'Other/Unknown') & (filter_by_sales['generation'] != '9th Gen')]
    
    critic_score_per_genre_gen = (
        ajust_generation.groupby(['genre', 'generation'])['critic_score']
        .mean()
        .sort_values(ascending = False)
        .reset_index()
        .round(1)
    )

    best_critic_score_per_gen = critic_score_per_genre_gen.groupby('generation').first().reset_index()
    
    return best_critic_score_per_gen

#===============================================
# Select Directory - Load Files and Clean Dataset
#===============================================

df1 = dataset_clean()

#======================================
# Create a Sidebar
#======================================

df1, filter_genero, filter_console, filter_manufacture, filter_generation = render_sidebar()

#======================================
# Create a Body Page
#======================================

#Create a Header
st.title ('Genre and Preferences')

with st.container():
    col1, col2, col3 = st.columns(3)

    with col1:
        best_genre_sales_na, best_genre_sales_na_qtd = top_genre_sales_na(df1)
        col1.metric("Top Genero Vendas - NA", best_genre_sales_na, f"{best_genre_sales_na_qtd} milh. unid.", delta_color = "off")
    
    with col2:
        best_genre_sales_jp, best_genre_sales_jp_qtd = top_genre_sales_jp(df1)
        col2.metric("Top Genero Vendas - JP", best_genre_sales_jp, f"{best_genre_sales_jp_qtd} milh. unid.", delta_color = "off")
    
    with col3:
        best_genre_sales_pal, best_genre_sales_pal_qtd = top_genre_sales_pal(df1)
        col3.metric("Top Genero Vendas - PAL", best_genre_sales_pal, f"{best_genre_sales_pal_qtd} milh. unid.", delta_color = "off")

with st.container():
    col4, col5 = st.columns(2)
    
    with col4:
        fig_sales_global_genre = genre_sales_global(df1)
        st.plotly_chart(fig_sales_global_genre, use_container_width = True)
    
    with col5:
        fig_critic_score_genre = critic_score_per_genre(df1)
        st.plotly_chart(fig_critic_score_genre, use_container_width = True)

with st.container():
    col6, col7 = st.columns(2)
    
    with col6:
        st.markdown("### 📊 Top Genero em Vendas por Geração")
        df_sales_genre_per_generation = sales_gen_per_generation(df1)
        st.dataframe(df_sales_genre_per_generation, use_container_width = True, hide_index = True)
    
    with col7:
        st.markdown("### 📊 Top Genero em Critica por Geração")
        df_critic_gen_per_generation = critic_gen_per_generation(df1)
        st.dataframe(df_critic_gen_per_generation, use_container_width = True, hide_index = True)
        
with st.container():
    fig_total_sales_critic_score = total_sales_per_critic(df1)
    st.plotly_chart(fig_total_sales_critic_score, use_container_width = True)

with st.container():
    fig_sales_genre = sales_by_genre_heatmap(df1)
    st.plotly_chart(fig_sales_genre, use_container_width = True)