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
        plataform_consoles.groupby(['generation','console','manufacture'])['total_sales']
        .sum()
        .sort_values(ascending = False)
        .reset_index(name='sales_per_generation')
        .round(2)
    )
    
    gen_sales = plataform_sum_sales_global_gen[(plataform_sum_sales_global_gen['generation'] != '9th Gen') & (plataform_sum_sales_global_gen['generation'] != 'Other/Unknown')]

    all_gen_sales_individual = gen_sales.groupby('generation').first().reset_index()
    
    colors = {
        'Sony': '#f1c40f',      # Amarelo/Ouro
        'Nintendo': '#e74c3c',  # Vermelho
        'Microsoft': '#f1948a', # Rosa/Salmon
        'Sega': '#1abc9c',      # Verde Água
        'Atari': '#3498db'      # Azul
    }
    
    df_all_gen_sales_format = (
        all_gen_sales_individual.style
        .applymap(
            lambda x: f'background-color: {colors.get(x, "")}; font-weight: bold;', 
            subset=['manufacture']
        )
        .format({
            'sales_per_generation': '{:.0f}'
        })
    )
    
    filter_all_gen_sales = gen_sales[gen_sales['sales_per_generation'] > 0.5].sort_values('generation', ascending = True).drop(columns=['console'])
    
    filter_all_gen_sales = filter_all_gen_sales.groupby(['generation','manufacture'])['sales_per_generation'].sum().reset_index()
    
    manufacturers = filter_all_gen_sales['manufacture'].unique()
    gen_order = ['2nd Gen', '3rd Gen', '4th Gen', '5th Gen', '6th Gen', '7th Gen', '8th Gen']
    
    fig = go.Figure()
    
    for mfr in manufacturers:
        df_mrf = filter_all_gen_sales[filter_all_gen_sales['manufacture'] == mfr]
        fig.add_trace(go.Bar(
            name=mfr,
            y=df_mrf['generation'],
            x=df_mrf['sales_per_generation'],
            orientation = 'h',
            marker_color=colors.get(mfr, '#95a5a6'),
            insidetextanchor='middle',
        ))
    fig.update_layout(
        barmode='stack',
        title=dict(text='Vendas por Geração e Fabricante'),
        xaxis=dict(title='Vendas (M)', tickformat=',.0f'),
        yaxis=dict(
            title='Geração',
            categoryorder='array',
            categoryarray=gen_order,
            autorange='reversed',  
        ),
        legend=dict(title='Fabricante', orientation='v'),
        height=450,
        margin=dict(l=20, r=20, t=50, b=20),
    )

    return df_all_gen_sales_format, fig

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
    
    plataform_lifecycle = plataform_lifecycle[plataform_lifecycle['total_sales'] > 1] 
    
    plataform_lifecycle['start_date'] = pd.to_datetime(plataform_lifecycle['start_year'], format='%Y')
    plataform_lifecycle['end_date'] = pd.to_datetime(plataform_lifecycle['end_year'], format='%Y')
    
    plataform_lifecycle = plataform_lifecycle.sort_values(['manufacture', 'start_year'])
    
    fig = px.timeline(
        plataform_lifecycle,
        x_start='start_date',
        x_end = 'end_date',
        y = 'console',
        title = 'Ciclo de Vida das Plat. (Vendas até 2024 e Acima de 1 mi de uni)',
        color = 'manufacture',
    )
    fig.update_yaxes(type='category')
    fig.update_layout(
        yaxis=dict(categoryorder = 'array', categoryarray=plataform_lifecycle['console'].tolist()),
        showlegend=False
    )
    
    return fig

def plataform_activity_years(df1):
    
    filter_total_sales = df1[(~df1['manufacture'].isin(['PC','Other/Unknown'])) & (df1['plataform'] == 'Console')].copy()
    
    activity_years_sales = (
        filter_total_sales.groupby(['console', 'manufacture'])
        .agg(
            activity_year = ('activity_years', 'first'),
            title_release = ('title', 'nunique')
        )
        .reset_index()
    )

    activity_years_sales['title_per_year'] = (activity_years_sales['title_release'] / activity_years_sales['activity_year']).round(0)
    activity_years_sales = activity_years_sales.sort_values('activity_year', ascending = False)
    
    activity_years_sales = activity_years_sales[(activity_years_sales['title_per_year'] > 10)]
    
    colors = {
        'Sony': '#f1c40f',      # Amarelo/Ouro
        'Nintendo': '#e74c3c',  # Vermelho
        'Microsoft': '#f1948a', # Rosa/Salmon
        'Sega': '#1abc9c',      # Verde Água
        'Atari': '#3498db',      # Azul
        'SNK': "#3efdd7dd"      # Verde Água
    }
    
    df_activity_years_sales_format = (
        activity_years_sales.style
        # Aplica cores de fundo na coluna manufacture
        .applymap(
            lambda x: f'background-color: {colors.get(x, "")}; font-weight: bold;', 
            subset=['manufacture']
        )
        .format({
            'activity_year': '{:.0f}',
            'title_per_year': '{:.0f}'
        })
    )
    
    return df_activity_years_sales_format


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

#Call the Functions
plataform_top, qtd_titles_p_80 = plataform_premium(df1)
console_na, qtd_sales_na = best_plataform_na(df1)
console_jp, qtd_sales_jp = best_plataform_jp(df1)
console_pal, qtd_sales_pal = best_plataform_pal(df1)
fig_mean_sales_global = global_sales_plataform(df1)
fig_unique_titles_plataform = unique_title_plataform(df1)
fig_genre_distinct = studios_per_plataform(df1)
plataform_by_generation, fig_plataform_sum_gen = sales_plataform_generation(df1)
lifecycle_plataforms_database = lifecycle_plataform(df1)
df_plataform_cycles = plataform_activity_years(df1)

#Create KPIs in Top the Page
with st.container():
    col1, col2, col3, col4 = st.columns(4)
    
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
        st.plotly_chart(fig_mean_sales_global, use_container_width = True)
    
    with col6:
        st.plotly_chart(fig_unique_titles_plataform, use_container_width = True)
    
    with col7:
        st.plotly_chart(fig_genre_distinct, use_container_width = True)

with st.container():
    st.dataframe(plataform_by_generation, use_container_width = True, hide_index = True)

with st.container():
    st.plotly_chart(fig_plataform_sum_gen, use_container_width = True)

with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(lifecycle_plataforms_database, use_container_width = True)
    
    with col2:
        st.markdown("#### 🎮 Anos de Atividade e Lançamentos")
        st.dataframe(df_plataform_cycles, use_container_width = True, hide_index = True)