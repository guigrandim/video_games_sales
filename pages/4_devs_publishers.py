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

def market_share_per_publisher(df1):
    df_market_share_publisher = df1.loc[:, ['total_sales', 'clean_name_publisher']]
    df_market_share_publisher = df_market_share_publisher[df_market_share_publisher['total_sales'] > 0]
    
    sales_per_publishers = (
        df_market_share_publisher.groupby('clean_name_publisher')['total_sales']
        .sum()
        .sort_values(ascending = False)
        .reset_index()
    )
    
    sales_per_publishers['market_share_per_publishers'] = ((sales_per_publishers['total_sales'] / sales_per_publishers['total_sales'].sum()) * 100).round(2)
    sales_per_publishers = sales_per_publishers.iloc[:10]
    
    fig = go.Figure(data=[go.Pie(
        labels = sales_per_publishers['clean_name_publisher'],
        values = sales_per_publishers['market_share_per_publishers'],
        hole=.3
    )])
    fig.update_layout(title_text = 'Market Share por Publishers (Top 10)')
    
    return fig

def cross_market_appeal(df1):
    
    df_cma = (
        df1.groupby('clean_name_publisher')
        .agg(
            na_sales = ('na_sales', 'sum'),
            jp_sales = ('jp_sales', 'sum'),
            pal_sales = ('pal_sales', 'sum'),
            other_sales = ('other_sales', 'sum'),
            total_sales = ('total_sales', 'sum'),
            unique_titles = ('title', 'nunique')
        )
        .reset_index()
        .round(2)
    )
    
    df_cma['avg_sales_per_title'] = (df_cma['total_sales'] / df_cma['unique_titles']).round(2)
    
    regioes = ['na_sales', 'jp_sales', 'pal_sales', 'other_sales']
    df_cma['cv'] = df_cma[regioes].std(axis=1) / df_cma[regioes].mean(axis=1)
    df_cma['cross_market_appeal'] = (1 / (1 + df_cma['cv'])).round(3)
    
    df_cma = df_cma[df_cma['total_sales'] >= 1].sort_values('cross_market_appeal', ascending=False).head(20)
    
    fig1 = px.bar(
        df_cma,
        x='cross_market_appeal',
        y='clean_name_publisher',
        orientation='h',
        title='Cross Market Appeal por Publishers (Top 20)',
        labels={'cross_market_appeal': 'Score (0-1)', 'clean_name_publisher': 'Publisher'},
        color='cross_market_appeal',
        color_continuous_scale='RdYlGn',
        text='cross_market_appeal',
        hover_data=['na_sales', 'jp_sales', 'pal_sales', 'other_sales', 'total_sales']
    )
    fig1.update_layout(
        height = 600,
        yaxis=dict(categoryorder='total ascending', tickmode='linear')
    )
    
    fig2 = px.bar(
        df_cma,
        x = 'total_sales',
        y = 'clean_name_publisher',
        orientation = 'h',
        title = 'Vendas Globais por Publishers (em Milhões)',
        labels = {'clean_name_publisher': 'Publisher'},
        color = 'total_sales',
        text = 'total_sales'
    )
    fig2.update_layout(
        height = 600,
        yaxis=dict(categoryorder='total ascending', tickmode='linear')
    )
    fig2.update_traces(textposition='outside', cliponaxis = False)
    
    fig3 = px.bar(
        df_cma,
        x = 'avg_sales_per_title',
        y = 'clean_name_publisher',
        orientation = 'h',
        title = 'Titulos Lançados por Publishers (em Milhões)',
        labels = {'clean_name_publisher': 'Publisher'},
        color = 'avg_sales_per_title',
        text = 'avg_sales_per_title'
    )
    fig3.update_layout(
        height = 600,
        yaxis=dict(categoryorder='total ascending', tickmode='linear')
    )
    fig3.update_traces(textposition='outside', cliponaxis = False)
    
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        x=df_cma['na_sales'],
        y=df_cma['clean_name_publisher'],
        orientation='h',
        name='NA'
    ))
    fig4.add_trace(go.Bar(
        x=df_cma['jp_sales'],
        y=df_cma['clean_name_publisher'],
        orientation='h',
        name='JP'
    ))
    fig4.add_trace(go.Bar(
        x=df_cma['pal_sales'],
        y=df_cma['clean_name_publisher'],
        orientation='h',
        name='PAL'
    ))
    fig4.add_trace(go.Bar(
        x=df_cma['other_sales'],
        y=df_cma['clean_name_publisher'],
        orientation='h',
        name='Other'
    ))
    fig4.update_layout(
        barmode='stack',
        title='Vendas por Região e Publisher',
        height=600,
        yaxis=dict(categoryorder='total ascending', tickmode='linear')
    )
    
    return fig1, fig2, fig3, fig4

def sales_per_region(df1):
    
    df_sales_global_region = (
        df1.groupby('country_publisher')
        .agg(
            na_sales = ('na_sales', 'sum'),
            jp_sales = ('jp_sales', 'sum'),
            pal_sales = ('pal_sales', 'sum'),
            other_sales = ('other_sales', 'sum'),
            total_sales = ('total_sales', 'sum')
        )
        .round(2)
    )
    
    df_sales_global_region = df_sales_global_region[df_sales_global_region['total_sales'] >=1].drop(columns='total_sales')
    
    heatmap_pivot = df_sales_global_region.T
    
    heatmap_norm = heatmap_pivot.div(heatmap_pivot.sum(axis=1), axis=0)
    
    fig = px.imshow(
        heatmap_norm,
        zmin=0, zmax=1,
        title = 'Venda por Pais da Publisher x Mercado (Escala Relativa por Liha)',
        labels=dict(color='Intensidade', x='Pais da Desenvolvedora', y='Região da Vendas'),
        color_continuous_scale = 'RdYlGn',
        text_auto = True
    )
    fig.update_traces(text=heatmap_pivot.values, texttemplate="%{text}")
    fig.update_layout(height=600)
    
    return fig

def critic_score_per_holdings(df1):
    
    critic_score_holdings = df1.dropna(subset = ['critic_score'])
    critic_score_holdings = df1[df1['total_sales'] >= 1]
    
    critic_score_holdings = critic_score_holdings.groupby('holdings_publisher').filter(lambda x: len(x) > 5)
    
    ordem_boxplot = (
        critic_score_holdings.groupby('holdings_publisher')['critic_score']
        .median()
        .sort_values(ascending = True)
        .index.tolist()
    )
    
    fig = px.box(
        critic_score_holdings,
        x="holdings_publisher",
        y="critic_score",
        color="holdings_publisher",
        title="Distribuição da Critia por Holding (> 5 jogos lançados)",
        points="outliers",
        category_orders={"holdings_publisher": ordem_boxplot}
    )
    fig.update_xaxes(showgrid=False, title_text="Holding / Publisher")
    
    return fig

def critic_score_per_publisher_country(df1):
    
    critic_score_clean = df1.dropna(subset=['critic_score', 'country_developer'])
    
    country_critic_score = (
        critic_score_clean.groupby('country_developer')
        .agg(
            critic_score_mean=('critic_score', 'mean'),
            game_count=('critic_score', 'count')
        )
        .reset_index()
        .round(2)
    )
    
    country_critic_score = country_critic_score[country_critic_score['game_count'] >= 5]
    
    fig = px.choropleth(
        country_critic_score,
        locations = 'country_developer',
        color = 'critic_score_mean',
        hover_data = {'critic_score_mean' : True, 'game_count' : True},
        title = 'Qualidade Média dos Jogos por Pais de Origem do Desenvolvedor (Critic_Score)',
        color_continuous_scale= 'RdYlGn',
        labels={'critic_score_mean' : 'Média Critic Score', 'game_count': 'Total de Jogos'}
    )
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular',
            bgcolor='rgba(0,0,0,0)',
            showocean=False,
            showlakes=False
        ),
        margin={"r":0,"t":40,"l":0,"b":0}
        
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
st.title ('Devs and Publishers')

tab1, tab2, tab3 = st.tabs(['Publishers', 'Developers', 'Holdings'])

#Functions Apply
fig_holding_market_share = market_share_per_publisher(df1)
fig_cross_market, fig_total_sales_publishers, fig_total_titles_publishers, fig_sales_per_region = cross_market_appeal(df1)
fig_sales_per_country = sales_per_region(df1)
fig_critic_score_holdings = critic_score_per_holdings(df1)
fig_critic_score_publishers = critic_score_per_publisher_country(df1)

#Figures
with tab1:
    with st.container():
        col1, col2 = st.columns(2)
    
        with col1:
            st.plotly_chart(fig_holding_market_share, use_container_width=True)
    
        with col2:
            st.plotly_chart(fig_cross_market, use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)
    
        with col1:
            st.plotly_chart(fig_total_sales_publishers, use_container_width=True)
    
        with col2:
            st.plotly_chart(fig_total_titles_publishers, use_container_width=True)

    with st.container():
        st.plotly_chart(fig_sales_per_region, use_container_width=True)

    with st.container():
        st.plotly_chart(fig_sales_per_country, use_container_width=True)

with tab2:
    with st.container():
        st.plotly_chart(fig_critic_score_publishers, use_container_width = True)

with tab3:
    with st.container():
        st.plotly_chart(fig_critic_score_holdings, use_container_width=True)