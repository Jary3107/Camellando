# Usar una imagen oficial de Python ligera
FROM python:3.10-slim

# Directorio de trabajo en el contenedor
WORKDIR /code

# Evitar que Python escriba archivos .pyc y habilitar logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema mínimas si es necesario (ej: compilación de bcrypt)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para aprovechar la caché de Docker
COPY requirements.txt /code/

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copiar el resto de la aplicación
COPY . /code/

# Exponer el puerto 8000 en el que corre FastAPI
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
