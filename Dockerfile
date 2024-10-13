# Utilizar una imagen base oficial de Python
FROM python:3.10-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el archivo de requisitos
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Exponer el puerto en el que Flask ejecutará la aplicación (el puerto por defecto es 5000)
EXPOSE 5050

# Establecer la variable de entorno para que Flask escuche en todas las interfaces
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Comando para ejecutar la aplicación
CMD ["flask", "run"]