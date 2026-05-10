"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARCHIVO: empresa/migrations/0003_vistas_sql.py
MOTOR:   PostgreSQL
Auditado contra los models.py reales del proyecto.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CORRECCIONES RESPECTO A VERSIONES ANTERIORES:

  Todas las FK tienen db_column explícito → columna = nombre sin _id
  La única excepción es datos_candidato.candidato (OneToOneField)
  que también usa db_column="candidato" → columna = "candidato"

  JOIN anterior (incorrecto):   ON dc.candidato_id = ca.id
  JOIN corregido:               ON dc.candidato    = ca.id
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from django.db import migrations


SQL_CREAR_VISTAS = """

-- ──────────────────────────────────────────────────────────
-- v_compania
-- ──────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW v_compania AS
SELECT
    c.id,
    c.descripcion,
    c.nit,
    c.objeto_social,
    c.representante_legal,
    c.direccion,
    c.telefono,
    c.ind_activa,
    c.ind_evaluacion_vacante,
    c.fecha_creacion,
    c.usuario_creacion,
    c.fecha_modificacion,
    c.usuario_modificacion
FROM compania c;


-- ──────────────────────────────────────────────────────────
-- v_unidad_org
-- compania → db_column="compania" → columna: compania
-- ──────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW v_unidad_org AS
SELECT
    u.id,
    u.compania                  AS compania_id,
    c.descripcion               AS compania_descripcion,
    c.nit                       AS compania_nit,
    u.id_interno,
    u.descripcion,
    u.especialidad,
    u.fecha_creacion,
    u.usuario_creacion,
    u.fecha_modificacion,
    u.usuario_modificacion
FROM unidad_org u
INNER JOIN compania c ON c.id = u.compania;


-- ──────────────────────────────────────────────────────────
-- v_rol
-- usuario.rol → db_column="rol" → columna: rol
-- ──────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW v_rol AS
SELECT
    r.id,
    r.descripcion,
    r.comentario,
    COUNT(u.id)                 AS total_usuarios,
    r.fecha_creacion,
    r.usuario_creacion,
    r.fecha_modificacion,
    r.usuario_modificacion
FROM rol r
LEFT JOIN usuario u ON u.rol = r.id
GROUP BY
    r.id,
    r.descripcion,
    r.comentario,
    r.fecha_creacion,
    r.usuario_creacion,
    r.fecha_modificacion,
    r.usuario_modificacion;


-- ──────────────────────────────────────────────────────────
-- v_modulo
-- modulo.modulo_padre → db_column="modulo_padre" → columna: modulo_padre
-- ──────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW v_modulo AS
SELECT
    m.id,
    m.modulo_padre              AS modulo_padre_id,
    mp.nombre_aplicacion        AS modulo_padre_nombre,
    m.descripcion,
    m.comentario,
    m.nombre_aplicacion,
    m.ind_visible,
    m.orden,
    m.icono,
    m.fecha_creacion,
    m.usuario_creacion,
    m.fecha_modificacion,
    m.usuario_modificacion
FROM modulo m
LEFT JOIN modulo mp ON mp.id = m.modulo_padre;


-- ──────────────────────────────────────────────────────────
-- v_analista
-- analista.compania       → db_column="compania"       → compania
-- analista.tipo_documento → db_column="tipo_documento" → tipo_documento
-- ──────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW v_analista AS
SELECT
    a.id,
    a.compania                  AS compania_id,
    c.descripcion               AS compania_descripcion,
    a.id_interno,
    a.tipo_documento            AS tipo_documento_id,
    td.descripcion              AS tipo_documento_descripcion,
    a.numero_documento,
    a.primer_nombre,
    a.segundo_nombre,
    a.primer_apellido,
    a.segundo_apellido,
    CONCAT_WS(' ',
        NULLIF(a.primer_nombre,    ''),
        NULLIF(a.segundo_nombre,   ''),
        NULLIF(a.primer_apellido,  ''),
        NULLIF(a.segundo_apellido, '')
    )                           AS nombre_completo,
    a.telefono,
    a.cargo,
    a.fecha_creacion,
    a.usuario_creacion,
    a.fecha_modificacion,
    a.usuario_modificacion
FROM analista a
INNER JOIN compania       c  ON c.id  = a.compania
LEFT  JOIN tipo_documento td ON td.id = a.tipo_documento;


-- ──────────────────────────────────────────────────────────
-- v_usuario
-- usuario.compania → db_column="compania" → compania
-- usuario.analista → db_column="analista" → analista
-- usuario.rol      → db_column="rol"      → rol
-- ──────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW v_usuario AS
SELECT
    u.id,
    u.compania                  AS compania_id,
    c.descripcion               AS compania_descripcion,
    u.id_interno,
    u.analista                  AS analista_id,
    CONCAT_WS(' ',
        NULLIF(a.primer_nombre,    ''),
        NULLIF(a.segundo_nombre,   ''),
        NULLIF(a.primer_apellido,  ''),
        NULLIF(a.segundo_apellido, '')
    )                           AS analista_nombre_completo,
    u.rol                       AS rol_id,
    r.descripcion               AS rol_descripcion,
    u.login,
    u.email,
    u.ind_super_usuario,
    u.ind_activo,
    u.ind_bloqueo,
    u.fecha_creacion,
    u.usuario_creacion,
    u.fecha_modificacion,
    u.usuario_modificacion
FROM usuario u
INNER JOIN compania c ON c.id = u.compania
INNER JOIN rol      r ON r.id = u.rol
LEFT  JOIN analista a ON a.id = u.analista;


-- ──────────────────────────────────────────────────────────
-- v_vacante
-- vacante.compania      → db_column="compania"      → compania
-- vacante.unidad        → db_column="unidad"        → unidad
-- vacante.estado        → db_column="estado"        → estado
-- vacante.tipo_contrato → db_column="tipo_contrato" → tipo_contrato
-- ──────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW v_vacante AS
SELECT
    v.id,
    v.compania                  AS compania_id,
    c.descripcion               AS compania_descripcion,
    v.id_interno,
    v.descripcion,
    v.unidad                    AS unidad_id,
    u.descripcion               AS unidad_descripcion,
    u.especialidad              AS unidad_especialidad,
    v.anio_experiencia,
    v.salario_minimo,
    v.salario_maximo,
    v.estado                    AS estado_id,
    ev.descripcion              AS estado_descripcion,
    v.tipo_contrato             AS tipo_contrato_id,
    tc.descripcion              AS tipo_contrato_descripcion,
    v.ind_activa,
    v.ind_publicada,
    v.fecha_publicacion,
    v.fecha_creacion,
    v.usuario_creacion,
    v.fecha_modificacion,
    v.usuario_modificacion
FROM vacante v
INNER JOIN compania       c  ON c.id  = v.compania
INNER JOIN unidad_org     u  ON u.id  = v.unidad
INNER JOIN estado_vacante ev ON ev.id = v.estado
INNER JOIN tipo_contrato  tc ON tc.id = v.tipo_contrato;


-- ──────────────────────────────────────────────────────────
-- v_candidato
-- candidato.compania           → db_column="compania"       → compania
-- datos_candidato.candidato    → db_column="candidato"      → candidato  ✓ (era candidato_id)
-- datos_candidato.tipo_documento → db_column="tipo_documento" → tipo_documento
-- ──────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW v_candidato AS
SELECT
    ca.id,
    ca.compania                 AS compania_id,
    c.descripcion               AS compania_descripcion,
    ca.id_interno,
    dc.tipo_documento           AS tipo_documento_id,
    td.descripcion              AS tipo_documento_descripcion,
    dc.numero_documento,
    dc.primer_nombre,
    dc.segundo_nombre,
    dc.primer_apellido,
    dc.segundo_apellido,
    CONCAT_WS(' ',
        NULLIF(dc.primer_nombre,    ''),
        NULLIF(dc.segundo_nombre,   ''),
        NULLIF(dc.primer_apellido,  ''),
        NULLIF(dc.segundo_apellido, '')
    )                           AS nombre_completo,
    dc.email,
    dc.telefono,
    ca.fecha_creacion,
    ca.usuario_creacion,
    ca.fecha_modificacion,
    ca.usuario_modificacion
FROM candidato ca
INNER JOIN compania        c  ON c.id  = ca.compania
LEFT  JOIN datos_candidato dc ON dc.candidato    = ca.id
LEFT  JOIN tipo_documento  td ON td.id = dc.tipo_documento;


-- ──────────────────────────────────────────────────────────
-- v_postulacion
-- postulacion.compania  → db_column="compania"  → compania
-- postulacion.vacante   → db_column="vacante"   → vacante
-- postulacion.candidato → db_column="candidato" → candidato
-- postulacion.estado    → db_column="estado"    → estado
-- datos_candidato.candidato → db_column="candidato" → candidato
-- ──────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW v_postulacion AS
SELECT
    p.id,
    p.compania                  AS compania_id,
    c.descripcion               AS compania_descripcion,
    p.id_interno,
    p.vacante                   AS vacante_id,
    v.descripcion               AS vacante_descripcion,
    p.candidato                 AS candidato_id,
    CONCAT_WS(' ',
        NULLIF(dc.primer_nombre,    ''),
        NULLIF(dc.segundo_nombre,   ''),
        NULLIF(dc.primer_apellido,  ''),
        NULLIF(dc.segundo_apellido, '')
    )                           AS candidato_nombre_completo,
    dc.email                    AS candidato_email,
    dc.numero_documento         AS candidato_documento,
    p.estado                    AS estado_id,
    ep.descripcion              AS estado_descripcion,
    p.descripcion               AS observaciones,
    p.fecha_postulacion,
    p.usuario_postulacion,
    p.fecha_creacion,
    p.usuario_creacion,
    p.fecha_modificacion,
    p.usuario_modificacion
FROM postulacion p
INNER JOIN compania           c  ON c.id  = p.compania
INNER JOIN vacante            v  ON v.id  = p.vacante
INNER JOIN candidato          ca ON ca.id = p.candidato
INNER JOIN estado_postulacion ep ON ep.id = p.estado
LEFT  JOIN datos_candidato    dc ON dc.candidato = ca.id;


-- ──────────────────────────────────────────────────────────
-- v_anexo_candidato
-- anexo_candidato.compania  → db_column="compania"  → compania
-- anexo_candidato.candidato → db_column="candidato" → candidato
-- datos_candidato.candidato → db_column="candidato" → candidato
-- ──────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW v_anexo_candidato AS
SELECT
    anx.id,
    anx.compania                AS compania_id,
    c.descripcion               AS compania_descripcion,
    anx.candidato               AS candidato_id,
    CONCAT_WS(' ',
        NULLIF(dc.primer_nombre,   ''),
        NULLIF(dc.primer_apellido, '')
    )                           AS candidato_nombre,
    anx.id_interno,
    anx.nombre_archivo,
    anx.tipo_archivo,
    anx.tamanio_bytes,
    anx.ruta_almacenamiento,
    anx.fecha_creacion,
    anx.usuario_creacion,
    anx.fecha_modificacion,
    anx.usuario_modificacion
FROM anexo_candidato anx
INNER JOIN compania        c  ON c.id  = anx.compania
INNER JOIN candidato       ca ON ca.id = anx.candidato
LEFT  JOIN datos_candidato dc ON dc.candidato = ca.id;


-- ──────────────────────────────────────────────────────────
-- v_evaluacion
-- evaluacion.compania           → db_column="compania"  → compania
-- evaluacion_habilidad.compania → db_column="compania"  → compania
-- evaluacion_habilidad.evaluacion → db_column="evaluacion" → evaluacion
-- ──────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW v_evaluacion AS
SELECT
    e.id,
    e.compania                  AS compania_id,
    c.descripcion               AS compania_descripcion,
    e.id_interno,
    e.descripcion,
    e.ind_activa,
    COUNT(eh.id)                AS total_habilidades,
    e.fecha_creacion,
    e.usuario_creacion,
    e.fecha_modificacion,
    e.usuario_modificacion
FROM evaluacion e
INNER JOIN compania             c  ON c.id = e.compania
LEFT  JOIN evaluacion_habilidad eh ON eh.evaluacion = e.id
                                  AND eh.compania   = e.compania
GROUP BY
    e.id,
    e.compania,
    c.descripcion,
    e.id_interno,
    e.descripcion,
    e.ind_activa,
    e.fecha_creacion,
    e.usuario_creacion,
    e.fecha_modificacion,
    e.usuario_modificacion;


-- ──────────────────────────────────────────────────────────
-- v_habilidad
-- pregunta.habilidad → db_column="habilidad" → habilidad
-- ind_activa = TRUE (booleano nativo PostgreSQL)
-- ──────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW v_habilidad AS
SELECT
    h.id,
    h.descripcion,
    h.dificultad,
    h.discriminacion,
    h.adivinabilidad,
    COUNT(CASE WHEN p.ind_activa = TRUE THEN 1 END) AS total_preguntas_activas,
    COUNT(p.id)                                      AS total_preguntas,
    h.fecha_creacion,
    h.fecha_modificacion
FROM habilidad h
LEFT JOIN pregunta p ON p.habilidad = h.id
GROUP BY
    h.id,
    h.descripcion,
    h.dificultad,
    h.discriminacion,
    h.adivinabilidad,
    h.fecha_creacion,
    h.fecha_modificacion;


-- ──────────────────────────────────────────────────────────
-- v_pregunta
-- pregunta.habilidad   → db_column="habilidad" → columna: habilidad
-- respuesta.pregunta   → db_column="pregunta"  → columna: pregunta
-- control_uso.pregunta → OneToOneField con db_column="pregunta"
--   db_column explícito prevalece siempre → columna: pregunta (sin _id)
-- ──────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW v_pregunta AS
SELECT
    p.id,
    p.habilidad                 AS habilidad_id,
    h.descripcion               AS habilidad_descripcion,
    p.contenido,
    p.criterio_a,
    p.criterio_b,
    p.criterio_c,
    p.ind_activa,
    COUNT(r.id)                 AS total_opciones,
    cu.tiempo_uso,
    cu.fecha_ultimo_uso,
    p.fecha_creacion,
    p.fecha_modificacion
FROM pregunta p
INNER JOIN habilidad   h  ON h.id       = p.habilidad
LEFT  JOIN respuesta   r  ON r.pregunta = p.id
LEFT  JOIN control_uso cu ON cu.pregunta    = p.id
GROUP BY
    p.id,
    p.habilidad,
    h.descripcion,
    p.contenido,
    p.criterio_a,
    p.criterio_b,
    p.criterio_c,
    p.ind_activa,
    cu.tiempo_uso,
    cu.fecha_ultimo_uso,
    p.fecha_creacion,
    p.fecha_modificacion;


-- ──────────────────────────────────────────────────────────
-- v_intento
-- intento.compania    → db_column="compania"    → compania
-- intento.postulacion → db_column="postulacion" → postulacion
-- intento.candidato   → db_column="candidato"   → candidato
-- intento.evaluacion  → db_column="evaluacion"  → evaluacion
-- intento.estado      → db_column="estado"      → estado
-- datos_candidato.candidato → db_column="candidato" → candidato
-- DATEDIFF → EXTRACT(EPOCH FROM ...) — PostgreSQL
-- ISNULL   → COALESCE                — PostgreSQL
-- GETDATE() → NOW()                  — PostgreSQL
-- ──────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW v_intento AS
SELECT
    i.id,
    i.compania                  AS compania_id,
    c.descripcion               AS compania_descripcion,
    i.id_interno,
    i.postulacion               AS postulacion_id,
    i.candidato                 AS candidato_id,
    CONCAT_WS(' ',
        NULLIF(dc.primer_nombre,    ''),
        NULLIF(dc.segundo_nombre,   ''),
        NULLIF(dc.primer_apellido,  ''),
        NULLIF(dc.segundo_apellido, '')
    )                           AS candidato_nombre_completo,
    i.evaluacion                AS evaluacion_id,
    e.descripcion               AS evaluacion_descripcion,
    i.estado                    AS estado_id,
    ei.descripcion              AS estado_descripcion,
    i.habilidad_estim,
    i.error_estandar,
    i.fecha_inicio,
    i.fecha_fin,
    EXTRACT(EPOCH FROM (COALESCE(i.fecha_fin, NOW()) - i.fecha_inicio))::INT
                                AS duracion_segundos,
    i.fecha_creacion,
    i.usuario_creacion,
    i.fecha_modificacion,
    i.usuario_modificacion
FROM intento i
INNER JOIN compania        c  ON c.id  = i.compania
INNER JOIN evaluacion      e  ON e.id  = i.evaluacion
INNER JOIN estado_intento  ei ON ei.id = i.estado
INNER JOIN candidato       ca ON ca.id = i.candidato
LEFT  JOIN datos_candidato dc ON dc.candidato = ca.id;


-- ──────────────────────────────────────────────────────────
-- v_reporte_postulacion
-- Aplica todas las correcciones anteriores.
-- TOP 1 subconsulta → DISTINCT ON (patrón PostgreSQL).
-- DATEDIFF(MINUTE) → EXTRACT(EPOCH FROM ...)::INT / 60
-- ──────────────────────────────────────────────────────────
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


SQL_ELIMINAR_VISTAS = """
DROP VIEW IF EXISTS v_reporte_postulacion;
DROP VIEW IF EXISTS v_intento;
DROP VIEW IF EXISTS v_pregunta;
DROP VIEW IF EXISTS v_habilidad;
DROP VIEW IF EXISTS v_evaluacion;
DROP VIEW IF EXISTS v_anexo_candidato;
DROP VIEW IF EXISTS v_postulacion;
DROP VIEW IF EXISTS v_candidato;
DROP VIEW IF EXISTS v_vacante;
DROP VIEW IF EXISTS v_analista;
DROP VIEW IF EXISTS v_usuario;
DROP VIEW IF EXISTS v_modulo;
DROP VIEW IF EXISTS v_rol;
DROP VIEW IF EXISTS v_unidad_org;
DROP VIEW IF EXISTS v_compania;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("empresa", "0002_datos_iniciales"),
    ]

    operations = [
        migrations.RunSQL(
            sql         = SQL_CREAR_VISTAS,
            reverse_sql = SQL_ELIMINAR_VISTAS,
        ),
    ]
