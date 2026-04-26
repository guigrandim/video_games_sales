import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Home", page_icon="🏡", layout = 'wide')

base_dir = Path(__file__).parents[0]
imagem_path1 = base_dir / "assets" / "img" / "logo1.png"
imagem_path2 = base_dir / "assets" / "img" / "logo2.png"

st.title("BrasCo - Gaming Ltd.")
if imagem_path1.exists():
    st.image(str(imagem_path1), width=800)
else:
    st.warning("Imagem não encontrada")

st.divider()
with st.sidebar:
        #Plot Logo BrasCo.
        if imagem_path2.exists():
            st.image(str(imagem_path2), width=300)
        else:
            st.warning("Imagem não encontrada")
        
        st.divider()


st.markdown(
    """
 ##### Esse dashboard foi construido para acompanhamento do mercado de video games e tomada de decisões estratégicas.

##### Como utilizar essa dashboard?
    - Pag 1:🏠 Home - Marketplace - Visão Geral (Marketplace Overview)
        - Métricas mostrando o tamanho do mercado e o comportamento geral de vendas
        
    - Pag 2:⏳ Evolução das Gerações - Ciclos de Mercado (Market Cycles)
        - Métricas apresentando o comportamento e a qualidade das vendas das empresas na indústria de forma temporal
        
    - Pag 3:🎮 Plataforma e Hardware - Eficiencia de Ativos (Asset Efficiency)
        - Métricas relacionadas a qualidade e quantidade de vendas das plataformas ao longo dos anos
        
    - Pag 4:👥 Preferência de Gênero - Comportamento do Consumidor (Consumer Behavior)
        - Métricas relacionadas ao comportamento dos clientes segmentado por genero e região de forma temporal
        
    - Pag 5:🏢 Holdings e Geopolítica - Inteligência Competitiva (Competitive Intelligence)
        - Métricas relacionadas ao comportamento da industria no desenvolvimento e publicação de jogos de forma temporal
        
    - Pag 6:⭐ Qualidade vs. Vendas - Predictive Validity (ROI)
        - Métricas relacionadas a qualidade dos jogos vendidos pela industria e o comportamento 
        do mercado mundial baseado nas notas da critica


- Autor: Guilherme Vinicius Moreira Grandim
    """)

with st.container():
    st.link_button("Visite meu LinkedIn ℹ️", "https://www.linkedin.com/in/guilherme-grandim/")
    st.link_button("Visite meu portifólio 🗂️", "https://guigrandim.github.io/portifolio_projetos/")
