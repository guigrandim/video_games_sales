import streamlit as st
import pandas as pd
from utils.data_loader import dataset_clean
from pathlib import Path

def render_sidebar_rodape() -> None:
    """
    Renderiza apenas o rodapé da barra lateral:
    logo secundária, nome do autor e links externos.
    """
    base_dir   = Path(__file__).parents[1]
    logo2_path = base_dir / 'assets' / 'img' / 'logo2.png'

    with st.sidebar:
        if logo2_path.exists():
            st.image(str(logo2_path), width=200)
        else:
            st.warning('Imagem não encontrada')

        st.markdown(
            "<p style='text-align: left;'>Owner: Guilherme Grandim</p>",
            unsafe_allow_html=True,
        )
        st.link_button("Visite meu LinkedIn ℹ️",   "https://www.linkedin.com/in/guilherme-grandim/")
        st.link_button("Visite meu portifólio 🗂️", "https://guigrandim.github.io/portifolio_projetos/")


def render_sidebar():
    """
    Renderiza a barra lateral do dashboard com filtros interativos e retorna
    o DataFrame filtrado junto com os valores selecionados em cada filtro.

    Filtros disponíveis
    -------------------
    - Geração       : selectbox — filtra por geração de console (ex: 7th Gen)
    - Empresa       : selectbox — filtra por fabricante (ex: Nintendo, Sony)
    - Gênero        : multiselect — filtra por gênero de jogo (ex: Action, Sports)
    - Console       : multiselect — filtra por console específico

    Os filtros de Geração e Empresa são aplicados antes de popular os
    multiselects de Gênero e Console, garantindo coerência entre os filtros.

    Parâmetros
    ----------
    Nenhum — carrega o dataset via dataset_clean() com cache do Streamlit.

    Retorna
    -------
    df1 : pd.DataFrame
        Dataset filtrado com todas as seleções aplicadas.
    filter_genero : list[str]
        Gêneros selecionados (todos se nenhum for desmarcado).
    filter_console : list[str]
        Consoles selecionados (todos se nenhum for desmarcado).
    filter_manufacture : str
        Fabricante selecionado ou "Todas as Empresas".
    filter_generation : str
        Geração selecionada ou "Todas as Gerações".
    """

    # ── Carregamento ──────────────────────────────────────────────────────────
    df1 = dataset_clean().copy()

    # ── Paths das imagens ─────────────────────────────────────────────────────
    base_dir   = Path(__file__).parents[1]
    logo1_path = base_dir / 'assets' / 'img' / 'logo1.png'
    logo2_path = base_dir / 'assets' / 'img' / 'logo2.png'

    # ── Opções dos filtros primários (antes de qualquer filtro) ───────────────
    MIN_MANUFACTURE_SALES = 0.5

    opcoes_generation  = ['Todas as Gerações'] + sorted(df1['generation'].unique().tolist())
    opcoes_manufacture = ['Todas as Empresas'] + (
        df1.groupby('manufacture')['total_sales']
        .sum()
        .loc[lambda s: s >= MIN_MANUFACTURE_SALES]
        .sort_values(ascending=False)
        .index.tolist()
    )

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:

        # Logo principal
        if logo1_path.exists():
            st.image(str(logo1_path))
        else:
            st.warning('Imagem não encontrada')

        st.divider()

        # Filtros primários
        filter_generation  = st.selectbox('Selecione a Geração', options=opcoes_generation,  index=0)
        filter_manufacture = st.selectbox('Selecione a Empresa', options=opcoes_manufacture, index=0)

        # Aplica filtros primários antes de popular os multiselects
        if filter_generation  != 'Todas as Gerações':
            df1 = df1[df1['generation']  == filter_generation]
        if filter_manufacture != 'Todas as Empresas':
            df1 = df1[df1['manufacture'] == filter_manufacture]

        # Opções dos filtros avançados — derivadas do df já filtrado
        opcoes_genero  = sorted(df1['genre'].unique().tolist())
        opcoes_console = (
            df1.groupby('console')['total_sales']
            .sum()
            .sort_values(ascending=False)
            .index.tolist()
        )

        with st.expander('Filtros Avançados'):
            filter_genero  = st.multiselect('Selecione o Gênero',  options=opcoes_genero,  default=opcoes_genero)
            filter_console = st.multiselect('Selecione o Console', options=opcoes_console, default=opcoes_console)

            # Garante que lista vazia não anula o filtro
            filter_genero  = filter_genero  if filter_genero  else opcoes_genero
            filter_console = filter_console if filter_console else opcoes_console

        st.divider()

        render_sidebar_rodape()

    # ── Aplica filtros avançados ──────────────────────────────────────────────
    df1 = df1[df1['genre'].isin(filter_genero)]
    df1 = df1[df1['console'].isin(filter_console)]

    return df1, filter_genero, filter_console, filter_manufacture, filter_generation