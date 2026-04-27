import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Home", page_icon="🏡", layout = 'wide')

base_dir = Path(__file__).parents[0]
imagem_path1 = base_dir / "assets" / "img" / "logo1.png"
imagem_path2 = base_dir / "assets" / "img" / "logo2.png"
imagem_path3 = base_dir / "assets" / "img" / "logo3.png"
imagem_path4 = base_dir / "assets" / "img" / "fluxo2.png"

st.title("BrasCo - Gaming Ltd.")
if imagem_path1.exists():
    st.image(str(imagem_path1), width=800)
else:
    st.warning("Imagem não encontrada")

st.divider()
with st.sidebar:
        #Plot Logo BrasCo.
        if imagem_path2.exists():
            st.image(str(imagem_path2), width=250)
        else:
            st.warning("Imagem não encontrada")
        
        st.markdown(
            "<p style='text-align: center;'>Owner: Guilherme Grandim</p>",
            unsafe_allow_html=True,
        )
        st.link_button("Visite meu LinkedIn ℹ️", "https://www.linkedin.com/in/guilherme-grandim/")
        st.link_button("Visite meu portifólio 🗂️", "https://guigrandim.github.io/portifolio_projetos/")
        
        st.divider()


st.markdown("## Resumo do Projeto e Resultados")
if imagem_path1.exists():
    st.image(str(imagem_path4), width=10000)
else:
    st.warning("Imagem não encontrada")

st.divider()

if imagem_path1.exists():
    st.image(str(imagem_path3), width=800)
else:
    st.warning("Imagem não encontrada")