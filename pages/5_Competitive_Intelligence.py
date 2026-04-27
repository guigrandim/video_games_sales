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
    """
    Gera um Treemap com a concentração de mercado das Top 20 holdings
    publicadoras por volume total de vendas, colorido pela paleta global
    de holdings com agrupamento geográfico implícito nas cores.

    Responde às perguntas:
    "Quão concentrado é o mercado de publicação de jogos?"
    "Quais holdings dominam o volume global de vendas?"
    "Como se distribui geograficamente o poder de publicação entre as maiores holdings?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com dataset_clean() aplicado.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Treemap com as Top 20 holdings por volume de vendas, colorido
        pela paleta global holdings_colors.
    """

    # ── 1. Limpeza: vendas > 0 e holdings não nulas ───────────────────────────
    df_clean = (
        df1.loc[df1['total_sales'] > 0]
        .dropna(subset=['holdings_publisher'])
        .pipe(lambda d: d[d['holdings_publisher'].str.strip() != ''])
    )

    # ── 2. Agrega vendas totais por holding ───────────────────────────────────
    sales_by_holding = (
        df_clean.groupby('holdings_publisher', as_index=False)['total_sales']
        .sum()
        .sort_values('total_sales', ascending=False)
    )

    # ── 3. Seleciona Top 20 holdings por volume ───────────────────────────────
    top_holdings = sales_by_holding.head(20).copy()

    # ── 4. Mapeia país da holding (primeira ocorrência no dataset) ────────────
    holding_to_country = (
        df_clean.dropna(subset=['holdings_publisher_country'])
        .groupby('holdings_publisher')['holdings_publisher_country']
        .first()
        .to_dict()
    )
    top_holdings['country'] = (
        top_holdings['holdings_publisher']
        .map(holding_to_country)
        .fillna('Unknown')
    )

    # ── 5. Market share do total das Top 20 ───────────────────────────────────
    total_top20 = top_holdings['total_sales'].sum()
    top_holdings['market_share'] = (
        (top_holdings['total_sales'] / total_top20 * 100).round(2)
    )

    # ── 6. Treemap ────────────────────────────────────────────────────────────
    fig = px.treemap(
        top_holdings,
        path=['holdings_publisher'],
        values='total_sales',
        color='holdings_publisher',
        color_discrete_map=holdings_colors,
        custom_data=['holdings_publisher', 'total_sales', 'country', 'market_share'],
        title='Concentração de Mercado — Top 20 Holdings Publicadoras',
    )

    fig.update_traces(
        texttemplate=(
            '<b>%{label}</b><br>'
            '%{customdata[1]:,.1f}M<br>'
            '%{customdata[3]:.1f}%'
        ),
        hovertemplate=(
            '<b>%{customdata[0]}</b><br>'
            'País: %{customdata[2]}<br>'
            'Vendas totais: %{customdata[1]:,.1f}M<br>'
            'Share no Top 20: %{customdata[3]:.2f}%'
            '<extra></extra>'
        ),
        textposition='middle center',
        marker=dict(line=dict(width=2, color='white')),
    )

    fig.update_layout(
        title=dict(
            text='Concentração de Mercado — Top 20 Holdings Publicadoras<br>'
                 '<sup>Tamanho = volume de vendas | Cor = origem geográfica da holding | % = share no Top 20</sup>',
            font=dict(size=18),
            x=0.01,
        ),
        margin=dict(t=70, l=10, r=10, b=10),
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig

#Função 2: Índice de Exportação - Vendas em regiões estrangeiras vs. país de origem
def top_holding_home_vs_foreign(df1):
    """
    Gera um gráfico de barras agrupadas comparando vendas domésticas e
    estrangeiras por país de origem da holding publicadora (Top 14 por volume).

    Vendas domésticas = vendas na região de origem do país da holding.
    Vendas estrangeiras = total de vendas menos as domésticas.

    Responde às perguntas:
    "Quais países de holding dependem mais do mercado doméstico?"
    "Quais holdings têm maior apelo internacional em relação às vendas locais?"
    "Existe diferença de estratégia global entre holdings americanas, japonesas e europeias?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com dataset_clean() aplicado.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Gráfico de barras agrupadas (escala log) com vendas domésticas
        vs. estrangeiras por país da holding, colorido pela paleta global de regiões.
    """

    # ── 1. Mapeamento país ISO3 → região de mercado ───────────────────────────
    home_region_map = {
        'USA': 'NA',
        'JPN': 'JP',
        'FRA': 'PAL', 'DEU': 'PAL', 'GBR': 'PAL', 'SWE': 'PAL',
        'ITA': 'PAL', 'NLD': 'PAL', 'DNK': 'PAL', 'FIN': 'PAL',
        'IRL': 'PAL', 'POL': 'PAL', 'CYP': 'PAL', 'AUS': 'PAL',
        'RUS': 'PAL',
        'KOR': 'Other', 'CHN': 'Other', 'IND': 'Other',
        'ARG': 'Other', 'HKG': 'Other',
    }

    # ── 2. Agrega vendas por país da holding ──────────────────────────────────
    df_cma = (
        df1.groupby('holdings_publisher_country')
        .agg(
            na_sales    = ('na_sales',    'sum'),
            jp_sales    = ('jp_sales',    'sum'),
            pal_sales   = ('pal_sales',   'sum'),
            other_sales = ('other_sales', 'sum'),
            total_sales = ('total_sales', 'sum'),
        )
        .reset_index()
        .round(2)
    )

    # ── 3. Mapeia região doméstica por país ───────────────────────────────────
    df_cma['home_region'] = df_cma['holdings_publisher_country'].map(home_region_map)

    # ── 4. Calcula vendas domésticas e estrangeiras ───────────────────────────
    region_col_map = {
        'NA':    'na_sales',
        'JP':    'jp_sales',
        'PAL':   'pal_sales',
        'Other': 'other_sales',
    }

    df_cma['domestic_sales'] = df_cma.apply(
        lambda row: row[region_col_map.get(row['home_region'], 'other_sales')], axis=1
    )
    df_cma['foreign_sales'] = df_cma['total_sales'] - df_cma['domestic_sales']

    # ── 5. % de vendas estrangeiras (indicador de internacionalização) ─────────
    df_cma['pct_foreign'] = (
        (df_cma['foreign_sales'] / df_cma['total_sales'] * 100).round(1)
    )

    # ── 6. Top 14 por volume total de vendas ──────────────────────────────────
    top20 = (
        df_cma[df_cma['total_sales'] > 0]
        .sort_values('total_sales', ascending=True)   # ascending=True → maior no topo
        .tail(14)
    )

    # ── 7. Gráfico de barras agrupadas ────────────────────────────────────────
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=top20['holdings_publisher_country'],
        x=top20['domestic_sales'],
        orientation='h',
        name='Vendas domésticas',
        marker_color=top20['home_region'].map(colors).fillna('#888888'),  # ← paleta global de regiões
        customdata=top20[['domestic_sales', 'home_region', 'pct_foreign']],
        hovertemplate=(
            '<b>%{y}</b><br>'
            'Região doméstica: %{customdata[1]}<br>'
            'Vendas domésticas: %{customdata[0]:.2f}M<br>'
            'Vendas ext.: %{customdata[2]:.1f}% do total'
            '<extra>Doméstico</extra>'
        ),
    ))

    fig.add_trace(go.Bar(
        y=top20['holdings_publisher_country'],
        x=top20['foreign_sales'],
        orientation='h',
        name='Vendas estrangeiras',
        marker_color='rgba(255,255,255,0.25)',              # ← neutro — contraste com doméstico
        customdata=top20[['foreign_sales', 'pct_foreign']],
        hovertemplate=(
            '<b>%{y}</b><br>'
            'Vendas estrangeiras: %{customdata[0]:.2f}M<br>'
            'Share estrangeiro: %{customdata[1]:.1f}%'
            '<extra>Estrangeiro</extra>'
        ),
    ))

    # ── 8. Layout ─────────────────────────────────────────────────────────────
    fig.update_xaxes(
        type='log',
        title='Vendas (M) — escala logarítmica',
        showgrid=True,
        gridcolor='rgba(0,0,0,0.06)',
    )

    fig.update_layout(
        barmode='group',
        title=dict(
            text='Vendas Domésticas vs. Estrangeiras por País da Holding (Top 14)<br>'
                 '<sup>Cor da barra doméstica = região de origem | Escala log para comparar magnitudes diferentes</sup>',
            font=dict(size=18),
            x=0.01,
        ),
        yaxis=dict(
            title='',
            categoryorder='total ascending',
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.30,
            xanchor='left',
            x=0,
        ),
        height=550,
        margin=dict(t=90, l=10, r=20, b=50),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig

#Função 3 - In House (National Synergy)
def national_synergy(df1):
    """
    Gera um heatmap de vendas totais por País Desenvolvedor x País Publicadora
    e um DataFrame com o ranking dos Top 10 países em sinergia In-House
    (desenvolvedor e publicador do mesmo país).

    Responde às perguntas:
    "Quais países têm maior sinergia entre desenvolvedores e publicadores locais?"
    "Existe dependência de publicadores estrangeiros para distribuir jogos locais?"
    "Quais cruzamentos Dev x Pub geram mais volume de vendas globalmente?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com dataset_clean() aplicado.

    Retorna
    -------
    fig1 : plotly.graph_objects.Figure
        Heatmap com vendas totais por País Dev × Pub (escala logarítmica,
        filtro mínimo de vendas por cruzamento).
    top10 : pd.DataFrame
        Top 10 países com maior sinergia In-House — vendas totais, ticket
        médio, gênero líder e volume de vendas do gênero líder.
    """

    # ── 1. Limpeza do DataFrame ───────────────────────────────────────────────
    df_clean = (
        df1.dropna(subset=['country_publisher', 'country_developer'])
        .copy()
    )
    df_clean = df_clean[~df_clean['country_publisher'].isin(['Unknown', ''])]
    df_clean = df_clean[~df_clean['country_developer'].isin(['Unknown', ''])]

    # Se não há dados suficientes, retorna figura vazia e DataFrame vazio
    if df_clean.empty:
        fig1 = go.Figure()
        fig1.add_annotation(
            text="Dados insuficientes para esta seleção (poucos jogos com país de desenvolvedor/publicador)",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig1.update_layout(height=600)
        return fig1, pd.DataFrame()

    # ── 2. Sinergia In-House para o top10 ─────────────────────────────────────
    inhouse = df_clean[df_clean['country_publisher'] == df_clean['country_developer']].copy()

    if inhouse.empty:
        fig1 = go.Figure()
        fig1.add_annotation(
            text="Nenhuma sinergia In-House encontrada para esta seleção",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig1.update_layout(height=600)
        return fig1, pd.DataFrame()

    # ── 3. Agrega vendas e ticket médio por país (In-House) ───────────────────
    sales_by_country = (
        inhouse.groupby('country_publisher')
        .agg(
            total_sales = ('total_sales', 'sum'),
            num_games   = ('title', 'nunique'),
        )
        .reset_index()
    )
    sales_by_country['ticket_medio'] = (
        sales_by_country['total_sales'] / sales_by_country['num_games']
    ).round(2)

    # ── 4. Gênero líder por país ──────────────────────────────────────────────
    genre_sales = (
        inhouse.groupby(['country_publisher', 'genre'])['total_sales']
        .sum()
        .reset_index()
    )
    idx = genre_sales.groupby('country_publisher')['total_sales'].idxmax()
    top_genres = genre_sales.loc[idx, ['country_publisher', 'genre', 'total_sales']]
    top_genres = top_genres.rename(columns={
        'genre': 'genero_lider',
        'total_sales': 'vendas_genero_lider',
    })

    # ── 5. Monta Top 10 In-House ──────────────────────────────────────────────
    country_stats = sales_by_country.merge(top_genres, on='country_publisher', how='left')
    top10 = (
        country_stats
        .sort_values('total_sales', ascending=False)
        .head(10)
        .reset_index(drop=True)
    )

    # ── 6. Pivot para o heatmap (cruzamento Dev × Pub) ────────────────────────
    pivot = pd.crosstab(
        df_clean['country_developer'],
        df_clean['country_publisher'],
        values=df_clean['total_sales'],
        aggfunc='sum',
        dropna=False,
    ).fillna(0)

    # Filtrar cruzamentos com vendas >= min_vendas
    min_vendas = 10
    mask = pivot >= min_vendas
    pivot_filtrado = pivot.loc[mask.any(axis=1), mask.any(axis=0)]

    # Se após o filtro não houver cruzamentos, retorna figura vazia
    if pivot_filtrado.empty:
        fig1 = go.Figure()
        fig1.add_annotation(
            text="Não há cruzamentos Dev × Pub com vendas significativas para esta seleção",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig1.update_layout(height=600)
        return fig1, top10

    # Remover linhas/colunas com soma zero após filtro
    pivot_filtrado = pivot_filtrado.loc[
        pivot_filtrado.sum(axis=1) > 0,
        pivot_filtrado.sum(axis=0) > 0,
    ]

    if pivot_filtrado.empty:
        fig1 = go.Figure()
        fig1.add_annotation(
            text="Dados insuficientes para gerar o heatmap de sinergia",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig1.update_layout(height=600)
        return fig1, top10

    # Ordenar por volume total
    pivot_ordenado = pivot_filtrado.loc[
        pivot_filtrado.sum(axis=1).sort_values(ascending=False).index,
        pivot_filtrado.sum(axis=0).sort_values(ascending=False).index,
    ]

    # ── 7. Escala logarítmica e cap de cor ────────────────────────────────────
    z_raw = pivot_ordenado.values.copy().astype(float)
    z_log = np.log1p(z_raw)

    # Calcular zmax_cap com proteção contra array vazio
    valores_positivos = z_log[z_log > 0]
    if len(valores_positivos) > 0:
        zmax_cap = float(np.percentile(valores_positivos, 95))
    else:
        # Se não há valores positivos, usa o máximo do array (pode ser zero)
        zmax_cap = float(z_log.max()) if z_log.size > 0 else 1.0

    # ── 8. Hover com valor real ───────────────────────────────────────────────
    hover_text = [[
        f'Dev: {pivot_ordenado.index[i]}<br>'
        f'Pub: {pivot_ordenado.columns[j]}<br>'
        f'Vendas: {z_raw[i, j]:.2f}M'
        for j in range(z_raw.shape[1])]
        for i in range(z_raw.shape[0])
    ]

    # ── 9. Heatmap ────────────────────────────────────────────────────────────
    fig1 = go.Figure(go.Heatmap(
        z=z_log,
        x=pivot_ordenado.columns.tolist(),
        y=pivot_ordenado.index.tolist(),
        text=hover_text,
        hovertemplate='%{text}<extra></extra>',
        colorscale='YlOrRd',
        zmin=0,
        zmax=zmax_cap,
        xgap=2,
        ygap=2,
        colorbar=dict(
            title=dict(text='Vendas (log)', side='right'),
            thickness=12,
            tickvals=[np.log1p(v) for v in [1, 10, 100, 500, 1000, 5000]],
            ticktext=['1M', '10M', '100M', '500M', '1B', '5B'],
        ),
    ))

    fig1.update_layout(
        title=dict(
            text=f'Sinergia Nacional: Vendas Totais por País Dev x Pub (≥ {min_vendas}M)<br>'
                 '<sup>Escala logarítmica | Cor = intensidade do cruzamento Dev x Pub</sup>',
            font=dict(size=18),
            x=0.01,
        ),
        xaxis=dict(title='País da Publicadora', tickangle=45),
        yaxis=dict(title='País do Desenvolvedor'),
        height=600,
        margin=dict(t=80, b=100, l=10, r=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig1, top10

#Função 4 - Cross Market Appeal
def cross_market_appeal_heatmap(df1):
    """
    Heatmap Cruzado: % de vendas por Holding Publicadora x Região de Destino.

    Normalização por coluna (região soma 100%) — cada célula responde:
    "Dentro das vendas da NA, quanto % veio de jogos publicados pela EA, Nintendo, Sony...?"
    Holdings fora do Top 15 por volume total são agrupadas em 'Outros'.

    Responde às perguntas:
    "Quais holdings dominam cada região de mercado?"
    "Existe alguma holding com presença verdadeiramente global e equilibrada?"
    "Holdings japonesas dominam o mercado japonês? Holdings americanas dominam a NA?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com dataset_clean() aplicado.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Heatmap normalizado por região com % de share e valores absolutos no hover.
    """

    # ── 1. Agrega vendas por holding × região ─────────────────────────────────
    df_region = (
        df1[df1['holdings_publisher'].notna()]
        .pipe(lambda d: d[d['holdings_publisher'].str.strip() != ''])
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

    # Verificação inicial: se não há dados, retorna figura vazia
    if df_region.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Dados insuficientes para esta seleção (sem holdings com vendas ≥ 1M)",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(height=400)
        return fig

    # ── 2. Agrupa holdings menores em "Outros" ────────────────────────────────
    top_n = 15
    top_holdings = df_region.nlargest(top_n, 'total')['holdings_publisher'].tolist()
    df_top = df_region[df_region['holdings_publisher'].isin(top_holdings)].copy()
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

    # ── 3. Normalização por coluna: % dentro de cada região ──────────────────
    regioes = ['na_sales', 'jp_sales', 'pal_sales', 'other_sales']
    df_pct = df_region.copy()

    for col in regioes:
        total_regiao = df_pct[col].sum()
        df_pct[col] = ((df_pct[col] / total_regiao) * 100).round(2) if total_regiao > 0 else 0

    # ── 4. Ordena por relevância total — "Outros" sempre no final ─────────────
    df_pct['rank_total'] = df_pct[regioes].sum(axis=1)
    df_outros_pct = df_pct[df_pct['holdings_publisher'] == 'Outros']
    df_top_pct = df_pct[df_pct['holdings_publisher'] != 'Outros'].sort_values('rank_total', ascending=True)
    df_pct = pd.concat([df_outros_pct, df_top_pct], ignore_index=True).drop(columns='rank_total')

    # ── 5. Pivot para o heatmap ───────────────────────────────────────────────
    REGION_LABELS = {
        'na_sales':    'América do Norte',
        'jp_sales':    'Japão',
        'pal_sales':   'PAL (Europa/Oceania)',
        'other_sales': 'Outros Mercados',
    }

    pivot = df_pct.set_index('holdings_publisher')[regioes].rename(columns=REGION_LABELS)
    df_abs = df_region.set_index('holdings_publisher')[regioes].rename(columns=REGION_LABELS)

    # Verificação se pivot está vazio
    if pivot.empty or pivot.values.size == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="Não foi possível gerar o heatmap (dados insuficientes após agrupamento)",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(height=400)
        return fig

    # ── 6. Texto nas células (só exibe se >= 1%) ──────────────────────────────
    annotations_text = [
        [f'{pivot.loc[h, r]:.1f}%' if pivot.loc[h, r] >= 1 else ''
         for r in pivot.columns]
        for h in pivot.index
    ]

    # ── 7. Hover com percentual + valor absoluto ──────────────────────────────
    hover_text = [
        [
            f'<b>{h} → {r}</b><br>'
            f'Share da região: {pivot.loc[h, r]:.2f}%<br>'
            f'Vendas absolutas: {df_abs.loc[h, r]:.2f}M'
            for r in pivot.columns
        ]
        for h in pivot.index
    ]

    # ── 8. Heatmap (agora pivot não está vazio) ───────────────────────────────
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
                 '<sup>% das vendas de cada região originadas por holding | "Outros" = holdings fora do Top 15</sup>',
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
    Gera um mapa coroplético com a distribuição de desenvolvedores únicos
    pelo mundo, usando escala logarítmica para revelar países menores
    sem deixar USA/JPN dominar toda a paleta de cores.

    Responde às perguntas:
    "Como o desenvolvimento da indústria está geograficamente organizado?"
    "Quais países concentram o maior número de estúdios desenvolvedores?"
    "Existem hubs de desenvolvimento fora dos mercados tradicionais (USA e JPN)?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com dataset_clean() aplicado.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Mapa coroplético com quantidade de desenvolvedores únicos por país
        em escala logarítmica, com títulos desenvolvidos no hover.
    """

    # ── 1. Agrupamento por país — desenvolvedores e títulos únicos ────────────
    count_devs_per_country = (
        df1.dropna(subset=['country_developer'])
        .pipe(lambda d: d[d['country_developer'].str.strip() != ''])
        .groupby('country_developer')
        .agg(
            count_devs    = ('clean_name_developer', 'nunique'),
            unique_titles = ('title',                'nunique'),
        )
        .reset_index()
        .sort_values('count_devs', ascending=False)
    )

    # ── 2. Remove países sem desenvolvedores ──────────────────────────────────
    count_devs_per_country = count_devs_per_country[
        count_devs_per_country['count_devs'] > 0
    ]

    # ── 3. Escala logarítmica — comprime outliers e revela países menores ─────
    count_devs_per_country['count_devs_log'] = np.log1p(
        count_devs_per_country['count_devs']
    )

    # ── 4. Mapa coroplético ───────────────────────────────────────────────────
    fig = px.choropleth(
        count_devs_per_country,
        locations='country_developer',
        color='count_devs_log',
        hover_data={
            'count_devs':     True,
            'unique_titles':  True,
            'count_devs_log': False,
        },
        title='Distribuição de Desenvolvedores Únicos por País',
        color_continuous_scale='RdYlGn',
        labels={
            'country_developer': 'País',
            'count_devs':        'Desenvolvedores Únicos',
            'unique_titles':     'Títulos Desenvolvidos',
        },
    )

    # ── 5. Colorbar com ticks legíveis (valores reais, não log) ───────────────
    fig.update_coloraxes(
        colorbar=dict(
            title='Nº de Devs',
            tickvals=[np.log1p(v) for v in [1, 5, 10, 50, 100, 500]],
            ticktext=['1', '5', '10', '50', '100', '500'],
        )
    )

    # ── 6. Layout do mapa ─────────────────────────────────────────────────────
    fig.update_layout(
        title=dict(
            text='Distribuição de Desenvolvedores Únicos por País<br>'
                 '<sup>Escala logarítmica | Cor verde = maior concentração de estúdios</sup>',
            font=dict(size=18),
            x=0.01,
        ),
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular',
            bgcolor='rgba(0,0,0,0)',
            showocean=False,
            showlakes=False,
        ),
        margin=dict(r=0, t=60, l=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig

#Função 6 - Holding Quality Devs
def quality_holdings_devs(df1):
    """
    Gera um gráfico de barras horizontal com a média do critic_score por holding
    desenvolvedora e uma linha de referência da média global.

    A análise considera apenas holdings com pelo menos 20 títulos distintos
    avaliados, garantindo estabilidade estatística. A cor de cada barra reflete
    a nota média, utilizando uma escala de vermelho (notas mais baixas) a verde
    (notas mais altas).

    Responde à pergunta:
    "Como é a qualidade média entregue por cada Holding no desenvolvimento?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame limpo, contendo as colunas 'critic_score', 'holdings_developer' e 'title'.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Gráfico de barras horizontal com a média do critic_score por holding
        desenvolvedora e linha de referência da média global.
    """

# ── 1. Limpeza local (segurança adicional) ─────────────────────
    df_clean = (
        df1.dropna(subset=['critic_score', 'holdings_developer', 'title'])
           .loc[df1['critic_score'] > 0]
           .pipe(lambda d: d[d['holdings_developer'].str.strip() != ''])
           .copy()
    )

    # ── 1.1 Se não há dados com crítica, retorna figura vazia ──────
    if df_clean.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Dados insuficientes para esta seleção (poucos jogos com nota de crítica)",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(height=400)
        return fig

    # ── 2. Agrupamento e métricas ─────────────────────────────────
    quality = (
        df_clean.groupby('holdings_developer', as_index=False)
        .agg(
            avg_critic    = ('critic_score', 'mean'),
            unique_titles = ('title', 'nunique'),
            total_sales = ('total_sales', 'sum')
        )
    )

    # Mantém apenas holdings com amostra significativa
    MIN_TITLES = 20
    quality = quality[quality['unique_titles'] >= MIN_TITLES]

    # ── 2.1 Se nenhuma holding atinge o mínimo de títulos, retorna aviso ──
    if quality.empty:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Nenhuma holding com pelo menos {MIN_TITLES} títulos avaliados nesta seleção",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(height=400)
        return fig

    # ── 3. Ordenação e média global ───────────────────────────────
    quality['avg_critic'] = quality['avg_critic'].round(2)
    quality.sort_values('avg_critic', ascending=True, inplace=True)

    global_avg = round(df_clean['critic_score'].mean(), 2)

    # ── 4. Construção do gráfico ──────────────────────────────────
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=quality['avg_critic'],
        y=quality['holdings_developer'],
        orientation='h',
        marker=dict(
            color=quality['avg_critic'],
            colorscale='RdYlGn',
            cmin=quality['avg_critic'].min(),
            cmax=quality['avg_critic'].max(),
            showscale=False,
        ),
        cliponaxis=False,
        text=quality.apply(lambda r: f"{r['avg_critic']:.2f} ({r['total_sales']:.0f}M)", axis=1),
        textposition='outside',
        customdata=quality[['unique_titles']],
        hovertemplate=(
            '<b>%{y}</b><br>'
            'Média critic score: %{x:.2f}<br>'
            'Títulos avaliados: %{customdata[0]}'
            '<extra></extra>'
        ),
    ))

    # ── Linha da média global ─────────────────────────────────────
    fig.add_vline(
        x=global_avg,
        line=dict(color='gray', width=2, dash='dash'),
        annotation_text=f'Média global: {global_avg}',
        annotation_font=dict(size=12, color='gray'),
        annotation_xanchor='left',
        annotation_yanchor='top',
    )

    # ── 5. Layout final ───────────────────────────────────────────
    # Usa min/max somente se houver dados (garantido pelo if quality.empty anterior)
    x_min = quality['avg_critic'].min()
    x_max = quality['avg_critic'].max()
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
            range=[x_min * 0.97, x_max * 1.03],
        ),
        yaxis=dict(title=''),
        height=max(400, len(quality) * 32),
        margin=dict(t=50, l=180, r=80, b=40),
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
st.markdown("""- Métricas relacionadas ao comportamento da industria no desenvolvimento e publicação de jogos de forma temporal """)

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
        st.markdown("### Organização da Industria - Hub de Desenvolvimento")
        st.plotly_chart(fig_hub_industry, width='stretch')
    
    st.divider()
    
    with st.container():
        st.markdown("### Qualidade das Holdings pelas suas Desenvolvedoras")
        st.plotly_chart(fig_quality_hold_devs, width='stretch')