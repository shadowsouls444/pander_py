"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
evaluacion/services.py
CAPA DE IMPLEMENTACIÓN — Notificación y gestión de tokens
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
 
import secrets
import uuid
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
 
 
class ServicioPostulacion:
    """
    Gestiona el flujo completo al postular un candidato:
    1. Verifica que el token del trigger ya existe (lo creó SQL Server)
    2. Si no existe (entorno sin triggers), lo crea en Python
    3. Envía el correo de notificación al candidato
    """
 
    VIGENCIA_HORAS = 72
 
    @staticmethod
    def obtener_o_crear_token(compania: int, postulacion: int, evaluacion: int):
        """
        El trigger trg_postulacion_generar_token debería haber creado
        el token. Este método es el fallback si los triggers están desactivados
        (entornos de desarrollo sin SQL Server).
        """
        from candidatos.models import PostulacionToken, Postulacion
 
        token_existente = PostulacionToken.objects.filter(
            compania=compania,
            postulacion=postulacion,
        ).first()
 
        if token_existente:
            return token_existente
 
        postulacion = Postulacion.objects.get(id=postulacion, compania=compania)
        token_valor = uuid.uuid4().hex + uuid.uuid4().hex
        llave_valor = secrets.token_hex(32)
 
        return PostulacionToken.objects.create(
            compania      = compania,
            postulacion      = postulacion,
            evaluacion    = evaluacion,
            token            = token_valor,
            llave            = llave_valor,
            fecha_creacion   = timezone.now(),
            fecha_expiracion = timezone.now() + timedelta(hours=ServicioPostulacion.VIGENCIA_HORAS),
        )
 
    @staticmethod
    def enviar_notificacion(token_obj, candidato_datos, vacante_descripcion: str, base_url: str):
        """
        Envía el correo de invitación al candidato con el enlace de evaluación.
        El enlace incluye el token y la llave como parámetros de seguridad.
        """
        if not candidato_datos.email:
            return False
 
        enlace = (
            f"{base_url}/evaluacion/acceso"
            f"?token={token_obj.token}"
            f"&llave={token_obj.llave}"
        )
 
        nombre = f"{candidato_datos.primer_nombre} {candidato_datos.primer_apellido}"
        expiracion = token_obj.fecha_expiracion.strftime("%d/%m/%Y a las %H:%M")
 
        asunto = f"Pander — Invitación a evaluación de competencias: {vacante_descripcion}"
        mensaje = f"""
Hola {nombre},
 
Has sido postulado(a) al proceso de selección para la vacante:
  {vacante_descripcion}
 
Como parte del proceso, te invitamos a completar nuestra evaluación
de competencias blandas. El proceso toma aproximadamente 20-30 minutos.
 
Accede a tu evaluación con el siguiente enlace (válido hasta el {expiracion}):
 
  {enlace}
 
Recomendaciones:
  - Usa un computador o tablet (no teléfono celular)
  - Asegúrate de tener conexión estable a internet
  - Responde con honestidad; no hay respuestas incorrectas absolutas
  - Una vez iniciada la evaluación, complétala sin interrupciones
 
Si tienes preguntas, comunícate con el área de Recursos Humanos.
 
Mucho éxito,
Equipo Pander
        """.strip()
 
        try:
            send_mail(
                subject      = asunto,
                message      = mensaje,
                from_email   = settings.DEFAULT_FROM_EMAIL,
                recipient_list = [candidato_datos.email],
                fail_silently = False,
            )
            return True
        except Exception:
            return False
 
    @staticmethod
    def validar_token(token: str, llave: str) -> tuple:
        """
        Valida que el token exista, no haya expirado y la llave coincida.
        Retorna (token_obj, error_msg)
        """
        from candidatos.models import PostulacionToken
 
        try:
            token_obj = PostulacionToken.objects.select_related(
                "postulacion", "evaluacion"
            ).get(token=token)
        except PostulacionToken.DoesNotExist:
            return None, "Token inválido."
 
        if token_obj.llave != llave:
            return None, "Credenciales incorrectas."
 
        if token_obj.fecha_expiracion < timezone.now():
            return None, "El enlace de evaluación ha expirado. Contacta al área de RRHH."
 
        return token_obj, None
 