"""
empresa/migrations/0008_auditoria_compania_eliminada.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Crea la tabla de auditoría compania_eliminada.
Usa RunSQL con CREATE TABLE IF NOT EXISTS para no fallar
si la tabla ya fue creada manualmente en PostgreSQL.
"""
from django.db import migrations


SQL_CREAR = """
CREATE TABLE IF NOT EXISTS compania_eliminada (
    id                             BIGSERIAL PRIMARY KEY,

    -- Snapshot de identificación (sin FK — la compañía ya no existe)
    compania_id                    INTEGER       NOT NULL,
    descripcion                    VARCHAR(255)  NOT NULL,
    nit                            VARCHAR(20)   NOT NULL,
    objeto_social                  TEXT,
    representante_legal            VARCHAR(150),
    direccion                      VARCHAR(255),
    telefono                       VARCHAR(20),
    ind_activa                     BOOLEAN       NOT NULL,
    ind_evaluacion_vacante         BOOLEAN       NOT NULL,

    -- Auditoría de creación original
    fecha_creacion_original        TIMESTAMP WITH TIME ZONE NOT NULL,
    usuario_creacion_original      INTEGER       NOT NULL,

    -- Auditoría de eliminación
    fecha_eliminacion              TIMESTAMP WITH TIME ZONE NOT NULL,
    usuario_eliminacion            INTEGER       NOT NULL,

    -- Contadores de impacto (registros eliminados en cascada)
    total_usuarios_eliminados      INTEGER NOT NULL DEFAULT 0,
    total_analistas_eliminados     INTEGER NOT NULL DEFAULT 0,
    total_unidades_eliminadas      INTEGER NOT NULL DEFAULT 0,
    total_vacantes_eliminadas      INTEGER NOT NULL DEFAULT 0,
    total_candidatos_eliminados    INTEGER NOT NULL DEFAULT 0,
    total_postulaciones_eliminadas INTEGER NOT NULL DEFAULT 0,
    total_evaluaciones_eliminadas  INTEGER NOT NULL DEFAULT 0,
    total_habilidades_eliminadas   INTEGER NOT NULL DEFAULT 0,
    total_preguntas_eliminadas     INTEGER NOT NULL DEFAULT 0,
    total_intentos_eliminados      INTEGER NOT NULL DEFAULT 0
);

COMMENT ON TABLE compania_eliminada IS
    'Auditoría inmutable de compañías eliminadas. '
    'Registra un snapshot en el momento de la eliminación.';
COMMENT ON COLUMN compania_eliminada.compania_id IS
    'ID original de la compañía eliminada (sin FK).';
COMMENT ON COLUMN compania_eliminada.fecha_eliminacion IS
    'Timestamp exacto en que fue eliminada la compañía.';
COMMENT ON COLUMN compania_eliminada.usuario_eliminacion IS
    'ID del usuario que ejecutó la eliminación.';
"""

SQL_DROP = "DROP TABLE IF EXISTS compania_eliminada;"


class Migration(migrations.Migration):

    dependencies = [
        ("empresa", "0007_triggers_configurabilidad_evaluaciones"),
    ]

    operations = [
        migrations.RunSQL(
            sql         = SQL_CREAR,
            reverse_sql = SQL_DROP,
        ),
    ]
