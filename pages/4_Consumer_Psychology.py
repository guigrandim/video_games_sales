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

st.set_page_config(page_title = 'Consumer Psychology', page_icon = '👥', layout = 'wide')

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
def sales_by_genre_heatmap(df1):
    
    filter_by_sales = df1[df1['total_sales'] >= 0.5]
    
    heatmap_data = (
        filter_by_sales.groupby('genre')
        .agg(
            na_sales = ('na_sales', 'sum'),
            jp_sales = ('jp_sales', 'sum'),
            pal_sales = ('pal_sales', 'sum'),
            other_sales = ('other_sales', 'sum')
        )
        .round(2)
    )
    
    heatmap_pivot = heatmap_data.T
    
    heatmap_norm = heatmap_pivot.div(heatmap_pivot.max(axis=1), axis=0)
    
    fig = px.imshow(
        heatmap_norm,
        zmin=0, zmax=1,
        title = 'Preferencia de Genero por Região (Escala Relativa por Linha)',
        labels = dict(color='Intensidade', x='Gênero', y='Região'),
        color_continuous_scale='RdYlGn',
        text_auto=True
    )
    fig.update_traces(text=heatmap_pivot.values, texttemplate="%{text}")
    fig.update_layout(height=600)
    
    return fig

#Função 2 - Rentabilidade por Genero e Por Critica e Avaliação Média de Cada Genero 
def profitability_per_genre_critic(df1):
    
    df_profitability_genre = df1.loc[df1['total_sales'] > 0]
    df_profitability_critic = df1.dropna(subset=['critic_score'])
    
    # ── Vendas médias por gênero ──────────────────────────────────────
    sales_per_title = (
        df_profitability_genre.groupby(['genre', 'title'])['total_sales']
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
    max_titles_sales = profitability_per_genre['total_titles'].max()
    profitability_per_genre['opacity'] = (
        0.4 + 0.6 * (profitability_per_genre['total_titles'] / max_titles_sales)
    ).round(3)

    # ── Crítica média por gênero ──────────────────────────────────────
    critic_per_title = (
        df_profitability_critic.groupby(['genre', 'title'])['critic_score']
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

    # ── Merge para o scatter ──────────────────────────────────────────
    genre_combined = profitability_per_genre.merge(
        critic_per_genre[['genre', 'mean_critic']],
        on='genre',
        how='inner'
    )

    # ── fig1: Rentabilidade por gênero ────────────────────────────────
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=profitability_per_genre['avg_sales'],
        y=profitability_per_genre['genre'],
        orientation='h',
        marker=dict(
            color=profitability_per_genre['total_titles'],
            colorscale='Blues',
            showscale=True,
            colorbar=dict(
                title=dict(text='Nº de<br>títulos', side='right'),
                thickness=12, len=0.5,
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
        title=dict(text='Rentabilidade por Gênero — Média de Vendas por Título',
                   font=dict(size=18), x=0.01),
        xaxis=dict(title='Média de vendas por título (M)', showgrid=True,
                   gridcolor='rgba(0,0,0,0.06)',
                   range=[0, profitability_per_genre['avg_sales'].max() * 1.35]),
        yaxis=dict(title='', categoryorder='total ascending'),
        height=max(400, len(profitability_per_genre) * 36),
        margin=dict(t=50, l=10, r=200, b=40),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
    )

    # ── fig2: Crítica média por gênero ────────────────────────────────
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=critic_per_genre['mean_critic'],
        y=critic_per_genre['genre'],
        orientation='h',
        marker=dict(
            color=critic_per_genre['total_titles'],
            colorscale='Greens',           # diferencia visualmente do fig1
            showscale=True,
            colorbar=dict(
                title=dict(text='Nº de<br>títulos', side='right'),
                thickness=12, len=0.5,
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
    fig2.update_layout(
        title=dict(text='Recepção Crítica por Gênero — Média de Pontuação',
                   font=dict(size=18), x=0.01),
        xaxis=dict(title='Pontuação média da crítica', showgrid=True,
                   gridcolor='rgba(0,0,0,0.06)',
                   range=[0, critic_per_genre['mean_critic'].max() * 1.35]),
        yaxis=dict(title='', categoryorder='total ascending'),
        height=max(400, len(critic_per_genre) * 36),
        margin=dict(t=50, l=10, r=200, b=40),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
    )

    # ── fig3: Scatter — Venda × Crítica por gênero ───────────────────
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=genre_combined['avg_sales'],
        y=genre_combined['mean_critic'],
        mode='markers+text',
        marker=dict(
            size=genre_combined['total_titles'],
            sizemode='area',
            sizeref=2. * genre_combined['total_titles'].max() / (40. ** 2),
            sizemin=6,
            color=genre_combined['avg_sales'],
            colorscale='Blues',
            showscale=False,
            line=dict(width=1, color='rgba(0,0,0,0.3)'),
        ),
        text=genre_combined['genre'],
        textposition='top center',
        customdata=genre_combined[['total_titles', 'avg_sales', 'mean_critic']],
        hovertemplate=(
            '<b>%{text}</b><br>'
            'Crítica média: %{x:.1f}<br>'
            'Média de vendas: %{y:.2f}M<br>'
            'Total de títulos: %{customdata[0]}'
            '<extra></extra>'
        ),
    ))
    fig3.update_layout(
        title=dict(text='Crítica vs. Vendas por Gênero',
                   font=dict(size=18), x=0.01),
        xaxis=dict(title='Pontuação média da crítica', showgrid=True,
                   gridcolor='rgba(0,0,0,0.06)'),
        yaxis=dict(title='Média de vendas por título (M)', showgrid=True,
                   gridcolor='rgba(0,0,0,0.06)'),
        height=500,
        margin=dict(t=50, l=60, r=40, b=60),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig1, fig2, fig3

#Função 3 - Caracterização dos Tipos e Qualidade dos Jogos
def size_quality_market_genre(df1):
    
    df_clean_quality_genre = df1.dropna(subset=['critic_score'])
    
    total_genres = df1['genre'].nunique()
    
    best_genre = (
        df_clean_quality_genre.groupby('genre')['critic_score']
        .mean()
        .idxmax()
    )
    
    best_genre_score = (
        df_clean_quality_genre.groupby('genre')['critic_score']
        .mean()
        .max()
    )
    
    return total_genres, best_genre, best_genre_score

#Função 4 - Migração de Popularidade
def genre_migration_by_generation(df1):
    
    # ── Limpeza dataframe ─────────────────────────────────────────────────────────
    
    df_gen = df1.loc[
        (df1['total_sales'] > 0) &
        (df1['generation'] != 'OtherUnknown') &
        (df1['genre'].notna())
    ]
    
    #Criação da Ordem das Gerações para inserir no grafico
    gen_order = df_gen['generation'].sort_values().unique()
    df_gen = df_gen[df_gen['generation'].isin(gen_order)]
    
    # ── Inicio do Tratamento ───────────────────────────────────────────────────────
    
    # Vendas por geração × gênero
    gen_genre = (
        df_gen.groupby(['generation', 'genre'])['total_sales']
        .sum()
        .reset_index()
    )
    
    # MarketShare por geração (% dento de cada geração)
    gen_genre['pct'] = (
        gen_genre.groupby('generation')['total_sales']
        .transform(lambda x: (x / x.sum() * 100).round(2))
    )
    
    # Ranking por geração
    gen_genre['rank'] = (
        gen_genre.groupby('generation')['total_sales']
        .rank(ascending=False, method='min')
        .astype(int)
    )
    
    # Filtra generos com mais relevância histórica
    top_genres = (
        gen_genre.groupby('genre')['total_sales']
        .sum()
        .nlargest(10)
        .index.tolist()
    )
    gen_genre = gen_genre[gen_genre['genre'].isin(top_genres)]
    
    # Pivoteia para Stacked Area
    pivot_area = gen_genre.pivot_table(
        index='generation', columns='genre', values='pct', aggfunc='sum'
    ).reindex(gen_order).fillna(0)
    
    #Pivoteia para Bump Chart
    pivot_bump = gen_genre.pivot_table(
        index='generation', columns='genre', values='rank', aggfunc='min'
    ).reindex(gen_order)
    
    # ── Inicio das Figuras ───────────────────────────────────────────────────
    
    # Bump Chart (Ranking de Popularidade)
    fig1 = go.Figure()

    for genre in pivot_bump.columns:
        color = genre_colors.get(genre, '#888888')
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
            text='Ranking de Popularidade de Gêneros por Geração',
            font=dict(size=18),
            x=0.01,
        ),
        yaxis=dict(
            autorange='reversed',
            tickvals=list(range(1, len(top_genres) + 1)),
            title='Ranking',
            gridcolor='rgba(0,0,0,0.06)',
        ),
        xaxis=dict(title='Geração de Console'),
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='left',
            x=0,
            font=dict(size=11),
        ),
        height=550,
        margin=dict(t=80, l=10, r=120, b=40),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    # Line Chart com % de market share por geração
    
    fig2 = go.Figure()

    for genre in pivot_area.columns:
        color = genre_colors.get(genre, '#888888')
        y_vals = pivot_area[genre].tolist()
        x_vals = pivot_area.index.tolist()

        # Identifica o pico do gênero para anotação
        peak_idx = pivot_area[genre].idxmax()
        peak_val = pivot_area[genre].max()

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

        # Marca o pico de cada gênero com uma estrela
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
        last_val = y_vals[-1]
        fig2.add_annotation(
            x=x_vals[-1],
            y=last_val,
            text=f'  {genre}',
            showarrow=False,
            xanchor='left',
            font=dict(size=10, color=color),
        )

    fig2.update_layout(
        title=dict(
            text='Evolução do Market Share de Gêneros por Geração',
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
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='left',
            x=0,
            font=dict(size=11),
        ),
        height=550,
        margin=dict(t=80, l=10, r=120, b=40),
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
st.title ('👥 Preferência de Gênero - Consumer Psychology')

#Call the Functions
fig_sales_genre_region = sales_by_genre_heatmap(df1)                                                            # <- Função 1 - Afinidade Regional (Vendas de Genero por Região)
fig_profit_per_genre, fig_critic_per_genre, fig_profit_critic_genre = profitability_per_genre_critic(df1)       # <- Função 2 - Rentabilidade por Genero e Por Critica e Avaliação Média de Cada Genero 
kpi_total_genre, kpi_best_genre, kpi_best_genre_score = size_quality_market_genre(df1)                          # <- Função 3 - Caracterização dos Tipos e Qualidade dos Jogos
fig_popularity_migration, fig_market_share_genre = genre_migration_by_generation(df1)                           # <- Função 4 - Migração de Popularidade e Market Share

st.divider()

#Create KPIs In Page

st.markdown("### Total de Generos no Mercado e Genero de maior qualidade")
col1, col2 = st.columns(2)
with st.container():
    with col1:
        st.metric("Totais de Generos no Mercado", kpi_total_genre)
    
    with col2:
        st.metric("Genero mais bem avaliado", kpi_best_genre, delta = f'{kpi_best_genre_score:.2f} critic score médio', delta_color="off")

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