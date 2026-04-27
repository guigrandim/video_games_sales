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

st.set_page_config(page_title = 'Market Cycles', page_icon = '⏳', layout = 'wide')

#===================================
# Functions
#===================================

#Função 1 - Ciclo de Vendas e Lançamentos Geracional
def games_per_year(df1):
    """
    Gera dois gráficos de barras com o ciclo de vendas e lançamentos por ano,
    coloridos por geração de console para evidenciar padrões geracionais.

    Responde às perguntas:
    "Como evoluíram as vendas e os lançamentos ao longo dos anos?"
    "Quais gerações de console impulsionaram os picos de vendas?"
    "Existe correlação entre volume de lançamentos e volume de vendas?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com dataset_clean() aplicado.

    Retorna
    -------
    fig1 : plotly.graph_objects.Figure
        Gráfico de barras de vendas por ano, colorido por geração.
    fig2 : plotly.graph_objects.Figure
        Gráfico de barras de lançamentos únicos por ano, colorido por geração.
    """

    # ── 1. Limpeza e extração do ano de lançamento ────────────────────────────
    clean_dataset = (
        df1[(df1['generation'] != 'OtherUnknown') & (df1['total_sales'] > 0)]
        .dropna(subset=['release_date'])
        .copy()
    )
    clean_dataset['release_year'] = pd.to_datetime(
        clean_dataset['release_date'], errors='coerce'
    ).dt.year

    # ── 2. Geração dominante por ano (para colorir as barras) ─────────────────
    gen_per_year = (
        clean_dataset.groupby(['release_year', 'generation'])['total_sales']
        .sum()
        .reset_index()
    )
    dominant_gen = (
        gen_per_year.loc[gen_per_year.groupby('release_year')['total_sales'].idxmax()]
        [['release_year', 'generation']]
    )

    # ── 3. Vendas por ano ─────────────────────────────────────────────────────
    sales_by_year = (
        clean_dataset.groupby('release_year')['total_sales']
        .sum()
        .reset_index()
    )
    sales_by_year.columns = ['release_year', 'total_sales']
    sales_by_year = sales_by_year.merge(dominant_gen, on='release_year', how='left')
    sales_by_year = sales_by_year[sales_by_year['total_sales'] > 33]

    # ── 4. Lançamentos únicos por ano ─────────────────────────────────────────
    release_by_year = (
        clean_dataset.groupby('release_year')['title']
        .nunique()
        .reset_index()
    )
    release_by_year.columns = ['release_year', 'unique_titles']
    release_by_year = release_by_year.merge(dominant_gen, on='release_year', how='left')
    release_by_year = release_by_year[release_by_year['unique_titles'] > 50]

    # ── 5. Paleta por geração ─────────────────────────────────────────────────
    GEN_COLORS = {
        '2nd Gen': '#8B008B',
        '3rd Gen': '#E63946',
        '4th Gen': '#FF9800',
        '5th Gen': '#FFEB3B',
        '6th Gen': '#4CAF50',
        '7th Gen': '#2196F3',
        '8th Gen': '#00BCD4',
        '9th Gen': '#9C27B0',
    }

    # ── 6. Fig1 — Vendas por ano ───────────────────────────────────────────────
    fig1 = go.Figure()

    for gen in sales_by_year['generation'].dropna().unique():
        df_gen = sales_by_year[sales_by_year['generation'] == gen]
        fig1.add_trace(go.Bar(
            x=df_gen['release_year'],
            y=df_gen['total_sales'],
            name=gen,
            marker_color=GEN_COLORS.get(gen, '#888888'),
            hovertemplate=(
                '<b>%{x}</b><br>'
                f'Geração: {gen}<br>'
                'Vendas: %{y:.2f}M'
                '<extra></extra>'
            ),
        ))

    fig1.update_layout(
        title=dict(text='Vendas por Ano — por Geração de Console (M)', font=dict(size=18), x=0.01),
        xaxis=dict(title='Ano', dtick=2),
        yaxis=dict(title='Vendas (M)', showgrid=True, gridcolor='rgba(0,0,0,0.06)'),
        barmode='stack',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0),
        height=450,
        margin=dict(t=80, l=10, r=20, b=50),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    # ── 7. Fig2 — Lançamentos únicos por ano ───────────────────────────────────
    fig2 = go.Figure()

    for gen in release_by_year['generation'].dropna().unique():
        df_gen = release_by_year[release_by_year['generation'] == gen]
        fig2.add_trace(go.Bar(
            x=df_gen['release_year'],
            y=df_gen['unique_titles'],
            name=gen,
            marker_color=GEN_COLORS.get(gen, '#888888'),
            showlegend=False,                            # legenda já aparece no fig1
            hovertemplate=(
                '<b>%{x}</b><br>'
                f'Geração: {gen}<br>'
                'Títulos únicos: %{y}'
                '<extra></extra>'
            ),
        ))

    fig2.update_layout(
        title=dict(text='Lançamentos Únicos por Ano — por Geração de Console', font=dict(size=18), x=0.01),
        xaxis=dict(title='Ano', dtick=2),
        yaxis=dict(title='Títulos Únicos', showgrid=True, gridcolor='rgba(0,0,0,0.06)'),
        barmode='stack',
        height=450,
        margin=dict(t=60, l=10, r=20, b=50),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig1, fig2

#Função 2 - Qualidade dos Jogos ao Longo dos Anos
def quality_score(df1):
    """
    Gera um gráfico de linha com a evolução da média do critic_score ao longo
    dos anos, com intervalo de confiança de 95% e faixas de geração de console.

    Responde às perguntas:
    "A qualidade dos jogos melhorou ou piorou ao longo dos anos?"
    "Quais períodos apresentaram maior consistência nas avaliações?"
    "Existe correlação entre geração de console e qualidade média dos jogos?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com dataset_clean() aplicado.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Gráfico de linha com média do critic_score, intervalo de confiança 95%
        e faixas coloridas por geração de console.
    """

    # ── 1. Limpeza e extração do ano ──────────────────────────────────────────
    clean_df = df1.dropna(subset=['critic_score', 'release_date']).copy()
    if clean_df.empty:
        return _empty_fig("Dados insuficientes (poucos jogos com nota)")

    clean_df['release_year'] = pd.to_datetime(clean_df['release_date'], errors='coerce').dt.year

    # ── 2. Agregação por ano (média, desvio, contagem) ────────────────────────
    yearly = (clean_df.groupby('release_year')['critic_score']
              .agg(mean='mean', std='std', count='count')
              .reset_index())
    yearly = yearly[yearly['count'] >= 15]          # mínimo de 15 jogos por ano

    if yearly.empty:
        return _empty_fig("Não há anos com pelo menos 15 jogos avaliados")

    # ── 3. Intervalo de confiança 95% ─────────────────────────────────────────
    z = 1.96
    yearly['ci'] = z * yearly['std'] / yearly['count'] ** 0.5
    yearly['upper'] = (yearly['mean'] + yearly['ci']).round(2)
    yearly['lower'] = (yearly['mean'] - yearly['ci']).round(2)
    yearly['mean'] = yearly['mean'].round(2)

    # ── 4. Geração: anos de início fixos (base histórica) ────────────────────
    GEN_ORDER = ['2nd Gen', '3rd Gen', '4th Gen', '5th Gen', '6th Gen', '7th Gen', '8th Gen', '9th Gen']
    GEN_START = {
        '2nd Gen': 1976, '3rd Gen': 1983, '4th Gen': 1988, '5th Gen': 1993,
        '6th Gen': 1998, '7th Gen': 2005, '8th Gen': 2012, '9th Gen': 2020
    }
    GEN_COLORS = {
        '2nd Gen': 'rgba(139,   0, 139, 0.15)',
        '3rd Gen': 'rgba(230,  57,  70, 0.15)',
        '4th Gen': 'rgba(255, 152,   0, 0.15)',
        '5th Gen': 'rgba(255, 235,  59, 0.15)',
        '6th Gen': 'rgba( 76, 175,  80, 0.15)',
        '7th Gen': 'rgba( 33, 150, 243, 0.15)',
        '8th Gen': 'rgba(  0, 188, 212, 0.15)',
        '9th Gen': 'rgba(156,  39, 176, 0.15)',
    }

    # ── 5. Filtrar gerações que efetivamente possuem dados ────────────────────
    min_year, max_year = yearly['release_year'].min(), yearly['release_year'].max()
    valid_gen = []
    for i, gen in enumerate(GEN_ORDER):
        start = GEN_START[gen]
        end = GEN_START[GEN_ORDER[i+1]] if i+1 < len(GEN_ORDER) else max_year + 1
        if any((yearly['release_year'] >= start) & (yearly['release_year'] < end)):
            valid_gen.append((gen, max(start, min_year)))

    if not valid_gen:
        return _empty_fig("Nenhuma geração com dados suficientes")

    # ── 6. Construção da figura ──────────────────────────────────────────────
    fig = go.Figure()

    # Faixas de fundo e anotações das gerações (apenas as válidas)
    for i, (gen, x0) in enumerate(valid_gen):
        x1 = valid_gen[i+1][1] if i+1 < len(valid_gen) else max_year
        if x1 > x0:
            fig.add_vrect(
                x0=x0, x1=x1,
                fillcolor=GEN_COLORS[gen],
                line_width=1,
                line_color='rgba(255,255,255,0.2)',
            )
        # Anotação centralizada
        x_center = (x0 + x1) / 2 if i+1 < len(valid_gen) else x0
        fig.add_annotation(
            x=x_center, y=1.02, xref='x', yref='paper',
            text=gen, showarrow=False,
            font=dict(size=10, color='white', weight='bold'),
            bgcolor='rgba(0,0,0,0.6)', borderpad=2, borderwidth=1,
        )

    # Faixa do intervalo de confiança
    fig.add_trace(go.Scatter(
        x=pd.concat([yearly['release_year'], yearly['release_year'][::-1]]),
        y=pd.concat([yearly['upper'], yearly['lower'][::-1]]),
        fill='toself', fillcolor='rgba(99, 179, 237, 0.15)',
        line=dict(color='rgba(255,255,255,0)'), name='IC 95%', hoverinfo='skip'
    ))

    # Linha da média anual
    fig.add_trace(go.Scatter(
        x=yearly['release_year'], y=yearly['mean'],
        mode='lines+markers', line=dict(color='#63B3ED', width=2.5),
        marker=dict(size=5, color='#63B3ED', line=dict(width=1, color='white')),
        name='Média Critic Score',
        customdata=yearly[['upper', 'lower', 'count']],
        hovertemplate=(
            '<b>%{x}</b><br>'
            'Média: %{y:.2f}<br>'
            'IC 95%: [%{customdata[1]:.2f} — %{customdata[0]:.2f}]<br>'
            'Jogos avaliados: %{customdata[2]}'
            '<extra></extra>'
        )
    ))

    # Linha de média global
    global_avg = round(clean_df['critic_score'].mean(), 2)
    fig.add_hline(
        y=global_avg, line=dict(color='white', width=1, dash='dash'),
        annotation_text=f'Média global: {global_avg}',
        annotation_font=dict(size=10, color='white'), annotation_xanchor='right'
    )

    # Layout final
    fig.update_layout(
        title=dict(
            text='Evolução do Critic Score ao Longo do Tempo<br>'
                 '<sup>Linha = média anual | Faixa = IC 95% | Fundo = geração</sup>',
            font=dict(size=18), x=0.01
        ),
        xaxis=dict(title='Ano', dtick=2, showgrid=False, range=[min_year-1, max_year+1]),
        yaxis=dict(title='Critic Score Médio', showgrid=True, gridcolor='rgba(0,0,0,0.06)'),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='left'),
        height=480, margin=dict(t=90, l=10, r=20, b=50),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

#Função 3 - Market Share por Fabricante
def market_share_per_manufacture(df1):
    """
    Gera um gráfico de barras empilhadas com o market share por fabricante
    em cada geração de console (Top 10 fabricantes por volume total de vendas).

    Responde às perguntas:
    "Como evoluiu o domínio de cada fabricante ao longo das gerações?"
    "Quais fabricantes surgiram, cresceram ou desapareceram entre gerações?"
    "Existe concentração de mercado em alguma geração específica?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com dataset_clean() aplicado.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Gráfico de barras empilhadas 100% com market share por fabricante
        e geração, colorido pela paleta de fabricantes.
    """

    # ── 1. Limpeza ────────────────────────────────────────────────────────────
    df_clean = (
        df1[['total_sales', 'manufacture', 'generation']]
        .loc[lambda d: (d['total_sales'] > 0) & (d['generation'] != 'OtherUnknown')]
        .copy()
    )

    # ── 2. Top 10 fabricantes por volume total ────────────────────────────────
    top10_manufactures = (
        df_clean.groupby('manufacture')['total_sales']
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .index.tolist()
    )

    df_clean = df_clean[df_clean['manufacture'].isin(top10_manufactures)]

    # ── 3. Vendas e market share por geração × fabricante ────────────────────
    sales_per_gen_manufacture = (
        df_clean.groupby(['generation', 'manufacture'])['total_sales']
        .sum()
        .reset_index()
    )

    sales_per_gen_manufacture['market_share'] = (
        sales_per_gen_manufacture.groupby('generation')['total_sales']
        .transform(lambda x: (x / x.sum() * 100).round(2))
    )

    # ── 4. Ordem cronológica das gerações ─────────────────────────────────────
    ordem_geracao = ['2nd Gen','3rd Gen','4th Gen','5th Gen','6th Gen','7th Gen','8th Gen','9th Gen']

    sales_per_gen_manufacture['generation'] = pd.Categorical(
        sales_per_gen_manufacture['generation'],
        categories=ordem_geracao,
        ordered=True,
    )
    sales_per_gen_manufacture = sales_per_gen_manufacture.sort_values('generation')

    # ── 5. Paleta por fabricante ──────────────────────────────────────────────
    MANUFACTURE_COLORS = {
        'Nintendo':  '#E4000F',
        'Sony':      '#003087',
        'Microsoft': '#107C10',
        'Sega':      '#1B4EBF',
        'Atari':     '#FF6600',
        'NEC':       '#6B6B6B',
        'SNK':       '#C8A000',
        '3DO':       '#8B008B',
        'Mattel':    '#FF1493',
    }

    # ── 6. Gráfico de barras empilhadas ───────────────────────────────────────
    fig = go.Figure()

    for manuf in top10_manufactures:
        df_manuf = sales_per_gen_manufacture[sales_per_gen_manufacture['manufacture'] == manuf]

        fig.add_trace(go.Bar(
            x=df_manuf['generation'],
            y=df_manuf['market_share'],
            name=manuf,
            marker_color=MANUFACTURE_COLORS.get(manuf, '#888888'),
            customdata=df_manuf[['total_sales']],
            hovertemplate=(
                f'<b>{manuf}</b><br>'
                'Geração: %{x}<br>'
                'Market share: %{y:.2f}%<br>'
                'Vendas absolutas: %{customdata[0]:.2f}M'
                '<extra></extra>'
            ),
        ))

    fig.update_layout(
        barmode='stack',
        title=dict(
            text='Market Share por Fabricante em cada Geração<br>'
                 '<sup>Top 10 fabricantes por volume total de vendas</sup>',
            font=dict(size=18),
            x=0.01,
        ),
        xaxis=dict(
            title='Geração',
            categoryorder='array',
            categoryarray=ordem_geracao,
        ),
        yaxis=dict(
            title='Market Share (%)',
            range=[0, 100],
            ticksuffix='%',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.06)',
        ),
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.25,
            xanchor='left',
            x=0,
        ),
        height=500,
        margin=dict(t=80, l=10, r=20, b=50),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig

#Função 4 - Pico de Vendas por Geração
def timeline_peak_generation(df1):
    """
    Gera um gráfico de Gantt horizontal com o ciclo de vida de cada geração
    de console e o marcador do ano de pico de vendas.

    Responde às perguntas:
    "Qual foi o período de vida de cada geração de console?"
    "Em que ano cada geração atingiu seu pico de vendas?"
    "Houve sobreposição entre gerações? Qual geração teve o maior pico absoluto?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com dataset_clean() aplicado.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Gráfico de Gantt com ciclo de vida por geração e marcador de pico de vendas.
    """

    # ── 1. Limpeza e extração do ano ──────────────────────────────────────────
    df_clean = df1[df1['generation'] != 'OtherUnknown'].copy()
    df_clean['release_date'] = pd.to_datetime(df_clean['release_date'], errors='coerce')
    df_clean['release_year'] = df_clean['release_date'].dt.year

    # ── 2. Ano de pico de vendas por geração ──────────────────────────────────
    peak_per_year = (
        df_clean.groupby(['generation', 'release_year'])['total_sales']
        .sum()
        .reset_index()
    )

    peak_df = (
        peak_per_year.loc[peak_per_year.groupby('generation')['total_sales'].idxmax()]
        .reset_index(drop=True)
    )

    # ── 3. Ciclo de vida (start e end year) por geração ───────────────────────
    lifecycle = (
        df_clean.groupby('generation')
        .agg(
            start_year = ('start_year', 'min'),
            end_year   = ('end_year',   'max'),
        )
        .reset_index()
    )

    dataset = lifecycle.merge(peak_df, on='generation')

    # ── 4. Ordem cronológica das gerações ─────────────────────────────────────
    ordem_geracao = ['2nd Gen','3rd Gen','4th Gen','5th Gen','6th Gen','7th Gen','8th Gen','9th Gen']

    dataset['generation'] = pd.Categorical(
        dataset['generation'], categories=ordem_geracao, ordered=True
    )
    dataset = dataset.sort_values('generation').reset_index(drop=True)

    # ── 5. Paleta por geração ─────────────────────────────────────────────────
    GEN_COLORS = {
        '2nd Gen': '#8B008B',
        '3rd Gen': '#E63946',
        '4th Gen': '#FF9800',
        '5th Gen': '#FFEB3B',
        '6th Gen': '#4CAF50',
        '7th Gen': '#2196F3',
        '8th Gen': '#00BCD4',
        '9th Gen': '#9C27B0',
    }

    # ── 6. Figura ─────────────────────────────────────────────────────────────
    fig = go.Figure()

    # Barras do ciclo de vida coloridas por geração
    for _, row in dataset.iterrows():
        gen      = row['generation']
        duration = int(row['end_year'] - row['start_year'])
        color    = GEN_COLORS.get(gen, '#888888')

        fig.add_trace(go.Bar(
            x=[duration],
            y=[gen],
            base=row['start_year'],
            orientation='h',
            showlegend=False,
            marker=dict(
                color=color,
                opacity=0.75,
                line=dict(color='white', width=1),
            ),
            hovertemplate=(
                f'<b>{gen}</b><br>'
                f'Início: {int(row["start_year"])}<br>'
                f'Fim: {int(row["end_year"])}<br>'
                f'Duração: {duration} anos<br>'
                f'Pico de vendas: {row["total_sales"]:.1f}M em {int(row["release_year"])}'
                '<extra></extra>'
            ),
        ))

    # Marcadores de pico coloridos por geração
    fig.add_trace(go.Scatter(
        x=dataset['release_year'],
        y=dataset['generation'],
        mode='markers+text',
        marker=dict(
            color=[GEN_COLORS.get(g, '#888888') for g in dataset['generation']],
            size=14,
            symbol='diamond',
            line=dict(color='white', width=1.5),
        ),
        text=dataset['release_year'].astype(int).astype(str) + '<br>' +
             dataset['total_sales'].apply(lambda x: f'{x:.0f}M'),
        textposition='top center',
        textfont=dict(size=10, color='white'),
        name='Ano de Pico de Vendas',
        hovertemplate=(
            '<b>%{y}</b><br>'
            'Ano de pico: %{x}<br>'
            'Vendas no pico: %{customdata:.1f}M'
            '<extra></extra>'
        ),
        customdata=dataset['total_sales'],
    ))

    fig.update_layout(
        title=dict(
            text='Ciclo de Vida e Pico de Vendas por Geração de Console<br>'
                 '<sup>Barras = período de vida | ◆ = ano de pico de vendas</sup>',
            font=dict(size=18),
            x=0.01,
        ),
        xaxis=dict(
            title='Ano',
            range=[1975, 2027],
            dtick=5,
            tickangle=45,
            showgrid=True,
            gridcolor='rgba(0,0,0,0.06)',
        ),
        yaxis=dict(
            title='Geração',
            categoryorder='array',
            categoryarray=ordem_geracao,
        ),
        barmode='overlay',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.25,
            xanchor='left',
            x=0,
        ),
        height=500,
        margin=dict(t=80, l=10, r=20, b=60),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig

#Função 5 - Coexistencia de Geração - Vendas por Geração
def timeline_coexistencia_geracao(df1):
    """
    Gera um gráfico de linhas com o volume de vendas por geração ao longo
    dos anos, destacando os períodos de coexistência entre gerações consecutivas.
    Retorna também um gráfico de barras empilhadas com o share percentual de
    vendas por geração durante cada período de coexistência, e um DataFrame
    com os dados de transição para análise estratégica de lançamentos.

    Responde às perguntas:
    "Por quanto tempo duas gerações coexistiram no mercado?"
    "Como as transições entre gerações impactaram o volume de vendas?"
    "Qual geração manteve relevância comercial por mais tempo após o lançamento da próxima?"
    "Em qual momento é mais vantajoso começar a lançar títulos para a próxima geração?"
    "Quando a nova geração ultrapassa 50% do share de vendas (ponto de cruzamento)?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com dataset_clean() aplicado.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Gráfico de linhas por geração com áreas de coexistência destacadas.

    fig_share : plotly.graph_objects.Figure
        Gráfico de barras empilhadas mostrando o share percentual de vendas
        entre a geração atual e a próxima em cada ano de coexistência.
        Inclui linha de referência em 50% (ponto de cruzamento).

    df_resumo : pd.DataFrame
        DataFrame com uma Uma linha por transição entre gerações consecutivas
    """

        # ── 1. Limpeza e extração do ano ──────────────────────────────────────────
    df_clean = df1[df1['generation'] != 'OtherUnknown'].copy()
    df_clean['release_date'] = pd.to_datetime(df_clean['release_date'], errors='coerce')
    df_clean['release_year'] = df_clean['release_date'].dt.year

    # ── 2. Ordem cronológica das gerações ─────────────────────────────────────
    ordem_geracao = ['2nd Gen','3rd Gen','4th Gen','5th Gen','6th Gen','7th Gen','8th Gen','9th Gen']

    # ── 3. Paleta por geração ─────────────────────────────────────────────────
    GEN_COLORS = {
        '2nd Gen': '#8B008B',
        '3rd Gen': '#E63946',
        '4th Gen': '#FF9800',
        '5th Gen': '#FFEB3B',
        '6th Gen': '#4CAF50',
        '7th Gen': '#2196F3',
        '8th Gen': '#00BCD4',
        '9th Gen': '#9C27B0',
    }

    # ── 4. Vendas por geração e ano ───────────────────────────────────────────
    vendas_ano = (
        df_clean[df_clean['total_sales'] > 0]
        .groupby(['generation', 'release_year'])['total_sales']
        .sum()
        .reset_index()
    )

    # ── 5. Ciclo de vida por geração ──────────────────────────────────────────
    lifecycle = (
        df_clean.groupby('generation')
        .agg(
            start_year = ('start_year', 'min'),
            end_year   = ('end_year',   'max'),
        )
        .reset_index()
    )

    lifecycle['generation'] = pd.Categorical(
        lifecycle['generation'], categories=ordem_geracao, ordered=True
    )
    lifecycle = lifecycle.sort_values('generation').reset_index(drop=True)

    # ── 6. Figura principal ───────────────────────────────────────────────────
    fig = go.Figure()

    # ── 7. Áreas de coexistência entre gerações consecutivas ──────────────────
    for i in range(len(lifecycle) - 1):
        gen_atual   = lifecycle.iloc[i]
        gen_proxima = lifecycle.iloc[i + 1]
        overlap_start = gen_proxima['start_year']
        overlap_end   = gen_atual['end_year']

        if overlap_start < overlap_end:
            fig.add_vrect(
                x0=overlap_start,
                x1=overlap_end,
                fillcolor='rgba(252, 129, 129, 0.10)',
                line_width=0,
            )
            for x_pos in [overlap_start, overlap_end]:
                fig.add_vline(
                    x=x_pos,
                    line=dict(color='rgba(252,129,129,0.4)', width=1, dash='dot'),
                )
            fig.add_annotation(
                x=(overlap_start + overlap_end) / 2,
                y=1,
                yref='paper',
                text=(
                    f'↕ {gen_atual["generation"]}<br>'
                    f'→ {gen_proxima["generation"]}<br>'
                    f'{int(overlap_end - overlap_start)}a'
                ),
                showarrow=False,
                font=dict(size=8, color='#FC8181'),
                bgcolor='rgba(0,0,0,0.4)',
                borderpad=3,
                yanchor='top',
            )

    # ── 8. Linhas de vendas por geração ───────────────────────────────────────
    for gen in ordem_geracao:
        df_gen = vendas_ano[vendas_ano['generation'] == gen]
        if df_gen.empty:
            continue

        color = GEN_COLORS.get(gen, '#888888')

        fig.add_trace(go.Scatter(
            x=df_gen['release_year'],
            y=df_gen['total_sales'],
            name=gen,
            mode='lines+markers',
            line=dict(color=color, width=2.5),
            marker=dict(size=5, color=color, line=dict(width=1, color='white')),
            hovertemplate=(
                f'<b>{gen}</b><br>'
                'Ano: %{x}<br>'
                'Vendas: %{y:.1f}M'
                '<extra></extra>'
            ),
        ))

    fig.update_layout(
        title=dict(
            text='Coexistência de Gerações — Impacto das Transições no Volume de Vendas<br>'
                 '<sup>Faixas rosas = períodos de coexistência entre gerações consecutivas</sup>',
            font=dict(size=18),
            x=0.01,
        ),
        xaxis=dict(
            title='Ano',
            dtick=5,
            tickangle=45,
            showgrid=True,
            gridcolor='rgba(0,0,0,0.06)',
        ),
        yaxis=dict(
            title='Total de Vendas (M)',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.06)',
        ),
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.30,
            xanchor='left',
            x=0,
        ),
        height=500,
        margin=dict(t=90, l=10, r=20, b=60),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    # ── 9. Dados de share % por coexistência (uso interno) ────────────────────
    def _recomendacao(share2y, crossover):
        if share2y >= 38 and crossover <= 2: return 'Entrar já'
        if share2y >= 25:                    return 'Janela ótima'
        if share2y >= 15:                    return 'Observar'
        return 'Aguardar'

    registros_share = []

    for i in range(len(lifecycle) - 1):
        gen_atual   = lifecycle.iloc[i]
        gen_proxima = lifecycle.iloc[i + 1]

        overlap_start = int(gen_proxima['start_year'])
        overlap_end   = int(gen_atual['end_year'])

        if overlap_start >= overlap_end:
            continue

        vendas_old_serie = vendas_ano[vendas_ano['generation'] == gen_atual['generation']]
        vendas_new_serie = vendas_ano[vendas_ano['generation'] == gen_proxima['generation']]

        for ano in range(overlap_start, overlap_end + 1):
            v_old = vendas_old_serie.loc[vendas_old_serie['release_year'] == ano, 'total_sales'].sum()
            v_new = vendas_new_serie.loc[vendas_new_serie['release_year'] == ano, 'total_sales'].sum()
            total = v_old + v_new

            registros_share.append({
                'transition'    : f"{gen_atual['generation']} → {gen_proxima['generation']}",
                'old_gen'       : gen_atual['generation'],
                'new_gen'       : gen_proxima['generation'],
                'year'          : ano,
                'years_elapsed' : ano - overlap_start + 1,
                'old_share_pct' : round(v_old / total * 100, 1) if total > 0 else None,
                'new_share_pct' : round(v_new / total * 100, 1) if total > 0 else None,
            })

    df_interno = pd.DataFrame(registros_share)

    # Ponto de cruzamento por transição
    crossovers = (
        df_interno[df_interno['new_share_pct'] > 50]
        .groupby('transition')['years_elapsed']
        .min()
        .reset_index()
        .rename(columns={'years_elapsed': 'crossover_year_elapsed'})
    )
    df_interno = df_interno.merge(crossovers, on='transition', how='left')
    df_interno = df_interno[df_interno['year'] <= 2018]

    # ── 10. Gráfico de barras empilhadas de share % ───────────────────────────
    fig2 = go.Figure()
    gens_na_legenda = set()

    for transition in df_interno['transition'].unique():
        df_t    = df_interno[df_interno['transition'] == transition]
        old_gen = df_t['old_gen'].iloc[0]
        new_gen = df_t['new_gen'].iloc[0]

        # rótulo único: ano + sigla da transição
        short = transition.replace(' Gen', '').replace(' → ', '→')
        x_labels = df_t['year'].astype(str) + f'<br><sup>{short}</sup>'

        fig2.add_trace(go.Bar(
            x=x_labels,
            y=df_t['old_share_pct'],
            name=old_gen,
            marker_color=GEN_COLORS.get(old_gen, '#888'),
            legendgroup=old_gen,
            showlegend=old_gen not in gens_na_legenda,
            hovertemplate='Ano: %{x}<br>' + old_gen + ': %{y:.1f}%<extra></extra>',
        ))
        gens_na_legenda.add(old_gen)

        fig2.add_trace(go.Bar(
            x=x_labels,
            y=df_t['new_share_pct'],
            name=new_gen,
            marker_color=GEN_COLORS.get(new_gen, '#aaa'),
            legendgroup=new_gen,
            showlegend=new_gen not in gens_na_legenda,
            hovertemplate='Ano: %{x}<br>' + new_gen + ': %{y:.1f}%<extra></extra>',
        ))
        gens_na_legenda.add(new_gen)

    fig2.add_hline(
        y=50,
        line=dict(color='rgba(252,129,129,0.7)', width=1.5, dash='dot'),
        annotation_text='50%',
        annotation_position='top right',
        annotation_font=dict(size=10, color='#FC8181'),
    )

    fig2.update_layout(
        title=dict(
            text='Share de Vendas — Períodos de Coexistência',
            font=dict(size=16),
            x=0.01,
        ),
        barmode='stack',
        xaxis=dict(
            title='Ano (por transição)',
            tickangle=45,
            showgrid=False,
            type='category',
        ),
        yaxis=dict(
            title='Share (%)',
            range=[0, 100],
            ticksuffix='%',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.06)',
        ),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=-0.40, xanchor='left', x=0),
        height=420,
        margin=dict(t=60, l=10, r=20, b=80),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    # ── 11. DataFrame resumido para exibição estratégica ─────────────────────
    resumo = []
    for t in df_interno['transition'].unique():
        df_t      = df_interno[df_interno['transition'] == t]
        start     = int(df_t['year'].min())
        end       = int(df_t['year'].max())
        duracao   = end - start + 1
        crossover = df_t['crossover_year_elapsed'].iloc[0]
        cross_ano = int(start + crossover - 1) if pd.notna(crossover) else None

        # share no ano anterior ao cruzamento (janela estratégica real)
        ano_entrada = crossover - 1 if pd.notna(crossover) else None
        share_entrada = df_t[df_t['years_elapsed'] == ano_entrada]['new_share_pct'].values
        share_entrada = float(share_entrada[0]) if len(share_entrada) > 0 else 0.0
        
        # share no 1º ano após lançamento (years_elapsed == 2)
        share_1ano = df_t[df_t['years_elapsed'] == 2]['new_share_pct'].values
        share_1ano = float(share_1ano[0]) if len(share_1ano) > 0 else 0.0

        resumo.append({
            'Transição'                : t,
            'Período coexist.'         : f'{start} – {end}',
            'Duração'                  : f'{duracao} anos',
            'Ponto de cruzamento'      : f'{cross_ano} (ano {int(crossover)})' if cross_ano else '—',
            'Share nova gen. (ano -1)' : f'{share_entrada:.0f}% (ano {int(ano_entrada)})' if ano_entrada else '—',
            'Share nova gen. (1º ano)' : f'{share_1ano:.0f}%',
            'Recomendação'             : _recomendacao(share_entrada, crossover if pd.notna(crossover) else 99),
        })
    
    df_resumo = pd.DataFrame(resumo)

    return fig, fig2, df_resumo

#Função Auxiliar - Retorna Figura Vazia - Erro quando não tenho dados  
def _empty_fig(msg):
    """Retorna figura vazia com mensagem de aviso."""
    fig = go.Figure()
    fig.add_annotation(
        text=msg, xref="paper", yref="paper", x=0.5, y=0.5,
        showarrow=False, font=dict(size=14, color="gray")
    )
    fig.update_layout(height=480)
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
st.title ('⏳ Evolução das Gerações - Ciclos de Mercado')
st.markdown("""- Métricas apresentando o comportamento e a qualidade das vendas das empresas na indústria de forma temporal """)

#Call the Functions
fig_sales_per_year, fig_release_per_year = games_per_year(df1)                                                  # <- Função 1 - Ciclo de Vendas e Lançamentos Geracional
fig_quality_score_history = quality_score(df1)                                                                  # <- Função 2 - Qualidade dos Jogos ao Longo dos Anos
fig_market_share_manf = market_share_per_manufacture(df1)                                                       # <- Função 3 - Market Share por Fabricante
fig_sales_peak_generation = timeline_peak_generation(df1)                                                       # <- Função 4 - Pico de Vendas por Geração
fig_coexist_generation, fig_share_generation, df_share_generation  = timeline_coexistencia_geracao(df1)         # <- Função 5 - Coexistencia de Geração - Vendas por Geração

st.divider()

#Create KPIs In Page
tab1, tab2 = st.tabs(['Comportamento de Vendas - Histórico', 'Comportamento de Lançamentos - Historico'])

with tab1:
    with st.container():
        st.markdown("### Ciclo de Vendas Geracional - Vendas Por Ano")
        st.plotly_chart(fig_sales_per_year, width='stretch')

    st.divider()
 
    with st.container():
        st.markdown("### Dominância de Fabricante - Market Share")
        st.plotly_chart(fig_market_share_manf, width='stretch')
        
    st.divider()
    
    with st.container():
        st.markdown("### Ciclo de Vida e Comportamento Historico de Vendas")
        st.plotly_chart(fig_sales_peak_generation, width='stretch')
    
    st.divider()
    
    with st.container():
        st.markdown("### Coexistencia e Comportamento das Vendas Historico")
        st.plotly_chart(fig_coexist_generation, use_container_width=True)
        st.plotly_chart(fig_share_generation, use_container_width=True)
        st.dataframe(df_share_generation, use_container_width=True, hide_index=True)
    
    st.divider()
    
with tab2:
    with st.container():
        st.markdown("### Ciclo de Lançamentos Geracional - Lançamentos por Ano")
        st.plotly_chart(fig_release_per_year, width='stretch')
    
    with st.container():
        st.markdown("### Qualidade dos Lançamentos ao Longo dos Anos - Comportamento da Critica (1991 - 2020)")
        st.plotly_chart(fig_quality_score_history, width='stretch')