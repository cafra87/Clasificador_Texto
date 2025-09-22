#!/usr/bin/env bash
#Se detiene si hay algún error
set -e

# Definimos los valores por defecto si no son establecidos en el entorno
: "${PORT:=8501}"
: "${API_URL:=http://localhost:5001/invocations}"


echo "[run.sh] API_URL=${API_URL}"
echo "[run.sh] PORT=${PORT}"

# Se Lanza streamlit
exec streamlit run /app/tablero_v2.py --server.port "${PORT}" --server.address 0.0.0.0