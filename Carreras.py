from DataBase import db
from sqlalchemy import text

class Carreras:
    def __init__(self):
        pass

    # ===============================
    # 1️⃣ CREAR TABLA CARRERAS
    # ===============================
    def crear_tabla_carreras(self):
        """Crea la tabla 'Carreras' si no existe."""
        try:
            with db.engine.connect() as conn:
                tabla_existe = conn.execute(text("""
                    SELECT COUNT(*) FROM information_schema.tables
                    WHERE table_name = 'Carreras'
                """)).scalar()

                if not tabla_existe:
                    conn.execute(text("""
                        CREATE TABLE Carreras (
                            idCarrera INT IDENTITY(1,1) PRIMARY KEY,
                            nombreCarrera VARCHAR(120) NOT NULL UNIQUE,
                            descripcion VARCHAR(255),
                            duracion INT NOT NULL CHECK (duracion > 0),
                            estado VARCHAR(20) NOT NULL DEFAULT 'Activa'
                                CHECK (estado IN ('Activa','Inactiva')),
                            fechaCreacion DATETIME NOT NULL DEFAULT GETDATE(),
                            fechaActualizacion DATETIME NOT NULL DEFAULT GETDATE()
                        )
                    """))

                    # Trigger para actualizar fechaActualizacion
                    conn.execute(text("""
                        CREATE TRIGGER trg_Update_Carreras
                        ON Carreras
                        AFTER UPDATE
                        AS
                        BEGIN
                            UPDATE Carreras
                            SET fechaActualizacion = GETDATE()
                            WHERE idCarrera IN (SELECT idCarrera FROM inserted);
                        END;
                    """))

                    print("✅ Tabla 'Carreras' creada exitosamente.")
                else:
                    print("ℹ️ La tabla 'Carreras' ya existe.")

                conn.commit()

        except Exception as e:
            print(f"❌ ERROR al crear la tabla 'Carreras': {str(e)}")

    # ===============================
    # 2️⃣ INSERTAR CARRERA
    # ===============================
    def insertar_carrera(self, nombre, descripcion, duracion, estado="Activa"):
        """Inserta una nueva carrera en la base de datos."""
        try:
            with db.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO Carreras (nombreCarrera, descripcion, duracion, estado)
                    VALUES (:nombre, :descripcion, :duracion, :estado)
                """), {
                    'nombre': nombre,
                    'descripcion': descripcion,
                    'duracion': duracion,
                    'estado': estado
                })
                conn.commit()
                print(f"✅ Carrera '{nombre}' registrada correctamente.")
        except Exception as e:
            print(f"❌ ERROR al registrar la carrera '{nombre}': {str(e)}")

    # ===============================
    # 3️⃣ VER TODAS LAS CARRERAS
    # ===============================
    def ver_carreras(self):
        """Muestra todas las carreras registradas."""
        try:
            with db.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT idCarrera, nombreCarrera, descripcion, duracion, estado
                    FROM Carreras
                    ORDER BY nombreCarrera
                """))

                carreras = result.fetchall()
                if not carreras:
                    print("📭 No hay carreras registradas.")
                    return

                print("\n🎓 LISTADO DE CARRERAS:")
                for carrera in carreras:
                    print(f"ID: {carrera.idCarrera} | "
                          f"Nombre: {carrera.nombreCarrera} | "
                          f"Duración: {carrera.duracion} semestres | "
                          f"Estado: {carrera.estado}")
        except Exception as e:
            print(f"❌ ERROR al consultar carreras: {str(e)}")

    # ===============================
    # 4️⃣ ACTUALIZAR CARRERA
    # ===============================
    def actualizar_carrera(self, id_carrera, nuevo_nombre=None, nueva_descripcion=None, nueva_duracion=None, nuevo_estado=None):
        """Actualiza la información de una carrera."""
        try:
            campos = []
            parametros = {'id': id_carrera}

            if nuevo_nombre:
                campos.append("nombreCarrera = :nombre")
                parametros['nombre'] = nuevo_nombre
            if nueva_descripcion:
                campos.append("descripcion = :descripcion")
                parametros['descripcion'] = nueva_descripcion
            if nueva_duracion:
                campos.append("duracion = :duracion")
                parametros['duracion'] = nueva_duracion
            if nuevo_estado:
                campos.append("estado = :estado")
                parametros['estado'] = nuevo_estado

            if not campos:
                print("⚠️ No se proporcionaron campos para actualizar.")
                return

            query = f"UPDATE Carreras SET {', '.join(campos)} WHERE idCarrera = :id"

            with db.engine.connect() as conn:
                conn.execute(text(query), parametros)
                conn.commit()
                print(f"✅ Carrera con ID {id_carrera} actualizada correctamente.")
        except Exception as e:
            print(f"❌ ERROR al actualizar la carrera {id_carrera}: {str(e)}")

    # ===============================
    # 5️⃣ ELIMINAR CARRERA
    # ===============================
    def eliminar_carrera(self, id_carrera):
        """Elimina una carrera según su ID."""
        try:
            with db.engine.connect() as conn:
                conn.execute(text("""
                    DELETE FROM Carreras WHERE idCarrera = :id
                """), {'id': id_carrera})
                conn.commit()
                print(f"🗑️ Carrera con ID {id_carrera} eliminada correctamente.")
        except Exception as e:
            print(f"❌ ERROR al eliminar la carrera {id_carrera}: {str(e)}")
