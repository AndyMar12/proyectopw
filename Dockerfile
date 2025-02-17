# Usa una imagen base con Python 3.12
FROM python:3.12-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos del proyecto al contenedor
COPY . /app

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto 8080 (Puerto predeterminado de Cloud Run)
EXPOSE 8080

# Definir el comando para ejecutar la app
CMD ["python", "run.py"]  # Asegúrate de que 'app.py' es el archivo de entrada
