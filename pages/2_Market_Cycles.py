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

    # ── 4. Lançamentos únicos por ano ─────────────────────────────────────────
    release_by_year = (
        clean_dataset.groupby('release_year')['title']
        .nunique()                                       # ← era count (contava duplicatas)
        .reset_index()
    )
    release_by_year.columns = ['release_year', 'unique_titles']
    release_by_year = release_by_year.merge(dominant_gen, on='release_year', how='left')

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
    clean_df = (
        df1.dropna(subset=['critic_score', 'release_date'])
        .copy()
    )
    clean_df['release_year'] = pd.to_datetime(
        clean_df['release_date'], errors='coerce'
    ).dt.year

    # ── 2. Média, desvio e contagem por ano ───────────────────────────────────
    quality_score_per_year = (
        clean_df.groupby('release_year')['critic_score']
        .agg(
            mean_cs  = 'mean',
            std_cs   = 'std',
            count_cs = 'count',
        )
        .reset_index()
    )

    # Filtra anos com amostra mínima para IC confiável
    quality_score_per_year = quality_score_per_year[quality_score_per_year['count_cs'] >= 4]

    # ── 3. Intervalo de confiança 95% ─────────────────────────────────────────
    z = 1.96
    quality_score_per_year['ci']    = z * (quality_score_per_year['std_cs'] / quality_score_per_year['count_cs'] ** 0.5)
    quality_score_per_year['upper'] = (quality_score_per_year['mean_cs'] + quality_score_per_year['ci']).round(2)
    quality_score_per_year['lower'] = (quality_score_per_year['mean_cs'] - quality_score_per_year['ci']).round(2)
    quality_score_per_year['mean_cs'] = quality_score_per_year['mean_cs'].round(2)

    # ── 4. Geração dominante por ano (para faixas de fundo) ───────────────────
    GEN_ORDER = ['2nd Gen','3rd Gen','4th Gen','5th Gen','6th Gen','7th Gen','8th Gen','9th Gen']
    GEN_COLORS = {
        '2nd Gen': 'rgba(139,   0, 139, 0.08)',
        '3rd Gen': 'rgba(230,  57,  70, 0.08)',
        '4th Gen': 'rgba(255, 152,   0, 0.08)',
        '5th Gen': 'rgba(255, 235,  59, 0.08)',
        '6th Gen': 'rgba( 76, 175,  80, 0.08)',
        '7th Gen': 'rgba( 33, 150, 243, 0.08)',
        '8th Gen': 'rgba(  0, 188, 212, 0.08)',
        '9th Gen': 'rgba(156,  39, 176, 0.08)',
    }

    # Ano de início de cada geração
    gen_years = (
        df1[df1['generation'].isin(GEN_ORDER)]
        .groupby('generation')['release_date']
        .min()
        .apply(lambda x: pd.to_datetime(x, errors='coerce').year)
        .reindex(GEN_ORDER)
        .dropna()
        .astype(int)
        .reset_index()
    )
    gen_years.columns = ['generation', 'start_year']

    # ── 5. Figura ─────────────────────────────────────────────────────────────
    fig = go.Figure()

    # Faixas de fundo por geração
    for i, row in gen_years.iterrows():
        gen   = row['generation']
        x0    = row['start_year']
        x1    = gen_years.iloc[i + 1]['start_year'] if i + 1 < len(gen_years) else quality_score_per_year['release_year'].max()
        color = GEN_COLORS.get(gen, 'rgba(128,128,128,0.05)')

        fig.add_vrect(
            x0=x0, x1=x1,
            fillcolor=color,
            line_width=0,
            annotation_text=gen,
            annotation_position='top left',
            annotation_font=dict(size=9, color='rgba(255,255,255,0.5)'),
        )

    # Faixa do intervalo de confiança
    fig.add_trace(go.Scatter(
        x=pd.concat([quality_score_per_year['release_year'], quality_score_per_year['release_year'][::-1]]),
        y=pd.concat([quality_score_per_year['upper'], quality_score_per_year['lower'][::-1]]),
        fill='toself',
        fillcolor='rgba(99, 179, 237, 0.15)',
        line=dict(color='rgba(255,255,255,0)'),
        name='IC 95%',
        hoverinfo='skip',
    ))

    # Linha da média
    fig.add_trace(go.Scatter(
        x=quality_score_per_year['release_year'],
        y=quality_score_per_year['mean_cs'],
        mode='lines+markers',
        line=dict(color='#63B3ED', width=2.5),
        marker=dict(size=5, color='#63B3ED', line=dict(width=1, color='white')),
        name='Média Critic Score',
        customdata=quality_score_per_year[['upper', 'lower', 'count_cs']],
        hovertemplate=(
            '<b>%{x}</b><br>'
            'Média: %{y:.2f}<br>'
            'IC 95%: [%{customdata[1]:.2f} — %{customdata[0]:.2f}]<br>'
            'Jogos avaliados: %{customdata[2]}'
            '<extra></extra>'
        ),
    ))

    # Linha de média global
    global_avg = clean_df['critic_score'].mean().round(2)
    fig.add_hline(
        y=global_avg,
        line=dict(color='rgba(255,255,255,0.3)', width=1, dash='dash'),
        annotation_text=f'Média global: {global_avg}',
        annotation_font=dict(size=10, color='rgba(255,255,255,0.5)'),
        annotation_xanchor='left',
    )

    fig.update_layout(
        title=dict(
            text='Evolução do Critic Score ao Longo do Tempo<br>'
                 '<sup>Linha = média anual | Faixa = intervalo de confiança 95% | Fundo = geração de console</sup>',
            font=dict(size=18),
            x=0.01,
        ),
        xaxis=dict(title='Ano', dtick=2, showgrid=False),
        yaxis=dict(
            title='Critic Score Médio',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.06)',
        ),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0),
        height=480,
        margin=dict(t=90, l=10, r=20, b=50),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
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
            y=1.02,
            xanchor='left',
            x=0,
        ),
        height=500,
        margin=dict(t=80, l=10, r=20, b=50),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig

#Função 4 - Timeline Peak Generation - Pico de Vendas por Geração
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
            y=1.02,
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

    df = df1[df1['generation'] != 'OtherUnknown'].copy()
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df['release_year'] = df['release_date'].dt.year

    ordem_geracao = ['2nd Gen', '3rd Gen', '4th Gen', '5th Gen', '6th Gen', '7th Gen', '8th Gen', '9th Gen']

    # Vendas por geração e ano
    vendas_ano = (
        df[df['total_sales'] > 0]
        .groupby(['generation', 'release_year'])['total_sales']
        .sum()
        .reset_index()
    )

    # Ciclo de vida
    lifecycle = (
        df.groupby('generation')
        .agg(start_year=('start_year', 'min'), end_year=('end_year', 'max'))
        .reset_index()
    )

    fig = go.Figure()

    # Linha de vendas por geração ao longo do tempo
    for gen in ordem_geracao:
        df_gen = vendas_ano[vendas_ano['generation'] == gen]
        if df_gen.empty:
            continue

        fig.add_trace(go.Scatter(
            x=df_gen['release_year'],
            y=df_gen['total_sales'],
            name=gen,
            mode='lines+markers',
            line=dict(width=2),
            hovertemplate=f'<b>{gen}</b><br>Ano: %{{x}}<br>Vendas: %{{y:.1f}}M<extra></extra>'
        ))

    # Área de coexistência entre gerações consecutivas
    lifecycle['generation'] = pd.Categorical(lifecycle['generation'], categories=ordem_geracao, ordered=True)
    lifecycle = lifecycle.sort_values('generation').reset_index(drop=True)

    for i in range(len(lifecycle) - 1):
        gen_atual   = lifecycle.iloc[i]
        gen_proxima = lifecycle.iloc[i + 1]
        overlap_start = gen_proxima['start_year']
        overlap_end   = gen_atual['end_year']

        if overlap_start < overlap_end:
            fig.add_vrect(
                x0=overlap_start,
                x1=overlap_end,
                fillcolor='rgba(252, 129, 129, 0.12)',
                line_width=0,
            )
            for x_pos in [overlap_start, overlap_end]:
                fig.add_vline(
                    x=x_pos,
                    line=dict(color='#FC8181', width=1, dash='dot')
                )
            # Anotação de transição
            fig.add_annotation(
                x=(overlap_start + overlap_end) / 2,
                y=1,
                yref='paper',
                text=f'↕ {gen_atual["generation"]}<br>→ {gen_proxima["generation"]}',
                showarrow=False,
                font=dict(size=8, color='#FC8181'),
                bgcolor='rgba(0,0,0,0.4)',
                borderpad=3,
                yanchor='top'
            )

    fig.update_layout(
        title='Coexistência de Gerações e Impacto da Transição no Volume de Vendas',
        xaxis_title='Ano',
        yaxis_title='Total de Vendas (M)',
        xaxis=dict(dtick=5, tickangle=45),
        hovermode='x unified',
        height=500,
        legend=dict(orientation='h', y=-0.2)
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
st.title ('⏳ Evolução das Gerações - Ciclos de Mercado')

#Call the Functions
fig_sales_per_year, fig_release_per_year = games_per_year(df1)  # <- Função 1 - Ciclo de Vendas e Lançamentos Geracional
fig_quality_score_history = quality_score(df1)                  # <- Função 2 - Qualidade dos Jogos ao Longo dos Anos
market_share_manf = market_share_per_manufacture(df1)           # <- Função 3 - Market Share por Fabricante
sales_peak_generation = timeline_peak_generation(df1)           # <- Função 4 - Pico de Vendas por Geração
coexist_generation = timeline_coexistencia_geracao(df1)         # <- Função 5 - Coexistencia de Geraçã - Vendas por Geração

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
        st.plotly_chart(market_share_manf, width='stretch')
        
    st.divider()
    
    with st.container():
        st.markdown("### Ciclo de Vida e Comportamento Historico de Vendas")
        st.plotly_chart(sales_peak_generation, width='stretch')
    
    with st.container():
        st.plotly_chart(coexist_generation, width='stretch')

with tab2:
    with st.container():
        st.markdown("### Ciclo de Lançamentos Geracional - Lançamentos por Ano")
        st.plotly_chart(fig_release_per_year, width='stretch')
    
    with st.container():
        st.markdown("### Qualidade dos Lançamentos ao Longo dos Anos - Comportamento da Critica (1991 - 2020)")
        st.plotly_chart(fig_quality_score_history, width='stretch')