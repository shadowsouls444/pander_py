"""
empresa/migrations/0004_evaluacion_estandar_y_triggers.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CORRECCIÓN CRÍTICA:
  La versión anterior usaba campos inexistentes en el estado
  histórico de la BD al correr esta migración:
    Pregunta(compania=..., evaluacion=...)    → TypeError
    Respuesta(compania=..., evaluacion=...)   → TypeError
    ControlUso(compania=..., evaluacion=..., habilidad=...) → TypeError

  Los campos reales en evaluacion.0001_initial son:
    Habilidad  → descripcion, dificultad, discriminacion, adivinabilidad,
                 compania (FK nullable) ← SÍ existe desde 0001
    Pregunta   → habilidad (FK), contenido, criterio_a/b/c, ind_activa
                 usuario_creacion, usuario_modificacion   ← SIN compania/evaluacion
    Respuesta  → pregunta (FK), contenido, ind_correcta, peso
                 usuario_creacion, usuario_modificacion   ← SIN compania/evaluacion
    ControlUso → pregunta (OneToOne PK), tiempo_uso       ← SIN compania/evaluacion/habilidad

  Los triggers SQL también se corrigen para usar solo las columnas
  reales de la BD en este estado:
    - Trigger 4: ya no filtra por compania en control_uso (columna no existe)
    - Trigger 5: copia preguntas/respuestas/control_uso sin compania/evaluacion
    - NIT corregido: '0000' (4 ceros) en todos los triggers
"""

from django.db import migrations
from django.utils import timezone


# ════════════════════════════════════════════════════════════
# A) RunPython — inserta datos iniciales
#    Usa SOLO los campos que existen en 0001_initial
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

    # Crear la evaluación estándar
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
                    "contenido": "Tienes dos soluciones posibles: una rápida pero temporal, y otra lenta pero definitiva. ¿Qué consideras para decidir?",
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
                    "contenido": "Recibes una crítica injusta en público de parte de tu líder. ¿Cuál es la respuesta emocionalmente más inteligente?",
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
        hab_data = bloque["habilidad"]

        # Habilidad: compania SÍ existe en 0001_initial
        habilidad = Habilidad.objects.create(
            compania       = compania_sistema,
            descripcion    = hab_data["descripcion"],
            dificultad     = hab_data["dificultad"],
            discriminacion = hab_data["discriminacion"],
            adivinabilidad = hab_data["adivinabilidad"],
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
            # Pregunta: SIN compania ni evaluacion (no existen en 0001_initial)
            pregunta = Pregunta.objects.create(
                habilidad      = habilidad,
                contenido      = preg["contenido"],
                criterio_a     = preg["criterio_a"],
                criterio_b     = preg["criterio_b"],
                criterio_c     = preg["criterio_c"],
                ind_activa     = True,
                fecha_creacion = now,
            )

            # ControlUso: SIN compania, evaluacion ni habilidad
            ControlUso.objects.create(
                pregunta       = pregunta,
                tiempo_uso     = 0,
                fecha_creacion = now,
            )

            for contenido_resp, es_correcta in preg["respuestas"]:
                # Respuesta: SIN compania ni evaluacion
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
    Compania   = apps.get_model("empresa",    "Compania")
    try:
        comp = Compania.objects.get(nit="0000")
        Evaluacion.objects.filter(compania=comp, id_interno=1).delete()
        Habilidad.objects.filter(compania=comp, descripcion__in=[
            "Comunicación Efectiva", "Trabajo en Equipo",
            "Adaptabilidad", "Resolución de Problemas", "Inteligencia Emocional",
        ]).delete()
    except Compania.DoesNotExist:
        pass


# ════════════════════════════════════════════════════════════
# B) TRIGGERS PL/pgSQL
#    Corregidos para usar solo columnas reales de la BD:
#    - Trigger 4: control_uso no tiene columna compania
#    - Trigger 5: pregunta/respuesta/control_uso sin compania/evaluacion
#    - NIT: '0000' (4 ceros) en todos los triggers
# ════════════════════════════════════════════════════════════

SQL_TRIGGERS = """

CREATE EXTENSION IF NOT EXISTS pgcrypto;


-- ══════════════════════════════════════════════════════════
-- TRIGGER 1: trg_postulacion_asignar_evaluacion
-- ══════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION trg_fn_postulacion_asignar_evaluacion()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_evaluacion      INTEGER;
    v_ind_ev_vacante  BOOLEAN;
    v_intento_interno INTEGER;
    v_estado          INTEGER;
BEGIN
    SELECT ind_evaluacion_vacante
      INTO v_ind_ev_vacante
      FROM compania
     WHERE id = NEW.compania;

    IF v_ind_ev_vacante = TRUE THEN
        SELECT evaluacion
          INTO v_evaluacion
          FROM evaluacion_vacante
         WHERE compania   = NEW.compania
           AND vacante    = NEW.vacante
           AND ind_activa = TRUE
           AND (fecha_fin IS NULL OR fecha_fin >= CURRENT_DATE)
         ORDER BY fecha_creacion DESC
         LIMIT 1;
    END IF;

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
          INTO v_intento_interno
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
            NEW.compania, v_intento_interno, NEW.id, NEW.candidato,
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
-- TRIGGER 2: trg_postulacion_generar_token
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
-- TRIGGER 3: trg_intento_actualizar_estado_postulacion
-- ══════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION trg_fn_intento_actualizar_estado_postulacion()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_nuevo_estado TEXT;
    v_estado_post  INTEGER;
BEGIN
    IF OLD.estado = NEW.estado THEN RETURN NEW; END IF;

    SELECT descripcion INTO v_nuevo_estado
      FROM estado_intento WHERE id = NEW.estado;

    IF v_nuevo_estado = 'Completado' THEN
        SELECT id INTO v_estado_post
          FROM estado_postulacion WHERE descripcion = 'En Evaluación' LIMIT 1;
        UPDATE postulacion
           SET estado = v_estado_post, fecha_modificacion = NOW()
         WHERE id = NEW.postulacion AND compania = NEW.compania;
    ELSIF v_nuevo_estado = 'Expirado' THEN
        SELECT id INTO v_estado_post
          FROM estado_postulacion WHERE descripcion = 'Recibida' LIMIT 1;
        UPDATE postulacion
           SET estado = v_estado_post, fecha_modificacion = NOW()
         WHERE id = NEW.postulacion AND compania = NEW.compania;
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
-- FIX: control_uso solo tiene columna 'pregunta' (PK).
--      No tiene columna compania en este estado de la BD.
-- ══════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION trg_fn_respuesta_candidato_control_uso()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE control_uso
       SET tiempo_uso       = tiempo_uso + 1,
           fecha_ultimo_uso = NOW()
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
-- NIT corregido: '0000' (4 ceros).
-- Copia evaluacion + evaluacion_habilidad + habilidades
-- + preguntas + respuestas + control_uso usando SOLO
-- las columnas reales de la BD en este estado.
-- ══════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION trg_fn_nueva_compania_copiar_evaluacion()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_eval_sistema  INTEGER;
    v_nueva_eval_pk INTEGER;
    v_nueva_eval_no INTEGER;
    v_compania_sys  INTEGER;
    v_hab_new       INTEGER;
    v_preg_new      INTEGER;
    r_hab           RECORD;
    r_preg          RECORD;
    r_resp          RECORD;
BEGIN
    IF NEW.nit = '0000' THEN RETURN NEW; END IF;

    SELECT id INTO v_compania_sys FROM compania WHERE nit = '0000' LIMIT 1;
    IF v_compania_sys IS NULL THEN RETURN NEW; END IF;

    SELECT id INTO v_eval_sistema
      FROM evaluacion
     WHERE compania = v_compania_sys AND ind_activa = TRUE
     ORDER BY fecha_creacion ASC LIMIT 1;
    IF v_eval_sistema IS NULL THEN RETURN NEW; END IF;

    SELECT COALESCE(MAX(id_interno), 0) + 1 INTO v_nueva_eval_no
      FROM evaluacion WHERE compania = NEW.id;

    INSERT INTO evaluacion (
        compania, id_interno, descripcion, ind_activa, fecha_creacion, usuario_creacion
    )
    SELECT NEW.id, v_nueva_eval_no, descripcion, TRUE, NOW(), 1
      FROM evaluacion WHERE id = v_eval_sistema
    RETURNING id INTO v_nueva_eval_pk;

    -- Copiar habilidades (habilidad SÍ tiene columna compania)
    FOR r_hab IN
        SELECT h.*
          FROM habilidad h
          JOIN evaluacion_habilidad eh
               ON eh.habilidad  = h.id
              AND eh.compania   = v_compania_sys
              AND eh.evaluacion = v_eval_sistema
         ORDER BY eh.orden
    LOOP
        INSERT INTO habilidad (
            compania, descripcion, dificultad, discriminacion, adivinabilidad,
            fecha_creacion, usuario_creacion
        ) VALUES (
            NEW.id, r_hab.descripcion, r_hab.dificultad,
            r_hab.discriminacion, r_hab.adivinabilidad, NOW(), 1
        ) RETURNING id INTO v_hab_new;

        INSERT INTO evaluacion_habilidad (
            compania, evaluacion, habilidad, orden, obligatoria,
            fecha_creacion, usuario_creacion
        )
        SELECT NEW.id, v_nueva_eval_pk, v_hab_new, eh.orden, eh.obligatoria, NOW(), 1
          FROM evaluacion_habilidad eh
         WHERE eh.compania  = v_compania_sys
           AND eh.evaluacion = v_eval_sistema
           AND eh.habilidad  = r_hab.id;

        -- Copiar preguntas: pregunta NO tiene columna compania en este estado
        FOR r_preg IN
            SELECT * FROM pregunta WHERE habilidad = r_hab.id
        LOOP
            INSERT INTO pregunta (
                habilidad, contenido,
                criterio_a, criterio_b, criterio_c, ind_activa,
                fecha_creacion, usuario_creacion
            ) VALUES (
                v_hab_new, r_preg.contenido,
                r_preg.criterio_a, r_preg.criterio_b, r_preg.criterio_c,
                r_preg.ind_activa, NOW(), 1
            ) RETURNING id INTO v_preg_new;

            -- Copiar respuestas: respuesta NO tiene columna compania
            FOR r_resp IN
                SELECT * FROM respuesta WHERE pregunta = r_preg.id
            LOOP
                INSERT INTO respuesta (
                    pregunta, contenido, ind_correcta, peso,
                    fecha_creacion, usuario_creacion
                ) VALUES (
                    v_preg_new, r_resp.contenido, r_resp.ind_correcta, r_resp.peso,
                    NOW(), 1
                );
            END LOOP;

            -- ControlUso: solo columna pregunta (PK)
            INSERT INTO control_uso (pregunta, tiempo_uso, fecha_creacion)
            VALUES (v_preg_new, 0, NOW());
        END LOOP;
    END LOOP;

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
-- ══════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION trg_fn_token_verificar_expiracion()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_estado_expirado INTEGER;
    v_estado_progreso INTEGER;
BEGIN
    IF NEW.fecha_expiracion >= NOW() THEN RETURN NEW; END IF;

    SELECT id INTO v_estado_expirado
      FROM estado_intento WHERE descripcion = 'Expirado' LIMIT 1;
    SELECT id INTO v_estado_progreso
      FROM estado_intento WHERE descripcion = 'En Progreso' LIMIT 1;

    UPDATE intento
       SET estado = v_estado_expirado, fecha_modificacion = NOW()
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
