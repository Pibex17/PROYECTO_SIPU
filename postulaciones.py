from sqlalchemy import text
from DataBase import db
import datetime

# 1. REPOSITORY SRP
class PostulacionRepository:
    def crear_tablas(self):
        with db.engine.connect() as conn:
            # Tabla Principal
            conn.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='Postulaciones')
                CREATE TABLE Postulaciones (
                    idPostulacion INT IDENTITY(1,1) PRIMARY KEY,
                    idAspirante INT NOT NULL, 
                    idCarrera INT NOT NULL,
                    idPeriodo INT NOT NULL,
                    fechaPostulacion DATETIME DEFAULT GETDATE(),
                    estado VARCHAR(20) DEFAULT 'Revision', -- Revision, Aceptada, Rechazada
                    promedioColegio FLOAT, -- Dato necesario para evaluar
                    tipoIngreso VARCHAR(50) DEFAULT 'Examen', -- Examen, Homologacion
                    fechaActualizacion DATETIME DEFAULT GETDATE()
                )
            """))
            
            # Tabla de Requisitos/Documentos entregados
            conn.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='PostulacionRequisitos')
                CREATE TABLE PostulacionRequisitos (
                    idRequisito INT IDENTITY(1,1) PRIMARY KEY,
                    idPostulacion INT NOT NULL,
                    nombreDocumento VARCHAR(100), -- Ej: 'Titulo Bachiller', 'Cedula'
                    entregado BIT DEFAULT 0,
                    FOREIGN KEY (idPostulacion) REFERENCES Postulaciones(idPostulacion)
                )
            """))
            conn.commit()

    def validar_periodo_activo(self):
        """Verifica si hay un periodo académico activo para postular"""
        with db.engine.connect() as conn:
            res = conn.execute(text("SELECT TOP 1 idPeriodo FROM Periodos WHERE estado = 'Activo'"))
            row = res.fetchone()
            return row.idPeriodo if row else None

    def existe_postulacion(self, id_aspirante, id_periodo):
        with db.engine.connect() as conn:
            res = conn.execute(text("""
                SELECT idPostulacion FROM Postulaciones 
                WHERE idAspirante = :asp AND idPeriodo = :per
            """), {'asp': id_aspirante, 'per': id_periodo})
            return res.fetchone() is not None

    def guardar_postulacion(self, id_aspirante, id_carrera, id_periodo, promedio):
        with db.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO Postulaciones (idAspirante, idCarrera, idPeriodo, promedioColegio, estado)
                VALUES (:asp, :car, :per, :prom, 'Revision')
            """), {'asp': id_aspirante, 'car': id_carrera, 'per': id_periodo, 'prom': promedio})
            conn.commit()
            
            # Retornar ID para guardar requisitos
            res = conn.execute(text("SELECT TOP 1 idPostulacion FROM Postulaciones ORDER BY idPostulacion DESC"))
            return res.fetchone().idPostulacion

    def guardar_requisitos(self, id_postulacion, lista_documentos):
        with db.engine.connect() as conn:
            for doc in lista_documentos:
                conn.execute(text("""
                    INSERT INTO PostulacionRequisitos (idPostulacion, nombreDocumento, entregado)
                    VALUES (:id, :doc, 1)
                """), {'id': id_postulacion, 'doc': doc})
            conn.commit()

    def actualizar_estado(self, id_postulacion, nuevo_estado):
        with db.engine.connect() as conn:
            conn.execute(text("UPDATE Postulaciones SET estado=:e, fechaActualizacion=GETDATE() WHERE idPostulacion=:id"),
                         {'e': nuevo_estado, 'id': id_postulacion})
            conn.commit()

    def obtener_pendientes(self):
        # Muestra datos completos para que el admin pueda evaluar
        with db.engine.connect() as conn:
            return conn.execute(text("""
                SELECT p.idPostulacion, rn.identificacion, rn.nombres + ' ' + rn.apellidos as aspirante,
                       c.nombreCarrera, p.promedioColegio, p.fechaPostulacion
                FROM Postulaciones p
                JOIN RegistroNacionalPersonas rn ON p.idAspirante = rn.idAspirante
                JOIN Carreras c ON p.idCarrera = c.idCarrera
                WHERE p.estado = 'Revision'
            """)).fetchall()

# 2. SERVICE (Lógica de Negocio) - Validaciones Fuertes
class PostulacionService:
    def __init__(self):
        self.repo = PostulacionRepository()

    def procesar_postulacion(self, cedula, id_carrera, promedio, documentos_check):
        # 1. Validar Periodo
        id_periodo = self.repo.validar_periodo_activo()
        if not id_periodo:
            raise Exception(" No hay un periodo académico activo para postulaciones.")

        # 2. Buscar Aspirante
        with db.engine.connect() as conn:
            asp = conn.execute(text("SELECT idAspirante FROM RegistroNacionalPersonas WHERE identificacion=:c"), {'c':cedula}).fetchone()
        
        if not asp:
            raise Exception(" El aspirante no existe en el Registro Nacional.")

        # 3. Validar Duplicidad (Regla de Negocio SIPU)
        if self.repo.existe_postulacion(asp.idAspirante, id_periodo):
            raise Exception(" Ya tiene una postulación registrada en este periodo.")

        # 4. Validar Documentación Mínima
        documentos_requeridos = ['Cedula', 'Titulo Bachiller', 'Foto']
        faltantes = [doc for doc in documentos_requeridos if doc not in documentos_check]
        
        if faltantes:
            raise Exception(f" Falta documentación requerida: {', '.join(faltantes)}")

        # 5. Guardar todo (Transacción lógica)
        id_post = self.repo.guardar_postulacion(asp.idAspirante, id_carrera, id_periodo, promedio)
        self.repo.guardar_requisitos(id_post, documentos_check)
        
        return id_post

# 3. FACADE 
class PostulacionesFacade:
    def __init__(self):
        self.service = PostulacionService()
        self.repo = PostulacionRepository()

    def inicializar(self):
        self.repo.crear_tablas()

    def nueva_postulacion(self, cedula, id_carrera, promedio, docs_entregados):
        try:
            id_gen = self.service.procesar_postulacion(cedula, id_carrera, promedio, docs_entregados)
            print(f"\n Postulación #{id_gen} registrada EXITOSAMENTE.")
            print("   Estado: En Revisión de Secretaría")
            return True
        except Exception as e:
            print(f"\n{str(e)}")
            return False

    def ver_pendientes(self):
        return self.repo.obtener_pendientes()