"""
BrasCo - Gaming Ltd. | Dashboard Principal
==========================================
Ponto de entrada da aplicação Streamlit.
Define a navegação multi-página e renderiza o conteúdo da Home.

Autor: Guilherme Grandim
"""

#==================================
# Import Library
#==================================

import streamlit as st
from pathlib import Path
from utils.sidebar import render_sidebar_rodape

#==================================
# Configuration Page
#==================================

st.set_page_config(page_title="Home", page_icon="🏡", layout = 'wide')

# ==================================
# Caminhos dos Assets
# ==================================

base_dir = Path(__file__).parents[0]
img_dir = base_dir / "assets" / "img"

logo_banner = img_dir / "logo1.png"
fluxo_img = img_dir / "fluxo2.png"
logo_rodape = img_dir / "logo3.png"

# ==================================
# Páginas
# ==================================

def render_home() -> None:
    """
    Renderiza o conteúdo da página Home.
    Exibe banner, resumo do projeto, diagrama de fluxo e logo de rodapé.
    A sidebar exibe apenas o rodapé via render_sidebar_rodape().
    """
    render_sidebar_rodape()
    
    st.title("BrasCo - Gaming Ltd.")

    if logo_banner.exists():
        st.image(str(logo_banner), width=800)
    else:
        st.warning("Banner principal não encontrado.")

    st.divider()

    st.markdown("## Resumo do Projeto e Resultados")
    st.markdown("###### - Organização do Projeto, Navegação e Principais Resultados")

    if fluxo_img.exists():
        st.image(str(fluxo_img), use_container_width=True)
    else:
        st.warning("Imagem de fluxo não encontrada.")

    st.divider()

    if logo_rodape.exists():
        st.image(str(logo_rodape), width=800)
    else:
        st.warning("Logo de rodapé não encontrada.")


def build_navigation() -> st.navigation:
    """
    Constrói e retorna o objeto de navegação com todas as páginas do dashboard.

    Returns:
        st.navigation: Objeto de navegação configurado com as páginas do app.
    """
    home                     = st.Page(render_home, title="Main Page", icon="🏡")
    marketplace_overview     = st.Page("pages/1_Marketplace_Overview.py", title="MarketPlace - Visão Geral", icon="🌐")
    market_cycles            = st.Page("pages/2_Market_Cycles.py", title="Ciclos dos Mercados", icon="⏳")
    asset_efficiency         = st.Page("pages/3_Asset_Efficiency.py", title="Plataforma e Hardware",    icon="🎮")
    consumer_behavior        = st.Page("pages/4_Consumer_Behavior.py", title="Preferência de Gênero",    icon="👥")
    competitive_intelligence = st.Page("pages/5_Competitive_Intelligence.py", title="Holdings e Geopolítica",   icon="🏢")
    predictive_validity      = st.Page("pages/6_Predictive_Validity.py", title="Qualidade vs. Vendas", icon="⭐")

    return st.navigation([
        home,
        marketplace_overview,
        market_cycles,
        asset_efficiency,
        consumer_behavior,
        competitive_intelligence,
        predictive_validity,
    ])

# ==================================
# Entry Point
# ==================================

def main() -> None:
    """
    Função principal da aplicação.
    Inicializa a navegação e executa a página ativa.
    """
    pg = build_navigation()
    pg.run()


main()