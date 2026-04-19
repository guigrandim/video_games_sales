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
import plotly.graph_objects as go

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

def market_share_per_region(df1):
    sales_global_per_region = pd.Series({
    'NA' : df1['na_sales'].fillna(0).sum(),
    'JP' : df1['jp_sales'].fillna(0).sum(),
    'PAL' : df1['pal_sales'].fillna(0).sum(),
    'Other' : df1['other_sales'].fillna(0).sum()
    }).sort_values(ascending = False).round(2).reset_index()
    sales_global_per_region.columns = ['region', 'sales_per_region']

    total_sales = df1['total_sales'].sum()

    sales_global_per_region['market_share'] = ((sales_global_per_region['sales_per_region'] / total_sales) * 100).round(2)
    
    fig = go.Figure(data=[go.Pie(
        labels=sales_global_per_region['region'], 
        values = sales_global_per_region['market_share'], 
        hole=.3
    )])
    fig.update_layout(title_text = 'Market Share por Região')
    
    sales_global = sales_global_per_region[['region', 'sales_per_region']]
    
    return fig

def market_share_per_holding(df1):
    df_market_share_holdings = df1.loc[:, ['total_sales', 'holdings_publisher']]
    df_market_share_holdings = df_market_share_holdings[df_market_share_holdings['total_sales'] > 0]
    
    sales_per_holdings = (
        df_market_share_holdings.groupby('holdings_publisher')['total_sales']
        .sum()
        .sort_values(ascending = False)
        .reset_index()
    )
    
    sales_per_holdings['market_share_per_holding'] = ((sales_per_holdings['total_sales'] / sales_per_holdings['total_sales'].sum()) * 100).round(2)
    sales_per_holdings = sales_per_holdings.iloc[:6]
    
    fig = go.Figure(data=[go.Pie(
        labels = sales_per_holdings['holdings_publisher'],
        values = sales_per_holdings['market_share_per_holding'],
        hole=.3
    )])
    fig.update_layout(title_text = 'Market Share por Holding (Top 5)')
    
    return fig

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

def release_region_games(df1):
    clean_release_date = df1.dropna(subset=['release_date'])

    release_title_region = pd.Series ({
        'NA' : clean_release_date[clean_release_date['na_sales'] > 0]['title'].nunique(),
        'JP' : clean_release_date[clean_release_date['jp_sales'] > 0]['title'].nunique(),
        'PAL' : clean_release_date[clean_release_date['pal_sales'] > 0]['title'].nunique(),
        'Other': clean_release_date[clean_release_date['other_sales'] > 0]['title'].nunique()
    }).sort_values(ascending = True).reset_index()
    release_title_region.columns = ['region', 'total_release']
    
    fig = go.Figure(go.Bar(
        x=release_title_region['total_release'],
        y=release_title_region['region'],
        orientation = 'h',
        marker_color='#82caff',
        text=release_title_region['total_release']
    ))
    fig.update_layout(title='Lançamentos Por Região')

    return fig

def critic_score_premium_region(df1):
    critic_score_premium_region = pd.Series ({
        'NA' : df1[(df1['classification'] == 'Premium') & (df1['na_sales'] > 0)]['title'].nunique(),
        'JP' : df1[(df1['classification'] == 'Premium') & (df1['jp_sales'] > 0)]['title'].nunique(),
        'PAL' : df1[(df1['classification'] == 'Premium') & (df1['pal_sales'] > 0)]['title'].nunique(),
        'Other': df1[(df1['classification'] =='Premium') & (df1['other_sales'] > 0)]['title'].nunique()
    }).sort_values(ascending = True).reset_index()
    critic_score_premium_region.columns = ['region', 'qte_premium']
    
    fig = go.Figure(go.Bar(
        x=critic_score_premium_region['qte_premium'],
        y=critic_score_premium_region['region'],
        orientation = 'h',
        marker_color='#82caff',
        text=critic_score_premium_region['qte_premium']
    ))
    fig.update_layout(title='Lançamentos Premium (>90) Por Região')
    
    return fig

def holdings_region_function(df1):
    clean_holdings = df1.dropna(subset=['holdings_publisher'])
    
    genre_region = pd.Series({
        'NA' : clean_holdings[clean_holdings['na_sales'] > 0]['holdings_publisher'].nunique(),
        'JP' : clean_holdings[clean_holdings['jp_sales'] > 0]['holdings_publisher'].nunique(),
        'PAL' : clean_holdings[clean_holdings['pal_sales'] > 0]['holdings_publisher'].nunique(),
        'Other' : clean_holdings[clean_holdings['other_sales'] > 0]['holdings_publisher'].nunique()
    }).sort_values(ascending = True).reset_index()
    genre_region.columns = ['region', 'qtd_release_holding']
    
    fig = go.Figure(go.Bar(
        x = genre_region['qtd_release_holding'],
        y = genre_region['region'],
        orientation = 'h',
        marker_color='#82caff',
        text = genre_region['qtd_release_holding']
    ))
    fig.update_layout(title='Lançamentos Totais Por Holdings')
    
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

#3 Create a Tabs in Page

tab1, tab2 = st.tabs(["Visão Geral Vendas", "Visão Geral Lançamentos"])
width_default = 350

#3. Tab 1 - First Line
with tab1:
    with st.container():
        col1, col2 = st.columns(2)
        fig_sales_market_share = market_share_per_region(df1)
        fig_holding_market_share = market_share_per_holding(df1)

        with col1:
            st.plotly_chart(fig_sales_market_share, use_container_width=True)

        with col2:
            st.plotly_chart(fig_holding_market_share, use_container_width=True)

#4. Tab1 - Second Line
    with st.container():
        fig_sales_games_per_year = sales_game_per_year(df1)
        st.plotly_chart(fig_sales_games_per_year, use_container_width=True)

with tab2:
    with st.container():
        col5, col6, col7 = st.columns(3)
    
        with col5:
                fig_release_games = release_region_games(df1)
                st.plotly_chart(fig_release_games, use_container_width=True)
    
        with col6:
                fig_critic_score_premium = critic_score_premium_region(df1)
                st.plotly_chart(fig_critic_score_premium, use_container_width=True)
        
        with col7:
                fig_genre_region_release = holdings_region_function(df1)
                st.plotly_chart(fig_genre_region_release, use_container_width=True)
    
    with st.container():
        fig_release_games_per_year = release_game_per_year(df1)
        st.plotly_chart(fig_release_games_per_year, use_container_width=True)