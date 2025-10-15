# Usa una imagen base de Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de la aplicación
COPY requirements.txt .
COPY app.py .

# Instala las dependencias (aunque en este caso no hay dependencias externas)
RUN pip install --no-cache-dir -r requirements.txt

# Crea el directorio de salida
RUN mkdir -p salida

# Establece permisos para escribir en el directorio de salida
RUN chmod 755 salida

# Comando por defecto para ejecutar la aplicación
CMD ["python", "app.py"]