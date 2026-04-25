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

st.set_page_config(page_title = 'Competitive Intelligence', page_icon = '🏢', layout = 'wide')

#===================================
# Functions
#===================================

holdings_colors = {
    # Estados Unidos (azul: do mais escuro ao mais claro)
    'Acclaim Entertainment': "#008031",      # navy
    'Disney': "#26CD00",                    # mediumblue
    'Electronic Arts': "#1EFF2D",           # dodgerblue
    'Microsoft Corporation': "#61E141",     # royalblue
    'Take Two Interactive': "#53B446",      # steelblue
    'THQ': "#7FA05F",                       # cadetblue
    'Warner Bros Discovery': "#88ED64",     # cornflowerblue

    # Japão (vermelho: do mais escuro ao mais alaranjado)
    'Bandai Namco': '#8B0000',              # darkred
    'Capcom': '#B22222',                    # firebrick
    'Koei Tecmo Holdings': '#DC143C',       # crimson
    'Konami Group': '#CD5C5C',              # indianred
    'Nintendo': '#FF0000',                  # red
    'Sega Sammy Holdings': '#FF4500',       # orangered
    'Sony Interactive Entertainment': '#FF6347',  # tomato
    'Square Enix Holdings': '#FF7F50',      # coral

    # França (azul francês: do mais escuro ao mais claro)
    'Atari SA': '#0055A4',                  # bleu de France escuro
    'Ubisoft': '#318CE7',                   # bleu de France médio
    'Vivendi': '#66B5F0',                   # bleu de France claro

    # Reino Unido (roxo)
    'Eidos Interactive': '#800080',         # purple

    # Suécia (amarelo ouro)
    'Embracer Group': '#FFD700',            # gold
}

colors = {
    'NA'    : '#63B3ED',  # azul claro
    'JP'    : '#0047AB',  # azul escuro
    'PAL'   : '#FC8181',  # rosa claro
    'Other' : '#E53E3E'   # vermelho
}

#Função 1 - Concentração de Mercado
def market_concentration(df1):
    # Limpeza: vendas > 0 e holdings não nulas
    df_clean = df1.loc[df1['total_sales'] > 0].dropna(subset=['holdings_publisher'])
    
    # Agrega vendas totais por holding
    sales_by_holding = (
        df_clean.groupby('holdings_publisher', as_index=False)['total_sales']
        .sum()
        .sort_values('total_sales', ascending=False)
    )
    
    # Seleciona as top N holdings
    top_holdings = sales_by_holding.head(20).copy()
    
    # Adiciona coluna com o país da holding (ISO3) – usando a primeira ocorrência
    holding_to_country = (
        df_clean.dropna(subset=['holdings_publisher_country'])
        .groupby('holdings_publisher')['holdings_publisher_country']
        .first()
        .to_dict()
    )
    top_holdings['country'] = top_holdings['holdings_publisher'].map(holding_to_country).fillna('Unknown')
    
    # Cria treemap (cores automáticas para cada holding)
    fig = px.treemap(
        top_holdings,
        path=['holdings_publisher'],
        values='total_sales',
        color= 'holdings_publisher',
        color_discrete_map=holdings_colors,
        custom_data=['holdings_publisher', 'total_sales', 'country'],
        title=f'Distribuição de Vendas - Top 20 Holdings'
    )
    
    fig.update_traces(
        texttemplate='<b>%{label}</b><br>%{customdata[1]:,.1f}M',
        hovertemplate=(
            '<b>%{label}</b><br>'
            'Holding: %{customdata[0]}<br>'
            'País: %{customdata[2]}<br>'
            'Vendas totais: %{customdata[1]:,.1f}M<br>'
            '<extra></extra>'
        ),
        textposition='middle center',
        marker=dict(line=dict(width=2, color='white')),
    )
    
    fig.update_layout(
        margin=dict(t=50, l=10, r=10, b=10),
        height=600,
        title=dict(font=dict(size=18), x=0.01),
    )
    
    return fig

#Função 2: Índice de Exportação - Vendas em regiões estrangeiras vs. país de origem
def top_holding_home_vs_foreign(df1):
    # Mapeamento país -> região
    home_region_map = {
        'USA': 'NA',
        'JPN': 'JP',
        'FRA': 'PAL', 'DEU': 'PAL', 'GBR': 'PAL', 'SWE': 'PAL',
        'ITA': 'PAL', 'NLD': 'PAL', 'DNK': 'PAL', 'FIN': 'PAL',
        'IRL': 'PAL', 'POL': 'PAL', 'CYP': 'PAL', 'AUS': 'PAL',
        'RUS': 'PAL',
        'KOR': 'Other', 'CHN': 'Other', 'IND': 'Other',
        'ARG': 'Other', 'HKG': 'Other'
    }

    # Agregação
    df_cma = df1.groupby('holdings_publisher_country').agg(
        na_sales=('na_sales', 'sum'),
        jp_sales=('jp_sales', 'sum'),
        pal_sales=('pal_sales', 'sum'),
        other_sales=('other_sales', 'sum'),
        total_sales=('total_sales', 'sum')
    ).reset_index().round(2)

    # Mapear região doméstica
    df_cma['home_region'] = df_cma['holdings_publisher_country'].map(home_region_map)

    # Calcular vendas domésticas e estrangeiras
    def calc_sales(row):
        if row['home_region'] == 'NA':
            dom = row['na_sales']
        elif row['home_region'] == 'JP':
            dom = row['jp_sales']
        elif row['home_region'] == 'PAL':
            dom = row['pal_sales']
        else:  # Other
            dom = row['other_sales']
        foreign = row['total_sales'] - dom
        return pd.Series({'domestic_sales': dom, 'foreign_sales': foreign})

    df_cma[['domestic_sales', 'foreign_sales']] = df_cma.apply(calc_sales, axis=1)

    # Selecionar top 20 por total_sales
    top20 = df_cma.sort_values('total_sales', ascending=False).head(14)

    # Gráfico de comparação
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=top20['holdings_publisher_country'],
        x=top20['domestic_sales'],
        orientation='h',
        name='Vendas no país de origem',
        marker_color='blue'
    ))
    fig.add_trace(go.Bar(
        y=top20['holdings_publisher_country'],
        x=top20['foreign_sales'],
        orientation='h',
        name='Vendas no exterior',
        marker_color='orange'
    ))
    fig.update_xaxes(type='log')
    fig.update_layout(
        barmode='group',
        title='Vendas Domésticas vs. Estrangeiras por Holding (Top 15)',
        xaxis_title='Vendas (milhões)',
        height=600,
        yaxis=dict(categoryorder='total ascending')  # ou 'total descending'
    )
    return fig

#Função 3 - In House (National Synergy)
def national_synergy(df1):
    """
    Gera dois gráficos Plotly para análise de sinergia nacional:
    1. Heatmap: Vendas totais por País Desenvolvedor x País Publicadora
       (filtra cruzamentos com vendas abaixo de min_sales_heatmap)
    2. Dataframe dos Top 10 Países com Sinergia In-House (vendas totais,
       ticket médio, Genero Lider em Vendas e Quantidade de Vendas)

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com a função dataset_clean() limpando e enriquecendo o DataFrame

    Retorna
    -------
    fig_heatmap : Figura do heatmap.
    top10 : Dataframe do Ranking
    """    

# ── Limpeza dos dados ──────────────────────────────────────────
    # Valor mínimo de vendas (em milhões) para considerar um cruzamento relevante no heatmap
    min_vendas = 10

    # Limpeza de NaN do Dataframe
    df_clean = df1.dropna(subset=['country_publisher', 'country_developer']).copy()
    df_clean = df_clean[~df_clean['country_publisher'].isin(['Unknown', ''])]
    df_clean = df_clean[~df_clean['country_developer'].isin(['Unknown', ''])]

# ── Criação das Analises ──────────────────────────────────────────

    # Cria o parametro InHouse (Devs e Pubs do Mesmo Pais)
    inhouse = df_clean[df_clean['country_publisher'] == df_clean['country_developer']].copy()
    
    # Agregações por país
    sales_by_country = inhouse.groupby('country_publisher').agg(
        total_sales=('total_sales', 'sum'),
        num_games=('total_sales', 'count')
    ).reset_index()
    
    sales_by_country['ticket_medio'] = sales_by_country['total_sales'] / sales_by_country['num_games']
    
    # Gênero líder por país e finalização do dataframe (top10)
    genre_sales = inhouse.groupby(['country_publisher', 'genre'])['total_sales'].sum().reset_index()
    idx = genre_sales.groupby('country_publisher')['total_sales'].idxmax()
    top_genres = genre_sales.loc[idx, ['country_publisher', 'genre', 'total_sales']]
    top_genres = top_genres.rename(columns={'genre': 'genero_lider', 'total_sales': 'vendas_genero_lider'})
    
    country_stats = sales_by_country.merge(top_genres, on='country_publisher', how='left')
    top10 = country_stats.sort_values('total_sales', ascending=False).head(10)

# ── Criação do HeatMap ──────────────────────────────────────────
    # Pivoteia a tabela para o HeatMap
    pivot = pd.crosstab(
        df_clean['country_developer'],
        df_clean['country_publisher'],
        values=df_clean['total_sales'],
        aggfunc='sum',
        dropna=False
    ).fillna(0)

    mask = pivot >= min_vendas
    linhas_validas = mask.any(axis=1)
    colunas_validas = mask.any(axis=0)
    pivot_filtrado = pivot.loc[linhas_validas, colunas_validas]
    
    pivot_filtrado = pivot_filtrado.loc[
        pivot_filtrado.sum(axis=1) > 0,
        pivot_filtrado.sum(axis=0) > 0
    ]
    
    row_sums_f = pivot_filtrado.sum(axis=1)
    col_sums_f = pivot_filtrado.sum(axis=0)
    pivot_ordenado = pivot_filtrado.loc[
        row_sums_f.sort_values(ascending=False).index,
        col_sums_f.sort_values(ascending=False).index
    ]

    # Escala log: comprime outliers e revela países menores
    z_raw = pivot_ordenado.values.copy().astype(float)
    z_log = np.log1p(z_raw)   # log(1 + x) → zeros viram 0, sem -inf

    # zmax no percentil 95 para não deixar EUA/Japão dominar toda a escala
    valores_positivos = z_log[z_log > 0]
    zmax_cap = float(np.percentile(valores_positivos, 95)) if len(valores_positivos) else z_log.max()

    # Texto customizado no hover (valor real, não log)
    hover_text = [[
        f'Dev: {pivot_ordenado.index[i]}<br>Pub: {pivot_ordenado.columns[j]}<br>Vendas: {z_raw[i,j]:.2f}M'
        for j in range(z_raw.shape[1])]
        for i in range(z_raw.shape[0])
    ]
    
    fig1 = go.Figure(data=go.Heatmap(
        z=z_log,
        x=pivot_ordenado.columns.tolist(),
        y=pivot_ordenado.index.tolist(),
        text=hover_text,
        hovertemplate='%{text}<extra></extra>',
        colorscale='YlOrRd',
        zmin=0,
        zmax=zmax_cap,          # ← cap no p95, outliers ficam na cor máxima
        xgap=2,
        ygap=2,
        colorbar=dict(
            title=dict(text='Vendas (log)', side='right'),
            thickness=12,
            tickvals=[np.log1p(v) for v in [1, 10, 100, 500, 1000, 5000]],
            ticktext=['1M', '10M', '100M', '500M', '1B', '5B'],  # labels legíveis
        ),
    ))

    fig1.update_layout(
        title=f'Sinergia Nacional: Vendas Totais por País Dev × Pub (≥ {min_vendas}M)',
        xaxis=dict(title='País da Publicadora', tickangle=45),
        yaxis=dict(title='País do Desenvolvedor'),
        height=600,
        margin=dict(t=50, b=100, l=10, r=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig1, top10

#Função 4 - Cross Market Appeal
def cross_market_appeal_heatmap(df1):
    """
    Heatmap Cruzado: % de vendas por Holding Publicadora × Região de Destino.

    Normalização por coluna (região soma 100%) — responde à pergunta:
    "Dentro das vendas da NA, quanto veio de jogos publicados pela EA, Nintendo, Sony...?"
    Holdings fora do Top 15 por volume total são agrupadas em 'Outros'.

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com dataset_clean() aplicado.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
    """

    # ── Agrega vendas por holding × região ────────────────────────────────────
    df_region = (
        df1[df1['holdings_publisher'].notna()]
        .pipe(lambda df: df[df['holdings_publisher'].str.strip() != ''])
        .groupby('holdings_publisher')
        .agg(
            na_sales    = ('na_sales',    'sum'),
            jp_sales    = ('jp_sales',    'sum'),
            pal_sales   = ('pal_sales',   'sum'),
            other_sales = ('other_sales', 'sum'),
        )
        .reset_index()
        .round(2)
    )

    df_region['total'] = df_region[['na_sales', 'jp_sales', 'pal_sales', 'other_sales']].sum(axis=1)
    df_region = df_region[df_region['total'] >= 1]

    # ── Agrupa holdings menores em "Outros" ───────────────────────────────────
    top_n = 15

    top_holdings = df_region.nlargest(top_n, 'total')['holdings_publisher'].tolist()

    df_top    = df_region[df_region['holdings_publisher'].isin(top_holdings)].copy()
    df_outros = df_region[~df_region['holdings_publisher'].isin(top_holdings)].copy()

    if not df_outros.empty:
        outros_row = pd.DataFrame([{
            'holdings_publisher': 'Outros',
            'na_sales':    df_outros['na_sales'].sum(),
            'jp_sales':    df_outros['jp_sales'].sum(),
            'pal_sales':   df_outros['pal_sales'].sum(),
            'other_sales': df_outros['other_sales'].sum(),
            'total':       df_outros['total'].sum(),
        }])
        df_region = pd.concat([df_top, outros_row], ignore_index=True)
    else:
        df_region = df_top

    df_region = df_region.drop(columns='total')

    # ── Normalização por coluna: % dentro de cada região ─────────────────────
    regioes = ['na_sales', 'jp_sales', 'pal_sales', 'other_sales']
    df_pct  = df_region.copy()

    for col in regioes:
        total_regiao = df_pct[col].sum()
        df_pct[col] = ((df_pct[col] / total_regiao) * 100).round(2) if total_regiao > 0 else 0

    # Ordena: maior relevância no topo, "Outros" sempre no final
    df_pct['rank_total'] = df_pct[regioes].sum(axis=1)
    df_outros_pct = df_pct[df_pct['holdings_publisher'] == 'Outros']
    df_top_pct    = df_pct[df_pct['holdings_publisher'] != 'Outros'].sort_values('rank_total', ascending=True)
    df_pct = pd.concat([df_outros_pct, df_top_pct], ignore_index=True).drop(columns='rank_total')

    # ── Pivot para o heatmap ──────────────────────────────────────────────────
    pivot = df_pct.set_index('holdings_publisher')[regioes]
    pivot.columns = ['América do Norte', 'Japão', 'PAL (Europa/Oceania)', 'Outros Mercados']

    df_abs = df_region.set_index('holdings_publisher')[regioes]
    df_abs.columns = pivot.columns

    # ── Texto nas células (só exibe se >= 1%) ─────────────────────────────────
    annotations_text = []
    for holding in pivot.index:
        row = []
        for regiao in pivot.columns:
            val = pivot.loc[holding, regiao]
            row.append(f'{val:.1f}%' if val >= 1 else '')
        annotations_text.append(row)

    # ── Hover com valor absoluto + percentual ─────────────────────────────────
    hover_text = []
    for holding in pivot.index:
        row = []
        for regiao in pivot.columns:
            pct_val = pivot.loc[holding, regiao]
            abs_val = df_abs.loc[holding, regiao]
            row.append(
                f'<b>{holding} → {regiao}</b><br>'
                f'Share da região: {pct_val:.2f}%<br>'
                f'Vendas absolutas: {abs_val:.2f}M'
            )
        hover_text.append(row)

    # ── Heatmap ───────────────────────────────────────────────────────────────
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        text=annotations_text,
        texttemplate='%{text}',
        customdata=hover_text,
        hovertemplate='%{customdata}<extra></extra>',
        colorscale='Blues',
        zmin=0,
        zmax=pivot.values.max(),
        xgap=3,
        ygap=3,
        colorbar=dict(
            title=dict(text='% da região', side='right'),
            thickness=12,
            ticksuffix='%',
            len=0.6,
        ),
    ))

    fig.update_layout(
        title=dict(
            text='Cross Market Appeal — Share Regional por Holding Publicadora<br>'
                 '<sup>% das vendas de cada região originadas por holding publicadora</sup>',
            font=dict(size=18),
            x=0.01,
        ),
        xaxis=dict(title='Região de Destino', side='bottom'),
        yaxis=dict(title='Holding Publicadora'),
        height=max(400, len(pivot) * 45),
        margin=dict(t=80, l=10, r=20, b=60),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig

#Função 5 - Concentração da Industria (Desenvolvedores)
def hub_developers(df1):
    """
    Gera um mapa coroplético com a distribuição das desenvolvdoras pelo mundo

    Agrupa os dados pelo país da developer_country, contando a quantidade de desenvolvedores por cada país. 
    Responde à pergunta:
    "Como o desenvolvimento da industria está organizado ?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com dataset_clean() aplicado.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Mapa coroplético com total de desenvolvedores por país.
    """
# ── Organização dos Dados ──────────────────────────────────────────
    #Agrupamento do país de desenvolvimento por cada desenvolvedor (único)
    count_devs_per_country = (
        df1.groupby('country_developer')
        .agg(
            count_devs = ('clean_name_developer', 'nunique'),
            unique_titles = ('title', 'nunique'),
        )
        .reset_index()
        .sort_values('count_devs', ascending=False)
    )

    #Elimina paises sem nenhum desenvolvedor
    count_devs_per_country = count_devs_per_country[
        count_devs_per_country['count_devs'] > 0
    ]
    
    #Transforma em logaritimo para compressão do count distribuindo as classificação mais heterogeneamente
    count_devs_per_country['count_devs_log'] = np.log1p(count_devs_per_country['count_devs'])

# ── Montagem do Gráfico ──────────────────────────────────────────
    fig = px.choropleth(
        count_devs_per_country,
        locations='country_developer',
        color='count_devs_log',
        hover_data={'count_devs': True, 'unique_titles': True, 'count_devs_log': False},
        title='Quantidade de Desenvolvedores Únicos por País',
        color_continuous_scale='RdYlGn',
        labels={
            'country_developer': 'País',
            'count_devs':        'Desenvolvedores Únicos',
            'unique_titles':     'Títulos Desenvolvidos',
        }
    )
    
    fig.update_coloraxes(
        colorbar=dict(
            title='Devs (log)',
            tickvals=[np.log1p(v) for v in [1, 5, 10, 50, 100, 500]],
            ticktext=['1', '5', '10', '50', '100', '500'],
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

#Função 6 - Holding Quality Devs
def quality_holdings_devs(df1):
    """
    Gera um gráfico de barras horizontal com a média do critic_score por holding
    desenvolvedora e uma linha de referência da média global.

    Agrupa os dados pelas holdings responsáveis diretamente pelos estúdios (developers),
    filtrando apenas jogos com avaliação válida (critic_score > 0).
    Responde à pergunta:
    "Como é a qualidade média entregue por cada Holding no desenvolvimento?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com dataset_clean() aplicado.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Gráfico de barras horizontal com a média do critic_score por holding
        desenvolvedora e linha de referência da média global.
    """

# ── Limpeza do Dataset ────────────────────────────────────────────────────
    df_clean_critic_score = (
        df1.loc[df1['critic_score'] > 0]
        .dropna(subset=['critic_score', 'holdings_developer'])
        .pipe(lambda df: df[df['holdings_developer'].str.strip() != ''])
    )

# ── Agrupamento das variáveis ─────────────────────────────────────────────
    quality_holdings = (
        df_clean_critic_score.groupby('holdings_developer')
        .agg(
            avg_critic    = ('critic_score', 'mean'),
            unique_titles = ('title', 'nunique'),
        )
        .reset_index()
    )
    
    # ── Filtra holdings com títulos avaliados insuficientes ───────────────────
    quality_holdings = quality_holdings[quality_holdings['unique_titles'] >= 20]
    
    # ── Organiza o Dataframe arredondando e pegando da maior para a menor média ───────────────────
    quality_holdings['avg_critic'] = quality_holdings['avg_critic'].round(2)
    quality_holdings = quality_holdings.sort_values('avg_critic', ascending=True)
    
    # ── Média global de referência ────────────────────────────────────────────
    global_avg = df_clean_critic_score['critic_score'].mean().round(2)
    
    # ── Gráfico ───────────────────────────────────────────────────────────────
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=quality_holdings['avg_critic'],
        y=quality_holdings['holdings_developer'],
        orientation='h',
        marker=dict(
            color=quality_holdings['avg_critic'],
            colorscale='RdYlGn',
            cmin=quality_holdings['avg_critic'].min(),
            cmax=quality_holdings['avg_critic'].max(),
            showscale=False,
        ),
        cliponaxis=False,
        text=quality_holdings['avg_critic'].apply(lambda x: f'{x:.2f}'),
        textposition='outside',
        customdata=quality_holdings[['unique_titles']],
        hovertemplate=(
            '<b>%{y}</b><br>'
            'Média critic score: %{x:.2f}<br>'
            'Títulos avaliados: %{customdata[0]}'
            '<extra></extra>'
        ),
    ))

    # ── Linha de média global ─────────────────────────────────────────────────
    fig.add_vline(
        x=global_avg,
        line=dict(color='white', width=1.5, dash='dash'),
        annotation_text=f'Média global: {global_avg}',
        annotation_font=dict(size=11, color='white'),
        annotation_xanchor='left',
        annotation_yanchor='top',
    )

    fig.update_layout(
        title=dict(
            text='Qualidade Média por Holding Desenvolvedora (Critic Score)',
            font=dict(size=18),
            x=0.01,
        ),
        xaxis=dict(
            title='Média do Critic Score',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.06)',
            range=[
                quality_holdings['avg_critic'].min() * 0.95,
                quality_holdings['avg_critic'].max() * 1.08,
            ],
        ),
        yaxis=dict(title='', categoryorder='total ascending'),
        height=max(400, len(quality_holdings) * 32),
        margin=dict(t=50, l=10, r=80, b=40),
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
st.title ('🏢 Holdings e Geopolítica - Competitive Intelligence')

#Call the Functions
fig_holdings_sales_concentration = market_concentration(df1)                        # <- Função 1 - Concentração de Mercado
fig_home_away_holdings = top_holding_home_vs_foreign(df1)                           # <- Função 2: Ranking das 5 Maiores Holdings por vendas
fig_national_sinergy_general, fig_national_sinergy_top10 = national_synergy(df1)    # <- Função 3 - In House (National Synergy)
fig_cross_market = cross_market_appeal_heatmap(df1)                                 # <- Função 4 - Cross Market Appeal
fig_hub_industry = hub_developers(df1)                                              # <- Função 5 - Concentração da Industria (Desenvolvedores)
fig_quality_hold_devs = quality_holdings_devs(df1)                                  # <- Função 6 - Holding Quality Devs


st.divider()

#Create KPIs In Page
tab1, tab2 = st.tabs(['Comportamento de Vendas das Empresas', 'Concentração e Avaliação da Industria'])

with tab1:
    with st.container():
        st.markdown('### Concentração de Vendas de Mercado - Holdings - (Cor por Pais de Origem)')
        st.plotly_chart(fig_holdings_sales_concentration, width='stretch')

    st.divider()

    with st.container():
        st.markdown("### Comportamento das Vendas das Holdings")
        st.plotly_chart(fig_home_away_holdings, width='stretch')

    st.divider()

    st.markdown("### Sinergia Nacional - Comportamento entre Devs x Pubs nas Vendas")
    with st.container():
        col1,col2 = st.columns([1, 1.1])
    
        with col1:
            st.plotly_chart(fig_national_sinergy_general, width='stretch')
    
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.dataframe(
                fig_national_sinergy_top10, 
                width='stretch', 
                hide_index = True, 
                height=400,
                column_config={
                    'country_publisher': st.column_config.TextColumn('País'),
                    'total_sales': st.column_config.NumberColumn('Vendas (M)', format='%.2f'),
                    'num_games': st.column_config.NumberColumn('Jogos'),
                    'ticket_medio': st.column_config.NumberColumn('Ticket Médio (M)', format='%.4f'),
                    'genero_lider': st.column_config.TextColumn('Gênero Líder'),
                    'vendas_genero_lider': st.column_config.NumberColumn('Vendas Gênero (M)', format='%.2f'),
        }
    )

    st.divider()

    with st.container():
        st.markdown("### Cross Market Appeal por Publishers")
        st.plotly_chart(fig_cross_market, width='stretch')

with tab2:
    with st.container():
        st.markdown("#Organização da Industria - Hub de Desenvolvimento")
        st.plotly_chart(fig_hub_industry, width='stretch')
    
    st.divider()
    
    with st.container():
        st.markdown("### Qualidade das Holdings pelas suas Desenvolvedoras")
        st.plotly_chart(fig_quality_hold_devs, width='stretch')