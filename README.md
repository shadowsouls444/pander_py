## INSTRUCCIONES PARA CORRER LA APP O SERVIDOR
Corres estos comandos (DENTRO DE LA CARPETA `PANDER_PY`):
1. python -m venv env
2. env\Scripts\activate
3. pip install -r requirements.txt
4. python manage.py runserver

## COMO CREAR UNA NUEVA APP
ejecutas el siguientes comando: `python manage.py startapp apps.nombre_app apps/nombre_app`

## GUARDAR DEPENDENCIAS DEL PROYECTO
Cada vez que se instale un nuevo paquete con `pip install`, es recomendable actualizar el archivo de dependencias del proyecto.
- comando: `pip freeze > requirements.txt`

### COMO CONECTAR DJANGO A SQL SERVER
**Nota:** Es importante que en SQL Server se utilice **Windows Authentication**, ya que Django se conectará usando la cuenta de Windows del sistema.

## 1. Abrir el archivo de configuracion
Ir a la carpeta `config` del proyecto y abrir el archivo `settings.py`

## 2. Configurar la base de datos
Buscar el diccionario `DATABASES` y modificarlo de la siguiente forma:

```python
DATABASES = {
    'default': {
        'ENGINE': 'mssql', # Motor de la base de datos
        'NAME': 'pander',  # Nombre de la base de datos
        'HOST': 'DESKTOP-FO2357P',  # Nombre del servidor
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 18 for SQL Server',
            'trusted_connection': 'yes',
            'extra_params': 'TrustServerCertificate=yes'
        }
    }
}
```

## CREDENCIALES SUPER USUARIO
username: pander
email: angel.acuna.meza@gmail.com
password: pander_py_12345

## COMO USAR REST FRAMEWORK EN DJANGO
1. Ingresa a la carpeta config y entras al archivo `settings`
2. Por `INSTALLED_APPS`, ingresamos el siguiente texto `rest_framework` y ya con eso le indicas a django vas a usar esa extension

## PAQUETES NECESARIOS (YA ESTAN INSTALADOS)
- Django
- djangorestframework
- virtualenv
- mssql-django

### PASO A PASO PARA CREAR UN PROYECTO EN DJANGO
`NOTA`: Primero asegurate de tener el paquete instalado `Django`

ejecutas este comando para crear el proyecto django: `django-admin startproject config .`

#### usar SQL Server en Django

## Instalacion de paquete para usar SQL Server en Django
- Ejecutamos el siguiente comando: `pip install mssql-django`

## Instalacion de SQL Server
1. Descargar **SQL Server 2025 Developer** desde la página oficial.
2. Seleccionar la opción **Enterprise Developer Edition**, que es gratuita para desarrollo y aprendizaje.

**Link de descarga:**  
https://www.microsoft.com/es-es/sql-server/sql-server-downloads

---

## Instalación de SQL Server Management Studio (SSMS)
Una vez finalizada la instalación de **SQL Server**, aparecerá la opción para instalar **SQL Server Management Studio (SSMS)**.

1. Haz clic en **Install SSMS**.
2. Sigue el asistente de instalación hasta completarlo.

SSMS es la herramienta gráfica que permite administrar bases de datos, ejecutar consultas SQL y gestionar servidores de SQL Server.

---

## Instalación del Driver ODBC para SQL Server
Para que las aplicaciones puedan conectarse a SQL Server, es necesario instalar el **ODBC Driver**.

1. Ir a la página de descarga del driver.
2. Descargar la opción **Microsoft ODBC Driver 18 for SQL Server (x64)**.
3. Ejecutar el instalador y completar la instalación.

**Link de descarga:**  
https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver17