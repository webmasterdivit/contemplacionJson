#!/bin/bash

# Script de configuración y utilidades para ejercicios espirituales
# Proporciona varias opciones para gestionar el procesador

set -e

# Configuración
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="ejercicios-espirituales"
DOCKER_SCRIPT="./run_ejercicios_docker.sh"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}  EJERCICIOS ESPIRITUALES TOOLS ${NC}"
    echo -e "${PURPLE}================================${NC}"
    echo ""
}

print_menu() {
    echo -e "${BLUE}Opciones disponibles:${NC}"
    echo "1. Ejecutar procesamiento completo"
    echo "2. Ejecutar con reconstrucción de imagen"
    echo "3. Solo verificar configuración"
    echo "4. Ver archivos de salida"
    echo "5. Limpiar archivos temporales"
    echo "6. Ver logs de URLs fallidas"
    echo "7. Estadísticas del último procesamiento"
    echo "8. Ejecutar en modo debug"
    echo "9. Salir"
    echo ""
}

verify_setup() {
    echo -e "${YELLOW}Verificando configuración...${NC}"
    
    # Verificar archivos necesarios
    local files=("app_ejercicios.py" "requirements.txt" "run_ejercicios_docker.sh")
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            echo -e "${GREEN}✓${NC} $file encontrado"
        else
            echo -e "${RED}✗${NC} $file NO encontrado"
            return 1
        fi
    done
    
    # Verificar Docker
    if command -v docker &> /dev/null; then
        echo -e "${GREEN}✓${NC} Docker disponible"
        if docker ps &> /dev/null; then
            echo -e "${GREEN}✓${NC} Docker daemon corriendo"
        else
            echo -e "${RED}✗${NC} Docker daemon no está corriendo"
            return 1
        fi
    else
        echo -e "${RED}✗${NC} Docker no está instalado"
        return 1
    fi
    
    # Verificar permisos
    if [ -x "$DOCKER_SCRIPT" ]; then
        echo -e "${GREEN}✓${NC} Script de Docker es ejecutable"
    else
        echo -e "${YELLOW}!${NC} Haciendo ejecutable el script..."
        chmod +x "$DOCKER_SCRIPT"
    fi
    
    echo -e "${GREEN}Configuración verificada correctamente${NC}"
    return 0
}

run_processing() {
    local rebuild_flag="$1"
    echo -e "${BLUE}Iniciando procesamiento de ejercicios espirituales...${NC}"
    
    if [ "$rebuild_flag" = "--rebuild" ]; then
        echo -e "${YELLOW}Reconstruyendo imagen Docker...${NC}"
        $DOCKER_SCRIPT --rebuild
    else
        $DOCKER_SCRIPT
    fi
}

show_output_files() {
    echo -e "${BLUE}Archivos de salida:${NC}"
    
    if [ -d "salida" ]; then
        echo ""
        echo -e "${GREEN}Directorio salida/:${NC}"
        ls -la salida/
        
        # Mostrar información detallada del JSON si existe
        local json_file="salida/ejercicios_espirituales.json"
        if [ -f "$json_file" ]; then
            echo ""
            echo -e "${GREEN}Información del archivo JSON:${NC}"
            echo "Archivo: $json_file"
            echo "Tamaño: $(ls -lh "$json_file" | awk '{print $5}')"
            echo "Modificado: $(ls -l "$json_file" | awk '{print $6, $7, $8}')"
            
            # Contar entradas si Python está disponible
            if command -v python3 &> /dev/null; then
                local count=$(python3 -c "import json; print(len(json.load(open('$json_file'))))" 2>/dev/null || echo "N/A")
                echo "Ejercicios: $count"
            fi
        fi
    else
        echo -e "${YELLOW}No se encontró el directorio de salida${NC}"
    fi
}

clean_temp_files() {
    echo -e "${YELLOW}Limpiando archivos temporales...${NC}"
    
    # Limpiar logs de URLs fallidas
    if ls failed_urls_ejercicios_*.log 1> /dev/null 2>&1; then
        echo "Eliminando logs de URLs fallidas..."
        rm -f failed_urls_ejercicios_*.log
        echo -e "${GREEN}✓${NC} Logs eliminados"
    fi
    
    # Limpiar Dockerfile temporal si existe
    if [ -f "Dockerfile.temp" ]; then
        rm -f "Dockerfile.temp"
        echo -e "${GREEN}✓${NC} Dockerfile temporal eliminado"
    fi
    
    # Opcionalmente limpiar imagen Docker
    read -p "¿Eliminar también la imagen Docker? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker rmi ejercicios-espirituales:latest 2>/dev/null || true
        echo -e "${GREEN}✓${NC} Imagen Docker eliminada"
    fi
    
    echo -e "${GREEN}Limpieza completada${NC}"
}

show_failed_urls() {
    echo -e "${BLUE}Logs de URLs fallidas:${NC}"
    
    if ls failed_urls_ejercicios_*.log 1> /dev/null 2>&1; then
        for log_file in failed_urls_ejercicios_*.log; do
            echo ""
            echo -e "${GREEN}Archivo: $log_file${NC}"
            echo "Tamaño: $(ls -lh "$log_file" | awk '{print $5}')"
            echo "Creado: $(ls -l "$log_file" | awk '{print $6, $7, $8}')"
            echo ""
            echo "Primeras 10 URLs fallidas:"
            head -15 "$log_file" | tail -10
            echo ""
            local total_failed=$(grep -c "^[0-9]" "$log_file" 2>/dev/null || echo "0")
            echo "Total de URLs fallidas: $total_failed"
        done
    else
        echo -e "${GREEN}No se encontraron logs de URLs fallidas${NC}"
        echo "Esto significa que todas las URLs se procesaron exitosamente."
    fi
}

show_statistics() {
    echo -e "${BLUE}Estadísticas del último procesamiento:${NC}"
    
    local json_file="salida/ejercicios_espirituales.json"
    if [ -f "$json_file" ] && command -v python3 &> /dev/null; then
        echo "Generando estadísticas..."
        
        python3 << EOF
import json
from collections import Counter

try:
    with open('$json_file', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\n📊 ESTADÍSTICAS GENERALES")
    print(f"Total de ejercicios: {len(data)}")
    
    # Estadísticas por tipo
    tipos = [item.get('tipo', 'N/A') for item in data]
    tipo_counts = Counter(tipos)
    
    print(f"\n📋 POR TIPO:")
    for tipo, count in tipo_counts.most_common():
        print(f"  {tipo}: {count}")
    
    # Estadísticas por categoría
    categorias = [item.get('categoria', 'N/A') for item in data]
    categoria_counts = Counter(categorias)
    
    print(f"\n🏷️  POR CATEGORÍA:")
    for categoria, count in categoria_counts.most_common():
        print(f"  {categoria}: {count}")
    
    # Ejercicios con lecturas
    con_lecturas = sum(1 for item in data if item.get('lecturas', '').strip())
    print(f"\n📖 CON LECTURAS: {con_lecturas} ({con_lecturas/len(data)*100:.1f}%)")
    
    # Análisis de títulos
    titulos_largos = sum(1 for item in data if len(item.get('titulo', '')) > 50)
    print(f"📝 TÍTULOS LARGOS (>50 chars): {titulos_largos}")
    
except Exception as e:
    print(f"Error al generar estadísticas: {e}")
EOF
    else
        echo -e "${YELLOW}No se puede generar estadísticas${NC}"
        echo "Archivo JSON no encontrado o Python3 no disponible"
    fi
}

run_debug_mode() {
    echo -e "${YELLOW}Ejecutando en modo debug...${NC}"
    echo "Esto mostrará información detallada del procesamiento"
    
    # Crear versión debug del script
    local debug_script="debug_ejercicios.py"
    
    # Modificar temporalmente el archivo para modo debug
    if [ -f "app_ejercicios.py" ]; then
        echo "Ejecutando con logging extendido..."
        
        # Ejecutar con variables de debug
        PYTHONUNBUFFERED=1 VERBOSE=1 python3 app_ejercicios.py
    else
        echo -e "${RED}Archivo app_ejercicios.py no encontrado${NC}"
    fi
}

main() {
    print_header
    
    while true; do
        print_menu
        read -p "Selecciona una opción (1-9): " choice
        echo ""
        
        case $choice in
            1)
                if verify_setup; then
                    run_processing
                fi
                ;;
            2)
                if verify_setup; then
                    run_processing "--rebuild"
                fi
                ;;
            3)
                verify_setup
                ;;
            4)
                show_output_files
                ;;
            5)
                clean_temp_files
                ;;
            6)
                show_failed_urls
                ;;
            7)
                show_statistics
                ;;
            8)
                run_debug_mode
                ;;
            9)
                echo -e "${GREEN}¡Hasta luego!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Opción inválida${NC}"
                ;;
        esac
        
        echo ""
        read -p "Presiona Enter para continuar..."
        echo ""
    done
}

# Ejecutar función principal
main