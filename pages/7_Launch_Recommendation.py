import streamlit as st
import plotly.graph_objects as go
from utils.data_loader import dataset_clean
from utils.sidebar import render_sidebar_rodape
from utils.launch_recommendation import compute_genre_scores

st.set_page_config(
    page_title='Launch Recommendation',
    page_icon='🏆',
    layout='wide',
)

render_sidebar_rodape()


def render_kpi_cards(df_scores):
    """
    Renderiza dois cards KPI destacando o gênero de maior oportunidade e o de maior risco.

    Exibe, lado a lado:
    - 🟢 Melhor Aposta: gênero com o maior opportunity_score
    - 🔴 Maior Risco: gênero com o maior risk_score

    Responde à pergunta:
    "Qual gênero oferece a melhor relação entre oportunidade e risco para um novo lançamento?"

    Parâmetros
    ----------
    df_scores : pd.DataFrame
        Saída de compute_genre_scores(). Deve conter 'genre', 'opportunity_score'
        e 'risk_score'.
    """
    best = df_scores.loc[df_scores['opportunity_score'].idxmax()]
    riskiest = df_scores.loc[df_scores['risk_score'].idxmax()]

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label='🟢 Melhor Aposta',
            value=best['genre'],
            delta=f"Oportunidade {best['opportunity_score']}/100",
        )
    with col2:
        st.metric(
            label='🔴 Maior Risco',
            value=riskiest['genre'],
            delta=f"Risco {riskiest['risk_score']}/100",
            delta_color='inverse',
        )


def render_ranking_chart(df_scores, title):
    """
    Gera um gráfico horizontal de barras + marcadores que posiciona cada gênero
    pelo seu score de oportunidade (barras verdes) e de risco (diamantes vermelhos).

    Os gêneros são ordenados de menor para maior opportunity_score no eixo Y,
    de forma que o melhor gênero aparece no topo. Ambas as séries compartilham
    o mesmo eixo X (0–100), permitindo comparação visual direta entre oportunidade
    e risco por gênero.

    Responde às perguntas:
    "Quais gêneros combinam alta oportunidade com baixo risco?"
    "Onde estão os gêneros com alto potencial mas alta volatilidade?"

    Parâmetros
    ----------
    df_scores : pd.DataFrame
        Saída de compute_genre_scores(). Deve conter 'genre', 'opportunity_score'
        e 'risk_score'.
    title : str
        Título exibido no cabeçalho do gráfico.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Gráfico com trace Bar (oportunidade) e trace Scatter (risco) sobre eixo
        compartilhado 0–100, renderizado via st.plotly_chart.
    """
    df_sorted = df_scores.sort_values('opportunity_score', ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_sorted['opportunity_score'],
        y=df_sorted['genre'],
        orientation='h',
        name='Oportunidade',
        marker_color='#2ecc71',
        opacity=0.85,
    ))
    fig.add_trace(go.Scatter(
        x=df_sorted['risk_score'],
        y=df_sorted['genre'],
        mode='markers',
        name='Risco',
        marker=dict(symbol='diamond', color='#e74c3c', size=12),
    ))
    height = max(280, len(df_sorted) * 30 + 80)
    fig.update_layout(
        title=title,
        xaxis=dict(title='Score (0–100)', range=[0, 100]),
        yaxis=dict(tickfont=dict(size=10)),
        height=height,
        template='plotly_dark',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=10, r=10, t=60, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_detail_table(df_scores):
    """
    Renderiza uma tabela de sub-métricas com uma linha por gênero, detalhando
    os fatores que compõem os scores de oportunidade e risco.

    Colunas exibidas: Gênero, Oportunidade, Risco, Melhor Plataforma
    e Nota Mínima sugerida (70º percentil
    do critic_score entre títulos acima da mediana de vendas do gênero).

    Linhas com cores alternadas (#1a1a2e / #16213e) para facilitar a leitura.
    Valores ausentes são exibidos como "—".

    Responde às perguntas:
    "Em qual plataforma e momento do ciclo devo lançar para maximizar vendas?"
    "Qual nota mínima de crítica é necessária para performar acima da mediana do gênero?"

    Parâmetros
    ----------
    df_scores : pd.DataFrame
        Saída de compute_genre_scores(). Deve conter 'genre', 'opportunity_score',
        'risk_score', 'best_platform', 'best_timing' e 'min_score'.

    Retorna
    -------
    fig : plotly.graph_objects.Figure
        Tabela estilizada renderizada via st.plotly_chart.
    """
    n = len(df_scores)
    row_colors = ['#1a1a2e' if i % 2 == 0 else '#16213e' for i in range(n)]

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Gênero</b>', '<b>Oportunidade</b>', '<b>Risco</b>',
                    '<b>Melhor Plataforma</b>', '<b>Nota Mínima</b>'],
            fill_color='#2c3e50',
            font=dict(color='white', size=13),
            align='left',
            height=32,
        ),
        cells=dict(
            values=[
                df_scores['genre'],
                df_scores['opportunity_score'],
                df_scores['risk_score'],
                df_scores['best_platform'].fillna('—'),
                df_scores['min_score'].fillna('—'),
            ],
            fill_color=[row_colors] * 5,
            font=dict(color='white', size=12),
            align='left',
            height=28,
        ),
    )])
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=min(60 + n * 30, 420))
    st.plotly_chart(fig, use_container_width=True)


# ── Constantes ────────────────────────────────────────────────────────────────
MIN_HIST = 20   # mínimo de títulos para aparecer no benchmark histórico
MIN_GEN  = 15   # mínimo de títulos por gênero para aparecer no benchmark por geração

# ── Main layout ───────────────────────────────────────────────────────────────
st.title('🏆 Launch Recommendation')
st.markdown('Síntese executiva: score de oportunidade e risco por gênero de jogo, derivado das 6 dimensões de análise do dashboard.')

df = dataset_clean().copy()
df_hist_all = compute_genre_scores(df)
df_hist = df_hist_all[df_hist_all['title_count'] >= MIN_HIST].reset_index(drop=True)

render_kpi_cards(df_hist)

st.divider()
st.subheader('📊 Benchmark Histórico — Todas as Gerações')
st.caption(f'Exibe apenas gêneros com pelo menos {MIN_HIST} títulos no dataset completo.')
render_ranking_chart(df_hist, 'Ranking por Oportunidade vs Risco — Histórico Completo')
render_detail_table(df_hist)

st.divider()
st.subheader('📊 Benchmark por Geração')
st.caption(f'Scores calculados independentemente por geração. Exibe apenas gêneros com pelo menos {MIN_GEN} títulos lançados na geração.')

gen_order = (
    df.groupby('generation')['start_year'].median()
    .sort_values()
    .index.tolist()
)

for gen in gen_order:
    df_gen_raw = df[df['generation'] == gen]
    eligible = df_gen_raw.groupby('genre')['total_sales'].count()
    df_gen_raw = df_gen_raw[df_gen_raw['genre'].isin(eligible[eligible >= MIN_GEN].index)]
    if df_gen_raw.empty:
        continue
    df_gen = compute_genre_scores(df_gen_raw)
    with st.expander(f'🎮 {gen}', expanded=(gen == gen_order[-1])):
        render_ranking_chart(df_gen, f'Ranking — {gen}')
        render_detail_table(df_gen)
