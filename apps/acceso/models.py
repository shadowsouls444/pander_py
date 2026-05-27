"""
MÓDULO: acceso
MOTOR:  Microsoft SQL Server  (paquete: mssql-django)
TABLAS: rol, modulo, rol_modulo, analista, usuario

Mapeo de tipos Django → SQL Server:
  CharField(max_length=n)  →  nvarchar(n)
  TextField                →  nvarchar(max)
  BooleanField             →  bit
  IntegerField             →  int
  BigIntegerField          →  bigint
  FloatField               →  float(53)
  DecimalField(p,s)        →  decimal(p,s)
  DateTimeField            →  datetime2      ← mayor precisión que datetime
  AutoField                →  int IDENTITY(1,1)
  EmailField               →  nvarchar(254)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
POLÍTICA DE NULOS — campos de auditoría
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  fecha_creacion        NOT NULL   auto_now_add=True, siempre presente
  usuario_creacion      NOT NULL   quién creó el registro (humano)
                        NULL       proceso automático / autoregistro candidato
  fecha_modificacion    NULL       None hasta la primera edición  (auto_now)
  usuario_modificacion  NULL       None hasta la primera edición

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
POLÍTICA DE NULOS — otros campos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Se documenta campo a campo en cada modelo.
  Criterio general: nullable solo cuando el dato es genuinamente
  opcional o lo genera un proceso, no como atajos de implementación.
"""

from django.db import models


# ─────────────────────────────────────────────────────────────
# ROL
# ─────────────────────────────────────────────────────────────
class Rol(models.Model):
    """
    Catálogo global de roles del sistema.
    No es multiempresa: los roles son compartidos por todas las compañías.
    Define qué módulos puede acceder cada tipo de usuario (vía RolModulo).

    Nulos:
      comentario  → NULL  texto libre opcional
    """
    descripcion = models.CharField(max_length=255)
    comentario  = models.TextField(null=True, blank=True)

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Rol [{self.pk}]: {self.descripcion}"

    class Meta:
        db_table = "rol"


# ─────────────────────────────────────────────────────────────
# MODULO
# ─────────────────────────────────────────────────────────────
class Modulo(models.Model):
    """
    Módulos / vistas del sistema con jerarquía autorelacional.

    modulo_padre IS NULL  →  nodo raíz (menú de primer nivel)
    modulo_padre = <id>   →  hijo / submenú

    Navegación recursiva en SQL Server mediante CTE:
      WITH cte AS (
          SELECT * FROM modulo WHERE modulo_padre IS NULL
          UNION ALL
          SELECT m.* FROM modulo m
          INNER JOIN cte c ON m.modulo_padre = c.id
      )
      SELECT * FROM cte ORDER BY orden;

    Nulos:
      modulo_padre  → NULL   nodo raíz
      comentario    → NULL   descripción técnica opcional
      icono         → NULL   clase CSS o nombre de ícono opcional
    """
    modulo_padre = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="hijos",
        db_column="modulo_padre"
    )
    descripcion       = models.CharField(max_length=255)
    comentario        = models.TextField(null=True, blank=True)
    nombre_aplicacion = models.CharField(max_length=150)
    ind_visible       = models.BooleanField(default=True)
    orden             = models.IntegerField(default=0)
    icono             = models.CharField(max_length=100, null=True, blank=True)

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        nivel = "(raíz)" if not self.modulo_padre else f"hijo de [{self.modulo_padre}]"
        return f"Modulo [{self.pk}]: {self.nombre_aplicacion} {nivel}"

    class Meta:
        db_table = "modulo"
        ordering = ["orden"]


# ─────────────────────────────────────────────────────────────
# ROL_MODULO  — pivote N:M con auditoría
# ─────────────────────────────────────────────────────────────
class RolModulo(models.Model):
    """
    Define qué módulos puede acceder cada rol.
    Gestionado manualmente (no con ManyToManyField) para conservar
    los campos de auditoría propios de la relación.
    unique_together genera un índice UNIQUE compuesto en SQL Server.
    """
    rol    = models.ForeignKey(Rol,    on_delete=models.CASCADE, db_column="rol")
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, db_column="modulo")

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"RolModulo: Rol[{self.rol}] → Modulo[{self.modulo}]"

    class Meta:
        db_table        = "rol_modulo"
        unique_together = [("rol", "modulo")]


# ─────────────────────────────────────────────────────────────
# ANALISTA
# ─────────────────────────────────────────────────────────────
class Analista(models.Model):
    """
    Perfil personal del operador de RRHH dentro de una compañía.
    Separado de Usuario para aislar datos personales sensibles
    del registro de acceso al sistema.

    id_interno: secuencial dentro de la compañía.
    unique_together (compania, id_interno) garantiza unicidad de negocio.
    La PK técnica es el id AutoField de Django → int IDENTITY(1,1).

    Nulos:
      tipo_documento   → NULL  no siempre disponible al crear el perfil
      numero_documento → NULL  ídem
      segundo_nombre   → NULL  no todas las personas tienen segundo nombre
      segundo_apellido → NULL  ídem
      telefono         → NULL  dato opcional de contacto
      cargo            → NULL  puede no conocerse al momento del registro
    """
    compania = models.ForeignKey(
        "empresa.Compania",
        on_delete=models.CASCADE,
        db_column="compania",
        related_name="analistas"
    )
    id_interno = models.IntegerField(
        help_text="Identificador secuencial dentro de la compañía"
    )

    tipo_documento = models.ForeignKey(
        "candidatos.TipoDocumento",
        on_delete=models.PROTECT,
        db_column="tipo_documento",
        null=True, blank=True
    )
    numero_documento = models.CharField(max_length=30,  null=True, blank=True)
    primer_nombre    = models.CharField(max_length=80)
    segundo_nombre   = models.CharField(max_length=80,  null=True, blank=True)
    primer_apellido  = models.CharField(max_length=80)
    segundo_apellido = models.CharField(max_length=80,  null=True, blank=True)
    telefono         = models.CharField(max_length=20,  null=True, blank=True)
    cargo            = models.CharField(max_length=120, null=True, blank=True)

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return (
            f"Analista [{self.compania}-{self.id_interno}]: "
            f"{self.primer_nombre} {self.primer_apellido}"
        )

    class Meta:
        db_table        = "analista"
        unique_together = [("compania", "id_interno")]


# ─────────────────────────────────────────────────────────────
# USUARIO
# ─────────────────────────────────────────────────────────────
class Usuario(models.Model):
    """
    Usuario operativo del sistema.

    pwd: almacenar SIEMPRE como hash (argon2 recomendado vía
         django.contrib.auth.hashers o passlib).

    ind_super_usuario: acceso total ignorando rol_modulo.
    ind_activo:        controla si el usuario puede iniciar sesión.
    ind_bloqueo:       bloqueo por intentos fallidos u orden administrativa.

    Nulos:
      analista  → NULL  superusuarios del sistema pueden no tener perfil analista
    """
    compania = models.ForeignKey(
        "empresa.Compania",
        on_delete=models.CASCADE,
        db_column="compania",
        related_name="usuarios"
    )
    id_interno = models.IntegerField(
        help_text="Identificador secuencial dentro de la compañía"
    )

    analista = models.ForeignKey(
        Analista,
        on_delete=models.PROTECT,
        db_column="analista",
        related_name="usuarios",
        null=True, blank=True
    )
    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        db_column="rol",
        related_name="usuarios"
    )

    login             = models.CharField(max_length=100)
    pwd               = models.CharField(max_length=255)
    email             = models.EmailField(max_length=150)
    ind_super_usuario = models.BooleanField(default=False)
    ind_activo        = models.BooleanField(default=True)
    ind_bloqueo       = models.BooleanField(default=False)
    fecha_bloqueo     = models.DateTimeField(
        null=True, blank=True,
        help_text=(
            "Timestamp del bloqueo activo. "
            "Si ind_bloqueo=True y NOW() < fecha_bloqueo + 15 min → acceso denegado. "
            "Pasados 15 min el LoginView desbloquea automáticamente. "
            "Si fecha_bloqueo es NULL con ind_bloqueo=True → bloqueo permanente."
        ),
    )

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Usuario [{self.compania}-{self.id_interno}]: {self.login}"

    class Meta:
        db_table        = "usuario"
        unique_together = [("compania", "id_interno")]

class VRol(models.Model):
    """
    Vista v_rol — roles con conteo de usuarios.
    Sin FKs en la vista, sin colisión.
    """
    descripcion          = models.CharField(max_length=255)
    comentario           = models.TextField(null=True)
    total_usuarios       = models.IntegerField()
    fecha_creacion       = models.DateTimeField()
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(null=True)
    usuario_modificacion = models.IntegerField(null=True)

    class Meta:
        managed  = False
        db_table = "v_rol"


class VModulo(models.Model):
    """
    Vista v_modulo.
    La vista SQL expone: m.modulo_padre AS modulo_padre_id
    """
    modulo_padre_id      = models.IntegerField(null=True)
    modulo_padre_nombre  = models.CharField(max_length=150, null=True)
    descripcion          = models.CharField(max_length=255)
    comentario           = models.TextField(null=True)
    nombre_aplicacion    = models.CharField(max_length=150)
    ind_visible          = models.BooleanField()
    orden                = models.IntegerField()
    icono                = models.CharField(max_length=100, null=True)
    fecha_creacion       = models.DateTimeField()
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(null=True)
    usuario_modificacion = models.IntegerField(null=True)

    class Meta:
        managed  = False
        db_table = "v_modulo"


class VAnalista(models.Model):
    """
    Vista v_analista.
    La vista SQL expone:
      a.compania       AS compania_id
      a.tipo_documento AS tipo_documento_id
    """
    compania_id                = models.IntegerField()
    compania_descripcion       = models.CharField(max_length=255)
    id_interno                 = models.IntegerField()
    tipo_documento_id          = models.IntegerField(null=True)
    tipo_documento_descripcion = models.CharField(max_length=100, null=True)
    numero_documento           = models.CharField(max_length=30, null=True)
    primer_nombre              = models.CharField(max_length=80)
    segundo_nombre             = models.CharField(max_length=80, null=True)
    primer_apellido            = models.CharField(max_length=80)
    segundo_apellido           = models.CharField(max_length=80, null=True)
    nombre_completo            = models.CharField(max_length=400)
    telefono                   = models.CharField(max_length=20, null=True)
    cargo                      = models.CharField(max_length=120, null=True)
    fecha_creacion             = models.DateTimeField()
    usuario_creacion           = models.IntegerField()
    fecha_modificacion         = models.DateTimeField(null=True)
    usuario_modificacion       = models.IntegerField(null=True)

    class Meta:
        managed  = False
        db_table = "v_analista"


class VUsuario(models.Model):
    """
    Vista v_usuario.
    La vista SQL expone:
      u.compania AS compania_id
      u.analista AS analista_id
      u.rol      AS rol_id
    pwd excluido de la vista intencionalmente.
    """
    compania_id               = models.IntegerField()
    compania_descripcion      = models.CharField(max_length=255)
    id_interno                = models.IntegerField()
    analista_id               = models.IntegerField(null=True)
    analista_nombre_completo  = models.CharField(max_length=400, null=True)
    rol_id                    = models.IntegerField()
    rol_descripcion           = models.CharField(max_length=255)
    login                     = models.CharField(max_length=100)
    email                     = models.EmailField(max_length=150)
    ind_super_usuario         = models.BooleanField()
    ind_activo                = models.BooleanField()
    ind_bloqueo               = models.BooleanField()
    fecha_creacion            = models.DateTimeField()
    usuario_creacion          = models.IntegerField()
    fecha_modificacion        = models.DateTimeField(null=True)
    usuario_modificacion      = models.IntegerField(null=True)

    class Meta:
        managed  = False
        db_table = "v_usuario"
