FROM python:3.11

# Crear usuario que ejecuta la app
RUN adduser --disabled-password --gecos '' api-user

# Definir directorio de trabajo 
WORKDIR /opt/mlflow-api

# Se copian el script y las dependencias al contenedor
COPY run.sh /opt/mlflow-api/
COPY requirements.txt /opt/mlflow-api/
COPY model /opt/mlflow-api/model

# Instalar dependencias NECESARIAS
RUN pip install --upgrade pip
RUN pip install -r /opt/mlflow-api/requirements.txt

# Se dan permisos para que el script se pueda ejecutar:
RUN chmod +x /opt/mlflow-api/run.sh
RUN chown -R api-user:api-user /opt/mlflow-api

#Se cambia al usuario api-user
USER api-user

# Puerto a exponer para la api 
EXPOSE 5001

# Comandos a ejecutar al correr el contenedor 
CMD ["bash", "/opt/mlflow-api/run.sh"]
