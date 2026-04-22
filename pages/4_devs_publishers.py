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
            total_sales = ('total_sales', 'sum')
        )
        .reset_index()
    )
    
    regioes = ['na_sales', 'jp_sales', 'pal_sales', 'other_sales']
    df_cma['cv'] = df_cma[regioes].std(axis=1) / df_cma[regioes].mean(axis=1)
    df_cma['cross_market_appeal'] = (1 / (1 + df_cma['cv'])).round(3)
    
    df_cma = df_cma[df_cma['total_sales'] >= 1].sort_values('cross_market_appeal', ascending=False).head(20)
    
    fig = px.bar(
        df_cma,
        x='cross_market_appeal',
        y='clean_name_publisher',
        orientation='h',
        title='Cross Market Appeal por Publishers (Top 20)',
        labels={'cross_market_appeal': 'Score (0-1)', 'clean_name_publisher': 'Publisher'},
        color='cross_market_appeal',
        color_continuous_scale='RdYlGn',  # ← estava 'color_continuos_scale' (typo)
        text='cross_market_appeal',
        hover_data=['na_sales', 'jp_sales', 'pal_sales', 'other_sales', 'total_sales']
    )
    
    fig.update_layout(
        height = 600,
        yaxis=dict(
            categoryorder='total ascending',
            tickmode='linear',
        )
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

with st.container():
    col1, col2 = st.columns (2)
    
    with col1:
        fig_holding_market_share = market_share_per_publisher(df1)
        st.plotly_chart(fig_holding_market_share, use_container_width=True)
    
    with col2:
        fig_cross_market = cross_market_appeal(df1)
        st.plotly_chart(fig_cross_market, use_container_width=True)