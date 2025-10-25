#!/bin/bash

# Script para ejecutar el procesador de ejercicios espirituales con Docker
# Autor: Sistema automatizado
# Fecha: $(date)

set -e  # Salir si hay errores

echo "=== PROCESADOR DE EJERCICIOS ESPIRITUALES CON DOCKER ==="
echo "Dominio: https://ejerciciosespirituales.wordpress.com"
echo "Fecha: $(date)"
echo ""

# Configuración
CONTAINER_NAME="ejercicios-espirituales-processor"
IMAGE_NAME="ejercicios-espirituales:latest"
WORKDIR="/app"
OUTPUT_DIR="./salida"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes con colores
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que Docker esté corriendo
print_status "Verificando Docker..."
if ! docker --version > /dev/null 2>&1; then
    print_error "Docker no está instalado o no está en el PATH"
    exit 1
fi

if ! docker ps > /dev/null 2>&1; then
    print_error "Docker no está corriendo o no tienes permisos para usarlo"
    exit 1
fi

print_success "Docker está disponible"

# Crear directorio de salida si no existe
print_status "Creando directorio de salida..."
mkdir -p "$OUTPUT_DIR"
print_success "Directorio $OUTPUT_DIR listo"

# Verificar si existe el archivo Python
if [ ! -f "app_ejercicios.py" ]; then
    print_error "No se encuentra el archivo app_ejercicios.py"
    exit 1
fi

print_success "Archivo app_ejercicios.py encontrado"

# Construir la imagen Docker si no existe o si se fuerza
BUILD_IMAGE=false
if [[ "$1" == "--rebuild" ]] || ! docker images | grep -q "$IMAGE_NAME"; then
    BUILD_IMAGE=true
fi

if [ "$BUILD_IMAGE" = true ]; then
    print_status "Construyendo imagen Docker..."
    
    # Crear Dockerfile temporal si no existe
    if [ ! -f "Dockerfile.ejercicios" ]; then
        print_status "Creando Dockerfile temporal..."
        cat > Dockerfile.ejercicios << 'EOF'
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements si existe, sino crear uno básico
COPY requirements.txt* ./
RUN if [ -f requirements.txt ]; then \
        pip install --no-cache-dir -r requirements.txt; \
    else \
        pip install --no-cache-dir requests beautifulsoup4; \
    fi

# Copiar el script de aplicación
COPY app_ejercicios.py .

# Crear directorio de salida
RUN mkdir -p salida

# Comando por defecto
CMD ["python", "app_ejercicios.py"]
EOF
        print_success "Dockerfile.ejercicios creado"
    fi
    
    # Construir imagen
    docker build -f Dockerfile.ejercicios -t "$IMAGE_NAME" .
    
    if [ $? -eq 0 ]; then
        print_success "Imagen Docker construida exitosamente"
    else
        print_error "Error al construir la imagen Docker"
        exit 1
    fi
else
    print_status "Usando imagen Docker existente"
fi

# Detener contenedor existente si está corriendo
if docker ps -a --format 'table {{.Names}}' | grep -q "$CONTAINER_NAME"; then
    print_status "Deteniendo contenedor existente..."
    docker stop "$CONTAINER_NAME" > /dev/null 2>&1 || true
    docker rm "$CONTAINER_NAME" > /dev/null 2>&1 || true
    print_success "Contenedor anterior limpiado"
fi

# Ejecutar el contenedor
print_status "Iniciando procesamiento de ejercicios espirituales..."
print_status "Contenedor: $CONTAINER_NAME"
print_status "Montando directorio: $(pwd)/$OUTPUT_DIR -> $WORKDIR/salida"

# Ejecutar el contenedor con montaje de volumen para persistir la salida
docker run --name "$CONTAINER_NAME" \
    --rm \
    -v "$(pwd)/$OUTPUT_DIR:$WORKDIR/salida" \
    -v "$(pwd)/app_ejercicios.py:$WORKDIR/app_ejercicios.py:ro" \
    "$IMAGE_NAME"

# Verificar el resultado
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    print_success "Procesamiento completado exitosamente"
    
    # Mostrar información de archivos generados
    if [ -d "$OUTPUT_DIR" ]; then
        print_status "Archivos generados en $OUTPUT_DIR:"
        ls -la "$OUTPUT_DIR"
        
        # Mostrar estadísticas básicas si existe el archivo JSON
        JSON_FILE="$OUTPUT_DIR/ejercicios_espirituales.json"
        if [ -f "$JSON_FILE" ]; then
            ENTRY_COUNT=$(python3 -c "import json; data=json.load(open('$JSON_FILE')); print(len(data))" 2>/dev/null || echo "N/A")
            FILE_SIZE=$(ls -lh "$JSON_FILE" | awk '{print $5}')
            print_success "Archivo JSON: $JSON_FILE"
            print_success "Ejercicios procesados: $ENTRY_COUNT"
            print_success "Tamaño del archivo: $FILE_SIZE"
        fi
    fi
    
    # Mostrar logs de URLs fallidas si existen
    if ls failed_urls_ejercicios_*.log 1> /dev/null 2>&1; then
        print_warning "Se encontraron logs de URLs fallidas:"
        ls -la failed_urls_ejercicios_*.log
    fi
    
else
    print_error "El procesamiento falló con código de salida: $EXIT_CODE"
    
    # Mostrar logs del contenedor si está disponible
    print_status "Mostrando logs del contenedor:"
    docker logs "$CONTAINER_NAME" 2>/dev/null || print_warning "No se pudieron obtener los logs del contenedor"
fi

# Limpieza opcional
if [[ "$1" == "--clean" ]] || [[ "$2" == "--clean" ]]; then
    print_status "Limpiando imagen Docker..."
    docker rmi "$IMAGE_NAME" > /dev/null 2>&1 || true
    rm -f Dockerfile.ejercicios
    print_success "Limpieza completada"
fi

echo ""
print_status "Script completado"
exit $EXIT_CODE