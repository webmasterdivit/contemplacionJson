# Procesador de Ejercicios Espirituales

Este proyecto replica el procesador de contemplaciones para el dominio `https://ejerciciosespirituales.wordpress.com`, generando un archivo JSON con todos los ejercicios espirituales encontrados.

## Archivos del Proyecto

### Archivos Principales

- **`app_ejercicios.py`** - Script principal que procesa los posts de WordPress
- **`run_ejercicios_docker.sh`** - Script para ejecutar el procesador con Docker
- **`ejercicios_tools.sh`** - Herramientas de gestión y utilidades
- **`Dockerfile.ejercicios`** - Configuración Docker específica para ejercicios

### Archivos de Configuración

- **`requirements.txt`** - Dependencias de Python (compartido con contemplaciones)
- **`docker-compose.yml`** - Configuración Docker Compose (si existe)

## Estructura de Datos

Cada ejercicio espiritual se almacena con la siguiente estructura:

```json
{
  "id": 12345,
  "categoria": "Ejercicios Ignacianos",
  "tipo": "Meditación",
  "titulo": "Meditación sobre la Encarnación",
  "lecturas": "Lc 1, 26-38; Jn 1, 14",
  "resumen": "Contemplamos el misterio de la Encarnación...",
  "link": "https://ejerciciosespirituales.wordpress.com/2024/01/15/meditacion-encarnacion/"
}
```

### Campos Explicados

- **`id`**: ID único generado basado en la URL del post
- **`categoria`**: Categoría del ejercicio (Ejercicios Ignacianos, Meditación Franciscana, etc.)
- **`tipo`**: Tipo de ejercicio (Meditación, Contemplación, Oración, etc.)
- **`titulo`**: Título del ejercicio extraído del post
- **`lecturas`**: Referencias bíblicas encontradas en el contenido
- **`resumen`**: Resumen del contenido (primeros 200 caracteres relevantes)
- **`link`**: URL original del post en WordPress

## Uso Rápido

### Opción 1: Script de Herramientas (Recomendado)

```bash
# Ejecutar herramientas interactivas
./ejercicios_tools.sh
```

Este script proporciona un menú interactivo con las siguientes opciones:
1. Ejecutar procesamiento completo
2. Ejecutar con reconstrucción de imagen
3. Solo verificar configuración
4. Ver archivos de salida
5. Limpiar archivos temporales
6. Ver logs de URLs fallidas
7. Estadísticas del último procesamiento
8. Ejecutar en modo debug
9. Salir

### Opción 2: Script Docker Directo

```bash
# Ejecución básica
./run_ejercicios_docker.sh

# Reconstruir imagen Docker
./run_ejercicios_docker.sh --rebuild

# Limpiar después de ejecutar
./run_ejercicios_docker.sh --clean
```

### Opción 3: Ejecución Directa (Sin Docker)

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar directamente
python3 app_ejercicios.py
```

## Configuración del Procesador

### Categorías de Ejercicios

El sistema clasifica automáticamente los ejercicios en estas categorías:

- **Ejercicios Ignacianos**: Basados en San Ignacio de Loyola
- **Meditación Franciscana**: Estilo franciscano
- **Oración Carmelitana**: Tradición carmelitana
- **Lectio Divina**: Lectura orante
- **Examen de Conciencia**: Revisión espiritual
- **Ejercicios Generales**: Categoría por defecto

### Tipos de Ejercicios

- **Meditación**: Ejercicios de reflexión profunda
- **Contemplación**: Ejercicios de observación espiritual
- **Oración**: Ejercicios de diálogo con Dios
- **Reflexión**: Ejercicios de análisis espiritual
- **Examen de conciencia**: Revisión del día/vida
- **Lectio Divina**: Lectura meditada de textos sagrados

## Archivos de Salida

### Archivo Principal
- **`salida/ejercicios_espirituales.json`**: Archivo JSON con todos los ejercicios procesados

### Archivos de Log
- **`failed_urls_ejercicios_YYYYMMDD_HHMMSS.log`**: URLs que no se pudieron procesar

## Características Técnicas

### Funcionalidades del Procesador

1. **API WordPress**: Intenta primero usar el API REST de WordPress
2. **Scraping de Respaldo**: Si el API falla, usa scraping HTML
3. **Detección Inteligente**: Clasifica automáticamente tipos y categorías
4. **Extracción de Lecturas**: Encuentra referencias bíblicas en el contenido
5. **Prevención de Duplicados**: Evita procesar URLs ya existentes
6. **Manejo de Errores**: Continúa procesando aunque algunas URLs fallen

### Optimizaciones

- **Procesamiento Incremental**: Solo procesa URLs nuevas
- **Control de Velocidad**: Delay entre peticiones para evitar bloqueos
- **Progreso en Tiempo Real**: Muestra el progreso del procesamiento
- **Logs Detallados**: Registra errores y estadísticas

## Requisitos del Sistema

### Software Necesario

- **Docker**: Para ejecución en contenedor
- **Python 3.11+**: Para ejecución directa
- **Bash**: Para los scripts de automatización

### Dependencias Python

```txt
requests>=2.31.0
beautifulsoup4>=4.12.0
```

## Solución de Problemas

### Problemas Comunes

1. **Docker no disponible**
   ```bash
   # Verificar instalación
   docker --version
   
   # Verificar daemon
   docker ps
   ```

2. **Permisos de archivos**
   ```bash
   # Hacer ejecutables los scripts
   chmod +x *.sh
   ```

3. **URLs fallidas**
   - Revisa los logs `failed_urls_ejercicios_*.log`
   - Las URLs fallidas se pueden reprocesar manualmente

4. **Memoria insuficiente**
   - Reduce el `max_posts` en `app_ejercicios.py`
   - Ejecuta en lotes más pequeños

### Logs y Debug

```bash
# Ver logs detallados
./ejercicios_tools.sh
# Seleccionar opción 8 (modo debug)

# Ver estadísticas
./ejercicios_tools.sh
# Seleccionar opción 7 (estadísticas)
```

## Comparación con Contemplaciones

| Aspecto | Contemplaciones | Ejercicios Espirituales |
|---------|----------------|-------------------------|
| Dominio | diegojavier.wordpress.com | ejerciciosespirituales.wordpress.com |
| Clasificación | Tiempo Litúrgico + Ciclo | Categoría + Tipo |
| Archivo Salida | contemplaciones.json | ejercicios_espirituales.json |
| Enfoque | Liturgia católica | Espiritualidad general |

## Mantenimiento

### Ejecuciones Periódicas

Se recomienda ejecutar el procesador periódicamente para obtener nuevos contenidos:

```bash
# Ejecución semanal recomendada
./run_ejercicios_docker.sh

# Verificar estadísticas
./ejercicios_tools.sh
```

### Limpieza del Sistema

```bash
# Limpiar archivos temporales
./ejercicios_tools.sh
# Seleccionar opción 5 (limpiar)

# Limpiar completamente incluyendo imagen Docker
./run_ejercicios_docker.sh --clean
```

## Soporte

Para problemas específicos:

1. Verificar logs en `failed_urls_ejercicios_*.log`
2. Ejecutar en modo debug con `ejercicios_tools.sh`
3. Revisar la configuración con la opción de verificación
4. Consultar este README para casos comunes

---

*Script generado automáticamente para procesar ejercicios espirituales desde WordPress*