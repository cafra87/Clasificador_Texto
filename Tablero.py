import streamlit as st

st.set_page_config(page_title="Clasificador de textos médicos", layout="wide")
col1, col2 = st.columns([1, 3])


with col1:
    st.markdown("## Clasificador de textos médicos")

    with st.container():
        st.markdown("""
        <div style="border:1px solid #ccc; border-radius:10px; padding:15px; margin-bottom:20px; box-shadow:2px 2px 5px rgba(0,0,0,0.1)">
            <h4 style="margin:0; color:#0a2c5f;">📋 Texto sencillo</h4>
            <ul>
                <li><a href="#">Texto sencillo 1</a></li>
                <li><a href="#">Texto sencillo 2</a></li>
                <li><a href="#">Texto sencillo 3</a></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with st.container():
        st.markdown("""
        <div style="border:1px solid #ccc; border-radius:10px; padding:15px; margin-bottom:20px; box-shadow:2px 2px 5px rgba(0,0,0,0.1)">
            <h4 style="margin:0; color:#0a2c5f;">💡 Texto técnico</h4>
            <ul>
                <li><a href="#">Texto técnico</a></li>
                <li><a href="#">Texto técnico</a></li>
                <li><a href="#">Texto técnico</a></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("**Texto clasificado como:**")
    clasificacion = st.text_input("", placeholder="(resultado aquí)")


    if st.button("🔎 Analizar", use_container_width=True):
        st.success("Clasificación ejecutada!")

with col2:

    st.markdown("""
        <div style="height:1000px; border:1px solid #aaa; border-radius:10px; margin-bottom:10px;">
        </div>
    """, unsafe_allow_html=True)

    user_text = st.text_input("Ingrese el texto")
