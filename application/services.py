from infrastructure.repositories import (
    EstudianteRepository, 
    GestionAcademicaRepository, 
    ProcesoInscripcionRepository, 
    OfertaRepository, 
    AdminRepository, 
    EvaluacionRepository,
    RegistroNacionalRepository
)
from application.Reportes import GeneradorReportes
from config.database import db

class AuthService:
    def __init__(self):
        self.repo = EstudianteRepository()
        self.repo_nacional = RegistroNacionalRepository()

    def login(self, cedula, password):
        if cedula == "1234567890" and password == "admin123": return "ADMIN"
        user = self.repo.buscar_por_cedula(cedula)
        if user and user.password == password: return user
        return None

    def consultar_datos_ciudadano(self, cedula):
        """Devuelve diccionario con nombres/apellidos si existe, o None."""
        return self.repo_nacional.obtener_datos_ciudadano(cedula)

    def registrar_estudiante(self, cedula, nombres, apellidos, email, telefono, password, confirm_pass):
        if password != confirm_pass: return False, "Contraseñas no coinciden."
        if not cedula.isdigit(): return False, "La cédula debe ser numérica."
        
        # 1. CONSULTA OFICIAL (SEGURIDAD)
        datos_oficiales = self.repo_nacional.obtener_datos_ciudadano(cedula)
        
        if not datos_oficiales:
            return False, "ERROR: La cédula no existe en el Registro Nacional."

        # 2. VALIDACIÓN DE DUPLICADOS
        if self.repo.buscar_por_cedula(cedula): 
            return False, "El usuario ya existe."
        
        # 3. REGISTRO (USANDO DATOS OFICIALES, NO LOS DEL INPUT)
        # Esto evita que alguien ponga la cédula de Juan y escriba el nombre "Pedro"
        exito = self.repo.crear(
            cedula, 
            datos_oficiales['nombres'],  # Forzado
            datos_oficiales['apellidos'], # Forzado
            email, 
            telefono, 
            password
        )
        return exito, "Registrado Correctamente" if exito else "Error en Base de Datos"

# ... (El resto de servicios se mantienen igual)
class AdminService:
    def __init__(self):
        self.repo_gestion = GestionAcademicaRepository()
        self.repo_proceso = ProcesoInscripcionRepository()
        self.repo_admin_stats = AdminRepository()
    def crear_carrera(self, nombre): return self.repo_gestion.crear_carrera(nombre, 9, 0)
    def actualizar_carrera(self, id_carrera, nombre): return self.repo_gestion.actualizar_carrera(id_carrera, nombre)
    def toggle_estado_carrera(self, id_carrera): return self.repo_gestion.alternar_estado_carrera(id_carrera)
    def eliminar_carrera(self, id_carrera): return self.repo_gestion.eliminar_carrera(id_carrera)
    def obtener_lista_carreras_activas(self): return self.repo_gestion.obtener_carreras_activas()
    def obtener_todas_carreras_admin(self): return self.repo_gestion.obtener_todas_carreras()
    def crear_periodo_semestral(self, anio, semestre, f_ini, f_fin): return self.repo_gestion.crear_periodo(f"{anio}-{semestre}", f_ini, f_fin)
    def eliminar_periodo(self, id_periodo):
        try: return self.repo_gestion.eliminar_periodo(id_periodo), "Periodo eliminado."
        except Exception as e: return False, str(e)
    def obtener_lista_periodos(self): return self.repo_gestion.obtener_periodos_activos()
    def crear_oferta_en_periodo(self, id_carrera, id_periodo, cupos): return self.repo_gestion.crear_oferta(id_carrera, id_periodo, cupos)
    def eliminar_oferta(self, id_oferta):
        try: return self.repo_gestion.eliminar_oferta(id_oferta), "Oferta eliminada."
        except Exception as e: return False, str(e)
    def obtener_ofertas_del_periodo(self, id_periodo): return self.repo_gestion.obtener_ofertas_por_periodo(id_periodo)
    def asignar_horarios_evaluacion(self, id_periodo, fecha, hora): return self.repo_proceso.asignar_horarios_evaluacion_por_periodo(id_periodo, fecha, hora)
    def obtener_inscripciones_pendientes(self): return self.repo_proceso.obtener_inscripciones_pendientes()
    def aceptar_inscripcion(self, id_inscripcion):
        try: return self.repo_proceso.aceptar_inscripcion(id_inscripcion), "Inscripción Aceptada"
        except Exception as e: return False, str(e)
    def rechazar_inscripcion(self, id_inscripcion):
        try: return self.repo_proceso.rechazar_inscripcion(id_inscripcion), "Inscripción Rechazada"
        except Exception as e: return False, str(e)
    def obtener_pendientes_calificacion(self): return self.repo_proceso.obtener_estudiantes_para_calificar()
    def cargar_notas_excel(self, ruta_archivo): return self.repo_proceso.cargar_notas_masivas_desde_excel(ruta_archivo)
    def obtener_matriz(self): return self.repo_proceso.obtener_matriz_final()
    def obtener_dashboard_stats(self): return self.repo_admin_stats.obtener_estadisticas()

class StudentService:
    def __init__(self):
        self.repo_oferta = OfertaRepository()
        self.repo_proceso = ProcesoInscripcionRepository()
        self.pdf_gen = GeneradorReportes()
    def ver_ofertas(self): return self.repo_oferta.obtener_disponibles()
    def inscribirse(self, estudiante, id_oferta, id_carrera):
        try: return self.repo_proceso.inscribir_estudiante(estudiante.id_estudiante, id_oferta, id_carrera), "Inscripción enviada."
        except Exception as e: return False, str(e)
    def ver_mis_procesos(self, estudiante):
        from sqlalchemy import text
        with db.get_connection() as conn:
            ins = conn.execute(text("SELECT c.nombreCarrera, i.estado, i.fechaInscripcion, p.nombrePeriodo FROM Inscripciones i JOIN Carreras c ON i.idCarrera=c.idCarrera JOIN OfertasAcademicas o ON i.idOferta=o.idOferta JOIN Periodos p ON o.idPeriodo=p.idPeriodo WHERE i.idEstudiante=:id"), {"id": estudiante.id_estudiante}).fetchall()
            exams = conn.execute(text("SELECT ev.nombreEvaluacion, ea.fechaVencimiento, ea.observaciones, ea.puntajeObtenido, ea.estado FROM EvaluacionesAsignadas ea JOIN Evaluaciones ev ON ea.idEvaluacion=ev.idEvaluacion WHERE ea.idEstudiante=:id"), {"id": estudiante.id_estudiante}).fetchall()
            return {"inscripciones": ins, "examenes": exams}
    def descargar_comprobante_examen(self, estudiante, nombre_examen, puntaje, estado, fecha): return self.pdf_gen.generar_comprobante_evaluacion(estudiante, nombre_examen, puntaje, estado, fecha)

class EvaluacionService:
    def __init__(self): self.repo = EvaluacionRepository()
    def obtener_matriz_calificaciones(self):
        raw_data = self.repo.obtener_matriz_consolidada()
        data_limpia = []
        for r in raw_data: data_limpia.append({"estudiante": r.Estudiante, "evaluacion": r.Evaluacion, "puntaje": f"{r.Puntaje:.2f}" if r.Puntaje is not None else "0.00", "estado": r.Estado, "obs": r.observaciones or "-"})
        return data_limpia