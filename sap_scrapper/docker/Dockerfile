FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    wget \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install chromium

# Copiar script de espera
COPY docker/wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Copiar el código
COPY . .

# Esperar a que MongoDB esté disponible antes de iniciar la aplicación
CMD ["/wait-for-it.sh", "mongodb:27017", "--", "python", "src/main.py"] 