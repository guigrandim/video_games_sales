import streamlit as st
import plotly.graph_objects as go
from utils.data_loader import dataset_clean
from utils.sidebar import render_sidebar_rodape
from utils.launch_recommendation import compute_genre_scores, get_current_gen_df

st.set_page_config(
    page_title='Launch Recommendation',
    page_icon='🏆',
    layout='wide',
)

render_sidebar_rodape()


def render_kpi_cards(df_scores):
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
    fig.update_layout(
        title=title,
        xaxis=dict(title='Score (0–100)', range=[0, 100]),
        height=420,
        template='plotly_dark',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=10, r=10, t=60, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_detail_table(df_scores):
    pass  # implemented in Task 5


# ── Main layout ───────────────────────────────────────────────────────────────
st.title('🏆 Launch Recommendation')
st.markdown('Síntese executiva: score de oportunidade e risco por gênero de jogo, derivado das 6 dimensões de análise do dashboard.')

df = dataset_clean().copy()
df_hist = compute_genre_scores(df)

render_kpi_cards(df_hist)

st.divider()
st.subheader('📊 Benchmark Histórico — Todas as Gerações')
render_ranking_chart(df_hist, 'Ranking por Oportunidade vs Risco — Histórico Completo')
