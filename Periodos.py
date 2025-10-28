from DataBase import db
from sqlalchemy import text

class Periodos:
    """Gestiona los períodos académicos del sistema"""
    def __init__(self):
        pass

    def crear_tabla_periodos(self):
        """
        Crea la tabla 'Periodos' con validaciones
        - Almacena períodos académicos (semestres, trimestres, etc)
        - Incluye fechas de inicio y fin
        - Valida que fechaFin > fechaInicio
        """
        try:
            with db.engine.connect() as conn:
                tabla_existe = conn.execute(text("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_name = 'Periodos'
                """)).scalar()
                
                if not tabla_existe:
                    conn.execute(text("""
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
                        CREATE TRIGGER trg_Update_Periodos
                        ON Periodos
                        AFTER UPDATE
                        AS
                        BEGIN
                            UPDATE Periodos
                            SET fechaActualizacion = GETDATE()
                            WHERE idPeriodo IN (SELECT idPeriodo FROM inserted);
                        END;
                    """))

                    print("Tabla 'Periodos' creada exitosamente.")
                else:
                    print("La tabla 'Periodos' ya existe.")
                
                conn.commit()

        except Exception as e:
            print(f"Error al crear la tabla 'Periodos': {str(e)}")

    def insertar_periodo(self, nombre, inicio, fin, estado):
        """Inserta un nuevo período en la tabla 'Periodos'"""
        try:
            with db.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO Periodos (nombrePeriodo, fechaInicio, fechaFin, estado)
                    VALUES (:nombre, :inicio, :fin, :estado)
                """), {
                    'nombre': nombre,
                    'inicio': inicio,
                    'fin': fin,
                    'estado': estado
                })
                conn.commit()
                print(f"Período '{nombre}' insertado exitosamente.")
        except Exception as e:
            print(f"Error al insertar el período '{nombre}': {str(e)}")
    
    def ver_periodos(self):
        """Muestra los períodos activos"""
        try:
            with db.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT idPeriodo, nombrePeriodo, fechaInicio, fechaFin, estado
                    FROM Periodos
                    WHERE estado = 'Activo'
                """))
                
                periodos = result.fetchall()
                
                if not periodos:
                    print("No hay períodos activos.")
                    return
                
                print("\nPeríodos activos:")
                for periodo in periodos:
                    print(f"ID: {periodo.idPeriodo} | Nombre: {periodo.nombrePeriodo} | Inicio: {periodo.fechaInicio} | Fin: {periodo.fechaFin} | Estado: {periodo.estado}")
        except Exception as e:
            print(f"Error al obtener los períodos: {str(e)}")    

    def desactivar_periodo(self, id_periodo):
        """Desactiva un período cambiando su estado a 'Cerrado'"""
        try:
            with db.engine.connect() as conn:
                conn.execute(text("""
                    UPDATE Periodos
                    SET estado = 'Cerrado'
                    WHERE idPeriodo = :id_periodo
                """), {'id_periodo': id_periodo})
                conn.commit()
                print(f"Período con ID '{id_periodo}' desactivado exitosamente.")
        except Exception as e:
            print(f"Error al desactivar el período con ID '{id_periodo}': {str(e)}")