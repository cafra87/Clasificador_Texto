import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Clasificador de textos médicos", layout="wide")

if "contador_sencillo" not in st.session_state:
    st.session_state.contador_sencillo = 0
if "contador_tecnico" not in st.session_state:
    st.session_state.contador_tecnico = 0
if "resultado" not in st.session_state:
    st.session_state.resultado = "(sin clasificar)"
if "textos_sencillos" not in st.session_state:
    st.session_state.textos_sencillos = []
if "textos_tecnicos" not in st.session_state:
    st.session_state.textos_tecnicos = []


# Función para diferenciar la claasificación de texto técnico y texto sencillo

def clasificar_texto(texto):
    palabras_tecnicas = ["diagnóstico", "síntoma", "tratamiento", "patología", "clínico"]
    if any(palabra in texto.lower() for palabra in palabras_tecnicas):
        return "Texto técnico"
    else:
        return "Texto sencillo"

col1, col2 = st.columns([1, 3])

# Seccion 2 menú y contadores

with col1:
    st.markdown("## Clasificador de textos médicos")

    # Texto sencillo con contador
    st.markdown(f"""
    <div style="border:1px solid #ccc; border-radius:10px; padding:15px; margin-bottom:10px; 
                box-shadow:2px 2px 5px rgba(0,0,0,0.1); display:flex; justify-content:space-between; align-items:center;">
        <h4 style="margin:0; color:#0a2c5f;">📋 Texto sencillo</h4>
        <span style="font-size:18px; font-weight:bold; color:#0a2c5f;">{st.session_state.contador_sencillo}</span>
    </div>
    """, unsafe_allow_html=True)

    # Listado de textos sencillos
    for i, texto in enumerate(st.session_state.textos_sencillos, 1):
        with st.expander(f"Texto sencillo {i}"):
            st.write(texto)

    # Texto técnico con contador
    st.markdown(f"""
    <div style="border:1px solid #ccc; border-radius:10px; padding:15px; margin-top:20px; margin-bottom:10px; 
                box-shadow:2px 2px 5px rgba(0,0,0,0.1); display:flex; justify-content:space-between; align-items:center;">
        <h4 style="margin:0; color:#0a2c5f;">💡 Texto técnico</h4>
        <span style="font-size:18px; font-weight:bold; color:#0a2c5f;">{st.session_state.contador_tecnico}</span>
    </div>
    """, unsafe_allow_html=True)

    # Listado de textos técnicos
    for i, texto in enumerate(st.session_state.textos_tecnicos, 1):
        with st.expander(f"Texto técnico {i}"):
            st.write(texto)

    # Mostrar clasificación
    st.markdown("**Texto clasificado como:**")
    st.info(st.session_state.resultado)

# Sección 1 entrada de texto y boton analizar
with col2:

    user_text = st.text_area("Ingrese el texto", height=800, placeholder="Escriba o pegue aquí el texto a analizar...")

    # Botón analizar
    if st.button("🔎 Analizar", use_container_width=True):
        if user_text.strip():
            resultado = clasificar_texto(user_text)
            st.session_state.resultado = resultado

            # Incrementra contador y guardar en lista
            if resultado == "Texto sencillo":
                st.session_state.contador_sencillo += 1
                st.session_state.textos_sencillos.append(user_text)
            else:
                st.session_state.contador_tecnico += 1
                st.session_state.textos_tecnicos.append(user_text)

            st.success("Clasificación ejecutada")
        else:
            st.warning("⚠️ Por favor, ingrese un texto antes de analizar.")
