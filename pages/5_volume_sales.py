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

st.set_page_config(page_title = 'Volume e Vendas', page_icon = '📉', layout = 'wide')

#===================================
# Functions
#===================================

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
    
    return fig, sales_global

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

def total_sales_per_critic_titles(df1):

    critic_score_clean = df1.dropna(subset=['critic_score'])
    critic_score_clean = critic_score_clean[critic_score_clean['total_sales'] >=1]
    
    sales_global_per_title =(
        critic_score_clean.groupby('title')
        .agg(
            title_unique = ('title', 'nunique'),
            mean_critic_score = ('critic_score', 'mean'),
            total_sales = ('total_sales', 'sum')  
        )
        .sort_values('total_sales', ascending = True)
        .reset_index()
        .round(2)
    )
    
    fig = px.scatter(
        sales_global_per_title,
        x = 'mean_critic_score',
        y = 'total_sales',
        title = 'Relação do Total de Vendas pela Critica ',
        labels = {
            'mean_critic_score': 'Nota Média da Crítica',
            'total_sales' : 'Vendas Totais (Milhões)'
        },
        color = 'mean_critic_score',
        size = 'total_sales'
    )
    fig.update_layout(showlegend=False)
    
    return fig

def first_hit_analysis(df1):
    
    df_hits = df_hits = df1[
        (df1['total_sales'] >= 1) & 
        (df1['release_date'].notna()) & 
        (df1['release_date_console'].notna()) &
        (df1['plataform'] == 'Console')
    ].copy()
    
    df_hits['days_to_hit'] = (df_hits['release_date'] - df_hits['release_date_console']).dt.days
    
    df_hits = df_hits[df_hits['days_to_hit'] >= 0]
    
    df_first_hit = (
        df_hits.loc[df_hits.groupby('console')['days_to_hit'].idxmin()]
        [['console_name', 'title', 'days_to_hit', 'total_sales', 'manufacture']]
        .sort_values('days_to_hit')
        .reset_index(drop=True)
    )
    
    colors = {
        'Sony': '#f1c40f',      # Amarelo/Ouro
        'Nintendo': '#e74c3c',  # Vermelho
        'Microsoft': '#f1948a', # Rosa/Salmon
        'Sega': '#1abc9c',      # Verde Água
        'Atari': '#3498db',      # Azul
        'SNK': "#3efdd7dd"      # Verde Água
    }
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x = df_first_hit['days_to_hit'],
        y = df_first_hit['console_name'],
        orientation = 'h',
        marker_color=df_first_hit['manufacture'].map(colors).fillna('#95a5a6'),
        customdata=df_first_hit[['title', 'total_sales', 'manufacture']],
        hovertemplate=(
            '<b>%{y}</b><br>'
            'Primeiro Hit: %{customdata[0]}<br>'
            'Dias até o Hit: %{x}<br>'
            'Vendas: %{customdata[1]:.2f}M<br>'
            'Fabricante: %{customdata[2]}'
            '<extra></extra>'
        ),
    ))
    fig.update_layout(
        title=dict(text='Tempo até o Primeiro Hit por Console'),
        xaxis=dict(title='Dias após lançamento do console'),
        yaxis=dict(
            title='Console',
            autorange='reversed',
        ),
        height=600,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    
    return fig

#-------------------------------------------- Beginning of the logical structure code --------------------- #

#===============================================
# Select Directory - Load Files and Clean Dataset
#===============================================

df1 = dataset_clean()

#======================================
# Create a Sidebar
#======================================

df1, filter_genero, filter_console, filter_manufacture, filter_generation = render_sidebar()

#=======================================
# Create a Body Page
#=======================================

#Create a Header
st.title ('Sales & Volume')

#Bulletpoins in Page

#Functions Apply
fig_sales_market_share, df_sales_global = market_share_per_region(df1)
fig_sales_games_per_year = sales_game_per_year(df1)
fig_sales_titles_per_critic = total_sales_per_critic_titles(df1)
fig_release_games = release_region_games(df1)
fig_critic_score_premium = critic_score_premium_region(df1)
fig_genre_region_release = holdings_region_function(df1)
fig_release_games_per_year = release_game_per_year(df1)
fig_first_hit_consoles = first_hit_analysis(df1)


#Create a Tabs in Page

tab1, tab2 = st.tabs(["Visão Geral Vendas", "Visão Geral Lançamentos"])
width_default = 350

#Tab 1 - Sales Tab
with tab1:
    with st.container():
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.plotly_chart(fig_sales_market_share, use_container_width=True)
        
        with col2:
            st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
            st.dataframe(df_sales_global, use_container_width = True, hide_index = True)

    with st.container():
        st.plotly_chart(fig_sales_games_per_year, use_container_width=True)
    
    with st.container():
        st.plotly_chart(fig_sales_titles_per_critic, use_container_width = True)
    
    with st.container():
        st.plotly_chart(fig_first_hit_consoles, use_container_width = True)

#Tab2 - Release Tab
with tab2:
    with st.container():
        col5, col6, col7 = st.columns(3)
    
        with col5:  
                st.plotly_chart(fig_release_games, use_container_width=True)
    
        with col6:
                st.plotly_chart(fig_critic_score_premium, use_container_width=True)
        
        with col7:
                st.plotly_chart(fig_genre_region_release, use_container_width=True)
    
    with st.container():
        st.plotly_chart(fig_release_games_per_year, use_container_width=True)