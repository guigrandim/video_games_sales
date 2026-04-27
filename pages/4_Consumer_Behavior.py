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

st.set_page_config(page_title = 'Consumer Behavior', page_icon = '👥', layout = 'wide')

#===================================
# Functions
#===================================

genre_colors = {
        'Action':       '#E63946',
        'Sports':       '#2196F3',
        'Shooter':      '#FF9800',
        'Role-Playing': '#9C27B0',
        'Platform':     '#4CAF50',
        'Racing':       '#00BCD4',
        'Misc':         '#9E9E9E',
        'Puzzle':       '#FFEB3B',
        'Adventure':    '#795548',
        'Strategy':     '#607D8B',
        'Fighting':     '#F06292',
        'Simulation':   '#80CBC4',
    }

#Função 1 - Afinidade Regional (Vendas de Genero por Região)
def sales_by_genre_heatmap(df1, min_sales=0.0):
    """
    Gera um heatmap de preferência de gênero por região, com escala normalizada
    por linha (cada região tem seu máximo = 1.0) e valores absolutos de vendas
    exibidos nas células.

    Responde às perguntas:
    "Quais gêneros são preferidos em cada região geográfica?"
    "O Japão tem preferências de gênero diferentes da América do Norte?"
    "Existe algum gênero com apelo verdadeiramente global?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com dataset_clean() aplicado.
    min_sales : float, opcional (padrão=0.0)
        Valor mínimo de total_sales (em milhões) para incluir o jogo na análise.
        Use 0.0 para todos os jogos com vendas > 0, ou 0.5/1.0 para focar em jogos com
        relevância comercial.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Heatmap normalizado por região com valores absolutos de vendas nas células.
    """

    # ── 1. Filtra jogos com vendas relevantes ─────────────────────────────────
    filter_by_sales = df1[df1['total_sales'] >= min_sales]

    # ── 2. Agrupamento de vendas por gênero e região ──────────────────────────
    heatmap_data = (
        filter_by_sales.groupby('genre')
        .agg(
            na_sales    = ('na_sales', 'sum'),
            jp_sales    = ('jp_sales', 'sum'),
            pal_sales   = ('pal_sales', 'sum'),
            other_sales = ('other_sales','sum'),
        )
        .round(2)
    )

    # ── 3. Transpõe: linhas = regiões, colunas = gêneros ─────────────────────
    heatmap_pivot = heatmap_data.T

    # Renomeia regiões para labels legíveis
    heatmap_pivot.index = ['América do Norte', 'Japão', 'PAL (Europa/Oceania)', 'Outros Mercados']

    # Ordena colunas (gêneros) pelo volume total decrescente
    col_order = heatmap_pivot.sum(axis=0).sort_values(ascending=False).index
    heatmap_pivot = heatmap_pivot[col_order]

    # ── 4. Normalização por linha: máximo de cada região = 1.0 ───────────────
    heatmap_norm = heatmap_pivot.div(heatmap_pivot.max(axis=1), axis=0).round(3)

    # ── 5. Texto das células: valor absoluto formatado em M ───────────────────
    text_values = heatmap_pivot.applymap(lambda x: f'{x:.1f}M')

    # ── 6. Heatmap ────────────────────────────────────────────────────────────
    fig = px.imshow(
        heatmap_norm,
        zmin=0,
        zmax=1,
        title='Preferência de Gênero por Região — Escala Relativa por Linha',
        labels=dict(color='Intensidade relativa', x='Gênero', y='Região'),
        color_continuous_scale='RdYlGn',
        text_auto=False,
        aspect='auto',
    )

    # Sobrescreve com valores absolutos formatados
    fig.update_traces(
        text=text_values.values,
        texttemplate='%{text}',
        textfont=dict(size=11),
        hovertemplate=(
            '<b>%{y} x %{x}</b><br>'
            'Intensidade relativa: %{z:.2f}<br>'
            'Vendas absolutas: %{text}'
            '<extra></extra>'
        ),
        xgap=2,
        ygap=2,
    )

    fig.update_layout(
        title=dict(
            text='Preferência de Gênero por Região — Escala Relativa por Linha<br>'
                 '<sup>Cor = intensidade relativa ao maior gênero da região | Valor = vendas absolutas em M</sup>',
            font=dict(size=18),
            x=0.01,
        ),
        xaxis=dict(
            title='Gênero',
            tickangle=45,
        ),
        yaxis=dict(title='Região'),
        coloraxis_colorbar=dict(
            title='Intensidade',
            tickvals=[0, 0.25, 0.5, 0.75, 1.0],
            ticktext=['0%', '25%', '50%', '75%', '100%'],
            thickness=12,
        ),
        height=350,
        margin=dict(t=80, l=10, r=20, b=100),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig

#Função 2 - Rentabilidade por Genero e Por Critica e Avaliação Média de Cada Genero 
def profitability_per_genre_critic(df1, min_sales=0.0):
    """
    Gera três gráficos para análise cruzada de rentabilidade e recepção crítica
    por gênero: barras de vendas médias, barras de critic score médio e scatter
    combinando as duas dimensões.

    Responde às perguntas:
    "Quais gêneros geram mais receita por título lançado?"
    "Quais gêneros são mais bem avaliados pela crítica?"
    "Existe correlação entre qualidade crítica e volume de vendas por gênero?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com dataset_clean() aplicado.
    min_sales : float, opcional (padrão=0.0)
        Valor mínimo de total_sales (em milhões) para incluir o jogo na análise.
        Use 0.0 para todos os jogos com vendas > 0, ou 0.5/1.0 para focar em jogos com
        relevância comercial.

    Retorna
    -------
    fig1 : plotly.graph_objects.Figure
        Barras horizontais — média de vendas por título por gênero.
    fig2 : plotly.graph_objects.Figure
        Barras horizontais — média de critic_score por gênero.
    fig3 : plotly.graph_objects.Figure
        Scatter — vendas médias x critic score, tamanho = volume de títulos.
    """

    # ── 1. Bases separadas para vendas e crítica ──────────────────────────────
    df_sales  = df1.loc[df1['total_sales'] > min_sales]
    df_critic = df1.dropna(subset=['critic_score'])

    # ── 2. Vendas médias por gênero ───────────────────────────────────────────
    sales_per_title = (
        df_sales.groupby(['genre', 'title'])['total_sales']
        .sum()
        .reset_index()
    )
    profitability_per_genre = (
        sales_per_title.groupby('genre')['total_sales']
        .agg(avg_sales='mean', total_titles='count')
        .reset_index()
        .sort_values('avg_sales', ascending=True)
        .round(2)
    )

    # ── 3. Crítica média por gênero ───────────────────────────────────────────
    critic_per_title = (
        df_critic.groupby(['genre', 'title'])['critic_score']
        .mean()
        .reset_index()
    )
    critic_per_genre = (
        critic_per_title.groupby('genre')['critic_score']
        .agg(mean_critic='mean', total_titles='count')
        .reset_index()
        .sort_values('mean_critic', ascending=True)
        .round(2)
    )

    # ── 4. Merge para o scatter ───────────────────────────────────────────────
    genre_combined = profitability_per_genre.merge(
        critic_per_genre[['genre', 'mean_critic']],
        on='genre',
        how='inner',
    )
    
    # ── 4.1 Filtro de representatividade — remove gêneros com amostra pequena ─
    MIN_TITLES = 20

    critic_per_genre = critic_per_genre[
        critic_per_genre['total_titles'] >= MIN_TITLES
    ]
    profitability_per_genre = profitability_per_genre[
        profitability_per_genre['total_titles'] >= MIN_TITLES
    ]

    genre_combined = profitability_per_genre.merge(
        critic_per_genre[['genre', 'mean_critic']],
        on='genre',
        how='inner',
    )

    MAX_AVG_SALES = genre_combined['avg_sales'].quantile(0.95)
    genre_combined = genre_combined[
        genre_combined['avg_sales'] <= MAX_AVG_SALES
    ]
    profitability_per_genre = profitability_per_genre[
        profitability_per_genre['genre'].isin(genre_combined['genre'])
    ]
    critic_per_genre = critic_per_genre[
        critic_per_genre['genre'].isin(genre_combined['genre'])
    ]

    # ── 5. Fig1: Rentabilidade por gênero (barras + colorscale por volume) ────
    fig1 = go.Figure(go.Bar(
        x=profitability_per_genre['avg_sales'],
        y=profitability_per_genre['genre'],
        orientation='h',
        marker=dict(
            color=profitability_per_genre['total_titles'],
            colorscale='Blues',
            showscale=True,
            colorbar=dict(
                title=dict(text='Nº de<br>títulos', side='right'),
                thickness=12,
                len=0.5,
            ),
        ),
        cliponaxis=False,
        text=profitability_per_genre.apply(
            lambda r: f"{r['avg_sales']:.2f}M  ({int(r['total_titles'])} títulos)", axis=1
        ),
        textposition='outside',
        customdata=profitability_per_genre[['total_titles', 'avg_sales']],
        hovertemplate=(
            '<b>%{y}</b><br>'
            'Média de vendas por título: %{x:.2f}M<br>'
            'Total de títulos: %{customdata[0]}'
            '<extra></extra>'
        ),
    ))

    fig1.update_layout(
        title=dict(
            text='Rentabilidade por Gênero — Média de Vendas por Título<br>'
                 '<sup>Cor da barra = volume de títulos | Barras mais escuras = gêneros com mais títulos</sup>',
            font=dict(size=18), x=0.01,
        ),
        xaxis=dict(
            title='Média de vendas por título (M)',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.06)',
            range=[0, profitability_per_genre['avg_sales'].max() * 1.35],
        ),
        yaxis=dict(title='', categoryorder='total ascending'),
        height=max(400, len(profitability_per_genre) * 36),
        margin=dict(t=70, l=10, r=200, b=40),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    # ── 6. Fig2: Recepção crítica por gênero ──────────────────────────────────
    fig2 = go.Figure(go.Bar(
        x=critic_per_genre['mean_critic'],
        y=critic_per_genre['genre'],
        orientation='h',
        marker=dict(
            color=critic_per_genre['total_titles'],
            colorscale='Greens',
            showscale=True,
            colorbar=dict(
                title=dict(text='Nº de<br>títulos', side='right'),
                thickness=12,
                len=0.5,
            ),
        ),
        cliponaxis=False,
        text=critic_per_genre.apply(
            lambda r: f"{r['mean_critic']:.1f}  ({int(r['total_titles'])} títulos)", axis=1
        ),
        textposition='outside',
        customdata=critic_per_genre[['total_titles', 'mean_critic']],
        hovertemplate=(
            '<b>%{y}</b><br>'
            'Crítica média: %{x:.1f}<br>'
            'Total de títulos: %{customdata[0]}'
            '<extra></extra>'
        ),
    ))
    
    # ── Bandas de qualidade ── inserir aqui ───────────────────────────────────
    score_min   = critic_per_genre['mean_critic'].min()
    score_max   = critic_per_genre['mean_critic'].max()


    fig2.update_layout(
        title=dict(
            text='Recepção Crítica por Gênero — Média de Pontuação<br>'
                 '<sup>Cor da barra = volume de títulos avaliados | Gêneros com mais críticas = mais escuros</sup>',
            font=dict(size=18), x=0.01,
        ),
        xaxis=dict(
            title='Pontuação média da crítica',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.06)',
            range=[score_min * 0.95, score_max * 1.15],
        ),
        yaxis=dict(title='', categoryorder='total ascending'),
        height=max(400, len(critic_per_genre) * 36),
        margin=dict(t=70, l=10, r=200, b=40),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    # ── 7. Fig3: Scatter — Vendas × Crítica por gênero ───────────────────────
    fig3 = go.Figure(go.Scatter(
        x=genre_combined['mean_critic'],
        y=genre_combined['avg_sales'],
        mode='markers+text',
        marker=dict(
            size=genre_combined['total_titles'],
            sizemode='area',
            sizeref=2. * genre_combined['total_titles'].max() / (40. ** 2),
            sizemin=6,
            color=[genre_colors.get(g, '#888888') for g in genre_combined['genre']],
            line=dict(width=1.5, color='white'),
        ),
        text=genre_combined['genre'],
        textposition='top center',
        textfont=dict(size=10),
        customdata=genre_combined[['total_titles', 'avg_sales', 'mean_critic']],
        hovertemplate=(
            '<b>%{text}</b><br>'
            'Crítica média: %{x:.1f}<br>'
            'Média de vendas: %{y:.2f}M<br>'
            'Total de títulos: %{customdata[0]}'
            '<extra></extra>'
        ),
    ))

    # Linhas de referência (médias globais) para quadrantear o scatter
    global_avg_sales  = genre_combined['avg_sales'].mean()
    global_avg_critic = genre_combined['mean_critic'].mean()

    fig3.add_hline(
        y=global_avg_sales,
        line=dict(color='rgba(255,255,255,0.2)', width=1, dash='dash'),
        annotation_text=f'Média de vendas: {global_avg_sales:.2f}M',
        annotation_font=dict(size=9, color='rgba(255,255,255,0.5)'),
        annotation_xanchor='left',
    )
    fig3.add_vline(
        x=global_avg_critic,
        line=dict(color='rgba(255,255,255,0.2)', width=1, dash='dash'),
        annotation_text=f'Média crítica: {global_avg_critic:.1f}',
        annotation_font=dict(size=9, color='rgba(255,255,255,0.5)'),
        annotation_yanchor='bottom',
    )

    fig3.update_layout(
        title=dict(
            text='Crítica vs. Vendas por Gênero<br>'
                 '<sup>Tamanho da bolha = volume de títulos | Cor = gênero | Linhas = médias globais</sup>',
            font=dict(size=18), x=0.01,
        ),
        xaxis=dict(
            title='Pontuação média da crítica',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.06)',
        ),
        yaxis=dict(
            title='Média de vendas por título (M)',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.06)',
        ),
        height=520,
        margin=dict(t=80, l=60, r=40, b=60),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    # Anotações de quadrante — adicionadas após update_layout para não
    # sobrescrever as anotações internas do add_hline / add_vline
    quadrantes = [
        dict(x=0.02, y=0.98, text='⚠ Nicho crítico<br><sup>Bem avaliado, vende pouco</sup>', xanchor='left',  yanchor='top'),
        dict(x=0.98, y=0.98, text='★ Zona de ouro<br><sup>Bem avaliado e vende muito</sup>', xanchor='right', yanchor='top'),
        dict(x=0.02, y=0.02, text='✗ Evitar<br><sup>Mal avaliado e vende pouco</sup>', xanchor='left',  yanchor='bottom'),
        dict(x=0.98, y=0.02, text='⚡ Volume popular<br><sup>Mal avaliado, vende muito</sup>', xanchor='right', yanchor='bottom'),
    ]

    for q in quadrantes:
        fig3.add_annotation(
            x=q['x'], y=q['y'],
            xref='paper', yref='paper',
            text=q['text'],
            showarrow=False,
            xanchor=q['xanchor'],
            yanchor=q['yanchor'],
            font=dict(size=11, color='rgba(255,255,255,0.35)'),
        )

    return fig1, fig2, fig3

#Função 3 - Caracterização dos Tipos e Qualidade dos Jogos
def size_quality_market_genre(df1):
    """
    Calcula métricas gerais do mercado por gênero para uso em st.metric:
    total de gêneros únicos, gênero com melhor média de critic_score e
    a pontuação média desse gênero.

    Responde às perguntas:
    "Quantos gêneros distintos compõem o mercado analisado?"
    "Qual gênero entrega consistentemente os jogos mais bem avaliados?"
    "Qual é a pontuação média do gênero mais bem avaliado?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com dataset_clean() aplicado.

    Retorna
    -------
    total_genres : int
        Quantidade de gêneros únicos no dataset.
    best_genre : str
        Nome do gênero com maior média de critic_score.
    best_genre_score : float
        Média de critic_score do gênero líder, arredondada em 2 casas.
    """

    # ── 1. Remove jogos sem avaliação crítica ─────────────────────────────────
    df_clean = df1.dropna(subset=['critic_score'])

    # ── 2. Total de gêneros únicos (base completa, sem filtro de crítica) ─────
    total_genres = df1['genre'].nunique()
    
    # ── 3. Validação: se não há jogos avaliados, retorna valores padrão ───────
    if df_clean.empty:
        return total_genres, "Nenhum gênero avaliado", 0.0
    
    # ── 4. Média de critic_score por gênero ───────────────────────────────────
    avg_critic_per_genre = df_clean.groupby('genre')['critic_score'].mean()
    
    # ── 5. Se mesmo assim a série estiver vazia (ex.: só gêneros sem nome) ────
    if avg_critic_per_genre.empty:
        return total_genres, "Dados insuficientes", 0.0
    
    # ── 6. Gênero com maior média e sua pontuação ─────────────────────────────
    best_genre       = avg_critic_per_genre.idxmax()
    best_genre_score = round(avg_critic_per_genre.max(), 2)

    return total_genres, best_genre, best_genre_score

#Função 4 - Migração de Popularidade
def genre_migration_by_generation(df1):
    """
    Gera dois gráficos para análise da migração de popularidade de gêneros
    ao longo das gerações de console: um Bump Chart de ranking e um Line Chart
    de evolução de market share.

    Responde às perguntas:
    "Como evoluiu o ranking de popularidade de cada gênero entre gerações?"
    "Quais gêneros cresceram, declinaram ou se mantiveram estáveis?"
    "Em qual geração cada gênero atingiu seu pico de market share?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com dataset_clean() aplicado.

    Retorna
    -------
    fig1 : plotly.graph_objects.Figure
        Bump Chart — ranking de popularidade por gênero e geração.
    fig2 : plotly.graph_objects.Figure
        Line Chart — evolução do market share (%) por gênero e geração.
    """

    # ── 1. Limpeza do DataFrame ───────────────────────────────────────────────
    df_gen = df1.loc[
        (df1['total_sales'] > 0) &
        (df1['generation'] != 'OtherUnknown') &
        (df1['genre'].notna())
    ].copy()

    # ── 2. Ordem cronológica das gerações ─────────────────────────────────────
    GEN_ORDER = ['2nd Gen','3rd Gen','4th Gen','5th Gen','6th Gen','7th Gen','8th Gen','9th Gen']
    df_gen = df_gen[df_gen['generation'].isin(GEN_ORDER)]

    # ── 3. Vendas por geração × gênero ───────────────────────────────────────
    gen_genre = (
        df_gen.groupby(['generation', 'genre'])['total_sales']
        .sum()
        .reset_index()
    )

    # ── 4. Market share por geração (% dentro de cada geração) ───────────────
    gen_genre['pct'] = (
        gen_genre.groupby('generation')['total_sales']
        .transform(lambda x: (x / x.sum() * 100).round(2))
    )

    # ── 5. Ranking por geração ────────────────────────────────────────────────
    gen_genre['rank'] = (
        gen_genre.groupby('generation')['total_sales']
        .rank(ascending=False, method='min')
        .astype(int)
    )

    # ── 6. Top 10 gêneros por relevância histórica ────────────────────────────
    top_genres = (
        gen_genre.groupby('genre')['total_sales']
        .sum()
        .nlargest(10)
        .index.tolist()
    )
    gen_genre = gen_genre[gen_genre['genre'].isin(top_genres)]

    # ── 7. Pivot para Bump Chart e Line Chart ─────────────────────────────────
    pivot_area = (
        gen_genre.pivot_table(
            index='generation', columns='genre', values='pct', aggfunc='sum'
        )
        .reindex(GEN_ORDER)                                  # ← ordem cronológica garantida
        .fillna(0)
    )

    pivot_bump = (
        gen_genre.pivot_table(
            index='generation', columns='genre', values='rank', aggfunc='min'
        )
        .reindex(GEN_ORDER)
    )

    # ── 8. Fig1: Bump Chart — Ranking de Popularidade ─────────────────────────
    fig1 = go.Figure()

    for genre in pivot_bump.columns:
        color  = genre_colors.get(genre, '#888888')          # ← paleta global de gêneros
        y_vals = pivot_bump[genre].tolist()
        x_vals = pivot_bump.index.tolist()

        fig1.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            name=genre,
            mode='lines+markers+text',
            line=dict(color=color, width=2.5, shape='spline'),
            marker=dict(size=14, color=color, line=dict(width=2, color='white')),
            text=[str(int(v)) if pd.notna(v) else '' for v in y_vals],
            textposition='middle center',
            textfont=dict(size=9, color='white'),
            hovertemplate=(
                f'<b>{genre}</b><br>'
                'Geração: %{x}<br>'
                'Ranking: #%{y}'
                '<extra></extra>'
            ),
        ))

        # Label do gênero na última geração válida
        last_valid = pivot_bump[genre].last_valid_index()
        if last_valid:
            last_rank = pivot_bump.loc[last_valid, genre]
            if pd.notna(last_rank):
                fig1.add_annotation(
                    x=last_valid,
                    y=last_rank,
                    text=f'  {genre}',
                    showarrow=False,
                    xanchor='left',
                    font=dict(size=10, color=color),
                )

    fig1.update_layout(
        title=dict(
            text='Ranking de Popularidade de Gêneros por Geração<br>'
                 '<sup>Número dentro do marcador = posição no ranking | Linhas cruzadas = mudança de posição</sup>',
            font=dict(size=18),
            x=0.01,
        ),
        yaxis=dict(
            autorange='reversed',                            # rank 1 no topo
            tickvals=list(range(1, len(top_genres) + 1)),
            title='Ranking',
            gridcolor='rgba(0,0,0,0.06)',
        ),
        xaxis=dict(title='Geração de Console'),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='left', x=0, font=dict(size=11)),
        height=550,
        margin=dict(t=90, l=10, r=120, b=40),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    # ── 9. Fig2: Line Chart — Evolução do Market Share ────────────────────────
    fig2 = go.Figure()

    pivot_area = pivot_area[pivot_area.index != '9th Gen']

    for genre in pivot_area.columns:
        color    = genre_colors.get(genre, '#888888')
        y_vals   = pivot_area[genre].tolist()
        x_vals   = pivot_area.index.tolist()
        peak_idx = pivot_area[genre].idxmax()
        peak_val = pivot_area[genre].max()

        # Linha de evolução
        fig2.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            name=genre,
            mode='lines+markers',
            line=dict(color=color, width=2.5, shape='spline'),
            marker=dict(size=8, color=color, line=dict(width=1.5, color='white')),
            hovertemplate=(
                f'<b>{genre}</b><br>'
                'Geração: %{x}<br>'
                'Market share: %{y:.1f}%'
                '<extra></extra>'
            ),
        ))

        # Marcador de pico (estrela)
        fig2.add_trace(go.Scatter(
            x=[peak_idx],
            y=[peak_val],
            mode='markers',
            marker=dict(size=14, symbol='star', color=color, line=dict(width=1, color='white')),
            showlegend=False,
            hovertemplate=(
                f'<b>{genre} — Pico</b><br>'
                'Geração: %{x}<br>'
                'Market share: %{y:.1f}%'
                '<extra></extra>'
            ),
        ))

        # Label na última geração
        fig2.add_annotation(
            x=x_vals[-1],
            y=y_vals[-1],
            text=f'  {genre}',
            showarrow=False,
            xanchor='left',
            font=dict(size=10, color=color),
        )

    fig2.update_layout(
        title=dict(
            text='Evolução do Market Share de Gêneros por Geração<br>'
                 '<sup>★ = geração de pico do gênero | % = share das vendas totais da geração</sup>',
            font=dict(size=18),
            x=0.01,
        ),
        yaxis=dict(
            title='% das vendas da geração',
            ticksuffix='%',
            gridcolor='rgba(0,0,0,0.06)',
        ),
        xaxis=dict(title='Geração de Console'),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='left', x=0, font=dict(size=11)),
        height=550,
        margin=dict(t=90, l=10, r=120, b=40),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig1, fig2

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
st.title ('👥 Preferência de Gênero - Consumer Behavior')
st.markdown("""- Métricas relacionadas ao comportamento dos clientes segmentado por genero e região de forma temporal """)

#Call the Functions
fig_sales_genre_region = sales_by_genre_heatmap(df1, min_sales=0.5)                                                            # <- Função 1 - Afinidade Regional (Vendas de Genero por Região)
fig_profit_per_genre, fig_critic_per_genre, fig_profit_critic_genre = profitability_per_genre_critic(df1, min_sales=0.0)       # <- Função 2 - Rentabilidade por Genero e Por Critica e Avaliação Média de Cada Genero 
kpi_total_genre, kpi_best_genre, kpi_best_genre_score = size_quality_market_genre(df1)                                         # <- Função 3 - Caracterização dos Tipos e Qualidade dos Jogos
fig_popularity_migration, fig_market_share_genre = genre_migration_by_generation(df1)                                          # <- Função 4 - Migração de Popularidade e Market Share

st.divider()

#Create KPIs In Page

st.markdown("### Total de Generos no Mercado e Genero de maior qualidade")
col1, col2 = st.columns(2)
with st.container():
    with col1:
        st.metric("Gêneros únicos", kpi_total_genre)
    
    with col2:
        st.metric('Gênero mais bem avaliado', kpi_best_genre, delta=f'{kpi_best_genre_score} critic score médio')

tab1, tab2 = st.tabs(['Comportamento por Vendas', 'Comportamento por Qualidade'])

with tab1:
    with st.container():
        st.markdown("### Preferencia de Genero por Região por Vendas")
        st.plotly_chart(fig_sales_genre_region, width='stretch')

    st.divider()

    with st.container():
        st.markdown("### Rentabilidade por Genero")
        st.plotly_chart(fig_profit_per_genre, width='stretch')

    st.divider()

    with st.container():
        st.markdown("### Comportamento do Consumidor - Vendas de Generos por Geração")
        st.plotly_chart(fig_market_share_genre, width='stretch')

with tab2:
    with st.container():
        st.markdown("### Qualidade dos Jogos Por Genero")
        st.plotly_chart(fig_critic_per_genre, width='stretch')
        
    with st.container():
        st.markdown("### Relação das Vendas vs Critica - Por Genero")
        st.plotly_chart(fig_profit_critic_genre, width='stretch')
    
    with st.container():
        st.markdown("### Comportamento do Consumidor - Preferencia de Generos por Geração")
        st.plotly_chart(fig_popularity_migration, width='stretch')