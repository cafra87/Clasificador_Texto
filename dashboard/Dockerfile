FROM python:3.11-slim

#Se Instala curl para el healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Crear usuario que ejecuta la app no root
RUN adduser --disabled-password --gecos '' app_user

#Directorio de trabajo
WORKDIR /app

# Dependencias e instalar
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# App se copia el código y el script
COPY tablero_v2.py /app/tablero_v2.py
COPY run.sh /app/run.sh

#Se dan los permisos a 
RUN chown -R app_user:app_user /app && chmod +x /app/run.sh

# Variables de entorno que se sobreescribiran en la ECS
ENV PORT=8501
ENV API_URL=http://localhost:5001/invocations

EXPOSE 8501

USER app_user

#iniciar
CMD ["/app/run.sh"]
