## COMO CORRER EL SERVIDOR
Corres estos comandos (DENTRO DE LA CARPETA ´PANDER_PY´):
1. python -m venv env
2. env\Scripts\activate
3. pip install -r requirements.txt
4. python manage.py runserver

## COMO CREAR UNA NUEVA APP
ejecutas el siguientes comando: ´python manage.py startapp apps.nombre_app apps/nombre_app´

## COMO USAR REST FRAMEWORK EN DJANGO
1. Ingresa a la carpeta config y entras al archivo ´settings´
2. Por ´INSTALLED_APPS´, ingresamos el siguiente texto ´rest_framework´ y ya con eso le indicas a django vas a usar esa extension

## PAQUETES NECESARIOS (YA ESTAN INSTALADOS)
- Django
- djangorestframework
- virtualenv

### PASO A PASO PARA CREAR UN PROYECTO EN DJANGO
´NOTA´: Primero asegurate de tener el paquete instalado ´Django´

ejecutas este comando para crear el proyecto django: ´django-admin startproject config .´