# Guía de Ejecución del SAP Table Scraper

## Requisitos Previos

1. Python 3.9 o superior
2. pip (gestor de paquetes de Python)
3. MongoDB instalado localmente o una conexión a MongoDB Atlas
4. Git (opcional, para clonar el repositorio)

## Configuración del Entorno

1. Crear y activar un entorno virtual:
```bash
# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual
source venv/bin/activate
```

2. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

3. Instalar Playwright y sus navegadores:
```bash
playwright install
```

4. Configurar las variables de entorno:
```bash
# Crear archivo .env desde el ejemplo
cp .env.example .env

# Editar .env con tu editor preferido
nano .env
```

## Validación del Archivo de Ejemplo

Para validar que el scraper puede procesar correctamente el archivo `sap_table.html` y sus referencias:

```bash
# Ejecutar el validador de ejemplo
python -m src.validator --file example/sap_table.html
```

Este comando verificará:
- La estructura del HTML de ejemplo
- Los enlaces a otras tablas SAP
- La navegación por índices (A-Z, SLASH, etc.)

## Ejecución del Scraper

1. Para ejecutar el scraper completo:
```bash
python -m src.main
```

2. Para ejecutar solo el scraping de índices específicos:
```bash
# Ejemplo para scrapear solo las tablas que empiezan con "/"
python -m src.main --index slash

# Ejemplo para scrapear tablas que empiezan con "A"
python -m src.main --index a
```

## Monitoreo

El scraper generará logs en `logs/scraper.log` con información sobre:
- Tablas procesadas
- Errores encontrados
- Progreso del scraping

## Verificación de Resultados

1. Revisar los datos en MongoDB:
```bash
# Abrir el shell de MongoDB
mongosh

# Seleccionar la base de datos
use sap_tables

# Verificar las tablas guardadas
db.tables.find().count()
```

2. Verificar la estructura de los datos:
```bash
# Mostrar una tabla de ejemplo
db.tables.findOne()
```

## Solución de Problemas Comunes

1. **Error de conexión a MongoDB**:
   - Verificar que MongoDB está corriendo: `brew services list`
   - Iniciar MongoDB si es necesario: `brew services start mongodb-community`

2. **Error de Playwright**:
   - Reinstalar navegadores: `playwright install --force`
   - Verificar permisos: `chmod -R 777 ~/Library/Caches/ms-playwright`

3. **Error de módulos no encontrados**:
   - Verificar que estás en el directorio correcto
   - Verificar que el entorno virtual está activado
   - Reinstalar dependencias: `pip install -r requirements.txt`

## Notas Adicionales

- El scraper implementa rate limiting para evitar sobrecarga del servidor
- Los datos se almacenan en formato JSON para fácil procesamiento
- Se mantiene un registro de URLs ya procesadas para evitar duplicados
- El proceso puede tomar varias horas dependiendo de la cantidad de tablas 