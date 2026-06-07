# 1. Usar una imagen oficial de Python ligera
FROM python:3.11-slim

# 2. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Evitar que Python escriba archivos .pyc y asegurar que los logs salgan directo
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 4. Instalar dependencias del sistema necesarias para PostgreSQL (psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 5. Copiar e instalar los requerimientos de Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 6. Copiar todo el código de nuestra aplicación de la carpeta local al contenedor
COPY . .

# 7. Exponer el puerto en el que corre FastAPI
EXPOSE 8000

# 8. Comando para arrancar la aplicación forzando a Python a buscar el módulo app
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]