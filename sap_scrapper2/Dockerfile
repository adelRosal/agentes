FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para aprovechar la caché de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Crear directorios necesarios
RUN mkdir -p contracts logs

# Configurar permisos
RUN chmod -R 755 /app

# Usuario no root para seguridad
RUN useradd -m scraper
RUN chown -R scraper:scraper /app
USER scraper

CMD ["python", "src/scraper.py"] 