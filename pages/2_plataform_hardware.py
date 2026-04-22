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

def plataform_premium(df1):
    plataform_consoles = df1.loc[df1['console'] != 'PC']
    
    mean_plataform_titles = (
    plataform_consoles.groupby(['console', 'title'])['critic_score']
    .mean()
    .reset_index(name='mean_critic_score')
    )

    plataform_titles_80 = mean_plataform_titles[mean_plataform_titles['mean_critic_score'] >= 8.0]
    count_titles_plataform_80 = plataform_titles_80.groupby('console')['title'].count().sort_values(ascending = False)
    plataform_best = count_titles_plataform_80.idxmax()
    qtd_titles_plataform_80 = count_titles_plataform_80.iloc[0]

    return plataform_best, qtd_titles_plataform_80

def best_plataform_na(df1):
    plataform_sum_sales_na = (
    df1.groupby('console')['na_sales']
    .sum()
    .sort_values(ascending = False)
    .reset_index(name='sum_sales_per_console')
    .round(2)
    )

    console_na = plataform_sum_sales_na.iloc[0]['console']
    total_sales_console_na = plataform_sum_sales_na.iloc[0]['sum_sales_per_console']
    
    return console_na, total_sales_console_na

def best_plataform_jp(df1):
    plataform_sum_sales_jp = (
    df1.groupby('console')['jp_sales']
    .sum()
    .sort_values(ascending = False)
    .reset_index(name='sum_sales_per_console')
    .round(2)
    )

    console_jp = plataform_sum_sales_jp.iloc[0]['console']
    total_sales_console_jp = plataform_sum_sales_jp.iloc[0]['sum_sales_per_console']

    return console_jp, total_sales_console_jp

def best_plataform_pal(df1):
    plataform_sum_sales_pal = (
        df1.groupby('console')['pal_sales']
        .sum()
        .sort_values(ascending = False)
        .reset_index(name='sum_sales_per_console')
        .round(2)
    )

    console_pal = plataform_sum_sales_pal.iloc[0]['console']
    total_sales_console_pal = plataform_sum_sales_pal.iloc[0]['sum_sales_per_console']
    
    return console_pal, total_sales_console_pal

def global_sales_plataform(df1):
    plataform_title_sales_global = (
    df1.groupby('console')['total_sales']
    .mean()
    .sort_values(ascending = True)
    .reset_index(name='mean_sales_per_title')
    .round(2)
    )
    plataform_title_sales_global.columns =['plataform', 'sales']
    
    plataform_title_sales_global = plataform_title_sales_global.dropna()
    plataform_title_sales_global = plataform_title_sales_global[plataform_title_sales_global['sales'] > 0.3 ]
    
    fig = go.Figure(go.Bar(
        x = plataform_title_sales_global['sales'],
        y = plataform_title_sales_global['plataform'],
        orientation = 'h',
        marker_color='#82caff',
        text = plataform_title_sales_global['sales']
    ))
    fig.update_layout(title='Vendas Medias por Plat. (Mundo)')
    
    return fig

def unique_title_plataform(df1):
    plataform_consoles = df1.loc[(df1['plataform'] == 'Console') & (df1['console'] != 'All')]
    
    count_plataform_unique_title = (
    plataform_consoles.groupby('console')['title']
    .nunique()
    .sort_values(ascending = False)
    .reset_index()
    )

    top_15_plataforms = count_plataform_unique_title.head(15)
    
    fig = go.Figure(go.Bar(
        x = top_15_plataforms['title'],
        y = top_15_plataforms['console'],
        orientation = 'h',
        marker_color='#82caff',
        text = top_15_plataforms['title']
    ))
    fig.update_layout(
        title = 'Titulos por Plataforma (Top 15)',
        yaxis=dict(categoryorder='total ascending')
    )

    return fig

def studios_per_plataform(df1):
    plataform_consoles = df1.loc[(df1['plataform'] == 'Console') & (df1['console'] != 'All')]
    
    developers_count_per_console = (
        plataform_consoles.groupby('console')['clean_name_developer']
        .nunique()
        .sort_values(ascending = False)
        .reset_index(name='developer_count')
    )
    
    top_15_developers = developers_count_per_console.head(15)
    
    fig = go.Figure(go.Bar(
        x = top_15_developers['developer_count'],
        y = top_15_developers['console'],
        orientation = 'h',
        marker_color='#82caff',
        text = top_15_developers['developer_count']
    ))
    fig.update_layout(
        title = 'Estudios Por Plataforma (Top 15)',
        yaxis=dict(categoryorder = 'total ascending')
    )
    
    return fig

def plataform_cycle(df1):
    
    plataform_consoles = df1.loc[(df1['plataform'] == 'Console') & (df1['console'] != 'All')]
    
    count_title_plataform = (
        plataform_consoles.groupby('console')['title']
        .agg(total_titles='count', unique_titles='nunique')
        .reset_index()
        .sort_values('total_titles', ascending=False)
    )

    return count_title_plataform

def sales_plataform_generation(df1):
    
    plataform_consoles = df1.loc[(df1['plataform'] == 'Console') & (df1['console'] != 'All')]
    
    plataform_sum_sales_global_gen = (
    plataform_consoles.groupby(['generation','console', 'manufacture'])['total_sales']
    .sum()
    .sort_values(ascending = False)
    .reset_index(name='sales_per_generation')
    )

    all_gen_sales = plataform_sum_sales_global_gen.groupby('generation').first().reset_index()
    all_gen_sales = all_gen_sales[(all_gen_sales['generation'] != '9th Gen') & (all_gen_sales['generation'] != 'Other/Unknown')]
    
    return all_gen_sales

def lifecycle_plataform(df1):
    
    plataform_consoles = df1.loc[(df1['plataform'] == 'Console') & (df1['console'] != 'All')]
    
    plataform_lifecycle = (
        plataform_consoles.groupby(['manufacture','console'])
        .agg(
            start_year = ('start_year', 'min'),
            end_year = ('end_year', 'max'),
            total_sales = ('total_sales', 'sum')
        )
        .reset_index()
    )
    
    plataform_lifecycle = plataform_lifecycle[plataform_lifecycle['total_sales'] > 0.5] 
    
    plataform_lifecycle['start_date'] = pd.to_datetime(plataform_lifecycle['start_year'], format='%Y')
    plataform_lifecycle['end_date'] = pd.to_datetime(plataform_lifecycle['end_year'], format='%Y')
    
    plataform_lifecycle = plataform_lifecycle.sort_values(['manufacture', 'start_year'])
    
    fig = px.timeline(
        plataform_lifecycle,
        x_start='start_date',
        x_end = 'end_date',
        y = 'console',
        title = 'Ciclo de Vida das Plataformas (Vendas até 2024 e Acima de 500 mil unidades)',
        color = 'manufacture',
    )
    
    fig.update_yaxes(type='category')
    
    fig.update_layout(
        yaxis=dict(categoryorder = 'array', categoryarray=plataform_lifecycle['console'].tolist()),
        showlegend=False
    )
    
    return fig

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
st.title ('Plataform & Hardware')

#Create KPIs in Top the Page
with st.container():
    col1, col2, col3, col4 = st.columns(4)
    plataform_top, qtd_titles_p_80 = plataform_premium()
    console_na, qtd_sales_na = best_plataform_na()
    console_jp, qtd_sales_jp = best_plataform_jp()
    console_pal, qtd_sales_pal = best_plataform_pal()

    with col1:
        col1.metric('Console Premium\n(Jogos > 80 Critic Score)', plataform_top)
        
    with col2:
        col2.metric('Plataforma Lider Vendas NA', console_na, f"{qtd_sales_na} un.ven", delta_color = "off")
    
    with col3:
        col3.metric('Plataforma Lider Vendas JP', console_jp, f"{qtd_sales_jp} un.ven", delta_color = "off")
    
    with col4:
        col4.metric('Plataforma Lider Vendas PAL', console_pal, f"{qtd_sales_pal} un.ven", delta_color = "off")
    
with st.container():
    col5, col6, col7 = st.columns(3)
        
    with col5:
        fig_mean_sales_global = global_sales_plataform(df1)
        st.plotly_chart(fig_mean_sales_global, use_container_width = True)
    
    with col6:
        fig_unique_titles_plataform = unique_title_plataform(df1)
        st.plotly_chart(fig_unique_titles_plataform, use_container_width = True)
    
    with col7:
        fig_genre_distinct = studios_per_plataform(df1)
        st.plotly_chart(fig_genre_distinct, use_container_width = True)

with st.container():
    plataform_by_generation = sales_plataform_generation(df1)
    st.dataframe(plataform_by_generation)

with st.container():
    lifecycle_plataforms_database = lifecycle_plataform(df1)
    st.plotly_chart(lifecycle_plataforms_database, use_container_width = True)