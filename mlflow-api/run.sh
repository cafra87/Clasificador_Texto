#!/usr/bin/env bash
#Se detiene si hay algún error
set -e

# Definimos la ruta del modelo directamente desde los artefactos
MLFLOW_MODEL_URI="/opt/mlflow-api/model"
PORT="${PORT:-5001}"

echo "Sirviendo modelo     : $MLFLOW_MODEL_URI"
echo "Puerto              : $PORT"

# Se Lanza el servidor de inferencia de MLflow
exec mlflow models serve -m "$MLFLOW_MODEL_URI" -h 0.0.0.0 -p "$PORT" --env-manager local

