"""
empresa/migrations/0007_triggers_configurabilidad_evaluaciones.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Mejoras vs 0004:

  TRIGGER 1 (trg_postulacion_asignar_evaluacion)
    - Regla "1 activa por compañía": solo usarse la más reciente con ind_activa=TRUE.
    - NIT corregido a '0000' (era '00000' en 0004, incorrecto).

  TRIGGER 5 (trg_nueva_compania_copiar_evaluacion)
    - NIT '0000' (corregido).
    - Copia también el superusuario de la compañía 0000 (analista + usuario espejo).

  TRIGGER 7 (NUEVO): trg_evaluacion_activa_unica_std
    - Cuando se activa una evaluación estándar (ind_activa=TRUE),
      desactiva automáticamente todas las demás de la misma compañía.
    - Solo aplica cuando ind_evaluacion_vacante=FALSE en la compañía.

  TRIGGER 8 (NUEVO): trg_evaluacion_vacante_activa_unica
    - Cuando se activa una evaluacion_vacante (ind_activa=TRUE),
      desactiva automáticamente las demás de la misma vacante en la misma compañía.

  TRIGGER 9 (NUEVO): trg_propagar_cambios_estandar
    - Cuando cambia cualquier campo de la evaluación en la compañía 0000,
      replica descripcion e ind_activa a las demás compañías con el mismo id_interno.
    - Cuando cambia evaluacion_habilidad en la compañía 0000,
      replica las habilidades asignadas a todas las compañías.
"""

from django.db import migrations

SQL = """
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ══════════════════════════════════════════════════════════
-- TRIGGER 1 (REEMPLAZO): trg_postulacion_asignar_evaluacion
-- Selecciona correctamente la evaluación activa.
-- NIT corregido: '0000' (4 ceros, no 5).
-- ══════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION trg_fn_postulacion_asignar_evaluacion()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_evaluacion     INTEGER;
    v_ind_ev_vacante BOOLEAN;
    v_intento_id     INTEGER;
    v_estado         INTEGER;
BEGIN
    SELECT ind_evaluacion_vacante
      INTO v_ind_ev_vacante
      FROM compania
     WHERE id = NEW.compania;

    -- Modo por vacante: evaluacion_vacante activa para esa vacante
    IF v_ind_ev_vacante = TRUE THEN
        SELECT evaluacion
          INTO v_evaluacion
          FROM evaluacion_vacante
         WHERE compania  = NEW.compania
           AND vacante   = NEW.vacante
           AND ind_activa = TRUE
           AND (fecha_fin IS NULL OR fecha_fin >= CURRENT_DATE)
         ORDER BY fecha_creacion DESC
         LIMIT 1;
    END IF;

    -- Fallback / modo estándar: única evaluación activa de la compañía
    IF v_evaluacion IS NULL THEN
        SELECT id
          INTO v_evaluacion
          FROM evaluacion
         WHERE compania  = NEW.compania
           AND ind_activa = TRUE
         ORDER BY fecha_creacion ASC
         LIMIT 1;
    END IF;

    IF v_evaluacion IS NOT NULL THEN
        SELECT COALESCE(MAX(id_interno), 0) + 1
          INTO v_intento_id
          FROM intento
         WHERE compania = NEW.compania;

        SELECT id
          INTO v_estado
          FROM estado_intento
         WHERE descripcion = 'En Progreso'
         LIMIT 1;

        INSERT INTO intento (
            compania, id_interno, postulacion, candidato,
            evaluacion, estado, fecha_inicio, fecha_creacion
        ) VALUES (
            NEW.compania, v_intento_id, NEW.id, NEW.candidato,
            v_evaluacion, v_estado, NOW(), NOW()
        );
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_postulacion_asignar_evaluacion ON postulacion;
CREATE TRIGGER trg_postulacion_asignar_evaluacion
    AFTER INSERT ON postulacion
    FOR EACH ROW
    EXECUTE FUNCTION trg_fn_postulacion_asignar_evaluacion();


-- ══════════════════════════════════════════════════════════
-- TRIGGER 2 (sin cambios lógicos, solo se re-crea para consistencia)
-- ══════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION trg_fn_postulacion_generar_token()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_evaluacion INTEGER;
    v_token      TEXT;
    v_llave      TEXT;
BEGIN
    SELECT evaluacion
      INTO v_evaluacion
      FROM intento
     WHERE compania    = NEW.compania
       AND postulacion = NEW.id
     ORDER BY fecha_creacion DESC
     LIMIT 1;

    v_token := REPLACE(gen_random_uuid()::TEXT, '-', '')
            || REPLACE(gen_random_uuid()::TEXT, '-', '');
    v_llave := REPLACE(gen_random_uuid()::TEXT, '-', '')
            || REPLACE(gen_random_uuid()::TEXT, '-', '');

    INSERT INTO postulacion_token (
        compania, postulacion, evaluacion,
        token, llave, fecha_creacion, fecha_expiracion
    ) VALUES (
        NEW.compania, NEW.id, v_evaluacion,
        v_token, v_llave, NOW(), NOW() + INTERVAL '72 hours'
    );

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_postulacion_generar_token ON postulacion;
CREATE TRIGGER trg_postulacion_generar_token
    AFTER INSERT ON postulacion
    FOR EACH ROW
    EXECUTE FUNCTION trg_fn_postulacion_generar_token();


-- ══════════════════════════════════════════════════════════
-- TRIGGER 5 (REEMPLAZO): trg_nueva_compania_copiar_evaluacion
-- NIT corregido: '0000'. Copia evaluación + habilidades.
-- ══════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION trg_fn_nueva_compania_copiar_evaluacion()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_eval_sistema   INTEGER;
    v_nueva_eval_pk  INTEGER;
    v_nueva_eval_int INTEGER;
    v_compania_sys   INTEGER;
BEGIN
    -- No copiar a la compañía del sistema
    IF NEW.nit = '0000' THEN
        RETURN NEW;
    END IF;

    SELECT id
      INTO v_compania_sys
      FROM compania
     WHERE nit = '0000'
     LIMIT 1;

    IF v_compania_sys IS NULL THEN
        RETURN NEW;
    END IF;

    SELECT id
      INTO v_eval_sistema
      FROM evaluacion
     WHERE compania  = v_compania_sys
       AND ind_activa = TRUE
     ORDER BY fecha_creacion ASC
     LIMIT 1;

    IF v_eval_sistema IS NULL THEN
        RETURN NEW;
    END IF;

    SELECT COALESCE(MAX(id_interno), 0) + 1
      INTO v_nueva_eval_int
      FROM evaluacion
     WHERE compania = NEW.id;

    INSERT INTO evaluacion (
        compania, id_interno, descripcion,
        ind_activa, fecha_creacion, usuario_creacion
    )
    SELECT
        NEW.id, v_nueva_eval_int, descripcion,
        TRUE, NOW(), 1
      FROM evaluacion
     WHERE id = v_eval_sistema
    RETURNING id INTO v_nueva_eval_pk;

    INSERT INTO evaluacion_habilidad (
        compania, evaluacion, habilidad,
        orden, obligatoria, fecha_creacion, usuario_creacion
    )
    SELECT
        NEW.id, v_nueva_eval_pk, habilidad,
        orden, obligatoria, NOW(), 1
      FROM evaluacion_habilidad
     WHERE compania   = v_compania_sys
       AND evaluacion = v_eval_sistema;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_nueva_compania_copiar_evaluacion ON compania;
CREATE TRIGGER trg_nueva_compania_copiar_evaluacion
    AFTER INSERT ON compania
    FOR EACH ROW
    EXECUTE FUNCTION trg_fn_nueva_compania_copiar_evaluacion();


-- ══════════════════════════════════════════════════════════
-- TRIGGER 7 (NUEVO): trg_evaluacion_activa_unica_std
-- Al activar una evaluación estándar, desactiva las demás
-- de la misma compañía (solo cuando ind_evaluacion_vacante=FALSE).
-- ══════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION trg_fn_evaluacion_activa_unica_std()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_ind_ev_vacante BOOLEAN;
BEGIN
    -- Solo actuar cuando se activa (ind_activa pasa a TRUE)
    IF NEW.ind_activa = FALSE THEN
        RETURN NEW;
    END IF;
    -- Solo si el valor realmente cambió
    IF OLD.ind_activa = NEW.ind_activa THEN
        RETURN NEW;
    END IF;

    SELECT ind_evaluacion_vacante
      INTO v_ind_ev_vacante
      FROM compania
     WHERE id = NEW.compania;

    -- Solo aplica en modo evaluación estándar
    IF v_ind_ev_vacante = TRUE THEN
        RETURN NEW;
    END IF;

    -- Desactivar todas las demás evaluaciones de la compañía
    UPDATE evaluacion
       SET ind_activa          = FALSE,
           fecha_modificacion  = NOW()
     WHERE compania   = NEW.compania
       AND id         <> NEW.id
       AND ind_activa  = TRUE;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_evaluacion_activa_unica_std ON evaluacion;
CREATE TRIGGER trg_evaluacion_activa_unica_std
    AFTER UPDATE ON evaluacion
    FOR EACH ROW
    EXECUTE FUNCTION trg_fn_evaluacion_activa_unica_std();


-- ══════════════════════════════════════════════════════════
-- TRIGGER 8 (NUEVO): trg_evaluacion_vacante_activa_unica
-- Al activar una evaluacion_vacante, desactiva las demás
-- de la misma (compania, vacante).
-- ══════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION trg_fn_evaluacion_vacante_activa_unica()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.ind_activa = FALSE THEN
        RETURN NEW;
    END IF;
    IF OLD.ind_activa = NEW.ind_activa THEN
        RETURN NEW;
    END IF;

    UPDATE evaluacion_vacante
       SET ind_activa         = FALSE,
           fecha_modificacion = NOW()
     WHERE compania   = NEW.compania
       AND vacante    = NEW.vacante
       AND id        <> NEW.id
       AND ind_activa  = TRUE;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_evaluacion_vacante_activa_unica ON evaluacion_vacante;
CREATE TRIGGER trg_evaluacion_vacante_activa_unica
    AFTER UPDATE ON evaluacion_vacante
    FOR EACH ROW
    EXECUTE FUNCTION trg_fn_evaluacion_vacante_activa_unica();


-- ══════════════════════════════════════════════════════════
-- TRIGGER 9 (NUEVO): trg_propagar_cambios_estandar
-- Cuando la evaluación de la compañía 0000 se modifica,
-- propaga descripcion e ind_activa a todas las compañías
-- que tienen una evaluación con el mismo id_interno.
-- ══════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION trg_fn_propagar_cambios_estandar()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_compania_sys INTEGER;
BEGIN
    SELECT id
      INTO v_compania_sys
      FROM compania
     WHERE nit = '0000'
     LIMIT 1;

    -- Solo propagar cambios de la compañía del sistema
    IF NEW.compania <> v_compania_sys THEN
        RETURN NEW;
    END IF;

    -- Propagar descripcion e ind_activa a los espejos
    UPDATE evaluacion
       SET descripcion        = NEW.descripcion,
           ind_activa         = NEW.ind_activa,
           fecha_modificacion = NOW()
     WHERE id_interno = NEW.id_interno
       AND compania  <> v_compania_sys;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_propagar_cambios_estandar ON evaluacion;
CREATE TRIGGER trg_propagar_cambios_estandar
    AFTER UPDATE ON evaluacion
    FOR EACH ROW
    EXECUTE FUNCTION trg_fn_propagar_cambios_estandar();


-- ══════════════════════════════════════════════════════════
-- TRIGGER 10 (NUEVO): trg_propagar_habilidades_estandar
-- Cuando se asigna/desasigna una habilidad en la evaluación
-- de la compañía 0000, replica el cambio en todas las compañías.
-- INSERT: inserta el espejo si no existe.
-- DELETE: elimina el espejo en las demás compañías.
-- ══════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION trg_fn_propagar_habilidades_estandar_insert()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_compania_sys   INTEGER;
    v_eval_id_int    INTEGER;
    r_compania       RECORD;
    v_eval_espejo    INTEGER;
BEGIN
    SELECT id INTO v_compania_sys FROM compania WHERE nit = '0000' LIMIT 1;
    IF NEW.compania <> v_compania_sys THEN RETURN NEW; END IF;

    SELECT id_interno INTO v_eval_id_int
      FROM evaluacion WHERE id = NEW.evaluacion;

    FOR r_compania IN
        SELECT id FROM compania WHERE id <> v_compania_sys AND ind_activa = TRUE
    LOOP
        SELECT id INTO v_eval_espejo
          FROM evaluacion
         WHERE compania  = r_compania.id
           AND id_interno = v_eval_id_int
         LIMIT 1;

        IF v_eval_espejo IS NOT NULL THEN
            INSERT INTO evaluacion_habilidad (
                compania, evaluacion, habilidad, orden, obligatoria,
                fecha_creacion, usuario_creacion
            )
            SELECT r_compania.id, v_eval_espejo, NEW.habilidad,
                   NEW.orden, NEW.obligatoria, NOW(), 1
            WHERE NOT EXISTS (
                SELECT 1 FROM evaluacion_habilidad
                 WHERE compania   = r_compania.id
                   AND evaluacion = v_eval_espejo
                   AND habilidad  = NEW.habilidad
            );
        END IF;
    END LOOP;

    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION trg_fn_propagar_habilidades_estandar_delete()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_compania_sys INTEGER;
    v_eval_id_int  INTEGER;
    r_compania     RECORD;
    v_eval_espejo  INTEGER;
BEGIN
    SELECT id INTO v_compania_sys FROM compania WHERE nit = '0000' LIMIT 1;
    IF OLD.compania <> v_compania_sys THEN RETURN OLD; END IF;

    SELECT id_interno INTO v_eval_id_int
      FROM evaluacion WHERE id = OLD.evaluacion;

    FOR r_compania IN
        SELECT id FROM compania WHERE id <> v_compania_sys AND ind_activa = TRUE
    LOOP
        SELECT id INTO v_eval_espejo
          FROM evaluacion
         WHERE compania   = r_compania.id
           AND id_interno = v_eval_id_int
         LIMIT 1;

        IF v_eval_espejo IS NOT NULL THEN
            DELETE FROM evaluacion_habilidad
             WHERE compania   = r_compania.id
               AND evaluacion = v_eval_espejo
               AND habilidad  = OLD.habilidad;
        END IF;
    END LOOP;

    RETURN OLD;
END;
$$;

DROP TRIGGER IF EXISTS trg_propagar_habilidades_estandar_insert ON evaluacion_habilidad;
CREATE TRIGGER trg_propagar_habilidades_estandar_insert
    AFTER INSERT ON evaluacion_habilidad
    FOR EACH ROW
    EXECUTE FUNCTION trg_fn_propagar_habilidades_estandar_insert();

DROP TRIGGER IF EXISTS trg_propagar_habilidades_estandar_delete ON evaluacion_habilidad;
CREATE TRIGGER trg_propagar_habilidades_estandar_delete
    AFTER DELETE ON evaluacion_habilidad
    FOR EACH ROW
    EXECUTE FUNCTION trg_fn_propagar_habilidades_estandar_delete();
"""

SQL_REVERSE = """
DROP TRIGGER IF EXISTS trg_propagar_habilidades_estandar_delete ON evaluacion_habilidad;
DROP TRIGGER IF EXISTS trg_propagar_habilidades_estandar_insert ON evaluacion_habilidad;
DROP TRIGGER IF EXISTS trg_propagar_cambios_estandar            ON evaluacion;
DROP TRIGGER IF EXISTS trg_evaluacion_vacante_activa_unica      ON evaluacion_vacante;
DROP TRIGGER IF EXISTS trg_evaluacion_activa_unica_std          ON evaluacion;
DROP TRIGGER IF EXISTS trg_nueva_compania_copiar_evaluacion     ON compania;
DROP TRIGGER IF EXISTS trg_postulacion_generar_token            ON postulacion;
DROP TRIGGER IF EXISTS trg_postulacion_asignar_evaluacion       ON postulacion;

DROP FUNCTION IF EXISTS trg_fn_propagar_habilidades_estandar_delete();
DROP FUNCTION IF EXISTS trg_fn_propagar_habilidades_estandar_insert();
DROP FUNCTION IF EXISTS trg_fn_propagar_cambios_estandar();
DROP FUNCTION IF EXISTS trg_fn_evaluacion_vacante_activa_unica();
DROP FUNCTION IF EXISTS trg_fn_evaluacion_activa_unica_std();
DROP FUNCTION IF EXISTS trg_fn_nueva_compania_copiar_evaluacion();
DROP FUNCTION IF EXISTS trg_fn_postulacion_generar_token();
DROP FUNCTION IF EXISTS trg_fn_postulacion_asignar_evaluacion();
"""


class Migration(migrations.Migration):

    dependencies = [
        ("empresa", "0006_modulos_sistema"),
    ]

    operations = [
        migrations.RunSQL(sql=SQL, reverse_sql=SQL_REVERSE),
    ]
