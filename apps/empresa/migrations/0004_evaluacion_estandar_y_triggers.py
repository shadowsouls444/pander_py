"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARCHIVO: empresa/migrations/0004_evaluacion_estandar_y_triggers.py
MOTOR:   PostgreSQL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Contenido:
  A) RunPython — banco de ítems estándar (sin cambios, es Python puro)
  B) RunSQL    — triggers reescritos en PL/pgSQL

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TABLA DE CONVERSIONES T-SQL → PL/pgSQL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  T-SQL                              PL/pgSQL
  ─────────────────────────────────────────────────────────
  CREATE TRIGGER … ON tabla          CREATE TRIGGER … ON tabla
  AFTER INSERT AS BEGIN … END        AFTER INSERT … EXECUTE FUNCTION f()
                                     + función separada RETURNS trigger

  SET NOCOUNT ON                     (no existe, no hace falta)
  DECLARE @var TYPE                  var TYPE;   (en DECLARE block)
  SET @var = valor                   var := valor;
  SELECT @var = col FROM ...         SELECT col INTO var FROM ...;
  IF condicion BEGIN … END           IF condicion THEN … END IF;
  IF NOT UPDATE(col) RETURN          IF OLD.col = NEW.col THEN RETURN NEW; END IF;

  inserted (tabla virtual)           NEW  (fila recién insertada/actualizada)
  deleted  (tabla virtual)           OLD  (fila antes de UPDATE/DELETE)

  GETDATE()                          NOW()
  DATEADD(HOUR, 72, GETDATE())       NOW() + INTERVAL '72 hours'
  CAST(GETDATE() AS DATE)            CURRENT_DATE
  ISNULL(x, y)                       COALESCE(x, y)
  TOP 1 … ORDER BY                   … ORDER BY … LIMIT 1
  SCOPEENTITY()                   (uso de RETURNING id en su lugar)
  NEWID()                            gen_random_uuid()   ← requiere pgcrypto
                                     o encode(gen_random_bytes(16),'hex')
  NVARCHAR(n)                        VARCHAR(n)  /  TEXT
  BIT                                BOOLEAN
  IF OBJECT(…) IS NOT NULL        DROP TRIGGER IF EXISTS …
    DROP TRIGGER …                   DROP FUNCTION IF EXISTS …
  GO                                 (no existe en PostgreSQL)

  UPDATE tabla SET col = val         UPDATE tabla SET col = val
    FROM … INNER JOIN inserted …       WHERE id = NEW.id   (NEW accesible directo)

  RETURN (en trigger sin valor)      RETURN NEW;   (INSERT/UPDATE)
                                     RETURN OLD;   (DELETE)
                                     RETURN NULL;  (cancelar operación)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARQUITECTURA DE TRIGGERS EN POSTGRESQL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
En PostgreSQL un trigger NO contiene lógica directamente.
Requiere dos objetos:
  1. FUNCTION  trg_fn_nombre() RETURNS trigger  → contiene la lógica
  2. TRIGGER   trg_nombre ON tabla              → invoca la función

El DROP también requiere ambos objetos:
  DROP TRIGGER IF EXISTS trg_nombre ON tabla;
  DROP FUNCTION IF EXISTS trg_fn_nombre();

Para usar gen_random_uuid() habilitar la extensión:
  CREATE EXTENSION IF NOT EXISTS pgcrypto;
(incluido en SQL_TRIGGERS al inicio)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from django.db import migrations
from django.utils import timezone


# ════════════════════════════════════════════════════════════
# A) DATOS: EVALUACIÓN ESTÁNDAR (Python puro, sin cambios)
# ════════════════════════════════════════════════════════════

def insertar_evaluacion_estandar(apps, schema_editor):
    now = timezone.now()

    Habilidad           = apps.get_model("evaluacion", "Habilidad")
    Pregunta            = apps.get_model("evaluacion", "Pregunta")
    Respuesta           = apps.get_model("evaluacion", "Respuesta")
    ControlUso          = apps.get_model("evaluacion", "ControlUso")
    Evaluacion          = apps.get_model("evaluacion", "Evaluacion")
    EvaluacionHabilidad = apps.get_model("evaluacion", "EvaluacionHabilidad")
    Compania            = apps.get_model("empresa",    "Compania")

    compania_sistema = Compania.objects.get(nit="0000")
    uid = 1

    evaluacion = Evaluacion.objects.create(
        compania         = compania_sistema,
        id_interno       = 1,
        descripcion      = "Evaluación Estándar de Competencias Blandas - Pander",
        ind_activa       = True,
        usuario_creacion = uid,
        fecha_creacion   = now,
    )

    banco = [
        # ────────────────────────────────────────────────────
        # HABILIDAD 1: COMUNICACIÓN EFECTIVA
        # ────────────────────────────────────────────────────
        {
            "habilidad": {
                "descripcion": "Comunicación Efectiva",
                "dificultad": 0.0, "discriminacion": 1.2, "adivinabilidad": 0.1,
            },
            "preguntas": [
                {
                    "contenido": "Durante una reunión de equipo, un colega presenta una idea con la que no estás de acuerdo. ¿Cuál es la mejor forma de expresar tu desacuerdo?",
                    "criterio_a": 1.4, "criterio_b": -0.5, "criterio_c": 0.10,
                    "respuestas": [
                        ("Esperar a que termine, luego expresar tu punto de vista con argumentos concretos y un tono respetuoso.", True),
                        ("Interrumpirlo para corregirlo de inmediato antes de que la idea se extienda.", False),
                        ("Guardar silencio en la reunión y comentarlo después con otros compañeros.", False),
                        ("Asentir durante la reunión y enviar un correo crítico al líder después.", False),
                    ]
                },
                {
                    "contenido": "Debes explicar un proceso técnico complejo a un cliente sin conocimientos del área. ¿Qué estrategia usas?",
                    "criterio_a": 1.3, "criterio_b": 0.2, "criterio_c": 0.10,
                    "respuestas": [
                        ("Usar analogías cotidianas, evitar tecnicismos y confirmar la comprensión con preguntas al cliente.", True),
                        ("Enviarle la documentación técnica completa para que la revise a su ritmo.", False),
                        ("Delegar la explicación a un colega más técnico.", False),
                        ("Explicar el proceso tal como lo harías con un par técnico, usando todos los términos precisos.", False),
                    ]
                },
                {
                    "contenido": "Recibes retroalimentación negativa de tu jefe sobre un informe que preparaste. ¿Cómo respondes?",
                    "criterio_a": 1.5, "criterio_b": 0.5, "criterio_c": 0.10,
                    "respuestas": [
                        ("Agradecer la retroalimentación, pedir claridad sobre los puntos específicos a mejorar y ajustar el informe.", True),
                        ("Defender tu trabajo explicando por qué tomaste cada decisión.", False),
                        ("Aceptar sin preguntar nada y rehacer el informe desde cero.", False),
                        ("Sentirte desmotivado y evitar presentar informes en el futuro.", False),
                    ]
                },
                {
                    "contenido": "Necesitas comunicar una decisión impopular a tu equipo (recorte de beneficios). ¿Cómo lo haces?",
                    "criterio_a": 1.6, "criterio_b": 1.0, "criterio_c": 0.10,
                    "respuestas": [
                        ("Reunir al equipo, explicar el contexto y las razones, escuchar sus reacciones y abrir espacio para preguntas.", True),
                        ("Enviar un correo formal para evitar confrontaciones directas.", False),
                        ("Pedirle a Recursos Humanos que lo comunique por ti.", False),
                        ("Anunciarlo brevemente al final de una reunión para minimizar el impacto.", False),
                    ]
                },
                {
                    "contenido": "En un correo profesional, ¿cuál de las siguientes aperturas comunica mejor asertividad y profesionalismo?",
                    "criterio_a": 1.1, "criterio_b": -1.0, "criterio_c": 0.15,
                    "respuestas": [
                        ("Espero que este correo te encuentre bien. Te escribo para coordinar los siguientes pasos del proyecto.", True),
                        ("Hola, soy yo de nuevo, perdona que insista pero necesito una respuesta.", False),
                        ("Estimado, como ya le había mencionado anteriormente, le reitero mi solicitud.", False),
                        ("Buenos días. Adjunto el archivo. Saludos.", False),
                    ]
                },
                {
                    "contenido": "Durante una presentación ante directivos, notas que el público parece confundido. ¿Qué haces?",
                    "criterio_a": 1.4, "criterio_b": 0.8, "criterio_c": 0.10,
                    "respuestas": [
                        ("Pausar, preguntar si hay dudas sobre lo presentado y reformular la explicación con un ejemplo práctico.", True),
                        ("Continuar la presentación para no perder el hilo y aclarar dudas al final.", False),
                        ("Acelerar el ritmo para terminar antes de que el ambiente se tense más.", False),
                        ("Reducir el contenido restante y finalizar la presentación cuanto antes.", False),
                    ]
                },
            ]
        },
        # ────────────────────────────────────────────────────
        # HABILIDAD 2: TRABAJO EN EQUIPO
        # ────────────────────────────────────────────────────
        {
            "habilidad": {
                "descripcion": "Trabajo en Equipo",
                "dificultad": 0.1, "discriminacion": 1.3, "adivinabilidad": 0.1,
            },
            "preguntas": [
                {
                    "contenido": "Tu equipo tiene un plazo ajustado y un miembro no está entregando a tiempo. ¿Qué haces?",
                    "criterio_a": 1.5, "criterio_b": 0.3, "criterio_c": 0.10,
                    "respuestas": [
                        ("Hablar con esa persona, entender sus bloqueos, ofrecer apoyo y, si es necesario, redistribuir tareas con el acuerdo del equipo.", True),
                        ("Asumir sus tareas tú mismo para asegurar la entrega sin involucrar al resto.", False),
                        ("Escalar el problema al líder inmediatamente para que tome acción.", False),
                        ("Ignorarlo y enfocarte en tus propias entregas.", False),
                    ]
                },
                {
                    "contenido": "En un proyecto grupal, ¿cuál es la característica más importante de un colaborador efectivo?",
                    "criterio_a": 1.2, "criterio_b": -0.8, "criterio_c": 0.15,
                    "respuestas": [
                        ("Cumplir sus responsabilidades, comunicar proactivamente sus avances y apoyar a otros cuando puede.", True),
                        ("Ser el miembro más creativo y proponer la mayoría de las ideas.", False),
                        ("Evitar los conflictos internos y mantener la armonía a cualquier costo.", False),
                        ("Ser el que más horas trabaja para demostrar compromiso.", False),
                    ]
                },
                {
                    "contenido": "Tu equipo toma una decisión con la que no estás de acuerdo pero que fue votada por mayoría. ¿Qué haces?",
                    "criterio_a": 1.4, "criterio_b": 0.6, "criterio_c": 0.10,
                    "respuestas": [
                        ("Expresar tu desacuerdo con argumentos en el momento, aceptar la decisión colectiva y comprometerte a ejecutarla bien.", True),
                        ("Acatar la decisión en silencio pero desvincularte del resultado.", False),
                        ("Negarte a participar en la ejecución hasta que se reconsidere.", False),
                        ("Buscar aliados para revocar la decisión antes de que se implemente.", False),
                    ]
                },
                {
                    "contenido": "¿Cuál de estos comportamientos destruye más rápidamente la confianza en un equipo?",
                    "criterio_a": 1.3, "criterio_b": -0.3, "criterio_c": 0.10,
                    "respuestas": [
                        ("Atribuirse méritos de logros colectivos sin reconocer la contribución de otros.", True),
                        ("Expresar opiniones contrarias a las del líder en reuniones grupales.", False),
                        ("Pedir ayuda cuando no se sabe cómo resolver algo.", False),
                        ("Llegar tarde ocasionalmente a reuniones no críticas.", False),
                    ]
                },
                {
                    "contenido": "Te asignan a un equipo con personas de áreas muy distintas a la tuya. ¿Cómo abordas el trabajo conjunto?",
                    "criterio_a": 1.4, "criterio_b": 0.1, "criterio_c": 0.10,
                    "respuestas": [
                        ("Mostrar interés genuino por el enfoque de cada área, identificar sinergias y establecer un lenguaje común para el proyecto.", True),
                        ("Concentrarte en los aspectos técnicos de tu especialidad y dejar que cada uno haga lo suyo.", False),
                        ("Esperar instrucciones claras del líder antes de interactuar con los demás.", False),
                        ("Asumir el liderazgo informal del grupo desde el inicio para evitar descoordinación.", False),
                    ]
                },
                {
                    "contenido": "Al finalizar un proyecto exitoso, ¿cuál es la actitud más valiosa para el equipo?",
                    "criterio_a": 1.2, "criterio_b": -0.5, "criterio_c": 0.15,
                    "respuestas": [
                        ("Reflexionar sobre lo que funcionó y lo que no, documentar aprendizajes y reconocer públicamente los aportes individuales.", True),
                        ("Celebrar el éxito y pasar rápidamente al siguiente proyecto.", False),
                        ("Presentar los resultados al área directiva destacando tu contribución personal.", False),
                        ("Identificar a los miembros menos productivos para señalarlo al líder.", False),
                    ]
                },
            ]
        },
        # ────────────────────────────────────────────────────
        # HABILIDAD 3: ADAPTABILIDAD
        # ────────────────────────────────────────────────────
        {
            "habilidad": {
                "descripcion": "Adaptabilidad",
                "dificultad": 0.2, "discriminacion": 1.4, "adivinabilidad": 0.1,
            },
            "preguntas": [
                {
                    "contenido": "A mitad de un proyecto importante, la dirección cambia el objetivo principal. ¿Cómo reaccionas?",
                    "criterio_a": 1.6, "criterio_b": 0.7, "criterio_c": 0.10,
                    "respuestas": [
                        ("Comprender las razones del cambio, evaluar el impacto en el plan actual y reorganizar las prioridades con el equipo.", True),
                        ("Expresar tu malestar y resistirte hasta que se justifique el cambio por escrito.", False),
                        ("Continuar con el plan original y adaptar la entrega al final.", False),
                        ("Esperar a que el caos se estabilice antes de tomar cualquier acción.", False),
                    ]
                },
                {
                    "contenido": "Te asignan una tarea fuera de tu área de expertise con un plazo corto. ¿Qué haces?",
                    "criterio_a": 1.5, "criterio_b": 0.4, "criterio_c": 0.10,
                    "respuestas": [
                        ("Aceptar el reto, identificar los recursos disponibles para aprender rápido y pedir apoyo puntual a quien domine el tema.", True),
                        ("Rechazar la tarea explicando que no es tu área de responsabilidad.", False),
                        ("Aceptarla sin decir nada y entregarla sin importar la calidad del resultado.", False),
                        ("Negociar el plazo pero no la tarea.", False),
                    ]
                },
                {
                    "contenido": "Tu empresa adopta una nueva herramienta digital que reemplaza el proceso que tú dominabas. ¿Cuál es tu actitud?",
                    "criterio_a": 1.3, "criterio_b": -0.2, "criterio_c": 0.10,
                    "respuestas": [
                        ("Ver la oportunidad de aprender algo nuevo, explorar la herramienta activamente y compartir los aprendizajes con el equipo.", True),
                        ("Resistirte hasta que se demuestre que la herramienta es mejor que el proceso actual.", False),
                        ("Seguir usando el proceso anterior de forma paralela por si la nueva herramienta falla.", False),
                        ("Aceptar la herramienta pero sin profundizar en su uso más allá de lo básico.", False),
                    ]
                },
                {
                    "contenido": "¿Cuál de estas actitudes describe mejor a una persona con alta adaptabilidad en entornos de incertidumbre?",
                    "criterio_a": 1.4, "criterio_b": 0.0, "criterio_c": 0.10,
                    "respuestas": [
                        ("Mantiene la calma, busca información disponible, toma decisiones con lo que tiene y ajusta conforme aparecen datos nuevos.", True),
                        ("Espera a tener toda la información antes de actuar.", False),
                        ("Sigue los procedimientos establecidos sin desviarse aunque el contexto haya cambiado.", False),
                        ("Delega las decisiones difíciles a su supervisor para evitar errores.", False),
                    ]
                },
                {
                    "contenido": "Has trabajado dos años en un proceso específico. La empresa decide rediseñarlo completamente. ¿Qué sientes y cómo actúas?",
                    "criterio_a": 1.5, "criterio_b": 0.9, "criterio_c": 0.10,
                    "respuestas": [
                        ("Reconoces que puede ser difícil soltar algo que dominabas, pero aportas tu experiencia para que el nuevo proceso sea mejor.", True),
                        ("Sientes que tu trabajo anterior fue en vano y te desmotivas.", False),
                        ("Te opones al cambio argumentando que el proceso actual funciona bien.", False),
                        ("Aceptas el cambio de manera pasiva sin aportar nada al nuevo diseño.", False),
                    ]
                },
                {
                    "contenido": "Trabajas en un proyecto remoto con un equipo en zona horaria diferente. ¿Cómo te adaptas?",
                    "criterio_a": 1.3, "criterio_b": -0.6, "criterio_c": 0.10,
                    "respuestas": [
                        ("Ajustas tu esquema de comunicación, estableces acuerdos claros de disponibilidad y usas herramientas asíncronas efectivamente.", True),
                        ("Insistes en tener reuniones en tu horario habitual.", False),
                        ("Reduces la comunicación al mínimo para evitar conflictos de horario.", False),
                        ("Solicitas que el equipo remoto ajuste su horario al tuyo.", False),
                    ]
                },
            ]
        },
        # ────────────────────────────────────────────────────
        # HABILIDAD 4: RESOLUCIÓN DE PROBLEMAS
        # ────────────────────────────────────────────────────
        {
            "habilidad": {
                "descripcion": "Resolución de Problemas",
                "dificultad": 0.3, "discriminacion": 1.5, "adivinabilidad": 0.1,
            },
            "preguntas": [
                {
                    "contenido": "Un cliente reporta un error crítico en producción un viernes a las 5 PM. ¿Cuál es tu primer paso?",
                    "criterio_a": 1.7, "criterio_b": 0.6, "criterio_c": 0.10,
                    "respuestas": [
                        ("Evaluar el impacto del error, contener el daño de inmediato y escalar al equipo necesario para resolverlo.", True),
                        ("Documentar el error y dejarlo registrado para atenderlo el lunes.", False),
                        ("Contactar al cliente para decirle que se atenderá el próximo día hábil.", False),
                        ("Esperar a que otros miembros del equipo lo detecten y actúen primero.", False),
                    ]
                },
                {
                    "contenido": "Tienes dos soluciones posibles para un problema: una rápida pero temporal, y otra lenta pero definitiva. ¿Qué consideras para decidir?",
                    "criterio_a": 1.5, "criterio_b": 0.8, "criterio_c": 0.10,
                    "respuestas": [
                        ("El impacto inmediato del problema, los recursos disponibles y si la solución temporal no genera riesgos adicionales.", True),
                        ("Siempre elegir la solución definitiva independientemente del tiempo que tome.", False),
                        ("Siempre la solución rápida para no detener el flujo de trabajo.", False),
                        ("Consultar al cliente cuál prefiere sin dar tu recomendación profesional.", False),
                    ]
                },
                {
                    "contenido": "Identificas un problema recurrente en tu área que nadie más ha reportado. ¿Qué haces?",
                    "criterio_a": 1.4, "criterio_b": 0.2, "criterio_c": 0.10,
                    "respuestas": [
                        ("Analizar la causa raíz, documentar el patrón, proponer una solución y presentarla a tu líder.", True),
                        ("Resolverlo cada vez que aparece sin comunicarlo para no parecer crítico.", False),
                        ("Esperar a que otros lo noten para abordar el tema en conjunto.", False),
                        ("Reportarlo sin proponer solución para no exceder tu rol.", False),
                    ]
                },
                {
                    "contenido": "¿Cuál de estas técnicas es más útil para encontrar la causa raíz de un problema complejo?",
                    "criterio_a": 1.3, "criterio_b": -0.4, "criterio_c": 0.15,
                    "respuestas": [
                        ("Los 5 Por Qué: preguntar '¿por qué?' de forma sucesiva hasta llegar al origen del problema.", True),
                        ("Buscar inmediatamente a quien cometió el error para asignar responsabilidad.", False),
                        ("Aplicar la solución más común usada en problemas similares sin analizar el caso.", False),
                        ("Reunir al equipo en lluvia de ideas sin estructura para generar ideas.", False),
                    ]
                },
                {
                    "contenido": "Tu propuesta de solución a un problema fue rechazada por tu líder. ¿Cómo reaccionas?",
                    "criterio_a": 1.4, "criterio_b": 0.5, "criterio_c": 0.10,
                    "respuestas": [
                        ("Preguntar las razones del rechazo, incorporar ese feedback y presentar una versión mejorada o una alternativa.", True),
                        ("Aceptar el rechazo y no volver a proponer soluciones para evitar frustraciones.", False),
                        ("Implementar tu solución de todas formas convencido de que es la correcta.", False),
                        ("Buscar el apoyo de otros colegas para presionar al líder a reconsiderar.", False),
                    ]
                },
                {
                    "contenido": "Debes tomar una decisión importante con información incompleta y poco tiempo. ¿Qué haces?",
                    "criterio_a": 1.6, "criterio_b": 1.2, "criterio_c": 0.10,
                    "respuestas": [
                        ("Usar la información disponible, identificar los supuestos clave, tomar la decisión más razonada y prepararte para ajustar.", True),
                        ("Posponer la decisión hasta tener más información, sin importar el tiempo.", False),
                        ("Delegar la decisión a otro para no asumir el riesgo.", False),
                        ("Tomar la decisión basándote en la intuición sin analizar la información disponible.", False),
                    ]
                },
            ]
        },
        # ────────────────────────────────────────────────────
        # HABILIDAD 5: INTELIGENCIA EMOCIONAL
        # ────────────────────────────────────────────────────
        {
            "habilidad": {
                "descripcion": "Inteligencia Emocional",
                "dificultad": 0.4, "discriminacion": 1.6, "adivinabilidad": 0.1,
            },
            "preguntas": [
                {
                    "contenido": "Un colega te hace un comentario hiriente frente al equipo. ¿Cómo respondes en ese momento?",
                    "criterio_a": 1.7, "criterio_b": 0.9, "criterio_c": 0.10,
                    "respuestas": [
                        ("Mantener la calma en el momento, no reaccionar impulsivamente y abordar el tema con esa persona en privado después.", True),
                        ("Responder de inmediato con el mismo tono para que no se repita.", False),
                        ("Ignorarlo completamente y actuar como si no hubiera pasado nada.", False),
                        ("Quejarte con el líder del equipo inmediatamente.", False),
                    ]
                },
                {
                    "contenido": "Notas que un compañero lleva días visiblemente estresado y su rendimiento ha bajado. ¿Qué haces?",
                    "criterio_a": 1.5, "criterio_b": 0.3, "criterio_c": 0.10,
                    "respuestas": [
                        ("Acercarte de manera genuina, preguntar cómo está y ofrecer apoyo dentro de tus posibilidades.", True),
                        ("Reportarlo al líder para que tome acción correctiva.", False),
                        ("No intervenir porque cada quien debe gestionar sus propios problemas.", False),
                        ("Comentarlo con otros colegas para ver si ellos también lo han notado.", False),
                    ]
                },
                {
                    "contenido": "Recibes una crítica injusta en público de parte de tu líder. ¿Cuál es la respuesta más emocionalmente inteligente?",
                    "criterio_a": 1.6, "criterio_b": 1.1, "criterio_c": 0.10,
                    "respuestas": [
                        ("Reconocer el impacto que sentiste, no reaccionar en caliente y solicitar una conversación privada para aclarar el malentendido.", True),
                        ("Defenderte públicamente en ese momento con argumentos.", False),
                        ("Aceptar la crítica sin decir nada aunque sepas que es injusta.", False),
                        ("Evitar a tu líder durante varios días como señal de tu desacuerdo.", False),
                    ]
                },
                {
                    "contenido": "¿Cuál de estas conductas refleja mejor la autogestión emocional en un entorno de alta presión?",
                    "criterio_a": 1.4, "criterio_b": 0.0, "criterio_c": 0.10,
                    "respuestas": [
                        ("Identificar la emoción que estás experimentando, nombrarla internamente y elegir conscientemente tu respuesta antes de actuar.", True),
                        ("Reprimir las emociones negativas para que no afecten tu desempeño.", False),
                        ("Expresar abiertamente tu frustración para no acumular tensión.", False),
                        ("Desconectarte emocionalmente de la situación como mecanismo de protección.", False),
                    ]
                },
                {
                    "contenido": "Durante una negociación tensa, la otra parte eleva la voz. ¿Cómo respondes?",
                    "criterio_a": 1.5, "criterio_b": 0.7, "criterio_c": 0.10,
                    "respuestas": [
                        ("Mantener un tono calmado, no igualar la intensidad emocional y redirigir la conversación hacia los intereses comunes.", True),
                        ("Elevar también tu tono para demostrar que no te intimida.", False),
                        ("Salir de la reunión para evitar el conflicto.", False),
                        ("Ceder en tus puntos para calmar la situación rápidamente.", False),
                    ]
                },
                {
                    "contenido": "Acabas de cometer un error significativo en el trabajo. ¿Cuál es la respuesta emocionalmente más saludable y profesional?",
                    "criterio_a": 1.6, "criterio_b": 0.5, "criterio_c": 0.10,
                    "respuestas": [
                        ("Reconocer el error, asumir la responsabilidad, analizar qué lo causó y proponer cómo evitarlo en el futuro.", True),
                        ("Minimizar el impacto del error para no afectar tu reputación.", False),
                        ("Buscar factores externos que justifiquen el error.", False),
                        ("Autoflagelarte de manera excesiva hasta el punto de paralizarte.", False),
                    ]
                },
            ]
        },
    ]

    orden_habilidad = 1
    for bloque in banco:
        hab = bloque["habilidad"]
        habilidad = Habilidad.objects.create(
            descripcion    = hab["descripcion"],
            dificultad     = hab["dificultad"],
            discriminacion = hab["discriminacion"],
            adivinabilidad = hab["adivinabilidad"],
            fecha_creacion = now,
        )
        EvaluacionHabilidad.objects.create(
            compania         = compania_sistema,
            evaluacion       = evaluacion,
            habilidad        = habilidad,
            orden            = orden_habilidad,
            obligatoria      = True,
            usuario_creacion = uid,
            fecha_creacion   = now,
        )
        orden_habilidad += 1

        for preg in bloque["preguntas"]:
            pregunta = Pregunta.objects.create(
                habilidad      = habilidad,
                contenido      = preg["contenido"],
                criterio_a     = preg["criterio_a"],
                criterio_b     = preg["criterio_b"],
                criterio_c     = preg["criterio_c"],
                ind_activa     = True,
                fecha_creacion = now,
            )
            ControlUso.objects.create(
                pregunta       = pregunta,
                tiempo_uso     = 0,
                fecha_creacion = now,
            )
            for contenido_resp, es_correcta in preg["respuestas"]:
                Respuesta.objects.create(
                    pregunta       = pregunta,
                    contenido      = contenido_resp,
                    ind_correcta   = es_correcta,
                    peso           = 1.0 if es_correcta else 0.0,
                    fecha_creacion = now,
                )


def revertir_evaluacion_estandar(apps, schema_editor):
    Evaluacion = apps.get_model("evaluacion", "Evaluacion")
    Habilidad  = apps.get_model("evaluacion", "Habilidad")
    Evaluacion.objects.filter(id_interno=1).delete()
    Habilidad.objects.filter(descripcion__in=[
        "Comunicación Efectiva", "Trabajo en Equipo",
        "Adaptabilidad", "Resolución de Problemas", "Inteligencia Emocional",
    ]).delete()


# ════════════════════════════════════════════════════════════
# B) TRIGGERS — PL/pgSQL (PostgreSQL)
# ════════════════════════════════════════════════════════════
# Cada trigger se compone de:
#   1) CREATE OR REPLACE FUNCTION trg_fn_*() RETURNS trigger
#   2) DROP TRIGGER IF EXISTS + CREATE TRIGGER … EXECUTE FUNCTION trg_fn_*()
# ════════════════════════════════════════════════════════════

SQL_TRIGGERS = """

-- Extensión necesaria para gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS pgcrypto;


-- ══════════════════════════════════════════════════════════
-- TRIGGER 1: trg_postulacion_asignar_evaluacion
-- Al insertar una postulación:
--   1. Busca la evaluación activa de la compañía.
--   2. Si ind_evaluacion_vacante=TRUE prioriza evaluacion_vacante.
--   3. Crea el intento correspondiente en estado "En Progreso".
-- ══════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION trg_fn_postulacion_asignar_evaluacion()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_evaluacion  INTEGER;
    v_ind_ev_vacante BOOLEAN;
    v_intento_interno INTEGER;
    v_estado      INTEGER;
BEGIN
    -- Leer flag de la compañía
    SELECT ind_evaluacion_vacante
      INTO v_ind_ev_vacante
      FROM compania
     WHERE id = NEW.compania;

    -- Modo evaluacion_vacante: buscar asignación específica activa
    IF v_ind_ev_vacante = TRUE THEN
        SELECT evaluacion
          INTO v_evaluacion
          FROM evaluacion_vacante
         WHERE compania = NEW.compania
           AND vacante  = NEW.vacante
           AND ind_activa  = TRUE
           AND (fecha_fin IS NULL OR fecha_fin >= CURRENT_DATE)
         ORDER BY fecha_creacion DESC
         LIMIT 1;
    END IF;

    -- Fallback: evaluación global activa de la compañía
    IF v_evaluacion IS NULL THEN
        SELECT id
          INTO v_evaluacion
          FROM evaluacion
         WHERE compania = NEW.compania
           AND ind_activa  = TRUE
         ORDER BY fecha_creacion ASC
         LIMIT 1;
    END IF;

    -- Crear intento solo si se encontró evaluación
    IF v_evaluacion IS NOT NULL THEN

        SELECT COALESCE(MAX(id_interno), 0) + 1
          INTO v_intento_interno
          FROM intento
         WHERE compania = NEW.compania;

        SELECT id
          INTO v_estado
          FROM estado_intento
         WHERE descripcion = 'En Progreso'
         LIMIT 1;

        INSERT INTO intento (
            compania,
            id_interno,
            postulacion,
            candidato,
            evaluacion,
            estado,
            fecha_inicio,
            fecha_creacion
        ) VALUES (
            NEW.compania,
            v_intento_interno,
            NEW.id,
            NEW.candidato,
            v_evaluacion,
            v_estado,
            NOW(),
            NOW()
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
-- TRIGGER 2: trg_postulacion_generar_token
-- Al insertar una postulación, genera token y llave
-- usando gen_random_uuid() (pgcrypto) con vigencia 72 horas.
-- Toma la evaluación del intento recién creado por trigger 1.
-- ══════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION trg_fn_postulacion_generar_token()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_evaluacion INTEGER;
    v_token         TEXT;
    v_llave         TEXT;
BEGIN
    -- Obtener evaluación del intento creado por trigger 1
    SELECT evaluacion
      INTO v_evaluacion
      FROM intento
     WHERE compania    = NEW.compania
       AND postulacion = NEW.id
     ORDER BY fecha_creacion DESC
     LIMIT 1;

    -- Generar token: dos UUIDs sin guiones concatenados
    v_token := REPLACE(gen_random_uuid()::TEXT, '-', '')
            || REPLACE(gen_random_uuid()::TEXT, '-', '');

    -- Generar llave: dos UUIDs sin guiones concatenados
    v_llave := REPLACE(gen_random_uuid()::TEXT, '-', '')
            || REPLACE(gen_random_uuid()::TEXT, '-', '');

    INSERT INTO postulacion_token (
        compania,
        postulacion,
        evaluacion,
        token,
        llave,
        fecha_creacion,
        fecha_expiracion
    ) VALUES (
        NEW.compania,
        NEW.id,
        v_evaluacion,
        v_token,
        v_llave,
        NOW(),
        NOW() + INTERVAL '72 hours'
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
-- TRIGGER 3: trg_intento_actualizar_estado_postulacion
-- Cuando el estado de un intento cambia:
--   Completado → postulación pasa a "En Evaluación"
--   Expirado   → postulación vuelve a "Recibida"
-- Solo actúa si el campo estado realmente cambió.
-- ══════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION trg_fn_intento_actualizar_estado_postulacion()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_nuevo_estado TEXT;
    v_estado_post  INTEGER;
BEGIN
    -- Solo actuar si estado cambió efectivamente
    IF OLD.estado = NEW.estado THEN
        RETURN NEW;
    END IF;

    SELECT descripcion
      INTO v_nuevo_estado
      FROM estado_intento
     WHERE id = NEW.estado;

    IF v_nuevo_estado = 'Completado' THEN
        SELECT id
          INTO v_estado_post
          FROM estado_postulacion
         WHERE descripcion = 'En Evaluación'
         LIMIT 1;

        UPDATE postulacion
           SET estado          = v_estado_post,
               fecha_modificacion = NOW()
         WHERE id          = NEW.postulacion
           AND compania = NEW.compania;

    ELSIF v_nuevo_estado = 'Expirado' THEN
        SELECT id
          INTO v_estado_post
          FROM estado_postulacion
         WHERE descripcion = 'Recibida'
         LIMIT 1;

        UPDATE postulacion
           SET estado          = v_estado_post,
               fecha_modificacion = NOW()
         WHERE id          = NEW.postulacion
           AND compania = NEW.compania;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_intento_actualizar_estado_postulacion ON intento;
CREATE TRIGGER trg_intento_actualizar_estado_postulacion
    AFTER UPDATE ON intento
    FOR EACH ROW
    EXECUTE FUNCTION trg_fn_intento_actualizar_estado_postulacion();


-- ══════════════════════════════════════════════════════════
-- TRIGGER 4: trg_respuesta_candidato_control_uso
-- Cada INSERT en respuesta_candidato incrementa el contador
-- de uso del ítem correspondiente en control_uso.
-- En PostgreSQL NEW apunta a la fila insertada directamente,
-- no se necesita JOIN con tabla virtual "inserted".
-- ══════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION trg_fn_respuesta_candidato_control_uso()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE control_uso
       SET tiempo_uso        = tiempo_uso + 1,
           fecha_ultimo_uso  = NOW(),
           fecha_modificacion = NOW()
     WHERE pregunta = NEW.pregunta;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_respuesta_candidato_control_uso ON respuesta_candidato;
CREATE TRIGGER trg_respuesta_candidato_control_uso
    AFTER INSERT ON respuesta_candidato
    FOR EACH ROW
    EXECUTE FUNCTION trg_fn_respuesta_candidato_control_uso();


-- ══════════════════════════════════════════════════════════
-- TRIGGER 5: trg_nueva_compania_copiar_evaluacion
-- Al insertar una nueva compañía (que no sea la del sistema),
-- copia la evaluación estándar (NIT 00000) como evaluación
-- inicial de la nueva empresa suscrita (modelo SaaS).
--
-- SCOPEENTITY() no existe en PostgreSQL.
-- Se usa RETURNING id INTO variable en su lugar.
-- ══════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION trg_fn_nueva_compania_copiar_evaluacion()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_eval_sistema  INTEGER;
    v_nueva_eval    INTEGER;
    v_nueva_eval_pk    INTEGER;
    v_compania_sys  INTEGER;
BEGIN
    -- No copiar a la compañía del sistema
    IF NEW.nit = '00000' THEN
        RETURN NEW;
    END IF;

    -- Obtener ID de la compañía del sistema
    SELECT id
      INTO v_compania_sys
      FROM compania
     WHERE nit = '00000'
     LIMIT 1;

    IF v_compania_sys IS NULL THEN
        RETURN NEW;
    END IF;

    -- Obtener evaluación estándar activa del sistema
    SELECT id
      INTO v_eval_sistema
      FROM evaluacion
     WHERE compania = v_compania_sys
       AND ind_activa  = TRUE
     ORDER BY fecha_creacion ASC
     LIMIT 1;

    IF v_eval_sistema IS NULL THEN
        RETURN NEW;
    END IF;

    -- Calcular id_interno para la nueva compañía
    SELECT COALESCE(MAX(id_interno), 0) + 1
      INTO v_nueva_eval
      FROM evaluacion
     WHERE compania = NEW.id;

    -- Insertar evaluación en la nueva compañía y capturar PK con RETURNING
    INSERT INTO evaluacion (
        compania,
        id_interno,
        descripcion,
        ind_activa,
        fecha_creacion,
        usuario_creacion
    )
    SELECT
        NEW.id,
        v_nueva_eval,
        descripcion,
        TRUE,
        NOW(),
        1
      FROM evaluacion
     WHERE id = v_eval_sistema
    RETURNING id INTO v_nueva_eval_pk;

    -- Copiar habilidades asociadas a la nueva evaluación
    INSERT INTO evaluacion_habilidad (
        compania,
        evaluacion,
        habilidad,
        orden,
        obligatoria,
        fecha_creacion,
        usuario_creacion
    )
    SELECT
        NEW.id,
        v_nueva_eval_pk,
        habilidad,
        orden,
        obligatoria,
        NOW(),
        1
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
-- TRIGGER 6: trg_token_verificar_expiracion
-- Al insertar o actualizar un token, si ya está vencido
-- marca los intentos activos asociados como "Expirado".
-- En PostgreSQL se usa NOW() en lugar de GETDATE().
-- El JOIN con "inserted" se reemplaza con el acceso directo a NEW.
-- ══════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION trg_fn_token_verificar_expiracion()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_estado_expirado INTEGER;
    v_estado_progreso INTEGER;
BEGIN
    -- Solo actuar si el token ya venció
    IF NEW.fecha_expiracion >= NOW() THEN
        RETURN NEW;
    END IF;

    SELECT id INTO v_estado_expirado
      FROM estado_intento
     WHERE descripcion = 'Expirado'
     LIMIT 1;

    SELECT id INTO v_estado_progreso
      FROM estado_intento
     WHERE descripcion = 'En Progreso'
     LIMIT 1;

    UPDATE intento
       SET estado          = v_estado_expirado,
           fecha_modificacion = NOW()
     WHERE postulacion = NEW.postulacion
       AND compania    = NEW.compania
       AND estado      = v_estado_progreso;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_token_verificar_expiracion ON postulacion_token;
CREATE TRIGGER trg_token_verificar_expiracion
    AFTER INSERT OR UPDATE ON postulacion_token
    FOR EACH ROW
    EXECUTE FUNCTION trg_fn_token_verificar_expiracion();

"""

SQL_DROP_TRIGGERS = """
DROP TRIGGER IF EXISTS trg_token_verificar_expiracion             ON postulacion_token;
DROP TRIGGER IF EXISTS trg_nueva_compania_copiar_evaluacion       ON compania;
DROP TRIGGER IF EXISTS trg_respuesta_candidato_control_uso        ON respuesta_candidato;
DROP TRIGGER IF EXISTS trg_intento_actualizar_estado_postulacion  ON intento;
DROP TRIGGER IF EXISTS trg_postulacion_generar_token              ON postulacion;
DROP TRIGGER IF EXISTS trg_postulacion_asignar_evaluacion         ON postulacion;

DROP FUNCTION IF EXISTS trg_fn_token_verificar_expiracion();
DROP FUNCTION IF EXISTS trg_fn_nueva_compania_copiar_evaluacion();
DROP FUNCTION IF EXISTS trg_fn_respuesta_candidato_control_uso();
DROP FUNCTION IF EXISTS trg_fn_intento_actualizar_estado_postulacion();
DROP FUNCTION IF EXISTS trg_fn_postulacion_generar_token();
DROP FUNCTION IF EXISTS trg_fn_postulacion_asignar_evaluacion();
"""


class Migration(migrations.Migration):

    dependencies = [
        ("empresa", "0003_vistas_sql"),
    ]

    operations = [
        migrations.RunPython(
            insertar_evaluacion_estandar,
            reverse_code=revertir_evaluacion_estandar,
        ),
        migrations.RunSQL(
            sql         = SQL_TRIGGERS,
            reverse_sql = SQL_DROP_TRIGGERS,
        ),
    ]
