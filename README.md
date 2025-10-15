# Generador de Contemplaciones Litúrgicas

Esta aplicación en Python genera un archivo JSON con contemplaciones litúrgicas organizadas según el año litúrgico católico.

## 📖 Conceptos Litúrgicos

### Tiempos Litúrgicos

El año litúrgico se divide en varios tiempos sagrados:

- **Adviento**: Un tiempo de cuatro semanas de preparación para la Navidad. Tiempo de esperanza y preparación para la venida del Señor.

- **Navidad**: Comienza el 25 de diciembre y celebra el nacimiento de Jesús. Tiempo de alegría por la Encarnación del Hijo de Dios.

- **Cuaresma**: Un período de cuarenta días de preparación para la Pascua, que comienza con el Miércoles de Ceniza. Tiempo de conversión, ayuno, oración y limosna.

- **Pascua**: El tiempo más importante del año litúrgico, que incluye la Semana Santa, el Triduo Pascual (Jueves Santo, Viernes Santo y Sábado Santo), y culmina con Pentecostés. Celebra la Resurrección de Cristo.

- **Tiempo Ordinario**: Es el tiempo más largo del año y se divide en dos partes; la primera va desde el final de Navidad hasta el inicio de la Cuaresma, y la segunda desde el final de la Pascua hasta el inicio del siguiente Adviento. Se centra en la vida, enseñanzas y milagros de Jesús.

### Lecturas Bíblicas

La nomenclatura litúrgica para las lecturas sigue este formato:

**Ejemplo: Jn 16, 12-15**
- `Jn`: Se refiere al Evangelio de San Juan
- `16`: Es el número del capítulo
- `12-15`: Indica los versículos del 12 al 15

### Ciclos Litúrgicos

El año litúrgico se organiza en tres ciclos que se alternan:

- **Ciclo A**: Se lee principalmente el Evangelio de San Mateo
- **Ciclo B**: Se lee principalmente el Evangelio de San Marcos  
- **Ciclo C**: Se lee principalmente el Evangelio de San Lucas

*Nota: El Evangelio de San Juan se lee en todos los ciclos, especialmente durante la Pascua.*

## 🏗️ Estructura de una Contemplación

Cada contemplación es un objeto JSON con la siguiente estructura:

```json
{
  "id": "001",
  "ciclo": "A",
  "tiempo_liturgico": "Adviento",
  "titulo": "La Anunciación del Señor",
  "lecturas": "Lc 1, 26-38",
  "resumen": "La palabra del Ángel resuena en el corazón de María. El momento decisivo de la historia de la salvación cuando el Ángel Gabriel anuncia a María que será la madre del Salvador..."
}
```

### Campos de la Contemplación

- **id**: Identificador único de la entrada
- **ciclo**: Ciclo litúrgico (A, B, o C)
- **tiempo_liturgico**: Tiempo del año litúrgico
- **titulo**: Título del post o contemplación
- **lecturas**: Referencias bíblicas en formato litúrgico
- **resumen**: Primeros 200 caracteres del contenido de la contemplación

## 🚀 Instalación y Uso

### Prerrequisitos

- Docker y Docker Compose instalados en tu sistema
- Git (para clonar el repositorio)

### Opción 1: Usando Docker Compose (Recomendado)

1. **Clonar o descargar el proyecto**:
   ```bash
   git clone <url-del-repositorio>
   cd contemplacionJson
   ```

2. **Ejecutar con Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. **Verificar el resultado**:
   El archivo `contemplaciones.json` se generará en el directorio `salida/`.

### Opción 2: Usando Docker directamente

1. **Construir la imagen**:
   ```bash
   docker build -t contemplaciones-app .
   ```

2. **Ejecutar el contenedor**:
   ```bash
   docker run --rm -v $(pwd)/salida:/app/salida contemplaciones-app
   ```

### Opción 3: Ejecución local (sin Docker)

1. **Instalar Python 3.11+**

2. **Ejecutar la aplicación**:
   ```bash
   python app.py
   ```

## 📁 Estructura del Proyecto

```
contemplacionJson/
├── app.py                 # Aplicación principal
├── Dockerfile            # Configuración de Docker
├── docker-compose.yml    # Configuración de Docker Compose
├── requirements.txt      # Dependencias de Python
├── README.md            # Este archivo
├── datos/               # Directorio para archivos de entrada (opcional)
└── salida/              # Directorio donde se genera el JSON
    └── contemplaciones.json  # Archivo de salida generado
```

## 🔧 Configuración

### Datos de Entrada

Por defecto, la aplicación utiliza datos de ejemplo integrados. Para usar tus propios datos:

1. Crea el directorio `datos/` en la raíz del proyecto
2. Añade tus archivos de texto con las contemplaciones
3. Modifica la función `cargar_datos_ejemplo()` en `app.py` para leer tus archivos

### Personalización

Puedes modificar el archivo `app.py` para:

- Cambiar los patrones de reconocimiento de tiempos litúrgicos
- Ajustar la extracción de lecturas bíblicas
- Modificar la longitud del resumen (por defecto 200 caracteres)
- Añadir nuevos campos a la estructura de contemplación

## 📊 Ejemplo de Salida

```json
[
  {
    "id": "001",
    "ciclo": "C",
    "tiempo_liturgico": "Adviento",
    "titulo": "La Anunciación del Señor",
    "lecturas": "Lc 1, 26-38",
    "resumen": "La palabra del Ángel resuena en el corazón de María. El momento decisivo de la historia de la salvación cuando el Ángel Gabriel anuncia a María que será la madre del Salvador..."
  },
  {
    "id": "002",
    "ciclo": "A",
    "tiempo_liturgico": "Navidad",
    "titulo": "La Natividad del Señor",
    "lecturas": "Mt 2, 1-12",
    "resumen": "En la noche de Belén, la luz del mundo nace en la humildad. La adoración de los Magos nos invita a contemplar el misterio de la Encarnación..."
  }
]
```

## 🐛 Solución de Problemas

### El contenedor no genera el archivo

1. Verifica que el directorio `salida/` tenga permisos de escritura
2. Revisa los logs del contenedor: `docker-compose logs`

### Error de permisos

```bash
# Dar permisos al directorio de salida
chmod 755 salida/
```

### Problemas con Docker

```bash
# Limpiar imágenes y contenedores
docker-compose down
docker system prune -f
docker-compose up --build
```

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Si tienes preguntas o encuentras problemas, por favor:

1. Revisa la sección de solución de problemas
2. Busca en los issues existentes
3. Crea un nuevo issue con detalles del problema

---

*Desarrollado con ❤️ para la comunidad católica*