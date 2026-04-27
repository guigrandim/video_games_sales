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
from plotly.subplots import make_subplots

#==================================
# Configuration Page
#==================================

st.set_page_config(page_title = 'Qualidade vs. Vendas- Predictive Validity (ROI)', page_icon = '⭐', layout = 'wide')

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

#Função 1 - Correlação entre Qualidade do Jogo e o Número de Vendas
def correlation_beteween_score_sales(df1):
    """
    Gera gráficos de dispersão e benchmark (threshold) para a relação entre nota da crítica e vendas médias.

    A função calcula a média de vendas por nota da crítica, traça uma linha de regressão linear e
    identifica o ponto de corte (benchmark) que maximiza a diferença de vendas médias entre os grupos
    "abaixo" e "acima/igual" da nota candidata.

    O objetivo é encontrar a nota mínima que garante bom retorno comercial sem exigir excelência máxima
    (notas muito altas), permitindo configurar faixas realistas de busca.

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame contendo as colunas 'critic_score' e 'total_sales'.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Gráfico principal (dispersão + linha de tendência + benchmark).
    fig_marginal : plotly.graph_objects.Figure ou None
        Gráfico de barras com o ganho marginal por nota candidata.

    Configurações ajustáveis (altere os valores no início da função)
    ----------------------------------------------------------------
    MIN_BENCHMARK_SCORE : int, padrão=5
        Menor nota candidata a threshold (limite inferior da busca).

    MAX_BENCHMARK_SCORE : int, padrão=8
        Maior nota candidata a threshold (limite superior da busca).
        Valores típicos: 8 para evitar notas extremas (9 ou 10), ou 9 se desejar incluí-las.

    MIN_GROUP_SIZE : int, padrão=20
        Número mínimo de jogos exigido em cada grupo (abaixo e acima do candidato).
        Valores maiores (≥20) garantem robustez estatística e descartam notas altas
        com poucos jogos, favorecendo oportunidades em notas médias (7-8).
        Valores menores (10-15) permitem capturar notas mais altas, mas com maior risco
        de viés por amostra pequena.

    MIN_TITLES_PER_SCORE : int, padrão=10
        Número mínimo de títulos únicos exigido para que uma nota seja exibida no gráfico
        de dispersão (não influencia o cálculo do benchmark, apenas a visualização).

    Exemplo de ajuste
    -----------------
    Para buscar benchmarks apenas entre notas 6 e 8, com grupos de pelo menos 30 jogos:
        MIN_BENCHMARK_SCORE = 6
        MAX_BENCHMARK_SCORE = 8
        MIN_GROUP_SIZE = 30
    """

    # ── 1. Limpeza dos dados ──────────────────────────────────────────
    df_clean = (
        df1.loc[df1['total_sales'] >= 0.5]
           .dropna(subset=['critic_score'])
           .copy()
    )

    # Remove outliers de vendas (top 5%)
    p95 = df_clean['total_sales'].quantile(0.95)
    df_clean = df_clean[df_clean['total_sales'] <= p95]

    if df_clean.empty or len(df_clean) < 20:
        fig = go.Figure()
        fig.add_annotation(
            text="Dados insuficientes para calcular correlação",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(height=500)
        return fig, None

    # Configurações Ajustaveis
    
    MIN_BENCHMARK_SCORE = 5      # menor nota candidata a threshold
    MAX_BENCHMARK_SCORE = 9      # maior nota candidata a threshold
    MIN_GROUP_SIZE = 20          # mínimo de jogos abaixo e acima do candidato
    MIN_TITLES_PER_SCORE = 10    # mínimo de títulos por nota (para exibição no gráfico)
    
    # ── 2. Agrupamento por nota: média e contagem de títulos ──────────
    score_stats = (
        df_clean.groupby('critic_score')
        .agg(
            mean_sales = ('total_sales', 'mean'),
            total_titles = ('title', 'nunique')
        )
        .reset_index()
    )

    # Filtra notas com pelo menos 10 títulos (para suavizar a curva)
    score_stats = score_stats[score_stats['total_titles'] >= MIN_TITLES_PER_SCORE]

    if len(score_stats) < 2:
        fig = go.Figure()
        fig.add_annotation(
            text="Dados insuficientes após filtro de mínimo de títulos por nota",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(height=500)
        return fig, None

    # ── 3. Regressão linear (no intervalo central) ───────────────────
    x = score_stats['critic_score'].values
    y = score_stats['mean_sales'].values

    q05, q95 = np.quantile(x, 0.05), np.quantile(x, 0.95)
    mask = (x >= q05) & (x <= q95)
    m, b = np.polyfit(x[mask], y[mask], 1)

    x_line = np.linspace(x.min(), x.max(), 100)
    y_line = m * x_line + b

    # ── 4. Benchmark robusto SOMENTE nas notas 5 a 8 ──────────────────
    best_score = None
    best_diff = -1
    best_mean_above = 0
    best_mean_below = 0
    marginal_gains = []  # guarda (score, diff) para gráfico auxiliar

    # Testa apenas as notas que interessam ao negócio
    for score in range(MIN_BENCHMARK_SCORE, MAX_BENCHMARK_SCORE + 1):
        above = df_clean[df_clean['critic_score'] >= score]['total_sales']
        below = df_clean[df_clean['critic_score'] < score]['total_sales']
        # Exige pelo menos 20 jogos em cada grupo (robustez)
        if len(above) >= 20 and len(below) >= 20:
            diff = above.mean() - below.mean()
            marginal_gains.append((score, diff, above.mean(), below.mean()))
            if diff > best_diff:
                best_diff = diff
                best_score = score
                best_mean_above = above.mean()
                best_mean_below = below.mean()

    # Fallback seguro (se nenhum atender, usa a mediana do intervalo 5-8)
    if best_score is None:
        df_range = df_clean[(df_clean['critic_score'] >= MIN_BENCHMARK_SCORE) & (df_clean['critic_score'] <= MAX_BENCHMARK_SCORE)]
        if not df_range.empty:
            best_score = int(df_range['critic_score'].median())
            best_mean_above = df_clean[df_clean['critic_score'] >= best_score]['total_sales'].mean()
            best_mean_below = df_clean[df_clean['critic_score'] < best_score]['total_sales'].mean()
            best_diff = best_mean_above - best_mean_below
        else:
            best_score = 7  # valor padrão sensato
            best_mean_above = df_clean[df_clean['critic_score'] >= best_score]['total_sales'].mean()
            best_mean_below = df_clean[df_clean['critic_score'] < best_score]['total_sales'].mean()
            best_diff = best_mean_above - best_mean_below

    delta_pct = (best_mean_above - best_mean_below) / best_mean_below * 100 if best_mean_below > 0 else 0

    # ── 5. Gráfico principal (dispersão + benchmark) ──────────────────
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode='markers',
        name='Média de vendas por nota',
        marker=dict(size=8, opacity=0.7, color='steelblue'),
        customdata=score_stats[['total_titles']].values,
        hovertemplate='Nota: %{x}<br>Venda Média: %{y:.2f}M<br>Títulos: %{customdata[0]}<extra></extra>',
    ))

    fig.add_trace(go.Scatter(
        x=x_line, y=y_line,
        mode='lines',
        name=f'Tendência (y = {m:.3f}x + {b:.2f})',
        line=dict(color='red', width=2),
    ))

    fig.add_vline(
        x=best_score,
        line=dict(color='rgba(46,204,113,0.8)', width=2, dash='dash'),
    )

    fig.add_annotation(
        x=best_score, y=1, yref='paper',
        text=(
            f'<b>Benchmark ({MIN_BENCHMARK_SCORE}-{MAX_BENCHMARK_SCORE}): Nota ≥ {best_score}</b><br>'
            f'Vendas médias acima: {best_mean_above:.2f}M<br>'
            f'Vendas médias abaixo: {best_mean_below:.2f}M<br>'
            f'Ganho: +{delta_pct:.0f}%'
        ),
        showarrow=False,
        xanchor='left' if best_score < 7 else 'right',
        font=dict(size=11, color='rgba(46,204,113,0.9)'),
        bgcolor='rgba(0,0,0,0.6)',
        borderpad=4,
        yanchor='top',
    )

    # Faixas visuais
    fig.add_vrect(
        x0=score_stats['critic_score'].min(), x1=best_score,
        fillcolor='rgba(231,76,60,0.05)', line_width=0,
    )
    fig.add_vrect(
        x0=best_score, x1=score_stats['critic_score'].max(),
        fillcolor='rgba(46,204,113,0.05)', line_width=0,
    )

    fig.update_layout(
        title=dict(
            text=(
                f'Relação entre Nota da Crítica e Vendas Médias por Título<br>'
                f'<sup>Benchmark calculado nas notas {MIN_BENCHMARK_SCORE}-{MAX_BENCHMARK_SCORE} | '
                f'Grupo mínimo: {MIN_GROUP_SIZE} jogos | Mínimo títulos por nota: {MIN_TITLES_PER_SCORE}</sup>'
            ),
            font=dict(size=16),
            x=0.01,
        ),
        xaxis=dict(title='Nota da Crítica', showgrid=True, gridcolor='rgba(0,0,0,0.06)'),
        yaxis=dict(title='Vendas Médias (milhões)', showgrid=True, gridcolor='rgba(0,0,0,0.06)'),
        height=500,
        margin=dict(t=80, l=60, r=40, b=50),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    # ── 6. Gráfico auxiliar: ganho marginal por nota candidata ──────
    if marginal_gains:
        scores = [g[0] for g in marginal_gains]
        diffs = [g[1] for g in marginal_gains]
        fig_marginal = go.Figure(go.Bar(
            x=scores, y=diffs,
            marker_color=['#2ECC71' if s == best_score else '#BDC3C7' for s in scores],
            text=[f'{d:.2f}M' for d in diffs],
            textposition='outside',
            hovertemplate='Nota candidata: %{x}<br>Ganho marginal: %{y:.2f}M<extra></extra>'
        ))
        fig_marginal.update_layout(
            title='Ganho marginal (vendas médias acima vs. abaixo) por nota candidata',
            xaxis_title='Nota candidata (threshold)',
            yaxis_title='Diferença de vendas médias (milhões)',
            height=300,
            margin=dict(t=50, b=30),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
    else:
        fig_marginal = None

    return fig, fig_marginal

# Função 2 - Matriz de Hype vs. Pérolas
def plot_hype_premium(df, min_sales=0.0):
    """
    Gera um gráfico de quadrantes (scatter plot) que cruza a nota da crítica
    com as vendas totais, dividindo o espaço por medianas para destacar quatro perfis:
    - Alta Nota / Alta Venda  → sucesso de crítica e público
    - Baixa Nota / Alta Venda → popular apesar das críticas (hype)
    - Alta Nota / Baixa Venda → aclamado, mas pouco vendido (hidden gem)
    - Baixa Nota / Baixa Venda → fracasso comercial e crítico

    Colorido por holding desenvolvedora com mínimo de 15 títulos avaliados.

    Responde às perguntas:
    "Quais jogos são superestimados ou subestimados pela crítica?"
    "Onde estão os outliers comerciais e os hidden gems?"
    "Qual holding desenvolvedora domina cada quadrante de qualidade × vendas?"

    Parâmetros
    ----------
    df : pd.DataFrame
        Deve conter 'critic_score', 'total_sales', 'title', 'plataform'
        e 'holdings_developer'.
    min_sales : float, opcional (padrão=0.0)
        Filtro mínimo de total_sales em milhões.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Gráfico de dispersão com 4 quadrantes, linhas de referência nas medianas
        e contagens na legenda por holding desenvolvedora.
    """

    # ── 1. Limpeza dos dados ──────────────────────────────────────────────────
    df_clean = (
        df.dropna(subset=['critic_score', 'holdings_developer'])
        .copy()
    )
    df_clean = df_clean[
        (df_clean['total_sales'] > min_sales) &
        (df_clean['holdings_developer'].str.strip() != '')
    ]

    # ── 2. Filtra holdings com mínimo de 15 títulos únicos avaliados ──────────
    holdings_validas = (
        df_clean.groupby('holdings_developer')['title']
        .nunique()
        .loc[lambda x: x >= 15]
        .index
    )
    df_clean = df_clean[df_clean['holdings_developer'].isin(holdings_validas)]

    # ── 3. Medianas de referência ─────────────────────────────────────────────
    median_score = df_clean['critic_score'].median()
    median_sales = df_clean['total_sales'].median()

    # Debug rápido — remova após confirmar
    print(f'Mediana critic_score: {median_score:.2f}')
    print(f'Mediana total_sales:  {median_sales:.4f}M')
    print(f'Min: {df_clean["total_sales"].min():.4f} | Max: {df_clean["total_sales"].max():.2f}')
    print(df_clean['total_sales'].describe())

    # ── 4. Classificação dos quadrantes ───────────────────────────────────────
    def classify_quadrant(row):
        high_score = row['critic_score'] >= median_score
        high_sales = row['total_sales']  >= median_sales
        if high_score and high_sales:
            return 'Alta Nota, Alta Venda'
        elif not high_score and high_sales:
            return 'Baixa Nota, Alta Venda'
        elif high_score and not high_sales:
            return 'Alta Nota, Baixa Venda'
        else:
            return 'Baixa Nota, Baixa Venda'

    df_clean['quadrant'] = df_clean.apply(classify_quadrant, axis=1)

    # ── 5. Figura ─────────────────────────────────────────────────────────────
    fig = go.Figure()

    # ── 6. Labels dos quadrantes nos cantos (via anotações em paper) ──────────
    quadrant_labels = [
        (1.0, 1.0, 'Alta Nota<br>Alta Venda ✓',   'right', 'top'),
        (0.0, 1.0, 'Baixa Nota<br>Alta Venda 🔥',  'left',  'top'),
        (1.0, 0.0, 'Alta Nota<br>Baixa Venda 💎',  'right', 'bottom'),
        (0.0, 0.0, 'Baixa Nota<br>Baixa Venda ✗', 'left',  'bottom'),
    ]

    for x, y, text, xanchor, yanchor in quadrant_labels:
        fig.add_annotation(
            x=x, y=y,
            xref='paper', yref='paper',              # ← posição relativa ao gráfico
            text=text,
            showarrow=False,
            xanchor=xanchor,
            yanchor=yanchor,
            font=dict(size=10, color='rgba(255,255,255,0.3)'),
        )

    # ── 7. Pontos coloridos por holding desenvolvedora ────────────────────────
    for holding in sorted(df_clean['holdings_developer'].unique()):
        subset = df_clean[df_clean['holdings_developer'] == holding]
        color  = holdings_colors.get(holding, '#888888')
        count  = len(subset)

        fig.add_trace(go.Scatter(
            x=subset['critic_score'],
            y=subset['total_sales'],
            mode='markers',
            name=f'{holding} ({count})',
            marker=dict(
                color=color,
                size=7,
                opacity=0.75,
                line=dict(width=0.5, color='white'),
            ),
            customdata=subset[['title', 'plataform', 'quadrant', 'holdings_developer']],
            hovertemplate=(
                '<b>%{customdata[0]}</b><br>'
                'Plataforma: %{customdata[1]}<br>'
                'Holding: %{customdata[3]}<br>'
                'Nota: %{x:.1f}<br>'
                'Vendas: %{y:.2f}M<br>'
                'Quadrante: %{customdata[2]}'
                '<extra></extra>'
            ),
        ))

    # ── 8. Linhas de referência nas medianas ──────────────────────────────────
    fig.add_hline(
        y=median_sales,
        line=dict(dash='dash', color='rgba(255,255,255,0.3)', width=1),
        annotation_text=f'Mediana vendas: {median_sales:.2f}M',
        annotation_font=dict(size=10, color='rgba(255,255,255,0.5)'),
        annotation_position='bottom right',
    )
    fig.add_vline(
        x=median_score,
        line=dict(dash='dash', color='rgba(255,255,255,0.3)', width=1),
        annotation_text=f'Mediana nota: {median_score:.1f}',
        annotation_font=dict(size=10, color='rgba(255,255,255,0.5)'),
        annotation_position='top left',
    )

    # ── 9. Layout ─────────────────────────────────────────────────────────────
    fig.update_layout(
            title=dict(
                text=f'Quadrantes: Nota da Crítica vs. Vendas Totais (min {min_sales}M)<br>'
                     '<sup>Cor = Holding Desenvolvedora (≥ 15 títulos) | Linhas = medianas</sup>',
                font=dict(size=18),
                x=0.01,
            ),
            xaxis=dict(
                title='Nota da Crítica',
                showgrid=True,
                gridcolor='rgba(0,0,0,0.06)',
                range=[
                    df_clean['critic_score'].min() - 0.5,
                    10.5,
                ],
            ),
            yaxis=dict(
                title='Vendas Totais (M)',
                type='log',
                showgrid=True,
                gridcolor='rgba(0,0,0,0.06)',
            ),
            legend=dict(
                orientation='v',
                x=1.02,
                y=1,
                font=dict(size=10),
            ),
            height=620,
            margin=dict(t=80, l=60, r=180, b=60),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )

    return fig


    """
    Identifica o limiar de nota da crítica (critic_score) que maximiza a diferença
    de vendas médias entre jogos acima e abaixo dele e exibe a curva da média de vendas
    por nota com destaque para o threshold.

    Responde às perguntas:
    "A partir de qual nota os jogos passam a vender significativamente mais?"
    "Qual é o fator multiplicativo de vendas para jogos que atingem essa nota?"

    Parâmetros
    ----------
    df : pd.DataFrame
        Deve conter as colunas 'critic_score' e 'total_sales'.
    min_sales : float, opcional (padrão=0.0)
        Filtro mínimo de vendas (em milhões) para incluir o jogo na análise.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Gráfico de linha com a média de vendas por nota, linha vertical no threshold
        e anotação com os KPIs principais.
    """
        # ── 1. Limpeza e filtro ────────────────────────────────────────
    df_clean = df.dropna(subset=['critic_score']).copy()
    df_clean = df_clean[df_clean['total_sales'] > min_sales]

    # ── 2. Verificação de dados suficientes ────────────────────────
    if df_clean.empty or len(df_clean) < 10:
        fig = go.Figure()
        fig.add_annotation(
            text="Dados insuficientes para análise de threshold (poucos jogos com nota e vendas)",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(height=500)
        return fig

    # ── 3. Encontrar o threshold ótimo ────────────────────────────
    best_score = None
    best_diff = -1
    # Usar notas inteiras de 1 a 10
    for score in range(1, 11):
        above = df_clean[df_clean['critic_score'] >= score]['total_sales']
        below = df_clean[df_clean['critic_score'] < score]['total_sales']
        if len(above) >= 5 and len(below) >= 5:
            diff = above.mean() - below.mean()
            if diff > best_diff:
                best_diff = diff
                best_score = score

    # Fallback seguro: se nenhum threshold atender ao critério, usa a mediana
    if best_score is None:
        # A mediana nunca será NaN porque df_clean não é vazio e critic_score não possui NaN
        median_val = df_clean['critic_score'].median()
        # Se por algum motivo median_val for NaN, usa 7 como valor padrão
        if pd.isna(median_val):
            median_val = 7.0
        best_score = int(median_val)

    threshold = best_score

    # ── 4. Métricas dos grupos ────────────────────────────────────
    above_mask = df_clean['critic_score'] >= threshold
    below_mask = ~above_mask

    mean_above = df_clean.loc[above_mask, 'total_sales'].mean()
    mean_below = df_clean.loc[below_mask, 'total_sales'].mean()
    count_above = above_mask.sum()
    count_below = below_mask.sum()
    uplift = mean_above / mean_below if mean_below > 0 else float('inf')

    # ── 5. Curva de vendas médias por nota ────────────────────────
    score_means = (
        df_clean.groupby('critic_score')['total_sales']
        .mean()
        .reset_index()
    )

    # Caso score_means esteja vazio (não deve acontecer, mas por segurança)
    if score_means.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Não foi possível gerar a curva de vendas médias",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(height=500)
        return fig

    # ── 6. Construir gráfico ──────────────────────────────────────
    fig = go.Figure()

    # Curva principal
    fig.add_trace(go.Scatter(
        x=score_means['critic_score'],
        y=score_means['total_sales'],
        mode='lines+markers',
        name='Vendas Médias por Nota',
        marker=dict(color='royalblue', size=8),
        line=dict(width=2),
        hovertemplate='Nota: %{x}<br>Venda Média: %{y:.2f}M<extra></extra>'
    ))

    # Linha vertical no threshold
    fig.add_vline(
        x=threshold,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Threshold = {threshold}",
        annotation_position="top left",
        annotation_font_color="red"
    )

    # Preencher área acima do threshold (opcional, dá destaque visual)
    fig.add_vrect(
        x0=threshold, x1=10,
        fillcolor="rgba(0,200,0,0.08)",
        line_width=0
    )

    # ── 7. Anotação com KPIs ──────────────────────────────────────
    kpi_text = (f"<b>Threshold ótimo:</b> {threshold}<br>"
                f"<b>Vendas médias acima:</b> {mean_above:.2f}M<br>"
                f"<b>Vendas médias abaixo:</b> {mean_below:.2f}M<br>"
                f"<b>Uplift (vezes):</b> {uplift:.1f}x")
    fig.add_annotation(
        text=kpi_text,
        x=0.99, y=0.99, xref='paper', yref='paper',
        showarrow=False,
        font=dict(size=13, color='white'),
        bgcolor='rgba(0,0,0,0)',
        bordercolor='gray',
        borderwidth=1,
        xanchor='right',
        yanchor='top'
    )

    # ── 8. Layout ──────────────────────────────────────────────────
    fig.update_layout(
        title='Score Threshold: Nota Mínima para o Salto de Vendas',
        xaxis_title='Nota da Crítica',
        yaxis_title='Vendas Médias (milhões)',
        height=500,
        width=800,
        margin=dict(t=50, b=50)
    )

    return fig

#Função 3 - Ticket por Ponto de Score (Venda por Avaliação)
def ticket_per_score_holdings(df1, min_sales=0.0):
    """
    Calcula o Ticket por Ponto de Score (Vendas por Avaliação) por holding
    desenvolvedora e exibe um gráfico de barras horizontal com linha de
    referência da média global.

    Responde às perguntas:
    "Qual holding extrai mais receita por cada ponto de qualidade entregue?"
    "Existe alguma holding monetizando além do que sua qualidade justifica?"
    "Quais holdings entregam qualidade mas não convertem em volume de vendas?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com dataset_clean() aplicado.
        Deve conter as colunas 'critic_score', 'total_sales',
        'holdings_developer' e 'title'.
    min_sales : float, opcional (padrão=0.0)
        Filtro mínimo de vendas em milhões para considerar o jogo na análise.
        Use 0.0 para todos os jogos ou 0.5/1.0 para focar em jogos com
        relevância comercial.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Gráfico de barras horizontal com o Ticket por Ponto de Score por
        holding desenvolvedora. Barras verdes = acima da média global,
        vermelhas = abaixo. Linha tracejada indica a média global do KPI.
    """
    
    # ── 1. Limpeza ──────────────────────────────────────────────────────────────
    df_clean = (
        df1.dropna(subset=['critic_score', 'total_sales', 'holdings_developer'])
           .loc[lambda d: (d['critic_score'] > 0) & (d['total_sales'] > min_sales)]
           .pipe(lambda d: d[d['holdings_developer'].str.strip() != ''])
    )

    # ── 2. Cálculo do KPI por holding ───────────────────────────────────────────
    ticket_score = (
        df_clean.groupby('holdings_developer')
        .agg(
            total_sales   = ('total_sales',   'sum'),
            sum_score     = ('critic_score',  'sum'),
            avg_score     = ('critic_score',  'mean'),
            unique_titles = ('title',         'nunique'),
        )
        .reset_index()
    )

    # Filtra holdings com títulos avaliados suficientes
    MIN_TITLES = 5
    ticket_score = ticket_score[ticket_score['unique_titles'] >= MIN_TITLES]

    # ── 3. Cálculo do indicador principal ───────────────────────────────────────
    ticket_score['ticket_per_score'] = (
        ticket_score['total_sales'] / ticket_score['sum_score']
    ).round(4)

    ticket_score = ticket_score.sort_values('ticket_per_score', ascending=True)

    # ── 4. Média global do indicador ────────────────────────────────────────────
    global_avg = (
        df_clean['total_sales'].sum() / df_clean['critic_score'].sum()
    ).round(4)

    # ── 5. Cor conforme posição em relação à média global ───────────────────────
    ticket_score['color'] = ticket_score['ticket_per_score'].apply(
        lambda x: '#2ECC71' if x >= global_avg else '#E74C3C'
    )

    # ── 6. Gráfico ──────────────────────────────────────────────────────────────
    fig = go.Figure(go.Bar(
        x=ticket_score['ticket_per_score'],
        y=ticket_score['holdings_developer'],
        orientation='h',
        marker_color=ticket_score['color'],
        cliponaxis=False,
        text=ticket_score['ticket_per_score'].apply(lambda x: f'{x:.4f}M'),
        textposition='outside',
        customdata=ticket_score[['total_sales', 'avg_score', 'unique_titles', 'sum_score']],
        hovertemplate=(
            '<b>%{y}</b><br>'
            'Ticket por Score: %{x:.4f}M<br>'
            'Vendas totais: %{customdata[0]:.2f}M<br>'
            'Score médio: %{customdata[1]:.2f}<br>'
            'Soma de scores: %{customdata[3]:.0f}<br>'
            'Títulos avaliados: %{customdata[2]}'
            '<extra></extra>'
        ),
    ))

    # ── Linha de referência ────────────────────────────────────────────────────
    fig.add_vline(
        x=global_avg,
        line=dict(color='gray', width=2, dash='dash'),
        annotation_text=f'Média global: {global_avg:.4f}M',
        annotation_font=dict(size=12, color='black'),
        annotation_xanchor='left',
    )

    # ── 7. Layout ───────────────────────────────────────────────────────────────
    fig.update_layout(
        title=dict(
            text='Ticket por Ponto de Score — Eficiência Financeira por Holding Desenvolvedora<br>'
                 '<sup>Vendas totais ÷ soma dos pontos de critic_score | Verde = acima da média global</sup>',
            font=dict(size=18),
            x=0.01,
        ),
        xaxis=dict(
            title='Vendas por Ponto de Score (M)',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.06)',
            range=[0, ticket_score['ticket_per_score'].max() * 1.15],
        ),
        yaxis=dict(title=''),
        height=max(400, len(ticket_score) * 32),
        margin=dict(t=70, l=10, r=100, b=40),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig

#Função 4 - Excelência Regional de Crítica por Desenvolvedores
def regional_excelence(df1):
    """
    Gera um mapa coroplético com a média do critic_score por país de origem
    dos desenvolvedores.

    Responde à pergunta:
    "Quais países produzem os jogos mais bem avaliados pela crítica?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame limpo, contendo as colunas 'critic_score', 'country_developer',
        'clean_name_developer' e 'title'.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Mapa coroplético com a média do critic_score e quantidade de
        desenvolvedores únicos por país.
    """
    # ── 1. Limpeza ────────────────────────────────────────────────────────────
    df_clean = (
        df1.dropna(subset=['critic_score', 'country_developer'])
           .loc[lambda d: d['critic_score'] > 0]
           .pipe(lambda d: d[d['country_developer'].str.strip() != ''])
           .copy()
    )

    # ── 2. Agrupamento por país ───────────────────────────────────────────────
    quality_by_country = (
        df_clean.groupby('country_developer')
        .agg(
            avg_critic  = ('critic_score',          'mean'),
            unique_devs = ('clean_name_developer',  'nunique'),
            total_titles= ('title',                 'nunique'),
        )
        .round(2)
        .reset_index()
    )

    # Filtra países com amostra mínima para evitar médias instáveis
    MIN_DEVS = 5
    quality_by_country = quality_by_country[quality_by_country['unique_devs'] >= MIN_DEVS]

    # ── 3. Mapa coroplético ───────────────────────────────────────────────────
    fig = px.choropleth(
        quality_by_country,
        locations='country_developer',
        color='avg_critic',
        hover_data={
            'avg_critic':   ':.2f',
            'unique_devs':  True,
            'total_titles': True,
        },
        title='Excelência Regional: Nota Média dos Jogos por País de Origem',
        color_continuous_scale='RdYlGn',
        labels={
            'country_developer': 'País',
            'avg_critic':        'Média do Critic Score',
            'unique_devs':       'Desenvolvedores Únicos',
            'total_titles':      'Títulos Desenvolvidos',
        }
    )

    # ── 4. Ajustes visuais ────────────────────────────────────────────────────
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor="LightGray",
            projection_type='equirectangular',
            bgcolor='rgba(0,0,0,0)',
            showocean=False,
            showlakes=False,
        ),
        margin=dict(r=0, t=40, l=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        coloraxis_colorbar=dict(
            title="Média do Critic Score",
            tickvals=[quality_by_country['avg_critic'].min(), quality_by_country['avg_critic'].max()],
            ticktext=["Baixa", "Alta"],
        ),
    )

    return fig

#Função 5 - Data Reliability (% de Jogos com Critic Score Preenchido)
def data_reliability(df1):
    """
    Gera um Gauge Chart com o percentual de jogos que possuem critic_score preenchido.

    Mede a confiabilidade dos dados de avaliação crítica do dataset —
    quanto maior o percentual, mais representativas são as análises
    baseadas em critic_score.

    Responde à pergunta:
    "Qual a cobertura de avaliações críticas no dataset?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com dataset_clean() aplicado.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Gauge Chart com o percentual de cobertura do critic_score.
    """

    # ── 1. Cálculo da cobertura ───────────────────────────────────────────────
    critic_score_total = len(df1['critic_score'])
    critic_score_without_nan = df1['critic_score'].count()

    pct_critic_score_info = round(
        (critic_score_without_nan / critic_score_total) * 100, 1
    )

    # ── 2. Define cor do gauge por nível de cobertura ─────────────────────────
    if pct_critic_score_info >= 75:
        bar_color = '#2ECC71'    # verde — cobertura alta
    elif pct_critic_score_info >= 50:
        bar_color = '#F39C12'    # amarelo — cobertura moderada
    else:
        bar_color = '#E74C3C'    # vermelho — cobertura baixa

    # ── 3. Gauge Chart ────────────────────────────────────────────────────────
    fig = go.Figure(go.Indicator(
        mode='gauge+number+delta',
        value=pct_critic_score_info,
        number=dict(suffix='%', font=dict(size=36)),
        delta=dict(
            reference=75,                            # referência: 75% como meta mínima
            suffix='%',
            increasing=dict(color='#2ECC71'),
            decreasing=dict(color='#E74C3C'),
        ),
        gauge=dict(
            axis=dict(
                range=[0, 100],
                ticksuffix='%',
                tickwidth=1,
            ),
            bar=dict(color=bar_color, thickness=0.3),
            bgcolor='rgba(0,0,0,0)',
            steps=[
                dict(range=[0,  50], color='rgba(231, 76, 60,  0.15)'),   # vermelho suave
                dict(range=[50, 75], color='rgba(243,156, 18,  0.15)'),   # amarelo suave
                dict(range=[75,100], color='rgba( 46,204,113,  0.15)'),   # verde suave
            ],
            threshold=dict(
                line=dict(color='white', width=2),
                thickness=0.75,
                value=75,                            # linha de meta em 75%
            ),
        ),
        title=dict(
            text=(
                'Cobertura de Critic Score<br>'
                f'<span style="font-size:13px">'
                f'{critic_score_without_nan:,} avaliados de {critic_score_total:,} jogos'
                f'</span>'
            ),
            font=dict(size=18),
        ),
    ))

    fig.update_layout(
        height=350,
        margin=dict(t=80, l=40, r=40, b=20),
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
st.title ('⭐ Qualidade vs. Vendas - Predictive Validity (ROI)')
st.markdown("""- Métricas relacionadas a qualidade dos jogos vendidos pela industria e o comportamento 
do mercado mundial baseado nas notas da critica """)

#Call the Functions
fig_coor_between_sales_critic, fig_marginal_gain = correlation_beteween_score_sales(df1)    # <- Função 1 - Correlação entre Qualidade do Jogo e o Número de Vendas
fig_hype_premium = plot_hype_premium(df1, min_sales=0.5)                                    # <- Função 2 - Matriz de Hype vs. Pérolas
fig_mean_ticket_holding = ticket_per_score_holdings(df1, min_sales=0.5)                     # <- Função 3 - Ticket por Ponto de Score (Venda por Avaliação)
fig_regional_devs_score = regional_excelence(df1)                                           # <- Função 4 - Excelência Regional de Crítica por Desenvolvedores
fig_confiability_critic = data_reliability(df1)                                             # <- Função 5 - Data Reliability (% de Jogos com Critic Score Preenchido)

st.divider()

#Create KPIs In Page

st.markdown("### Qualidade do Critic Score do Dataset")
with st.container():
        st.plotly_chart(fig_confiability_critic, width='stretch')

tab1, tab2 = st.tabs(['Qualidade das Vendas Por Jogos', 'Qualidade das Vendas por Holdings'])

with tab1:
    with st.container():
        st.markdown("### Relação entre a Qualidade do Jogo e o Número de Vendas")
        st.plotly_chart(fig_coor_between_sales_critic, width='stretch')
        if fig_marginal_gain:
            st.plotly_chart(fig_marginal_gain, width='stretch')
        st.plotly_chart(fig_hype_premium, width='stretch')

    st.divider()

with tab2:
    with st.container():
        st.markdown("### Relação entre a Qualidade da Holding e o Número de Vendas")
        st.plotly_chart(fig_mean_ticket_holding, width='stretch')
    
    st.divider()
    
    with st.container():
        st.markdown("### Qualidade da produção de jogos segundo o Critic Score")
        st.plotly_chart(fig_regional_devs_score, width='stretch')