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

st.set_page_config(page_title = 'Predictive Validity (ROI)', page_icon = '⭐', layout = 'wide')

#===================================
# Functions
#===================================
#Função 1 - Correlação entre Qualidade do Jogo e o Número de Vendas
def correlation_beteween_score_sales(df1):
    """
    Gera um gráfico de dispersão com linha de tendência entre a nota da crítica (critic_score)
    e o total de vendas (total_sales), utilizando regressão linear para destacar a correlação.

    Agrupa as vendas totais por nota da crítica (soma), mantendo apenas jogos com vendas
    positivas e avaliação válida.

    Responde à pergunta:
    "Existe uma relação positiva entre a nota da crítica e o sucesso comercial dos jogos?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame contendo as colunas 'critic_score' e 'total_sales'.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Gráfico de dispersão com pontos representando a soma das vendas por nota da crítica
        e linha de tendência (regressão linear) exibindo a equação da reta.
    """
    # ── Limpeza dos dados ──────────────────────────────────────────
    
    df_clean_score_sales = df1.loc[df1['total_sales'] > 0].dropna(subset=['critic_score'])
    
    # ── Agrupamento dos Dados ──────────────────────────────────────────
    
    clean_score_sales = (
        df_clean_score_sales.groupby('critic_score')['total_sales']
        .sum()
        .reset_index()
    )
    
    x = clean_score_sales['critic_score'].values
    y = clean_score_sales['total_sales'].values

    # ── Regressão linear com numpy ────────────────────────────────
    m, b = np.polyfit(x, y, 1)
    x_line = np.linspace(x.min(), x.max(), 100)
    y_line = m * x_line + b

    # ── Gráfico ───────────────────────────────────────────────────
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode='markers',
        name='Dados',
        marker=dict(size=8, opacity=0.7, color='steelblue'),
        hovertemplate='Nota: %{x}<br>Vendas: %{y:.2f}M<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=x_line, y=y_line,
        mode='lines',
        name=f'Tendência (y = {m:.3f}x + {b:.2f})',
        line=dict(color='red', width=2)
    ))

    fig.update_layout(
        title='Relação entre Nota da Crítica e Vendas Totais (Soma por Nota)',
        xaxis_title='Nota da Crítica',
        yaxis_title='Vendas Totais (milhões)',
        height=500,
        width=700,
        margin=dict(t=50, b=50)
    )

    return fig

# Função 2 - Matriz de Hype vs. Pérolas
def plot_hype_premium(df, min_sales=0.0):
    """
    Gera um gráfico de quadrantes (scatter plot) que cruza a nota da crítica
    com as vendas totais, dividindo o espaço por medianas para destacar quatro perfis:
    - Alta Nota / Alta Venda (sucesso de crítica e público)
    - Baixa Nota / Alta Venda (popular apesar das críticas)
    - Baixa Nota / Baixa Venda (fracasso)
    - Alta Nota / Baixa Venda (aclamado, mas pouco vendido)

    Responde à pergunta:
    "Quais jogos são superestimados ou subestimados? Onde estão os outliers comerciais?"

    A legenda inclui a quantidade de jogos em cada quadrante.

    Parâmetros
    ----------
    df : pd.DataFrame
        Deve conter as colunas 'critic_score' e 'total_sales', além de 'title' e 'plataform'
        para identificação no hover.
    min_sales : float, opcional (padrão=0.0)
        Valor mínimo de total_sales (em milhões) para incluir o jogo na análise.
        Use 0.0 para todos os jogos com vendas > 0, ou 0.5/1.0 para focar em jogos com
        relevância comercial.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Gráfico de dispersão com 4 quadrantes, linhas de referência e contagens na legenda.
    """
    # ── 1. Limpeza dos dados ──────────────────────────────────────
    df_clean = df.dropna(subset=['critic_score']).copy()
    df_clean = df_clean[df_clean['total_sales'] > min_sales]

    # ── 2. Cálculo das medianas ────────────────────────────────────
    median_score = df_clean['critic_score'].median()
    median_sales = df_clean['total_sales'].median()

    # ── 3. Classificação dos quadrantes ────────────────────────────
    def quadrant(row):
        if row['critic_score'] >= median_score and row['total_sales'] >= median_sales:
            return 'Alta Nota, Alta Venda'
        elif row['critic_score'] < median_score and row['total_sales'] >= median_sales:
            return 'Baixa Nota, Alta Venda'
        elif row['critic_score'] < median_score and row['total_sales'] < median_sales:
            return 'Baixa Nota, Baixa Venda'
        else:
            return 'Alta Nota, Baixa Venda'

    df_clean['quadrant'] = df_clean.apply(quadrant, axis=1)

    # ── 4. Cores por quadrante ─────────────────────────────────────
    color_map = {
        'Alta Nota, Alta Venda': 'green',
        'Baixa Nota, Alta Venda': 'orange',
        'Baixa Nota, Baixa Venda': 'red',
        'Alta Nota, Baixa Venda': 'blue'
    }

    # ── 5. Construção do gráfico ───────────────────────────────────
    fig = go.Figure()

    for quad, color in color_map.items():
        subset = df_clean[df_clean['quadrant'] == quad]
        count = len(subset)
        fig.add_trace(go.Scatter(
            x=subset['critic_score'],
            y=subset['total_sales'],
            mode='markers',
            name=f'{quad} ({count})',   # ← contagem incluída na legenda
            marker=dict(color=color, size=7, opacity=0.6),
            text=subset['title'] + '<br>' + subset['plataform'],
            hovertemplate='%{text}<br>Nota: %{x}<br>Vendas: %{y:.2f}M<extra></extra>'
        ))

    # ── 6. Linhas de referência ────────────────────────────────────
    fig.add_hline(y=median_sales, line_dash="dash", line_color="grey",
                  annotation_text=f"Mediana Vendas: {median_sales:.2f}M",
                  annotation_position="bottom right")
    fig.add_vline(x=median_score, line_dash="dash", line_color="grey",
                  annotation_text=f"Mediana Nota: {median_score:.1f}",
                  annotation_position="top left")

    # ── 7. Layout ──────────────────────────────────────────────────
    fig.update_layout(
        title=f'Quadrantes: Nota da Crítica vs. Vendas Totais (min {min_sales}M)',
        xaxis_title='Nota da Crítica',
        yaxis_title='Vendas Totais (milhões)',
        yaxis_type='log',
        height=600,
        width=800,
        margin=dict(t=50, b=50)
    )

    return fig

#Função 3 - Valor Exponencial de Venda por Critic Score
def score_threshold_analysis(df, min_sales=0.0):
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

    # ── 2. Encontrar o threshold ótimo ────────────────────────────
    best_score = None
    best_diff = -1
    for score in range(1, 10):
        above = df_clean[df_clean['critic_score'] >= score]['total_sales'].mean()
        below = df_clean[df_clean['critic_score'] < score]['total_sales'].mean()
        if pd.notna(above) and pd.notna(below):
            diff = above - below
            if diff > best_diff:
                best_diff = diff
                best_score = score

    # Fallback
    if best_score is None:
        best_score = 7

    threshold = best_score

    # ── 3. Métricas dos grupos ────────────────────────────────────
    above_mask = df_clean['critic_score'] >= threshold
    below_mask = ~above_mask
    mean_above = df_clean.loc[above_mask, 'total_sales'].mean()
    mean_below = df_clean.loc[below_mask, 'total_sales'].mean()
    uplift = mean_above / mean_below if mean_below > 0 else float('inf')

    # ── 4. Curva de vendas médias por nota ────────────────────────
    score_means = df_clean.groupby('critic_score')['total_sales'].mean().reset_index()

    # ── 5. Construir gráfico ──────────────────────────────────────
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

    # ── 6. Anotação com KPIs ──────────────────────────────────────
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

    # ── 7. Layout ──────────────────────────────────────────────────
    fig.update_layout(
        title='Score Threshold: Nota Mínima para o Salto de Vendas',
        xaxis_title='Nota da Crítica',
        yaxis_title='Vendas Médias (milhões)',
        height=500,
        width=800,
        margin=dict(t=50, b=50)
    )

    return fig

#Função 4 - Ticket por Ponto de Score (Venda por Avaliação)
def ticket_per_score_holdings(df1, min_sales=0.0):
    """
    Calcula o Ticket por Ponto de Score (Venda por Avaliação) por holding desenvolvedora.

    Métrica: total_sales / soma de critic_score dos jogos avaliados.
    Mede a eficiência financeira — quanto de receita cada ponto de qualidade
    gera para a holding. Holdings com ticket alto e score baixo monetizam
    além da qualidade; holdings com score alto e ticket baixo entregam
    qualidade sem converter em vendas.

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com dataset_clean() aplicado.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Gráfico de barras horizontal com o Ticket por Ponto de Score por holding,
        linha de média global e cor diferenciando holdings acima/abaixo da média.
    """

    # ── 1. Limpeza ───────────────────────────────────────────────────────────────
    df_clean = (
        df1.dropna(subset=['critic_score', 'total_sales', 'holdings_developer'])
        .loc[lambda d: (d['critic_score'] > 0) & (d['total_sales'] > min_sales)]
        .pipe(lambda d: d[d['holdings_developer'].str.strip() != ''])
    )

    # ── 2. Cálculo do KPI por holding ────────────────────────────────────────────
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
    ticket_score = ticket_score[ticket_score['unique_titles'] >= 5]

    # KPI: total_sales / soma dos pontos de critic_score
    ticket_score['ticket_per_score'] = (
        ticket_score['total_sales'] / ticket_score['sum_score']
    ).round(4)

    ticket_score = ticket_score.sort_values('ticket_per_score', ascending=True)

    # ── 3. Média global do KPI ───────────────────────────────────────────────────
    global_avg = (
        df_clean['total_sales'].sum() / df_clean['critic_score'].sum()
    ).round(4)

    # ── 4. Cor: acima ou abaixo da média global ──────────────────────────────────
    ticket_score['color'] = ticket_score['ticket_per_score'].apply(
        lambda x: '#2ECC71' if x >= global_avg else '#E74C3C'
    )

    # ── 5. Gráfico ───────────────────────────────────────────────────────────────
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

    fig.add_vline(
        x=global_avg,
        line=dict(color='white', width=1.5, dash='dash'),
        annotation_text=f'Média global: {global_avg:.4f}M',
        annotation_font=dict(size=11, color='white'),
        annotation_xanchor='left',
    )

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
            range=[0, ticket_score['ticket_per_score'].max() * 1.2],
        ),
        yaxis=dict(title='', categoryorder='total ascending'),
        height=max(400, len(ticket_score) * 32),
        margin=dict(t=70, l=10, r=100, b=40),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig

#Função 5 - Excelência Regional de Crítica por Desenvolvedores
def regional_excelence(df1):
    """
    Gera um mapa coroplético com a média do critic_score por país de origem
    dos desenvolvedores.

    Responde à pergunta:
    "Quais países produzem os jogos mais bem avaliados pela crítica?"

    Parâmetros
    ----------
    df1 : pd.DataFrame
        DataFrame video_game_sales.csv com dataset_clean() aplicado.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Mapa coroplético com a média do critic_score e quantidade de
        desenvolvedores únicos por país.
    """

    # ── 1. Limpeza ────────────────────────────────────────────────────────────
    df_clean = (
        df1.dropna(subset=['critic_score', 'country_developer'])  # ← faltava vírgula
        .loc[lambda d: d['critic_score'] > 0]
        .pipe(lambda d: d[d['country_developer'].str.strip() != ''])
    )

    # ── 2. Agrupamento por país ───────────────────────────────────────────────
    quality_by_country = (
        df_clean.groupby('country_developer')
        .agg(
            avg_critic  = ('critic_score',          'mean'),
            unique_devs = ('clean_name_developer',  'nunique'),
            total_titles= ('title',                 'nunique'),  # contexto adicional
        )
        .round(2)
        .reset_index()
    )

    # Filtra países com amostra mínima para evitar distorção
    quality_by_country = quality_by_country[quality_by_country['unique_devs'] >= 5]

    # ── 3. Figura ─────────────────────────────────────────────────────────────
    fig = px.choropleth(
        quality_by_country,
        locations='country_developer',
        color='avg_critic',                         # ← era 'critic_score' (não existe no df agregado)
        hover_data={
            'avg_critic':   True,
            'unique_devs':  True,
            'total_titles': True,
        },
        title='Qualidade dos Desenvolvedores no Planeta',
        color_continuous_scale='RdYlGn',
        labels={
            'country_developer': 'País',
            'avg_critic':        'Média do Critic Score',
            'unique_devs':       'Desenvolvedores Únicos',
            'total_titles':      'Títulos Desenvolvidos',
        }
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

#Função 6 - Data Reliability (% de Jogos com Critic Score Preenchido)
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
st.title ('⭐ Qualidade vs. Lucro - Predictive Validity (ROI)')

#Call the Functions
fig_coor_between_sales_critic = correlation_beteween_score_sales(df1)                   # <- Função 1 - Correlação entre Qualidade do Jogo e o Número de Vendas
fig_hype_premium = plot_hype_premium(df1, min_sales=0.5)                                # <- Função 2 - Matriz de Hype vs. Pérolas
fig_treshold_score = score_threshold_analysis(df1, min_sales=0.5)                       # <- Função 3 - Valor Exponencial de Venda por Critic Score
fig_mean_ticket_holding = ticket_per_score_holdings(df1, min_sales=0.5)                 # <- Função 4 - Ticket por Ponto de Score (Venda por Avaliação)
fig_regional_devs_score = regional_excelence(df1)                                       # <- Função 5 - Excelência Regional de Crítica por Desenvolvedores
fig_confiability_critic = data_reliability(df1)                                         # <- Função 6 - Data Reliability (% de Jogos com Critic Score Preenchido)


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
        st.plotly_chart(fig_hype_premium, width='stretch')
        st.plotly_chart(fig_treshold_score, width='stretch')

    st.divider()

with tab2:
    with st.container():
        st.markdown("### Relação entre a Qualidade da Holding e o Número de Vendas")
        st.plotly_chart(fig_mean_ticket_holding, width='stretch')
    
    st.divider()
    
    with st.container():
        st.markdown("### Qualidade da produção de jogos segundo o Critic Score")
        st.plotly_chart(fig_regional_devs_score, width='stretch')