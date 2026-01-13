from abc import ABC, abstractmethod
from sqlalchemy import text
from DataBase import db
from postulaciones import PostulacionRepository

# INTERFAZ OBSERVER (OCP - Open/Closed Principle)
class IEvaluacionObserver(ABC):
    @abstractmethod
    def procesar(self, id_postulacion, resultado_evaluacion):
        pass

# REPOSITORY DE EVALUACIÓN
class EvaluacionRepository:
    def crear_tablas(self):
        with db.engine.connect() as conn:
            conn.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='EvaluacionesAdmision')
                CREATE TABLE EvaluacionesAdmision (
                    idEvaluacion INT IDENTITY(1,1) PRIMARY KEY,
                    idPostulacion INT NOT NULL,
                    puntajeExamen FLOAT,
                    observacion VARCHAR(200),
                    resultadoFinal VARCHAR(20), -- 'ADMITIDO', 'NO ADMITIDO'
                    fechaEvaluacion DATETIME DEFAULT GETDATE()
                )
            """))
            # Tabla de Horarios generados automáticamente
            conn.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='MatriculaInicial')
                CREATE TABLE MatriculaInicial (
                    idMatricula INT IDENTITY(1,1) PRIMARY KEY,
                    idPostulacion INT NOT NULL,
                    bloqueHorario VARCHAR(50),
                    estado VARCHAR(20) DEFAULT 'Generada'
                )
            """))
            conn.commit()

    def guardar_evaluacion(self, id_post, puntaje, obs, resultado):
        with db.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO EvaluacionesAdmision (idPostulacion, puntajeExamen, observacion, resultadoFinal)
                VALUES (:id, :pt, :obs, :res)
            """), {'id': id_post, 'pt': puntaje, 'obs': obs, 'res': resultado})
            conn.commit()

    def crear_matricula_horario(self, id_post, bloque):
        with db.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO MatriculaInicial (idPostulacion, bloqueHorario)
                VALUES (:id, :bloque)
            """), {'id': id_post, 'bloque': bloque})
            conn.commit()

# OBSERVERS CONCRETOS

class CambioEstadoPostulacionObserver(IEvaluacionObserver):
    """Actualiza el estado en el módulo de Postulaciones"""
    def __init__(self):
        self.repo_post = PostulacionRepository()

    def procesar(self, id_postulacion, resultado_evaluacion):
        nuevo_estado = "Aceptada" if resultado_evaluacion == "ADMITIDO" else "Rechazada"
        print(f"🔄 [SISTEMA] Actualizando estado de postulación a: {nuevo_estado}")
        self.repo_post.actualizar_estado(id_postulacion, nuevo_estado)

class GeneracionHorarioObserver(IEvaluacionObserver):
    """Si es admitido, le genera su primera matrícula/horario"""
    def __init__(self, repo_ev):
        self.repo = repo_ev

    def procesar(self, id_postulacion, resultado_evaluacion):
        if resultado_evaluacion == "ADMITIDO":
            # Lógica de asignación
            horario = "Nivel 1 - Matutino A (07:00 - 13:00)"
            print(f"📅 [SISTEMA] Generando matrícula automática: {horario}")
            self.repo.crear_matricula_horario(id_postulacion, horario)

# FACADE DE EVALUACIÓN
class EvaluacionFacade:
    def __init__(self):
        self.repo = EvaluacionRepository()
        self.observers = []
        
        # Conectar los cables del Observer
        self.agregar_observer(CambioEstadoPostulacionObserver())
        self.agregar_observer(GeneracionHorarioObserver(self.repo))

    def inicializar(self):
        self.repo.crear_tablas()

    def agregar_observer(self, observer):
        self.observers.append(observer)

    def evaluar_aspirante(self, id_postulacion, puntaje_examen, observacion):
        # 1. Determinar resultado
        resultado = "ADMITIDO" if puntaje_examen >= 70 else "NO ADMITIDO"

        # 2. Guardar evaluación
        self.repo.guardar_evaluacion(id_postulacion, puntaje_examen, observacion, resultado)
        print(f"\n Evaluación registrada. Resultado: {resultado}")

        # 3. Disparar eventos automáticos (Observer)
        print(" Ejecutando procesos automáticos del SIPU...")
        for obs in self.observers:
            obs.procesar(id_postulacion, resultado)