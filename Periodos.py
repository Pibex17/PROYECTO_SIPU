from sqlalchemy import text
from datetime import date
from dataclasses import dataclass
from DataBase import db


# ---Domain--- #

@dataclass
class Periodo:
    nombre: str
    fecha_inicio: date
    fecha_fin: date
    estado: str = "Planeado"

# ---Repository--- #
class PeriodoRepository:

    def crear_tabla(self):
        with db.engine.connect() as conn:
            conn.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='Periodos')
                CREATE TABLE Periodos (
                    idPeriodo INT IDENTITY(1,1) PRIMARY KEY,
                    nombrePeriodo VARCHAR(100) NOT NULL UNIQUE,
                    fechaInicio DATE NOT NULL,
                    fechaFin DATE NOT NULL,
                    estado VARCHAR(20) NOT NULL DEFAULT 'Planeado'
                        CHECK (estado IN ('Activo','Cerrado','Planeado')),
                    fechaCreacion DATETIME NOT NULL DEFAULT GETDATE(),
                    fechaActualizacion DATETIME NOT NULL DEFAULT GETDATE(),
                    CONSTRAINT CHK_Fechas_Periodo CHECK (fechaFin > fechaInicio)
                )
            """))

            conn.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.triggers WHERE name='trg_Update_Periodos')
                EXEC('
                    CREATE TRIGGER trg_Update_Periodos
                    ON Periodos
                    AFTER UPDATE
                    AS
                    BEGIN
                        UPDATE Periodos
                        SET fechaActualizacion = GETDATE()
                        WHERE idPeriodo IN (SELECT idPeriodo FROM inserted);
                    END
                ')
            """))
            conn.commit()

    def insertar(self, periodo: Periodo):
        with db.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO Periodos (nombrePeriodo, fechaInicio, fechaFin, estado)
                VALUES (:nombre, :inicio, :fin, :estado)
            """), {
                "nombre": periodo.nombre,
                "inicio": periodo.fecha_inicio,
                "fin": periodo.fecha_fin,
                "estado": periodo.estado
            })
            conn.commit()

    def cerrar(self, id_periodo: int):
        with db.engine.connect() as conn:
            conn.execute(text("""
                UPDATE Periodos
                SET estado = 'Cerrado'
                WHERE idPeriodo = :id
            """), {"id": id_periodo})
            conn.commit()

    def obtener_activos(self):
        with db.engine.connect() as conn:
            return conn.execute(text("""
                SELECT idPeriodo, nombrePeriodo, fechaInicio, fechaFin, estado
                FROM Periodos
                WHERE estado = 'Activo'
            """)).fetchall()


# ---Service--- #
class PeriodoService:

    def __init__(self, repository: PeriodoRepository):
        self.repository = repository

    def inicializar(self):
        self.repository.crear_tabla()

    def crear_periodo(self, nombre, inicio, fin, estado="Planeado"):
        if fin <= inicio:
            raise ValueError("❌ La fecha de fin debe ser mayor que la fecha de inicio")

        periodo = Periodo(
            nombre=nombre,
            fecha_inicio=inicio,
            fecha_fin=fin,
            estado=estado
        )

        self.repository.insertar(periodo)

    def cerrar_periodo(self, id_periodo: int):
        self.repository.cerrar(id_periodo)

    def listar_periodos_activos(self):
        return self.repository.obtener_activos()

# ---Facade--- #
class PeriodosFacade:

    def __init__(self):
        self._repository = PeriodoRepository()
        self._service = PeriodoService(self._repository)

    def crear_tabla(self):
        self._service.inicializar()

    def crear_periodo(self, nombre, inicio, fin, estado="Planeado"):
        self._service.crear_periodo(nombre, inicio, fin, estado)

    def cerrar_periodo(self, id_periodo):
        self._service.cerrar_periodo(id_periodo)

    def ver_periodos_activos(self):
        return self._service.listar_periodos_activos()
