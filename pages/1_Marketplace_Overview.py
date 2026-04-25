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
import numpy as np

#==================================
# Configuration Page
#==================================

st.set_page_config(page_title = 'Marketplace Overview', page_icon = '🏠', layout = 'wide')

#===================================
# Functions
#===================================

#Define as cores dos graficos e dataframes
colors = {
    'NA'    : '#63B3ED',  # azul claro
    'JP'    : '#0047AB',  # azul escuro
    'PAL'   : '#FC8181',  # rosa claro
    'Other' : '#E53E3E'   # vermelho
}

#Função 1: Total de Vendas e Contagem de Titulos
def total_sales_and_titles(df1):
    """
    Calcula métricas gerais de volume do dataset.

    Retorna o total de vendas globais, a contagem total de registros
    e a quantidade de títulos únicos — usados tipicamente em st.metric
    para dar contexto ao usuário antes das análises detalhadas.

    Responde às perguntas:
    "Qual o volume total de vendas do mercado analisado?"
    "Quantos jogos únicos existem no dataset?"
    "Quantos registros existem considerando entradas multi-plataforma?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com dataset_clean() aplicado.

    Retorna
    -------
    total_sales : Soma total de vendas globais em milhões.
    total_titles : Total de registros no DataFrame (incluindo duplicatas por plataforma).
    unique_titles : Quantidade de títulos únicos no dataset.
    """

    # ── 1. Vendas totais globais ───────────────────────────────────────────────
    total_sales = df1['total_sales'].sum().round(1)

    # ── 2. Contagem de registros e títulos únicos ─────────────────────────────
    total_titles  = df1['title'].count()    # total de linhas — um jogo multi-plataforma conta N vezes
    unique_titles = df1['title'].nunique()  # títulos distintos independente de plataforma

    return total_sales, total_titles, unique_titles

#Função 2: Market Share e Total de Vendas por Região
def market_share_per_region(df1):
    """
    Calcula o market share e o total de vendas por região geográfica,
    e exibe um gráfico de donut com a distribuição percentual.

    Responde às perguntas:
    "Qual região concentra o maior volume de vendas globais?"
    "Qual o peso percentual de cada região no mercado total?"
    "Quanto cada região vendeu em valores absolutos?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com dataset_clean() aplicado.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Gráfico de donut com market share por região.
    sales_global : pd.DataFrame
        DataFrame com região e vendas absolutas em milhões.
    """

    # ── 1. Vendas totais por região ───────────────────────────────────────────
    sales_global_per_region = pd.Series({
        'NA':    df1['na_sales'].fillna(0).sum(),
        'JP':    df1['jp_sales'].fillna(0).sum(),
        'PAL':   df1['pal_sales'].fillna(0).sum(),
        'Other': df1['other_sales'].fillna(0).sum(),
    }).sort_values(ascending=False).round(2).reset_index()

    sales_global_per_region.columns = ['region', 'sales_per_region']

    # ── 2. Cálculo do market share ────────────────────────────────────────────
    total_sales = df1['total_sales'].sum()

    sales_global_per_region['market_share'] = (
        (sales_global_per_region['sales_per_region'] / total_sales) * 100
    ).round(2)

    # ── 3. Gráfico de donut ───────────────────────────────────────────────────
    fig = go.Figure(go.Pie(
        labels=sales_global_per_region['region'],
        values=sales_global_per_region['market_share'],
        hole=0.45,
        marker=dict(
            colors=[colors[r] for r in sales_global_per_region['region']],  # ← paleta global
            line=dict(color='rgba(0,0,0,0.2)', width=2),
        ),
        texttemplate='<b>%{label}</b><br>%{value:.1f}%',
        textposition='outside',
        hovertemplate=(
            '<b>%{label}</b><br>'
            'Market share: %{value:.2f}%<br>'
            'Vendas: %{customdata:.2f}M'
            '<extra></extra>'
        ),
        customdata=sales_global_per_region['sales_per_region'],
    ))

    # Anotação central com total global
    fig.add_annotation(
        text=f'<b>{total_sales/1000:.1f}B</b><br>vendas globais',
        x=0.5, y=0.5,
        xref='paper', yref='paper',
        showarrow=False,
        font=dict(size=13, color='white'),
        align='center',
    )

    fig.update_layout(
        title=dict(
            text='Market Share por Região',
            font=dict(size=18),
            x=0.01,
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.15,
            xanchor='left',
            x=0,
        ),
        height=420,
        margin=dict(t=50, l=10, r=10, b=60),
        paper_bgcolor='rgba(0,0,0,0)',
    )

    # ── 4. DataFrame de retorno ───────────────────────────────────────────────
    sales_global = sales_global_per_region[['region', 'sales_per_region']]

    return fig, sales_global

#Função 3: Total de Vendas Premium por Região
def region_premium_title(df1):
    """
    Calcula o total de vendas de títulos Premium por região geográfica
    e identifica a região com maior volume de vendas premium.

    Responde às perguntas:
    "Qual região consome mais jogos considerados Premium?"
    "Como se distribuem as vendas de títulos premium entre as regiões?"
    "Existe alguma região com apetite desproporcional por jogos de alta qualidade?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com dataset_clean() aplicado.
        Deve conter a coluna 'classification' com o valor 'Premium'.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Gráfico de barras horizontais com vendas premium por região.
    sales_global_premium_top : str
        Nome da região com maior volume de vendas premium.
    sales_global_premium_per_region : pd.DataFrame
        DataFrame com região e vendas premium em milhões.
    """

    # ── 1. Filtra títulos Premium ─────────────────────────────────────────────
    df_premium = df1[df1['classification'] == 'Premium']

    # ── 2. Vendas premium por região ──────────────────────────────────────────
    sales_global_premium_per_region = pd.Series({
        'NA':    df_premium['na_sales'].fillna(0).sum(),
        'JP':    df_premium['jp_sales'].fillna(0).sum(),
        'PAL':   df_premium['pal_sales'].fillna(0).sum(),
        'Other': df_premium['other_sales'].fillna(0).sum(),
    }).sort_values(ascending=True).round(2).reset_index()   # ascending=True → maior no topo

    sales_global_premium_per_region.columns = ['region', 'sales_premium_per_region']

    # ── 3. Região líder em vendas premium ─────────────────────────────────────
    sales_global_premium_top = sales_global_premium_per_region.iloc[-1]['region']

    # ── 4. % do total premium por região ─────────────────────────────────────
    total_premium = sales_global_premium_per_region['sales_premium_per_region'].sum()
    sales_global_premium_per_region['pct'] = (
        (sales_global_premium_per_region['sales_premium_per_region'] / total_premium) * 100
    ).round(1)

    # ── 5. Gráfico de barras horizontais ──────────────────────────────────────
    fig = go.Figure(go.Bar(
        x=sales_global_premium_per_region['sales_premium_per_region'],
        y=sales_global_premium_per_region['region'],
        orientation='h',
        marker_color=[colors[r] for r in sales_global_premium_per_region['region']],
        cliponaxis=False,
        text=sales_global_premium_per_region.apply(
            lambda r: f"{r['sales_premium_per_region']:.2f}M  ({r['pct']:.1f}%)", axis=1
        ),
        textposition='outside',
        hovertemplate=(
            '<b>%{y}</b><br>'
            'Vendas Premium: %{x:.2f}M<br>'
            'Share do premium: %{customdata:.1f}%'
            '<extra></extra>'
        ),
        customdata=sales_global_premium_per_region['pct'],
    ))

    fig.update_layout(
        title=dict(
            text='Vendas de Títulos Premium por Região',
            font=dict(size=18),
            x=0.01,
        ),
        xaxis=dict(
            title='Vendas Totais Premium (M)',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.06)',
            range=[0, sales_global_premium_per_region['sales_premium_per_region'].max() * 1.3],
        ),
        yaxis=dict(title='', categoryorder='total ascending'),
        height=300,
        margin=dict(t=50, l=10, r=150, b=40),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig, sales_global_premium_top, sales_global_premium_per_region

#Função 4: Distribuição de Vendas por País
def sales_per_country(df1):
    """
    Gera um mapa coroplético com o total de vendas por país de origem
    da holding publicadora.

    Responde às perguntas:
    "Quais países concentram o maior volume de vendas da indústria?"
    "Existe dominância geográfica na publicação de jogos?"
    "Como se distribui globalmente o poder de mercado das holdings?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com dataset_clean() aplicado.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Mapa coroplético com total de vendas e títulos únicos por país.
    """

    # ── 1. Agrupamento por país da holding publicadora ────────────────────────
    sales_per_country_holdings = (
        df1.groupby('holdings_publisher_country')
        .agg(
            total_sales   = ('total_sales', 'sum'),
            unique_titles = ('title',       'nunique'),  # ← era count (contava duplicatas)
        )
        .reset_index()
        .sort_values('total_sales', ascending=False)
    )

    # ── 2. Remove países sem vendas ───────────────────────────────────────────
    sales_per_country_holdings = sales_per_country_holdings[
        sales_per_country_holdings['total_sales'] > 0
    ]

    # ── 3. Escala logarítmica para não deixar USA/JPN dominar a paleta ────────
    sales_per_country_holdings['total_sales_log'] = np.log1p(
        sales_per_country_holdings['total_sales']
    )

    # ── 4. Mapa coroplético ───────────────────────────────────────────────────
    fig = px.choropleth(
        sales_per_country_holdings,
        locations='holdings_publisher_country',
        color='total_sales_log',
        hover_data={
            'total_sales':     True,
            'unique_titles':   True,
            'total_sales_log': False,
        },
        title='Vendas Totais por País de Origem da Holding Publicadora',
        color_continuous_scale='RdYlGn',
        labels={
            'holdings_publisher_country': 'País',
            'total_sales':                'Vendas Totais (M)',
            'unique_titles':              'Títulos Únicos',
            'total_sales_log':            'Escala Log',
        }
    )

    fig.update_coloraxes(
        colorbar=dict(
            title='Vendas (log)',
            tickvals=[np.log1p(v) for v in [1, 10, 100, 500, 1000, 5000]],
            ticktext=['1M', '10M', '100M', '500M', '1B', '5B'],
        )
    )

    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular',
            bgcolor='rgba(0,0,0,0)',
            showocean=False,
            showlakes=False,
        ),
        margin=dict(r=0, t=40, l=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig

#Função 5: Ranking das 5 maiores holdings por volume total de vendas
def top5_holdings_ranking(df1):
    """
    Gera um gráfico de barras horizontal com o ranking das 5 maiores holdings
    por volume total de vendas, segmentado por região e com indicadores de
    eficiência (ticket médio e score médio).

    Responde à pergunta:
    "Quais são as 5 maiores holdings em vendas e como se distribuem
     globalmente entre as regiões?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com dataset_clean() aplicado.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Gráfico de barras empilhadas por região com anotações de ticket médio
        e score médio por holding.
    """

    # ── 1. Limpeza ────────────────────────────────────────────────────────────
    df_clean = (
        df1.dropna(subset=['holdings_publisher'])
        .pipe(lambda d: d[d['holdings_publisher'].str.strip() != ''])
        .loc[lambda d: d['total_sales'] > 0]
    )

    # ── 2. Agrupamento ────────────────────────────────────────────────────────
    top5 = (
        df_clean.groupby('holdings_publisher')
        .agg(
            total_sales   = ('total_sales',   'sum'),
            na_sales      = ('na_sales',      'sum'),
            jp_sales      = ('jp_sales',      'sum'),
            pal_sales     = ('pal_sales',     'sum'),
            other_sales   = ('other_sales',   'sum'),
            avg_score     = ('critic_score',  'mean'),
            unique_titles = ('title',         'nunique'),
        )
        .round(2)
        .reset_index()
        .nlargest(5, 'total_sales')
        .sort_values('total_sales', ascending=True)  # ascending=True → maior no topo
    )

    top5['ticket_medio'] = (top5['total_sales'] / top5['unique_titles']).round(2)

    # ── 3. Paleta de regiões ──────────────────────────────────────────────────
    REGION_COLORS = {
        'América do Norte': '#2196F3',
        'Japão':            '#E4000F',
        'PAL':              '#4CAF50',
        'Outros':           '#9E9E9E',
    }

    region_map = {
        'na_sales':    'América do Norte',
        'jp_sales':    'Japão',
        'pal_sales':   'PAL',
        'other_sales': 'Outros',
    }

    # ── 4. Barras empilhadas por região ───────────────────────────────────────
    fig = go.Figure()

    for col, label in region_map.items():
        fig.add_trace(go.Bar(
            x=top5[col],
            y=top5['holdings_publisher'],
            name=label,
            orientation='h',
            marker_color=REGION_COLORS[label],
            hovertemplate=(
                f'<b>%{{y}}</b><br>'
                f'{label}: %{{x:.2f}}M'
                '<extra></extra>'
            ),
        ))

    # ── 5. Anotações de ticket médio e score por holding ──────────────────────
    for _, row in top5.iterrows():
        fig.add_annotation(
            x=row['total_sales'],
            y=row['holdings_publisher'],
            text=(
                f"  🎯 {row['ticket_medio']:.2f}M/título"
                f"  ⭐ {row['avg_score']:.1f}"
            ),
            showarrow=False,
            xanchor='left',
            font=dict(size=10, color='white'),
        )

    # ── 6. Layout ─────────────────────────────────────────────────────────────
    fig.update_layout(
        barmode='stack',
        title=dict(
            text='Top 5 Holdings por Volume de Vendas — Breakdown Regional<br>'
                 '<sup>Barras empilhadas por região | 🎯 Ticket médio por título | ⭐ Score médio</sup>',
            font=dict(size=18),
            x=0.01,
        ),
        xaxis=dict(
            title='Vendas Totais (M)',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.06)',
            range=[0, top5['total_sales'].max() * 1.25],  # espaço para anotações
        ),
        yaxis=dict(title=''),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.30,
            xanchor='left',
            x=0,
        ),
        height=420,
        margin=dict(t=60, l=10, r=20, b=80),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
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
st.title ('🏠 Home - Marketplace Overview')

#Call the Functions
kpi_total_sales_global, kpi_total_title_dataset, kpi_unique_titles = total_sales_and_titles(df1)                        # <- Função 1: Total de Vendas e Contagem de Titulos
fig_sales_market_share, df_sales_global = market_share_per_region(df1)                                                  # <- Função 2: Market Share e Total de Vendas por Região
fig_sales_premium_region, kpi_sales_global_premium, df_sales_global_premium_per_region  = region_premium_title(df1)     # <- Função 3: Total de Vendas Premium por Região
fig_sales_world = sales_per_country(df1)                                                                                # <- Função 4: Mapa das Vendas de Jogos no Mundo.
fig_top5_holdings = top5_holdings_ranking(df1)                                                                          # <- Função 5: Ranking das 5 maiores holdings por volume total de vendas

st.divider()

#Create KPIs In Page
with st.container():
    st.markdown("### Vendas de Jogos Globais e Titulos Vendidos")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Vendas Globais", f"{kpi_total_sales_global:,.1f} M")
    
    with col2:
        st.metric('Reg. Vendas Premium -  Até 12/24', kpi_sales_global_premium)
    
    with col3:
        st.metric('Registros', f'{kpi_total_title_dataset:,}',
            delta=f'{kpi_total_title_dataset - kpi_unique_titles:,} entradas multi-plataforma',
            delta_color='off')
    
    with col4:
        st.metric('Títulos Únicos', f'{kpi_total_title_dataset:,}')

st.divider()

with st.container():
    st.markdown("### Comportamento e Segmentação Global de Vendas")
    col1, col2 = st.columns([2,1])
    
    with col1:
        st.plotly_chart(fig_sales_market_share, width='stretch')
    
    with col2:
        st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
        st.dataframe(df_sales_global, width='stretch', hide_index = True)

st.divider()

with st.container():
    st.markdown("### Vendas Premium por Região")
    col1, col2 = st.columns([2,1])
    
    with col1:
        st.plotly_chart(fig_sales_premium_region, width='stretch')
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(df_sales_global_premium_per_region, width='stretch', hide_index = True)

st.divider()

with st.container():
    st.markdown("### Top 5 Holdings em Vendas")
    st.plotly_chart(fig_top5_holdings, width='stretch')

st.divider()

with st.container():
    st.markdown("### Distribuição de Vendas no Mundo")
    st.plotly_chart(fig_sales_world, width='stretch')