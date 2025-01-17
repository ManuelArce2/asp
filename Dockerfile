# Usar una imagen base de Python
FROM python:3.10-slim

# Configurar el directorio de trabajo
WORKDIR /app

# Copiar los archivos de la aplicación al contenedor
COPY . /app

# Instalar las dependencias necesarias
RUN pip install --no-cache-dir flask flask-socketio eventlet matplotlib

# Exponer el puerto donde se ejecutará la aplicación
EXPOSE 5000

# Comando para iniciar la aplicación
CMD ["python", "app.py"]
