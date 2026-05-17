"""
empresa/migrations/0005_fix_vista_reporte_id.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Recrea v_reporte_postulacion añadiendo la columna "id"
que Django requiere como PK implícita en modelos managed=False.

Se usa ROW_NUMBER() OVER (ORDER BY p.id) para generar un entero
único por fila. No afecta el resto de la lógica de la vista.
"""

from django.db import migrations

SQL_DROP = "DROP VIEW IF EXISTS v_reporte_postulacion;"

SQL_CREATE = """
CREATE OR REPLACE VIEW v_reporte_postulacion AS
WITH ultimo_intento AS (
    SELECT DISTINCT ON (postulacion, compania)
        id,
        postulacion,
        compania,
        evaluacion,
        estado,
        habilidad_estim,
        error_estandar,
        fecha_inicio,
        fecha_fin
    FROM intento
    ORDER BY postulacion, compania, fecha_inicio DESC
)
SELECT
    ROW_NUMBER() OVER (ORDER BY p.id)       AS id,
    p.compania                              AS compania_id,
    c.descripcion                           AS compania,
    p.id                                    AS postulacion_id,
    p.fecha_postulacion,
    p.vacante                               AS vacante_id,
    v.descripcion                           AS vacante,
    u.descripcion                           AS unidad,
    CONCAT_WS(' ',
        NULLIF(dc.primer_nombre,    ''),
        NULLIF(dc.segundo_nombre,   ''),
        NULLIF(dc.primer_apellido,  ''),
        NULLIF(dc.segundo_apellido, '')
    )                                       AS candidato_nombre_completo,
    dc.numero_documento                     AS candidato_documento,
    dc.email                                AS candidato_email,
    dc.telefono                             AS candidato_telefono,
    ep.descripcion                          AS estado_postulacion,
    i.habilidad_estim                       AS theta_final,
    i.error_estandar                        AS error_estandar_final,
    ei.descripcion                          AS estado_intento,
    i.fecha_inicio                          AS intento_inicio,
    i.fecha_fin                             AS intento_fin,
    EXTRACT(EPOCH FROM (i.fecha_fin - i.fecha_inicio))::INT / 60
                                            AS duracion_minutos,
    CASE ep.descripcion
        WHEN 'Seleccionado' THEN 'SELECCIONADO'
        WHEN 'Descartado'   THEN 'DESCARTADO'
        WHEN 'Finalizado'   THEN 'FINALIZADO'
        ELSE                     'EN PROCESO'
    END                                     AS decision
FROM postulacion p
INNER JOIN compania           c  ON c.id  = p.compania
INNER JOIN vacante            v  ON v.id  = p.vacante
INNER JOIN unidad_org         u  ON u.id  = v.unidad
INNER JOIN candidato          ca ON ca.id = p.candidato
INNER JOIN estado_postulacion ep ON ep.id = p.estado
LEFT  JOIN datos_candidato    dc ON dc.candidato = ca.id
LEFT  JOIN ultimo_intento     i  ON i.postulacion = p.id
                                AND i.compania    = p.compania
LEFT  JOIN estado_intento     ei ON ei.id = i.estado;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("empresa", "0004_evaluacion_estandar_y_triggers"),
    ]

    operations = [
        migrations.RunSQL(
            sql=SQL_DROP + SQL_CREATE,
            reverse_sql=SQL_DROP,
        ),
    ]
