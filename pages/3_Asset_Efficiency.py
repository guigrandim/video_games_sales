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

st.set_page_config(page_title = 'Asset Efficiency', page_icon = '🎮', layout = 'wide')

#===================================
# Functions
#===================================

manufacture_colors = {
        'Sony': '#f1c40f',
        'Nintendo': '#e74c3c',
        'Microsoft': '#f1948a',
        'Sega': '#1abc9c',
        'Atari': '#3498db',
        'NEC' : "#f5299d",
        'SNK': "#00FFFB",
        '3DO': "#B1B19D",
        'Mattel':"#2D0018"
    }

#Função 1 - Market Share de Consoles na Historia
def market_share_consoles_history(df1):
    
    plataform_consoles = df1.loc[(df1['plataform'] == 'Console') & (df1['console'] != 'All') & (df1['total_sales'] > 0)]
    
    total_sales_console = (
        plataform_consoles.groupby(['console_name', 'manufacture'])['total_sales']
        .sum()
        .sort_values(ascending = False)
        .reset_index()
    )
    
    total_sales_console['market_share'] = (
    total_sales_console.groupby('manufacture')['total_sales']
    .transform(lambda x: (x / x.sum() * 100).round(2))
    )
    
    total_sales_console['color'] = (
        total_sales_console['manufacture']
        .map(manufacture_colors)
        .fillna('#888888')
    )
    
    fig = px.treemap(
        total_sales_console,
        path=['manufacture', 'console_name'],
        values='total_sales',
        color='manufacture',
        color_discrete_map=manufacture_colors,
        custom_data=['market_share', 'total_sales', 'manufacture'],
        title='Ranking Histórico de Consoles — Volume Total de Vendas',
    )

    fig.update_traces(
        texttemplate='<b>%{label}</b><br>%{customdata[1]:,.1f}M',
        hovertemplate=(
            '<b>%{label}</b><br>'
            'Fabricante: %{customdata[2]}<br>'
            'Vendas totais: %{customdata[1]:,.1f}M<br>'
            'Market share (fabricante): %{customdata[0]:.2f}%'
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

#Função 2 - Attach Rate (Eficiencia)
def eficience_per_console(df1):
    plataform_consoles = df1.loc[(df1['plataform'] == 'Console') & (df1['console'] != 'All') & (df1['total_sales'] > 0)]
    
    eficience_sales_console = (
        plataform_consoles.groupby(['console_name', 'manufacture'])
        .agg(
            total_sales = ('total_sales', 'sum'),
            unique_title = ('title', 'nunique')
        )
        .reset_index()
    )

    eficience_sales_console = eficience_sales_console[eficience_sales_console['unique_title'] > 5]
    eficience_sales_console['attach_ratio'] = (eficience_sales_console['total_sales'] / eficience_sales_console['unique_title']).round(3)
    eficience_sales_console = eficience_sales_console.sort_values('attach_ratio', ascending = False)
    
    eficience_sales_console['color'] = (eficience_sales_console['manufacture'].map(manufacture_colors).fillna('#888888'))
    
    fig = go.Figure(go.Bar(
        x=eficience_sales_console['attach_ratio'],
        y=eficience_sales_console['console_name'],
        orientation='h',
        marker_color=eficience_sales_console['color'],
        text=eficience_sales_console['attach_ratio'].apply(lambda x: f'{x:.2f}M'),
        textposition='outside',
        cliponaxis=False,
        customdata=eficience_sales_console[['manufacture', 'total_sales', 'unique_title']],
        hovertemplate=(
            '<b>%{y}</b><br>'
            'Fabricante: %{customdata[0]}<br>'
            'Attach ratio: %{x:.2f}M vendas/título<br>'
            'Vendas totais: %{customdata[1]:,.1f}M<br>'
            'Títulos únicos: %{customdata[2]}'
            '<extra></extra>'
        ),
    ))
    fig.update_layout(
        title=dict(text='Eficiência por Console — Vendas por Título', font=dict(size=18), x=0.01),
        xaxis=dict(
            title='Vendas médias por título (M)',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.06)',
            automargin=True,
        ),
        yaxis=dict(title='', categoryorder='total ascending'),
        height=max(400, len(eficience_sales_console) * 32),
        margin=dict(t=50, l=10, r=150, b=40),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig

#Função 3 - Console Premium Index (% de jogos com Critic_Score > 8.0)

def console_premium_index(df1):
    
    plataform_consoles = df1.loc[
        (df1['plataform'] == 'Console') &
        (df1['console'] != 'All') &
        (df1['total_sales'] > 0)
    ]
    
    total_avaliados = (
        plataform_consoles[plataform_consoles['critic_score'].notna()]
        .groupby(['console_name', 'manufacture'])['title']
        .nunique()
        .reset_index()
        .rename(columns={'title': 'total_avaliados'})
    )
    
    total_avaliados = total_avaliados[total_avaliados['total_avaliados'] >= 10]
    consoles_validos = total_avaliados['console_name'].tolist()
    
    premium = (
        plataform_consoles[
            (plataform_consoles['critic_score'] > 8.0) &
            (plataform_consoles['console_name'].isin(consoles_validos))
        ]
        .groupby('console_name')['title']
        .nunique()
        .reset_index()
        .rename(columns={'title': 'titulos_premium'})
    )
    
    result = total_avaliados.merge(premium, on='console_name', how='left')
    result['titulos_premium'] = result['titulos_premium'].fillna(0)
    result['pct_premium'] = (
        (result['titulos_premium'] / result['total_avaliados'] * 100).round(1)
    )
    result = result.sort_values('pct_premium', ascending=False)
    
    result['color'] = result['manufacture'].map(manufacture_colors).fillna('#888888')
    
    fig = go.Figure(go.Bar(
        x=result['pct_premium'],
        y=result['console_name'],
        orientation='h',
        marker_color=result['color'],
        cliponaxis=False,
        text=result.apply(
            lambda r: f"{r['pct_premium']}%  ({int(r['titulos_premium'])}/{int(r['total_avaliados'])})",
            axis=1
        ),
        textposition='outside',
        customdata=result[['manufacture', 'titulos_premium', 'total_avaliados']],
        hovertemplate=(
            '<b>%{y}</b><br>'
            'Fabricante: %{customdata[0]}<br>'
            'Títulos premium: %{customdata[1]}<br>'
            'Total avaliados: %{customdata[2]}<br>'
            'Biblioteca premium: %{x:.1f}%'
            '<extra></extra>'
        ),
    ))

    fig.update_layout(
        title=dict(
            text='% da Biblioteca Premium por Console (critic score > 8.0)',
            font=dict(size=18),
            x=0.01,
        ),
        xaxis=dict(
            title='% de títulos com nota > 8.0',
            ticksuffix='%',
            range=[0, result['pct_premium'].max() * 1.25],  # espaço pro texto externo
            showgrid=True,
            gridcolor='rgba(0,0,0,0.06)',
        ),
        yaxis=dict(
            title='',
            categoryorder='total ascending',
            categoryarray=result['console_name'].tolist(),
        ),
        height=max(400, len(result) * 32),
        margin=dict(t=50, l=10, r=180, b=40),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig

#Função 4 - Ciclo de Vitalidade dos Consoles
def vitality_cycle_consoles(df1):

    plataform_consoles = df1.loc[
        (df1['plataform'] == 'Console') &
        (df1['console'] != 'All') &
        (df1['total_sales'] > 0) &
        (df1['start_year'].notna()) &
        (df1['release_date'].notna())
    ].copy()

    plataform_consoles['release_year_title'] = (
        pd.to_datetime(plataform_consoles['release_date'], errors='coerce').dt.year
    )

    plataform_consoles = plataform_consoles[plataform_consoles['release_year_title'].notna()]

    plataform_consoles['life_year'] = (
        plataform_consoles['release_year_title'] - plataform_consoles['start_year'] + 1
    ).astype(int)

    plataform_consoles = plataform_consoles[
        (plataform_consoles['life_year'] >= 1) &
        (plataform_consoles['life_year'] <= 15)
    ]

    cycle = (
        plataform_consoles.groupby(['console_name', 'manufacture', 'life_year'])['total_sales']
        .sum()
        .reset_index()
    )

    cycle['pct'] = (
        cycle.groupby('console_name')['total_sales']
        .transform(lambda x: (x / x.sum() * 100).round(2))
    )

    valid_consoles = (
        cycle.groupby('console_name')['life_year']
        .nunique()
        .loc[lambda x: x >= 3]
        .index
    )
    cycle = cycle[cycle['console_name'].isin(valid_consoles)]

    console_order = (
        cycle[['console_name', 'manufacture']]
        .drop_duplicates()
        .sort_values(['manufacture', 'console_name'])
        ['console_name']
        .tolist()
    )

    max_life = int(cycle['life_year'].max())

    pivot = (
        cycle.pivot_table(
            index='console_name',
            columns='life_year',
            values='pct',
            aggfunc='sum'
        )
        .reindex(index=console_order)
        .reindex(columns=range(1, max_life + 1))
    )

    manufacture_map = (
        cycle.drop_duplicates('console_name')
        .set_index('console_name')['manufacture']
    )

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[f'Ano {i}' for i in pivot.columns],
        y=pivot.index.tolist(),
        colorscale=[
            [0.0,  'rgba(0,0,0,0)'],
            [0.01, '#EFF6FF'],
            [0.25, '#93C5FD'],
            [0.55, '#2563EB'],
            [0.80, '#1E3A8A'],
            [1.0,  '#0F172A'],
        ],
        zmin=0,
        zmax=float(pd.DataFrame(pivot.values).stack().max()),
        xgap=2,
        ygap=2,
        hovertemplate=(
            '<b>%{y}</b><br>'
            '%{x}<br>'
            'Participação: %{z:.1f}% das vendas totais'
            '<extra></extra>'
        ),
        colorbar=dict(
            title=dict(text='% vendas<br>históricas', side='right'),
            thickness=12,
            len=0.6,
            ticksuffix='%',
        ),
    ))

    for console in pivot.index:
        row = pivot.loc[console]
        if row.isna().all():
            continue
        peak_col = row.idxmax()
        if pd.isna(peak_col):
            continue
        col_idx = list(pivot.columns).index(peak_col)
        row_idx = pivot.index.tolist().index(console)
        fig.add_annotation(
            x=col_idx, y=row_idx,
            text='▲', showarrow=False,
            font=dict(size=8, color='white'),
            opacity=0.9,
        )

    consoles_list = pivot.index.tolist()
    prev_manufacture = None
    for i, console in enumerate(consoles_list):
        current_manufacture = manufacture_map.get(console, '')
        if prev_manufacture and current_manufacture != prev_manufacture:
            fig.add_hline(
                y=i - 0.5,
                line=dict(color='rgba(255,255,255,0.6)', width=2, dash='dot'),
            )
        prev_manufacture = current_manufacture

    tick_colors = [
        manufacture_colors.get(manufacture_map.get(c, ''), '#888888')
        for c in consoles_list
    ]

    fig.update_layout(
        title=dict(
            text='Ciclo de Vitalidade dos Consoles — % de Vendas por Ano de Vida',
            font=dict(size=18),
            x=0.01,
        ),
        xaxis=dict(title='Ano de vida do console', tickangle=0, side='bottom'),
        yaxis=dict(
            title='',
            autorange='reversed',
            tickmode='array',
            tickvals=list(range(len(consoles_list))),
            ticktext=[
                f'<span style="color:{tick_colors[i]}">{c}</span>'
                for i, c in enumerate(consoles_list)
            ],
        ),
        height=max(500, len(pivot) * 28),
        margin=dict(t=60, l=160, r=20, b=60),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig

#Função 5 - Dias até o Primeiro Hit (Vendas Acima de 1M)
def first_hit_analysis(df1):

    df_hits = df1[
        (df1['total_sales'] >= 1) &
        (df1['release_date'].notna()) & 
        (df1['release_date_console'].notna()) &
        (df1['plataform'] == 'Console')
    ].copy()

    df_hits['release_date'] = pd.to_datetime(df_hits['release_date'], errors='coerce')
    df_hits['release_date_console'] = pd.to_datetime(df_hits['release_date_console'], errors='coerce')

    df_hits['days_to_hit'] = (df_hits['release_date'] - df_hits['release_date_console']).dt.days
    df_hits = df_hits[df_hits['days_to_hit'] >= 0]

    df_first_hit = (
        df_hits.loc[df_hits.groupby('console_name')['days_to_hit'].idxmin()]
        [['console_name', 'title', 'days_to_hit', 'total_sales', 'manufacture']]
        .sort_values('days_to_hit')
        .reset_index(drop=True)
    )

    # Consoles com days_to_hit = 0 → ajusta para 1 para visibilidade no gráfico
    df_first_hit['days_to_hit_plot'] = df_first_hit['days_to_hit'].clip(lower=1)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_first_hit['days_to_hit_plot'],
        y=df_first_hit['console_name'],
        orientation='h',
        marker_color=df_first_hit['manufacture'].map(manufacture_colors).fillna('#95a5a6'),
        cliponaxis=False,
        text=df_first_hit['days_to_hit'].apply(
            lambda x: 'Lançamento' if x == 0 else f'{int(x)} dias'
        ),
        textposition='outside',
        customdata=df_first_hit[['title', 'total_sales', 'manufacture', 'days_to_hit']],
        hovertemplate=(
            '<b>%{y}</b><br>'
            'Primeiro Hit: %{customdata[0]}<br>'
            'Dias até o Hit: %{customdata[3]}<br>'
            'Vendas: %{customdata[1]:.2f}M<br>'
            'Fabricante: %{customdata[2]}'
            '<extra></extra>'
        ),
    ))

    fig.update_layout(
        title=dict(text='Tempo até o Primeiro Hit por Console', font=dict(size=18), x=0.01),
        xaxis=dict(
            title='Dias após lançamento do console',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.06)',
        ),
        yaxis=dict(
            title='',
            categoryorder='total ascending',
        ),
        height=max(500, len(df_first_hit) * 32),
        margin=dict(l=10, r=150, t=50, b=20),
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
st.title ('🎮 Plataforma e Hardware - Eficiencia de Ativos')

#Call the Functions
fig_market_share_consoles = market_share_consoles_history(df1)  # <- Função 1 - Market Share de Consoles na Historia
fig_ratio_sales_per_title_unique = eficience_per_console(df1)   # <- Função 2 - #Função 2 - Attach Rate (Eficiencia)
fig_console_premium = console_premium_index(df1)                # <- Função 3 - Console Premium Index (% de jogos com Critic_Score > 8.0)
fig_vitality_cycle = vitality_cycle_consoles(df1)               # <- Função 4 - Ciclo de Vitalidade dos Consoles
fig_first_hit_analysis = first_hit_analysis(df1)                # <- Função 5 - Dias até o Primeiro Hit (Vendas Acima de 1M)

st.divider()

#Create KPIs In Page
with st.container():
    st.markdown("### Dominância Historico de Console - Market Share")
    st.plotly_chart(fig_market_share_consoles, width='stretch')

st.divider()

st.markdown("### Classificação dos Consoles conforme Venda e Critic Score")
col1, col2 = st.columns(2)
with st.container():
    with col1:
        st.plotly_chart(fig_ratio_sales_per_title_unique, width='stretch')

    with col2:
        st.plotly_chart(fig_console_premium, width='stretch')

st.divider()

with st.container():
    st.markdown("### Ciclo de Vitalidade dos Consoles")
    st.plotly_chart(fig_vitality_cycle, width='stretch')

st.divider()

with st.container():
    st.markdown("### Dias até o Primeiro Hit (Vendas > 1M)")
    st.plotly_chart(fig_first_hit_analysis, width='stretch')