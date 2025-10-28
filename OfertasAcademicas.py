from DataBase import db
from sqlalchemy import text

class OfertasAcademicas:
    def __init__(self):
        pass

    # ===============================
    # 1️⃣ CREAR TABLAS
    # ===============================
    def crear_tablas_ofertas(self):
        """Crea las tablas OfertasAcademicas y OfertaDetalle si no existen."""
        try:
            with db.engine.connect() as conn:
                # Tabla OfertasAcademicas
                conn.execute(text("""
                    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'OfertasAcademicas')
                    CREATE TABLE OfertasAcademicas (
                        idOferta INT IDENTITY(1,1) PRIMARY KEY,
                        nombreOferta VARCHAR(120) NOT NULL,
                        idPeriodo INT NOT NULL,
                        estado VARCHAR(20) NOT NULL DEFAULT 'Activa'
                            CHECK (estado IN ('Activa','Inactiva')),
                        fechaCreacion DATETIME NOT NULL DEFAULT GETDATE(),
                        fechaActualizacion DATETIME NOT NULL DEFAULT GETDATE()
                    )
                """))

                # Tabla detalle de carreras en la oferta
                conn.execute(text("""
                    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'OfertaDetalle')
                    CREATE TABLE OfertaDetalle (
                        idDetalle INT IDENTITY(1,1) PRIMARY KEY,
                        idOferta INT NOT NULL,
                        idCarrera INT NOT NULL,
                        jornada VARCHAR(50) NOT NULL,
                        modalidad VARCHAR(50) NOT NULL,
                        tipoCupo VARCHAR(50) NOT NULL,
                        totalCupos INT NOT NULL CHECK (totalCupos > 0),
                        FOREIGN KEY (idOferta) REFERENCES OfertasAcademicas(idOferta),
                        FOREIGN KEY (idCarrera) REFERENCES Carreras(idCarrera)
                    )
                """))

                # Trigger para actualizar fechaActualizacion
                conn.execute(text("""
                    CREATE OR ALTER TRIGGER trg_Update_Ofertas
                    ON OfertasAcademicas
                    AFTER UPDATE
                    AS
                    BEGIN
                        UPDATE OfertasAcademicas
                        SET fechaActualizacion = GETDATE()
                        WHERE idOferta IN (SELECT idOferta FROM inserted)
                    END
                """))

                conn.commit()
                print("✅ Tablas de Ofertas Académicas creadas correctamente.")
        except Exception as e:
            print(f"❌ ERROR al crear tablas: {str(e)}")

    # ===============================
    # 2️⃣ CREAR OFERTA
    # ===============================
    def crear_oferta(self, nombre_oferta, id_periodo, estado="Activa", carreras_cupos=[]):
        """
        Crea una oferta académica con estado y detalle de carreras.
        carreras_cupos: lista de diccionarios con
        {'idCarrera': 1, 'jornada': 'Diurna', 'modalidad': 'Presencial', 'tipoCupo': 'Regular', 'totalCupos': 50}
        """
        try:
            with db.engine.connect() as conn:
                result = conn.execute(text("""
                    INSERT INTO OfertasAcademicas (nombreOferta, idPeriodo, estado)
                    VALUES (:nombre, :periodo, :estado);
                    SELECT SCOPE_IDENTITY() AS idOferta;
                """), {'nombre': nombre_oferta, 'periodo': id_periodo, 'estado': estado})

                id_oferta = result.fetchone()[0]

                for c in carreras_cupos:
                    conn.execute(text("""
                        INSERT INTO OfertaDetalle (idOferta, idCarrera, jornada, modalidad, tipoCupo, totalCupos)
                        VALUES (:idOferta, :idCarrera, :jornada, :modalidad, :tipoCupo, :totalCupos)
                    """), {
                        'idOferta': id_oferta,
                        'idCarrera': c['idCarrera'],
                        'jornada': c['jornada'],
                        'modalidad': c['modalidad'],
                        'tipoCupo': c['tipoCupo'],
                        'totalCupos': c['totalCupos']
                    })

                conn.commit()
                print(f"✅ Oferta '{nombre_oferta}' creada con éxito. Estado: {estado}")
        except Exception as e:
            print(f"❌ ERROR al crear la oferta: {str(e)}")

    # ===============================
    # 3️⃣ VER OFERTAS
    # ===============================
    def ver_ofertas(self, id_periodo=None):
        """
        Muestra todas las ofertas, opcionalmente filtrando por periodo.
        Desglosa las carreras con jornada, modalidad, tipo de cupo y total de cupos.
        """
        try:
            with db.engine.connect() as conn:
                query = """
                    SELECT o.idOferta, o.nombreOferta, o.idPeriodo, o.estado,
                           c.nombreCarrera, d.jornada, d.modalidad, d.tipoCupo, d.totalCupos
                    FROM OfertasAcademicas o
                    LEFT JOIN OfertaDetalle d ON o.idOferta = d.idOferta
                    LEFT JOIN Carreras c ON d.idCarrera = c.idCarrera
                """
                params = {}
                if id_periodo:
                    query += " WHERE o.idPeriodo = :periodo"
                    params['periodo'] = id_periodo

                query += " ORDER BY o.nombreOferta, c.nombreCarrera"

                result = conn.execute(text(query), params)
                ofertas = result.fetchall()

                if not ofertas:
                    print("📭 No hay ofertas registradas.")
                    return

                current_oferta = None
                for fila in ofertas:
                    if current_oferta != fila.idOferta:
                        current_oferta = fila.idOferta
                        print(f"\n🎯 Oferta: {fila.nombreOferta} | Periodo: {fila.idPeriodo} | Estado: {fila.estado}")
                        print("Carreras:")
                    if fila.nombreCarrera:
                        print(f"  - {fila.nombreCarrera} | Jornada: {fila.jornada} | Modalidad: {fila.modalidad} | Tipo Cupo: {fila.tipoCupo} | Total Cupos: {fila.totalCupos}")

        except Exception as e:
            print(f"❌ ERROR al consultar ofertas: {str(e)}")

    # ===============================
    # 4️⃣ MODIFICAR OFERTA
    # ===============================
    def modificar_oferta(self, id_oferta, nuevo_nombre=None, nuevo_periodo=None, nuevo_estado=None,
                         agregar_carreras=[], eliminar_carreras=[], modificar_carreras=[]):
        """
        Modifica la oferta:
        - nuevo_nombre, nuevo_periodo, nuevo_estado
        - agregar_carreras: lista de dicts como en crear_oferta
        - eliminar_carreras: lista de idCarrera a eliminar
        - modificar_carreras: lista de dicts con idCarrera + campos a modificar
        """
        try:
            with db.engine.connect() as conn:
                campos = []
                params = {'idOferta': id_oferta}

                if nuevo_nombre:
                    campos.append("nombreOferta = :nombre")
                    params['nombre'] = nuevo_nombre
                if nuevo_periodo:
                    campos.append("idPeriodo = :periodo")
                    params['periodo'] = nuevo_periodo
                if nuevo_estado:
                    campos.append("estado = :estado")
                    params['estado'] = nuevo_estado

                if campos:
                    query = f"UPDATE OfertasAcademicas SET {', '.join(campos)} WHERE idOferta = :idOferta"
                    conn.execute(text(query), params)

                # Eliminar carreras
                for id_c in eliminar_carreras:
                    conn.execute(text("DELETE FROM OfertaDetalle WHERE idOferta = :idOferta AND idCarrera = :idCarrera"),
                                 {'idOferta': id_oferta, 'idCarrera': id_c})

                # Agregar carreras
                for c in agregar_carreras:
                    conn.execute(text("""
                        INSERT INTO OfertaDetalle (idOferta, idCarrera, jornada, modalidad, tipoCupo, totalCupos)
                        VALUES (:idOferta, :idCarrera, :jornada, :modalidad, :tipoCupo, :totalCupos)
                    """), {
                        'idOferta': id_oferta,
                        'idCarrera': c['idCarrera'],
                        'jornada': c['jornada'],
                        'modalidad': c['modalidad'],
                        'tipoCupo': c['tipoCupo'],
                        'totalCupos': c['totalCupos']
                    })

                # Modificar carreras existentes
                for c in modificar_carreras:
                    campos_detalle = []
                    params_detalle = {'idOferta': id_oferta, 'idCarrera': c['idCarrera']}
                    for campo in ['jornada','modalidad','tipoCupo','totalCupos']:
                        if campo in c:
                            campos_detalle.append(f"{campo} = :{campo}")
                            params_detalle[campo] = c[campo]
                    if campos_detalle:
                        query_det = f"UPDATE OfertaDetalle SET {', '.join(campos_detalle)} WHERE idOferta = :idOferta AND idCarrera = :idCarrera"
                        conn.execute(text(query_det), params_detalle)

                conn.commit()
                print(f"✅ Oferta con ID {id_oferta} modificada correctamente.")

        except Exception as e:
            print(f"❌ ERROR al modificar oferta: {str(e)}")

    # ===============================
    # 5️⃣ ELIMINAR OFERTA
    # ===============================
    def eliminar_oferta(self, id_oferta):
        try:
            with db.engine.connect() as conn:
                conn.execute(text("DELETE FROM OfertaDetalle WHERE idOferta = :idOferta"), {'idOferta': id_oferta})
                conn.execute(text("DELETE FROM OfertasAcademicas WHERE idOferta = :idOferta"), {'idOferta': id_oferta})
                conn.commit()
                print(f"🗑️ Oferta con ID {id_oferta} eliminada correctamente.")
        except Exception as e:
            print(f"❌ ERROR al eliminar oferta: {str(e)}")

