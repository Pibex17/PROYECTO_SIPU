from DataBase import db
from sqlalchemy import text

class Inscripciones:
    """Gestiona estudiantes e inscripciones en ofertas académicas"""
    def __init__(self):
        pass

    def crear_tablas_inscripciones(self):
        """
        Crea las tablas de Estudiantes e Inscripciones
        - Tabla Estudiantes: datos personales y estado
        - Tabla Inscripciones: relación estudiante-oferta-carrera
        """
        try:
            with db.engine.connect() as conn:
                # Crea tabla Estudiantes con validaciones
                conn.execute(text("""
                    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'Estudiantes')
                    CREATE TABLE Estudiantes (
                        idEstudiante INT IDENTITY(1,1) PRIMARY KEY,
                        nombres VARCHAR(100) NOT NULL,
                        apellidos VARCHAR(100) NOT NULL,
                        cedula VARCHAR(20) NOT NULL UNIQUE,
                        email VARCHAR(100) NOT NULL UNIQUE,
                        telefono VARCHAR(20),
                        direccion VARCHAR(255),
                        fechaNacimiento DATE NOT NULL,
                        estado VARCHAR(20) NOT NULL DEFAULT 'Activo'
                            CHECK (estado IN ('Activo','Inactivo','Suspendido')),
                        fechaCreacion DATETIME NOT NULL DEFAULT GETDATE(),
                        fechaActualizacion DATETIME NOT NULL DEFAULT GETDATE()
                    )
                """))

                conn.execute(text("""
                    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'Inscripciones')
                    CREATE TABLE Inscripciones (
                        idInscripcion INT IDENTITY(1,1) PRIMARY KEY,
                        idEstudiante INT NOT NULL,
                        idOferta INT NOT NULL,
                        idCarrera INT NOT NULL,
                        fechaInscripcion DATETIME NOT NULL DEFAULT GETDATE(),
                        estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente'
                            CHECK (estado IN ('Pendiente','Aprobada','Rechazada','Cancelada')),
                        observaciones VARCHAR(500),
                        fechaActualizacion DATETIME NOT NULL DEFAULT GETDATE(),
                        FOREIGN KEY (idEstudiante) REFERENCES Estudiantes(idEstudiante),
                        FOREIGN KEY (idOferta) REFERENCES OfertasAcademicas(idOferta),
                        FOREIGN KEY (idCarrera) REFERENCES Carreras(idCarrera)
                    )
                """))

                conn.execute(text("""
                    CREATE OR ALTER TRIGGER trg_Update_Estudiantes
                    ON Estudiantes
                    AFTER UPDATE
                    AS
                    BEGIN
                        UPDATE Estudiantes
                        SET fechaActualizacion = GETDATE()
                        WHERE idEstudiante IN (SELECT idEstudiante FROM inserted)
                    END
                """))

                conn.execute(text("""
                    CREATE OR ALTER TRIGGER trg_Update_Inscripciones
                    ON Inscripciones
                    AFTER UPDATE
                    AS
                    BEGIN
                        UPDATE Inscripciones
                        SET fechaActualizacion = GETDATE()
                        WHERE idInscripcion IN (SELECT idInscripcion FROM inserted)
                    END
                """))

                conn.commit()
                print("Tablas de inscripciones creadas correctamente.")
        except Exception as e:
            print(f"Error al crear tablas: {str(e)}")

    def registrar_estudiante(self, nombres, apellidos, cedula, email, telefono, direccion, fecha_nacimiento, estado="Activo"):
        """Registra un nuevo estudiante en la base de datos."""
        try:
            with db.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO Estudiantes (nombres, apellidos, cedula, email, telefono, direccion, fechaNacimiento, estado)
                    VALUES (:nombres, :apellidos, :cedula, :email, :telefono, :direccion, :fechaNacimiento, :estado)
                """), {
                    'nombres': nombres,
                    'apellidos': apellidos,
                    'cedula': cedula,
                    'email': email,
                    'telefono': telefono,
                    'direccion': direccion,
                    'fechaNacimiento': fecha_nacimiento,
                    'estado': estado
                })
                conn.commit()
                print(f"Estudiante '{nombres} {apellidos}' registrado correctamente.")
        except Exception as e:
            print(f"Error al registrar estudiante: {str(e)}")

    def ver_estudiantes(self, estado=None):
        """Muestra todos los estudiantes, opcionalmente filtrados por estado."""
        try:
            with db.engine.connect() as conn:
                query = """
                    SELECT idEstudiante, nombres, apellidos, cedula, email, telefono, estado
                    FROM Estudiantes
                """
                params = {}
                if estado:
                    query += " WHERE estado = :estado"
                    params['estado'] = estado
                
                query += " ORDER BY apellidos, nombres"

                result = conn.execute(text(query), params)
                estudiantes = result.fetchall()

                if not estudiantes:
                    print("No hay estudiantes registrados.")
                    return

                print("\nListado de estudiantes:")
                for est in estudiantes:
                    print(f"ID: {est.idEstudiante} | Nombre: {est.nombres} {est.apellidos} | Cédula: {est.cedula} | Email: {est.email} | Estado: {est.estado}")
        except Exception as e:
            print(f"Error al consultar estudiantes: {str(e)}")

    def crear_inscripcion(self, id_estudiante, id_oferta, id_carrera, observaciones=None, estado="Pendiente"):
        """Crea una nueva inscripción para un estudiante."""
        try:
            with db.engine.connect() as conn:
                est = conn.execute(text("""
                    SELECT estado FROM Estudiantes WHERE idEstudiante = :id
                """), {'id': id_estudiante}).fetchone()
                
                if not est:
                    print(f"No existe estudiante con ID {id_estudiante}")
                    return
                
                if est.estado != 'Activo':
                    print(f"El estudiante no está activo (Estado: {est.estado})")
                    return

                duplicado = conn.execute(text("""
                    SELECT COUNT(*) FROM Inscripciones 
                    WHERE idEstudiante = :est AND idOferta = :oferta AND idCarrera = :carrera
                    AND estado NOT IN ('Rechazada', 'Cancelada')
                """), {'est': id_estudiante, 'oferta': id_oferta, 'carrera': id_carrera}).scalar()
                
                if duplicado > 0:
                    print("El estudiante ya tiene una inscripción activa para esta oferta y carrera.")
                    return

                conn.execute(text("""
                    INSERT INTO Inscripciones (idEstudiante, idOferta, idCarrera, estado, observaciones)
                    VALUES (:estudiante, :oferta, :carrera, :estado, :obs)
                """), {
                    'estudiante': id_estudiante,
                    'oferta': id_oferta,
                    'carrera': id_carrera,
                    'estado': estado,
                    'obs': observaciones
                })
                conn.commit()
                print(f"Inscripción creada exitosamente con estado: {estado}")
        except Exception as e:
            print(f"Error al crear inscripción: {str(e)}")

    def ver_inscripciones(self, id_estudiante=None, id_oferta=None, estado=None):
        """Muestra inscripciones con filtros opcionales."""
        try:
            with db.engine.connect() as conn:
                query = """
                    SELECT i.idInscripcion, i.fechaInscripcion, i.estado,
                           e.nombres, e.apellidos, e.cedula,
                           c.nombreCarrera,
                           o.nombreOferta,
                           i.observaciones
                    FROM Inscripciones i
                    JOIN Estudiantes e ON i.idEstudiante = e.idEstudiante
                    JOIN Carreras c ON i.idCarrera = c.idCarrera
                    JOIN OfertasAcademicas o ON i.idOferta = o.idOferta
                    WHERE 1=1
                """
                params = {}
                
                if id_estudiante:
                    query += " AND i.idEstudiante = :estudiante"
                    params['estudiante'] = id_estudiante
                if id_oferta:
                    query += " AND i.idOferta = :oferta"
                    params['oferta'] = id_oferta
                if estado:
                    query += " AND i.estado = :estado"
                    params['estado'] = estado
                
                query += " ORDER BY i.fechaInscripcion DESC"

                result = conn.execute(text(query), params)
                inscripciones = result.fetchall()

                if not inscripciones:
                    print("No hay inscripciones registradas.")
                    return

                print("\nListado de inscripciones:")
                for insc in inscripciones:
                    print(f"\nID: {insc.idInscripcion} | Fecha: {insc.fechaInscripcion.strftime('%Y-%m-%d %H:%M')}")
                    print(f"  Estudiante: {insc.nombres} {insc.apellidos} (CI: {insc.cedula})")
                    print(f"  Carrera: {insc.nombreCarrera}")
                    print(f"  Oferta: {insc.nombreOferta}")
                    print(f"  Estado: {insc.estado}")
                    if insc.observaciones:
                        print(f"  Observaciones: {insc.observaciones}")
        except Exception as e:
            print(f"Error al consultar inscripciones: {str(e)}")

    def actualizar_inscripcion(self, id_inscripcion, nuevo_estado=None, nuevas_observaciones=None):
        """Actualiza el estado y/u observaciones de una inscripción."""
        try:
            with db.engine.connect() as conn:
                campos = []
                params = {'id': id_inscripcion}

                if nuevo_estado:
                    campos.append("estado = :estado")
                    params['estado'] = nuevo_estado
                if nuevas_observaciones is not None:
                    campos.append("observaciones = :obs")
                    params['obs'] = nuevas_observaciones

                if not campos:
                    print("No se proporcionaron campos para actualizar.")
                    return

                query = f"UPDATE Inscripciones SET {', '.join(campos)} WHERE idInscripcion = :id"
                conn.execute(text(query), params)
                conn.commit()
                print(f"Inscripción ID {id_inscripcion} actualizada correctamente.")
        except Exception as e:
            print(f"Error al actualizar inscripción: {str(e)}")

    def eliminar_inscripcion(self, id_inscripcion):
        """Elimina una inscripción según su ID."""
        try:
            with db.engine.connect() as conn:
                conn.execute(text("""
                    DELETE FROM Inscripciones WHERE idInscripcion = :id
                """), {'id': id_inscripcion})
                conn.commit()
                print(f"Inscripción ID {id_inscripcion} eliminada correctamente.")
        except Exception as e:
            print(f"Error al eliminar inscripción: {str(e)}")