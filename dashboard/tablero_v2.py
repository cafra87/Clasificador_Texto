# -*- coding: utf-8 -*-
"""
Created on Fri Sep 19 16:32:55 2025

@author: LENOVO
"""

import streamlit as st
import os
import json
import requests

#Configuración de la página
st.set_page_config(page_title="Clasificador de Textos Médicos", layout="wide")

#seteamos como variable de entorno la URL de la API
API_URL = os.environ.get("API_URL", "http://localhost:5001/invocations")

#Estado de la sesión: contadores y listas:
if "contador_sencillo" not in st.session_state:
    st.session_state.contador_sencillo = 0
if "contador_tecnico" not in st.session_state:
    st.session_state.contador_tecnico = 0
if "textos_sencillos" not in st.session_state:
    st.session_state.textos_sencillos = []
if "textos_tecnicos" not in st.session_state:
    st.session_state.textos_tecnicos = []
if "resultado" not in st.session_state:
    st.session_state.resultado = "(sin clasificar)"
    
# clave: usamos un "versión" para recrear el widget al limpiar
if "input_version" not in st.session_state: st.session_state.input_version = 0

# Función para limpiar
def limpiar_texto():
    st.session_state.resultado = "(sin clasificar)"
    st.session_state.input_version += 1  # fuerza nuevo key → textarea vacío

col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("## Clasificador de textos médicos")
    st.caption(f"API: `{API_URL}`")

    # Tarjeta: Texto sencillo
    st.markdown(f"""
    <div style="border:1px solid #ccc; border-radius:10px; padding:15px; margin-bottom:10px; 
                box-shadow:2px 2px 5px rgba(0,0,0,0.08); display:flex; justify-content:space-between; align-items:center;">
        <h4 style="margin:0;">📋 Texto sencillo</h4>
        <span style="font-size:18px; font-weight:bold;">{st.session_state.contador_sencillo}</span>
    </div>
    """, unsafe_allow_html=True)

    # Tarjeta: Texto técnico
    st.markdown(f"""
    <div style="border:1px solid #ccc; border-radius:10px; padding:15px; margin-top:10px; margin-bottom:10px; 
                box-shadow:2px 2px 5px rgba(0,0,0,0.08); display:flex; justify-content:space-between; align-items:center;">
        <h4 style="margin:0;">💡 Texto técnico</h4>
        <span style="font-size:18px; font-weight:bold;">{st.session_state.contador_tecnico}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Texto clasificado como:**")
    st.info(st.session_state.resultado)

    # Listados plegables de lo clasificado
    if st.session_state.textos_sencillos:
        with st.expander("Ver textos sencillos"):
            for i, t in enumerate(st.session_state.textos_sencillos, 1):
                st.write(f"**{i}.** {t}")
    if st.session_state.textos_tecnicos:
        with st.expander("Ver textos técnicos"):
            for i, t in enumerate(st.session_state.textos_tecnicos, 1):
                st.write(f"**{i}.** {t}")

with col2:
    st.markdown("### Ingrese el texto")
    
    user_text = st.text_area(
        "Escriba o pegue aquí el texto a analizar...",
        height=350,
        key=f"user_text_input_{st.session_state.input_version}"
    )

    cA, cB = st.columns([2,1])
    with cA:
        enviar = st.button("🔎 Enviar a la API", use_container_width=True)
    with cB:
        st.button("🧹 Limpiar", use_container_width=True, on_click=limpiar_texto)

    
    # Función para llamar a la API 
    def invocar_api(texto: str):
        """
        Envía un JSON de la siguiente forma:
            {"inputs": ["<texto>"]}
        y devuelve (json_respuesta, error)
        """
        headers = {"Content-Type": "application/json"}
        payload = {"inputs": [texto]}
        try:
            r = requests.post(API_URL, headers=headers, data=json.dumps(payload), timeout=60)
            r.raise_for_status()
            return r.json(), None
        except requests.RequestException as e:
            return None, str(e)

    # Lógica al enviar 
    if enviar:
        if not user_text or not user_text.strip():
            st.warning("⚠️ Por favor, ingrese un texto antes de analizar.")
        else:
            with st.spinner("Consultando API..."):
                data, err = invocar_api(user_text)

            if err:
                st.error(f"Error llamando a la API: {err}")
            else:
                st.success("✅ Respuesta recibida")
                # Mostrar siempre el JSON crudo para transparencia/depuración
                st.subheader("Respuesta de la API (JSON)")
                st.json(data)

                # ================================
                # MAPE0: 1 → Texto sencillo | 0 → Texto técnico
                # ================================
                pred = None
                if isinstance(data, dict) and "predictions" in data:
                    preds = data["predictions"]
                    if isinstance(preds, list) and len(preds) > 0:
                        pred = preds[0]

                if pred is None:
                    st.warning("No encontré `predictions[0]` en la respuesta.")
                else:
                    if pred == 1:
                        st.session_state.resultado = "Texto sencillo"
                        st.session_state.contador_sencillo += 1
                        st.session_state.textos_sencillos.append(user_text)
                    else:
                        # Todo lo que no sea 1 lo tratamos como técnico (incluye 0)
                        st.session_state.resultado = "Texto técnico"
                        st.session_state.contador_tecnico += 1
                        st.session_state.textos_tecnicos.append(user_text)

                    # Mostrar el resultado ya decidido
                    st.info(f"**Clasificación:** {st.session_state.resultado}")