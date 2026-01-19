from sqlalchemy import text
from domain.models import Estudiante, Carrera
from config.database import db
import pandas as pd

# ==========================================
# 1. GESTIÓN DE USUARIOS
# ==========================================
class EstudianteRepository:
    def buscar_por_cedula(self, cedula):
        with db.get_connection() as conn:
            res = conn.execute(text("SELECT * FROM Estudiantes WHERE cedula = :c"), {"c": cedula}).fetchone()
            if res:
                return Estudiante(res.idEstudiante, res.cedula, res.nombres, res.apellidos, 
                                  res.email, res.telefono, res.contrasena)
            return None

    def crear(self, cedula, nombres, apellidos, email, telefono, password):
        with db.get_connection() as conn:
            conn.execute(text("""
                INSERT INTO Estudiantes (cedula, nombres, apellidos, email, telefono, contrasena, estado)
                VALUES (:c, :n, :a, :e, :t, :p, 'Activo')
            """), {"c": cedula, "n": nombres, "a": apellidos, "e": email, "t": telefono, "p": password})
            conn.commit()
            return True

# ==========================================
# 2. VALIDACIÓN EXTERNA (MODIFICADO)
# ==========================================
class RegistroNacionalRepository:
    """Consulta la base de datos del Registro Nacional."""
    
    def obtener_datos_ciudadano(self, cedula):
        """
        Retorna los datos reales (Nombres, Apellidos) si existe.
        Retorna None si no existe.
        """
        with db.get_connection() as conn:
            cedula_limpia = str(cedula).strip()
            
            res = conn.execute(text("""
                SELECT identificacion, nombres, apellidos 
                FROM RegistroNacionalPersonas 
                WHERE identificacion = :c
            """), {"c": cedula_limpia}).fetchone()
            
            if res:
                return {
                    "cedula": res.identificacion,
                    "nombres": res.nombres,
                    "apellidos": res.apellidos
                }
            return None

# ==========================================
# 3. GESTIÓN ACADÉMICA
# ==========================================
class GestionAcademicaRepository:
    
    def crear_carrera(self, nombre, duracion, cupos):
        with db.get_connection() as conn:
            conn.execute(text("""
                IF NOT EXISTS (SELECT * FROM Carreras WHERE nombreCarrera = :n)
                INSERT INTO Carreras (nombreCarrera, duracion, cupos, estado)
                VALUES (:n, :d, :c, 'Activa')
            """), {"n": nombre, "d": duracion, "c": cupos})
            conn.commit()
            return True

    def actualizar_carrera(self, id_carrera, nombre):
        with db.get_connection() as conn:
            conn.execute(text("""
                UPDATE Carreras SET nombreCarrera=:n WHERE idCarrera=:id
            """), {"n": nombre, "id": id_carrera})
            conn.commit()
            return True

    def alternar_estado_carrera(self, id_carrera):
        with db.get_connection() as conn:
            actual = conn.execute(text("SELECT estado FROM Carreras WHERE idCarrera=:id"), {"id": id_carrera}).scalar()
            nuevo_estado = 'Inactiva' if actual == 'Activa' else 'Activa'
            conn.execute(text("UPDATE Carreras SET estado = :ne WHERE idCarrera=:id"), 
                         {"ne": nuevo_estado, "id": id_carrera})
            conn.commit()
            return True

    def eliminar_carrera(self, id_carrera):
        with db.get_connection() as conn:
            try:
                conn.execute(text("DELETE FROM Carreras WHERE idCarrera=:id"), {"id": id_carrera})
            except:
                conn.execute(text("UPDATE Carreras SET estado='Inactiva', nombreCarrera=nombreCarrera + ' (ELIM)' WHERE idCarrera=:id"), {"id": id_carrera})
            conn.commit()
            return True

    def crear_periodo(self, nombre, fecha_ini, fecha_fin):
        with db.get_connection() as conn:
            conn.execute(text("""
                INSERT INTO Periodos (nombrePeriodo, fechaInicio, fechaFin, estado)
                VALUES (:n, :fi, :ff, 'Activo')
            """), {"n": nombre, "fi": fecha_ini, "ff": fecha_fin})
            conn.commit()
            return True

    def eliminar_periodo(self, id_periodo):
        with db.get_connection() as conn:
            ofertas = conn.execute(text("SELECT COUNT(*) FROM OfertasAcademicas WHERE idPeriodo=:id"), {"id": id_periodo}).scalar()
            if ofertas > 0:
                raise Exception(f"No se puede borrar: El periodo tiene {ofertas} ofertas asociadas.")
            conn.execute(text("DELETE FROM Periodos WHERE idPeriodo=:id"), {"id": id_periodo})
            conn.commit()
            return True

    def crear_oferta(self, id_carrera, id_periodo, cupos):
        with db.get_connection() as conn:
            existe = conn.execute(text("""
                SELECT idOferta FROM OfertasAcademicas WHERE idCarrera=:ic AND idPeriodo=:ip
            """), {"ic": id_carrera, "ip": id_periodo}).fetchone()
            if existe: return False 

            conn.execute(text("""
                INSERT INTO OfertasAcademicas (nombreOferta, idCarrera, idPeriodo, cupos, estado, fechaInicio, fechaFin)
                VALUES ('Oferta ' + (SELECT nombreCarrera FROM Carreras WHERE idCarrera=:ic), :ic, :ip, :c, 'Activo', GETDATE(), DATEADD(year, 1, GETDATE()))
            """), {"ic": id_carrera, "ip": id_periodo, "c": cupos})
            conn.commit()
            return True

    def eliminar_oferta(self, id_oferta):
        with db.get_connection() as conn:
            # 1. Borrar inscripciones
            conn.execute(text("DELETE FROM Inscripciones WHERE idOferta=:id"), {"id": id_oferta})
            # 2. Borrar oferta
            conn.execute(text("DELETE FROM OfertasAcademicas WHERE idOferta=:id"), {"id": id_oferta})
            conn.commit()
            return True
            
    def obtener_periodos_activos(self):
        with db.get_connection() as conn:
            return conn.execute(text("SELECT idPeriodo, nombrePeriodo, fechaInicio, fechaFin FROM Periodos WHERE estado='Activo' ORDER BY idPeriodo DESC")).fetchall()

    def obtener_carreras_activas(self):
        with db.get_connection() as conn:
            # Busca exacto o con espacios por seguridad
            return conn.execute(text("SELECT idCarrera, nombreCarrera FROM Carreras WHERE estado LIKE 'Activa%'")).fetchall()

    def obtener_todas_carreras(self):
        with db.get_connection() as conn:
            return conn.execute(text("SELECT idCarrera, nombreCarrera, cupos, estado FROM Carreras")).fetchall()

    def obtener_ofertas_por_periodo(self, id_periodo):
        with db.get_connection() as conn:
            return conn.execute(text("""
                SELECT o.idOferta, c.nombreCarrera, o.cupos, o.estado 
                FROM OfertasAcademicas o
                JOIN Carreras c ON o.idCarrera = c.idCarrera
                WHERE o.idPeriodo = :ip
            """), {"ip": id_periodo}).fetchall()

# ==========================================
# 4. PROCESO DE INSCRIPCIÓN
# ==========================================
class ProcesoInscripcionRepository:

    def inscribir_estudiante(self, id_estudiante, id_oferta, id_carrera):
        with db.get_connection() as conn:
            aceptada = conn.execute(text("SELECT idInscripcion FROM Inscripciones WHERE idEstudiante=:ie AND estado='Aceptada'"), {"ie": id_estudiante}).fetchone()
            if aceptada: raise Exception("Ya tienes un cupo ACEPTADO.")

            existe = conn.execute(text("SELECT idInscripcion FROM Inscripciones WHERE idEstudiante=:ie AND idOferta=:io"), {"ie": id_estudiante, "io": id_oferta}).fetchone()
            if existe: raise Exception("Ya enviaste solicitud a esta oferta.")

            conn.execute(text("""
                INSERT INTO Inscripciones (idEstudiante, idOferta, idCarrera, estado, fechaInscripcion)
                VALUES (:ie, :io, :ic, 'Pendiente', GETDATE())
            """), {"ie": id_estudiante, "io": id_oferta, "ic": id_carrera})
            conn.commit()
            return True

    def obtener_inscripciones_pendientes(self):
        with db.get_connection() as conn:
            return conn.execute(text("""
                SELECT i.idInscripcion, e.nombres + ' ' + e.apellidos as Estudiante, 
                       c.nombreCarrera, i.fechaInscripcion, e.idEstudiante
                FROM Inscripciones i
                JOIN Estudiantes e ON i.idEstudiante = e.idEstudiante
                JOIN Carreras c ON i.idCarrera = c.idCarrera
                WHERE i.estado = 'Pendiente'
            """)).fetchall()

    def aceptar_inscripcion(self, id_inscripcion):
        with db.get_connection() as conn:
            id_est = conn.execute(text("SELECT idEstudiante FROM Inscripciones WHERE idInscripcion=:id"), {"id": id_inscripcion}).scalar()
            
            ya_tiene = conn.execute(text("SELECT COUNT(*) FROM Inscripciones WHERE idEstudiante=:id AND estado='Aceptada'"), {"id": id_est}).scalar()
            if ya_tiene > 0: raise Exception("El estudiante YA TIENE un cupo aceptado.")

            conn.execute(text("UPDATE Inscripciones SET estado='Aceptada' WHERE idInscripcion=:id"), {"id": id_inscripcion})
            conn.execute(text("UPDATE Inscripciones SET estado='Rechazada' WHERE idEstudiante=:id AND estado='Pendiente'"), {"id": id_est})
            conn.commit()
            return True

    def rechazar_inscripcion(self, id_inscripcion):
        with db.get_connection() as conn:
            conn.execute(text("UPDATE Inscripciones SET estado='Rechazada' WHERE idInscripcion=:id"), {"id": id_inscripcion})
            conn.commit()
            return True

    def asignar_horarios_evaluacion_por_periodo(self, id_periodo, fecha_evaluacion, hora_inicio):
        with db.get_connection() as conn:
            try:
                inscritos = conn.execute(text("""
                    SELECT i.idEstudiante FROM Inscripciones i
                    JOIN OfertasAcademicas o ON i.idOferta = o.idOferta
                    WHERE o.idPeriodo = :ip AND i.estado = 'Aceptada'
                """), {"ip": id_periodo}).fetchall()

                if not inscritos: return 0

                id_eval = conn.execute(text("SELECT TOP 1 idEvaluacion FROM Evaluaciones WHERE tipoEvaluacion='Admision'")).scalar()
                if not id_eval:
                    conn.execute(text("INSERT INTO Evaluaciones (nombreEvaluacion, tipoEvaluacion) VALUES ('Examen Admision General', 'Admision')"))
                    conn.commit()
                    id_eval = conn.execute(text("SELECT TOP 1 idEvaluacion FROM Evaluaciones WHERE tipoEvaluacion='Admision'")).scalar()

                count = 0
                for est in inscritos:
                    existe = conn.execute(text("SELECT idAsignacion FROM EvaluacionesAsignadas WHERE idEstudiante=:ie AND idEvaluacion=:iev"), {"ie": est.idEstudiante, "iev": id_eval}).fetchone()
                    if not existe:
                        conn.execute(text("""
                            INSERT INTO EvaluacionesAsignadas (idEvaluacion, idEstudiante, estado, fechaVencimiento, observaciones)
                            VALUES (:iev, :ie, 'Pendiente', :fec, :hora)
                        """), {"iev": id_eval, "ie": est.idEstudiante, "fec": fecha_evaluacion, "hora": hora_inicio})
                        count += 1
                conn.commit()
                return count
            except Exception as e:
                print(f"Error asignando horarios: {e}")
                return -1

    def obtener_estudiantes_para_calificar(self):
        with db.get_connection() as conn:
            return conn.execute(text("""
                SELECT ea.idAsignacion, e.cedula, e.nombres + ' ' + e.apellidos as Estudiante, 
                       ev.nombreEvaluacion, ea.fechaVencimiento
                FROM EvaluacionesAsignadas ea
                JOIN Estudiantes e ON ea.idEstudiante = e.idEstudiante
                JOIN Evaluaciones ev ON ea.idEvaluacion = ev.idEvaluacion
                WHERE ea.estado = 'Pendiente'
            """)).fetchall()

    def registrar_puntaje(self, id_asignacion, puntaje):
        with db.get_connection() as conn:
            estado_final = "Aprobado" if float(puntaje) >= 70 else "Reprobado"
            conn.execute(text("""
                UPDATE EvaluacionesAsignadas SET puntajeObtenido = :p, estado = :e, fechaCompletada = GETDATE() WHERE idAsignacion = :id
            """), {"p": puntaje, "e": estado_final, "id": id_asignacion})
            conn.commit()
            return True

    def cargar_notas_masivas_desde_excel(self, ruta_archivo):
        try:
            df = pd.read_excel(ruta_archivo, dtype=str)
            df.columns = [str(c).upper().strip() for c in df.columns]
            
            col_nota = 'PUNTAJE_POSTULACION' if 'PUNTAJE_POSTULACION' in df.columns else None
            if not col_nota and 'NOTA' in df.columns: col_nota = 'NOTA'
            if not col_nota: return False, "Falta columna PUNTAJE_POSTULACION o NOTA"

            col_id = None
            for c in ['CEDULA', 'IDENTIFICACION', 'CUS_ID', 'ID']:
                if c in df.columns: 
                    col_id = c
                    break
            
            if not col_id: return False, "Falta columna CUS_ID o CEDULA"

            actualizados = 0
            errores = []

            with db.get_connection() as conn:
                for index, row in df.iterrows():
                    raw_id = row[col_id]
                    if pd.isna(raw_id): continue
                    cedula = str(raw_id).strip().replace('.0', '') 

                    try:
                        val_nota = str(row[col_nota]).replace(',', '.')
                        nota = float(val_nota)
                    except:
                        errores.append(f"ID {cedula}: Nota inválida")
                        continue 
                    
                    id_est = conn.execute(text("SELECT idEstudiante FROM Estudiantes WHERE cedula=:c"), {"c": cedula}).scalar()
                    
                    if id_est:
                        id_asig = conn.execute(text("""
                            SELECT TOP 1 idAsignacion FROM EvaluacionesAsignadas 
                            WHERE idEstudiante=:id AND estado='Pendiente'
                            ORDER BY idAsignacion DESC
                        """), {"id": id_est}).scalar()
                        
                        if id_asig:
                            umbral = 700 if nota > 100 else 70
                            estado_final = "Aprobado" if nota >= umbral else "Reprobado"
                            conn.execute(text("""
                                UPDATE EvaluacionesAsignadas SET puntajeObtenido=:p, estado=:e, fechaCompletada=GETDATE() WHERE idAsignacion=:id
                            """), {"p": nota, "e": estado_final, "id": id_asig})
                            actualizados += 1
                        else:
                            errores.append(f"{cedula}: Sin examen pendiente.")
                    else:
                        errores.append(f"{cedula}: No existe.")
                conn.commit()
                return True, f"Procesados: {actualizados}. Errores: {len(errores)}"
        except Exception as e: return False, str(e)

    def obtener_matriz_final(self):
        with db.get_connection() as conn:
            return conn.execute(text("""
                SELECT e.cedula, e.nombres + ' ' + e.apellidos as Estudiante, c.nombreCarrera, ea.puntajeObtenido, ea.estado
                FROM EvaluacionesAsignadas ea
                JOIN Estudiantes e ON ea.idEstudiante = e.idEstudiante
                JOIN Inscripciones i ON i.idEstudiante = e.idEstudiante AND i.estado = 'Aceptada'
                JOIN Carreras c ON i.idCarrera = c.idCarrera
                WHERE ea.estado IN ('Aprobado', 'Reprobado')
                ORDER BY ea.puntajeObtenido DESC
            """)).fetchall()

# ==========================================
# 4. REPOSITORIOS DE SOPORTE
# ==========================================
class OfertaRepository:
    def obtener_disponibles(self):
        with db.get_connection() as conn:
            return conn.execute(text("""
                SELECT o.idOferta, c.nombreCarrera, p.nombrePeriodo, o.idCarrera
                FROM OfertasAcademicas o
                JOIN Carreras c ON o.idCarrera = c.idCarrera
                JOIN Periodos p ON o.idPeriodo = p.idPeriodo
                WHERE o.estado LIKE 'Activo%' AND p.estado LIKE 'Activo%'
            """)).fetchall()

class EvaluacionRepository:
    def obtener_matriz_consolidada(self):
        with db.get_connection() as conn:
            return conn.execute(text("""
                SELECT e.nombres + ' ' + e.apellidos AS Estudiante, ev.nombreEvaluacion AS Evaluacion, ea.puntajeObtenido AS Puntaje, ea.estado AS Estado, ea.observaciones
                FROM EvaluacionesAsignadas ea
                JOIN Estudiantes e ON ea.idEstudiante = e.idEstudiante
                JOIN Evaluaciones ev ON ea.idEvaluacion = ev.idEvaluacion
            """)).fetchall()

class AdminRepository:
    def obtener_estadisticas(self):
        with db.get_connection() as conn:
             return {
                "estudiantes": conn.execute(text("SELECT COUNT(*) FROM Estudiantes")).scalar(),
                "inscripciones": conn.execute(text("SELECT COUNT(*) FROM Inscripciones")).scalar(),
                "pendientes": conn.execute(text("SELECT COUNT(*) FROM Inscripciones WHERE estado='Pendiente'")).scalar(),
                "aceptadas": conn.execute(text("SELECT COUNT(*) FROM Inscripciones WHERE estado='Aceptada'")).scalar(),
                "evaluados": conn.execute(text("SELECT COUNT(*) FROM EvaluacionesAsignadas WHERE estado IN ('Aprobado','Reprobado')")).scalar(),
                "carreras_activas": conn.execute(text("SELECT COUNT(*) FROM Carreras WHERE estado='Activa'")).scalar()
            }