from DataBase import db
from sqlalchemy import text
import datetime

class Inscripciones:
    """Gestiona estudiantes e inscripciones en ofertas académicas - VERSIÓN COMPATIBLE"""
    def __init__(self):
        pass

    def crear_tablas_compatibles(self):
        """
        Crea las tablas de forma compatible con tu sistema existente
        """
        try:
            with db.engine.connect() as conn:
                print("\n CREANDO SISTEMA DE INSCRIPCIONES")
                print("=" * 50)
                
                # 1. Crear tabla OfertasAcademicas
                conn.execute(text("""
                    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'OfertasAcademicas')
                    CREATE TABLE OfertasAcademicas (
                        idOferta INT IDENTITY(1,1) PRIMARY KEY,
                        nombreOferta VARCHAR(100) NOT NULL,
                        descripcion VARCHAR(500),
                        idPeriodo INT NOT NULL,
                        idCarrera INT NOT NULL,
                        cupos INT DEFAULT 50,
                        estado VARCHAR(20) DEFAULT 'Activo',
                        fechaInicio DATE NOT NULL,
                        fechaFin DATE NOT NULL,
                        fechaCreacion DATETIME DEFAULT GETDATE()
                    )
                """))
                print(" Tabla 'OfertasAcademicas' creada/verificada")
                
                # 2. Asegurar que la tabla Estudiantes existe con estructura simple
                conn.execute(text("""
                    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'Estudiantes')
                    CREATE TABLE Estudiantes (
                        idEstudiante INT IDENTITY(1,1) PRIMARY KEY,
                        cedula VARCHAR(50) NOT NULL UNIQUE,
                        nombres VARCHAR(100) NOT NULL,
                        apellidos VARCHAR(100) NOT NULL,
                        fechaNacimiento DATE,
                        carreraId INT NOT NULL,
                        estado VARCHAR(20) DEFAULT 'Activo',
                        fechaRegistro DATETIME DEFAULT GETDATE()
                    )
                """))
                print(" Tabla 'Estudiantes' verificada")
                
                # 3. Agregar campos adicionales si no existen
                try:
                    conn.execute(text("""
                        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                                    WHERE TABLE_NAME = 'Estudiantes' AND COLUMN_NAME = 'email')
                        ALTER TABLE Estudiantes ADD email VARCHAR(100) NULL;
                    """))
                    print(" Campo 'email' agregado (si no existía)")
                    
                    conn.execute(text("""
                        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                                    WHERE TABLE_NAME = 'Estudiantes' AND COLUMN_NAME = 'telefono')
                        ALTER TABLE Estudiantes ADD telefono VARCHAR(20) NULL;
                    """))
                    print(" Campo 'telefono' agregado (si no existía)")
                except:
                    pass 
                
                # 4. Crear tabla Inscripciones
                conn.execute(text("""
                    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'Inscripciones')
                    CREATE TABLE Inscripciones (
                        idInscripcion INT IDENTITY(1,1) PRIMARY KEY,
                        idEstudiante INT NOT NULL,
                        idOferta INT NOT NULL,
                        idCarrera INT NOT NULL,
                        fechaInscripcion DATETIME NOT NULL DEFAULT GETDATE(),
                        estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente',
                        observaciones VARCHAR(500),
                        fechaActualizacion DATETIME NOT NULL DEFAULT GETDATE()
                    )
                """))
                print(" Tabla 'Inscripciones' creada")
                
                conn.commit()
                print("\n SISTEMA DE INSCRIPCIONES LISTO PARA USAR")
                return True
                
        except Exception as e:
            print(f" Error al crear tablas compatibles: {str(e)}")
            return False

    def registrar_estudiante_compatible(self, registro_aspirante, id_carrera, email="", telefono=""):
        """
        Registra un estudiante de forma compatible con tu sistema actual
        """
        try:
            with db.engine.connect() as conn:
                # Verificar si ya existe
                result = conn.execute(text("""
                    SELECT idEstudiante FROM Estudiantes WHERE cedula = :cedula
                """), {'cedula': registro_aspirante.identificacion})
                
                if result.fetchone():
                    print("  El estudiante ya está registrado")
                    return False
                
                # Insertar usando estructura compatible
                conn.execute(text("""
                    INSERT INTO Estudiantes (cedula, nombres, apellidos, carreraId, email, telefono, estado)
                    VALUES (:cedula, :nombres, :apellidos, :carreraId, :email, :telefono, 'Activo')
                """), {
                    'cedula': registro_aspirante.identificacion,
                    'nombres': registro_aspirante.nombres,
                    'apellidos': registro_aspirante.apellidos,
                    'carreraId': id_carrera,
                    'email': email,
                    'telefono': telefono
                })
                conn.commit()
                
                print(f" Estudiante registrado exitosamente:")
                print(f"   • Cédula: {registro_aspirante.identificacion}")
                print(f"   • Nombres: {registro_aspirante.nombres} {registro_aspirante.apellidos}")
                print(f"   • Carrera ID: {id_carrera}")
                return True
                
        except Exception as e:
            print(f" Error al registrar estudiante: {str(e)}")
            return False

    def crear_inscripcion_automatica(self, cedula_estudiante, id_carrera):
        """
        Crea una inscripción automática para un estudiante
        """
        try:
            with db.engine.connect() as conn:
                # 1. Obtener ID del estudiante
                estudiante = conn.execute(text("""
                    SELECT idEstudiante, nombres, apellidos 
                    FROM Estudiantes 
                    WHERE cedula = :cedula
                """), {'cedula': cedula_estudiante}).fetchone()
                
                if not estudiante:
                    print(" Estudiante no encontrado")
                    return False
                
                # 2. Buscar o crear una oferta académica para la carrera
                # Primero, buscar si existe oferta activa
                oferta = conn.execute(text("""
                    SELECT TOP 1 idOferta 
                    FROM OfertasAcademicas 
                    WHERE idCarrera = :carrera AND estado = 'Activo'
                """), {'carrera': id_carrera}).fetchone()
                
                # Si no existe, crear una automáticamente
                if not oferta:
                    print(" Creando oferta académica automáticamente...")
                    
                    # Obtener período activo o crear uno
                    periodo = conn.execute(text("""
                        SELECT TOP 1 idPeriodo FROM Periodos WHERE estado = 'Activo'
                    """)).fetchone()
                    
                    if not periodo:
                        # Crear un período por defecto
                        conn.execute(text("""
                            INSERT INTO Periodos (nombrePeriodo, fechaInicio, fechaFin, estado)
                            VALUES ('Periodo 2024-01', GETDATE(), DATEADD(MONTH, 6, GETDATE()), 'Activo')
                        """))
                        conn.commit()
                        periodo = conn.execute(text("SELECT @@IDENTITY as id")).fetchone()
                    
                    # Crear la oferta
                    conn.execute(text("""
                        INSERT INTO OfertasAcademicas (nombreOferta, descripcion, idPeriodo, idCarrera, fechaInicio, fechaFin)
                        VALUES ('Oferta Inicial', 'Oferta académica inicial', :periodo, :carrera, GETDATE(), DATEADD(MONTH, 6, GETDATE()))
                    """), {
                        'periodo': periodo.idPeriodo,
                        'carrera': id_carrera
                    })
                    conn.commit()
                    
                    oferta = conn.execute(text("SELECT @@IDENTITY as idOferta")).fetchone()
                
                # 3. Crear la inscripción
                conn.execute(text("""
                    INSERT INTO Inscripciones (idEstudiante, idOferta, idCarrera, estado)
                    VALUES (:estudiante, :oferta, :carrera, 'Pendiente')
                """), {
                    'estudiante': estudiante.idEstudiante,
                    'oferta': oferta.idOferta,
                    'carrera': id_carrera
                })
                conn.commit()
                
                print(f" Inscripción creada exitosamente para:")
                print(f"   • Estudiante: {estudiante.nombres} {estudiante.apellidos}")
                print(f"   • Estado: Pendiente de revisión")
                return True
                
        except Exception as e:
            print(f" Error al crear inscripción: {str(e)}")
            return False

    def ver_inscripciones_estudiante(self, cedula_estudiante):
        """
        Muestra las inscripciones de un estudiante
        """
        try:
            with db.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT 
                        i.idInscripcion,
                        i.fechaInscripcion,
                        i.estado,
                        c.nombreCarrera,
                        o.nombreOferta,
                        i.observaciones
                    FROM Inscripciones i
                    JOIN Estudiantes e ON i.idEstudiante = e.idEstudiante
                    JOIN Carreras c ON i.idCarrera = c.idCarrera
                    LEFT JOIN OfertasAcademicas o ON i.idOferta = o.idOferta
                    WHERE e.cedula = :cedula
                    ORDER BY i.fechaInscripcion DESC
                """), {'cedula': cedula_estudiante})
                
                inscripciones = result.fetchall()
                
                if not inscripciones:
                    print(" No tienes inscripciones registradas")
                    return
                
                print(f"\n TUS INSCRIPCIONES:")
                print("=" * 70)
                for insc in inscripciones:
                    print(f"\n ID: {insc.idInscripcion}")
                    print(f" Fecha: {insc.fechaInscripcion.strftime('%Y-%m-%d')}")
                    print(f" Carrera: {insc.nombreCarrera}")
                    print(f" Oferta: {insc.nombreOferta or 'Generada automáticamente'}")
                    print(f" Estado: {insc.estado}")
                    if insc.observaciones:
                        print(f" Observaciones: {insc.observaciones}")
                print("=" * 70)
                
        except Exception as e:
            print(f" Error al consultar inscripciones: {str(e)}")

    def ver_todas_inscripciones(self):
        """
        Muestra todas las inscripciones del sistema (para administradores)
        """
        try:
            with db.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT 
                        i.idInscripcion,
                        e.nombres + ' ' + e.apellidos as estudiante,
                        e.cedula,
                        c.nombreCarrera,
                        i.estado,
                        i.fechaInscripcion,
                        i.observaciones
                    FROM Inscripciones i
                    JOIN Estudiantes e ON i.idEstudiante = e.idEstudiante
                    JOIN Carreras c ON i.idCarrera = c.idCarrera
                    ORDER BY i.fechaInscripcion DESC
                """))
                
                inscripciones = result.fetchall()
                
                if not inscripciones:
                    print(" No hay inscripciones en el sistema")
                    return
                
                print(f"\n TODAS LAS INSCRIPCIONES:")
                print("=" * 90)
                print(f"{'ID':<5} {'ESTUDIANTE':<25} {'CÉDULA':<12} {'CARRERA':<20} {'ESTADO':<12} {'FECHA':<12}")
                print("=" * 90)
                
                for insc in inscripciones:
                    print(f"{insc.idInscripcion:<5} {insc.estudiante:<25} {insc.cedula:<12} {insc.nombreCarrera:<20} {insc.estado:<12} {insc.fechaInscripcion.strftime('%Y-%m-%d'):<12}")
                print("=" * 90)
                
        except Exception as e:
            print(f" Error al consultar inscripciones: {str(e)}")

    def actualizar_estado_inscripcion(self, id_inscripcion, nuevo_estado, observaciones=None):

        """
        Actualiza el estado de una inscripción
        """
        try:
            with db.engine.connect() as conn:
                conn.execute(text("""
                    UPDATE Inscripciones 
                    SET estado = :estado, 
                        observaciones = :obs,
                        fechaActualizacion = GETDATE()
                    WHERE idInscripcion = :id
                """), {
                    'id': id_inscripcion,
                    'estado': nuevo_estado,
                    'obs': observaciones
                })
                conn.commit()
                
                print(f" Inscripción ID {id_inscripcion} actualizada a estado: {nuevo_estado}")
                return True
                
        except Exception as e:
            print(f" Error al actualizar inscripción: {str(e)}")
            return False

    def ver_todas_inscripciones_detalladas(self):
        """
        Muestra TODAS las inscripciones con información completa (para admin)
        VERSIÓN CORREGIDA - sin duracionSemestres
        """
        try:
            with db.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT 
                        i.idInscripcion,
                        i.fechaInscripcion,
                        i.estado,
                        e.nombres + ' ' + e.apellidos as estudiante_completo,
                        e.cedula,
                        e.email,
                        e.telefono,
                        c.nombreCarrera,
                        -- c.duracionSemestres,  -- COMENTADO TEMPORALMENTE
                        o.nombreOferta,
                        i.observaciones,
                        i.fechaActualizacion
                    FROM Inscripciones i
                    JOIN Estudiantes e ON i.idEstudiante = e.idEstudiante
                    JOIN Carreras c ON i.idCarrera = c.idCarrera
                    LEFT JOIN OfertasAcademicas o ON i.idOferta = o.idOferta
                    ORDER BY i.estado, i.fechaInscripcion DESC
                """))
                
                inscripciones = result.fetchall()
                
                if not inscripciones:
                    print("\n📭 No hay inscripciones registradas en el sistema")
                    return []
                
                print(f"\n TODAS LAS INSCRIPCIONES - VISTA DE ADMINISTRADOR")
                print("=" * 120)
                print(f"{'ID':<4} {'FECHA':<12} {'ESTADO':<12} {'ESTUDIANTE':<25} {'CÉDULA':<12} {'CARRERA':<20}")
                print("=" * 120)
                
                for insc in inscripciones:
                    fecha = insc.fechaInscripcion.strftime('%Y-%m-%d')
                    estado_color = ""
                    if insc.estado == 'Aprobada':
                        estado_color = "✅ "
                    elif insc.estado == 'Rechazada':
                        estado_color = "❌ "
                    elif insc.estado == 'Pendiente':
                        estado_color = "⏳ "
                    
                    print(f"{insc.idInscripcion:<4} {fecha:<12} {estado_color + insc.estado:<12} {insc.estudiante_completo:<25} {insc.cedula:<12} {insc.nombreCarrera:<20}")
                
                return inscripciones
                
        except Exception as e:
            print(f" Error al consultar inscripciones: {str(e)}")
            return []

    def ver_detalle_inscripcion(self, id_inscripcion):
        """
        Muestra el detalle completo de una inscripción específica
        """
        try:
            with db.engine.connect() as conn:
                query = """
                    SELECT 
                        i.idInscripcion,
                        i.fechaInscripcion,
                        i.estado,
                        i.observaciones,
                        i.fechaActualizacion,
                        e.nombres,
                        e.apellidos,
                        e.cedula,
                        e.email,
                        e.telefono,
                        e.fechaNacimiento,
                        c.nombreCarrera,
                        c.descripcion as descripcion_carrera,
                        c.duracionSemestres,
                        o.nombreOferta,
                        o.descripcion as descripcion_oferta,
                        o.fechaInicio,
                        o.fechaFin
                    FROM Inscripciones i
                    JOIN Estudiantes e ON i.idEstudiante = e.idEstudiante
                    JOIN Carreras c ON i.idCarrera = c.idCarrera
                    LEFT JOIN OfertasAcademicas o ON i.idOferta = o.idOferta
                    WHERE i.idInscripcion = :id
                """
                result = conn.execute(text(query), {'id': id_inscripcion})
                inscripcion = result.fetchone()
                
                if not inscripcion:
                    print(f" No se encontró inscripción con ID {id_inscripcion}")
                    return None
                
                # Mostrar resultados
                print(f"\n DETALLE COMPLETO DE INSCRIPCIÓN #{inscripcion.idInscripcion}")
                print("=" * 60)
                print(f" Fecha de inscripción: {inscripcion.fechaInscripcion.strftime('%Y-%m-%d %H:%M')}")
                print(f" Estado actual: {inscripcion.estado}")
                
                if inscripcion.fechaActualizacion:
                    print(f" Última actualización: {inscripcion.fechaActualizacion.strftime('%Y-%m-%d %H:%M')}")
                
                print(f"\n INFORMACIÓN DEL ESTUDIANTE:")
                print(f"   • Nombre completo: {inscripcion.nombres} {inscripcion.apellidos}")
                print(f"   • Cédula: {inscripcion.cedula}")
                
                if inscripcion.email:
                    print(f"   • Email: {inscripcion.email}")
                    
                if inscripcion.telefono:
                    print(f"   • Teléfono: {inscripcion.telefono}")
                    
                if inscripcion.fechaNacimiento:
                    try:
                        edad = (datetime.datetime.now().date() - inscripcion.fechaNacimiento).days // 365
                        print(f"   • Fecha nacimiento: {inscripcion.fechaNacimiento} (Aprox. {edad} años)")
                    except:
                        print(f"   • Fecha nacimiento: {inscripcion.fechaNacimiento}")
                
                print(f"\n🎓 INFORMACIÓN DE LA CARRERA:")
                print(f"   • Carrera: {inscripcion.nombreCarrera}")
                
                if inscripcion.descripcion_carrera:
                    print(f"   • Descripción: {inscripcion.descripcion_carrera}")
                    
                if inscripcion.duracionSemestres:
                    print(f"   • Duración: {inscripcion.duracionSemestres} semestres")
                
                if inscripcion.nombreOferta:
                    print(f"\n INFORMACIÓN DE LA OFERTA ACADÉMICA:")
                    print(f"   • Oferta: {inscripcion.nombreOferta}")
                    
                    if inscripcion.descripcion_oferta:
                        print(f"   • Descripción: {inscripcion.descripcion_oferta}")
                        
                    if inscripcion.fechaInicio:
                        print(f"   • Fecha inicio: {inscripcion.fechaInicio}")
                        
                    if inscripcion.fechaFin:
                        print(f"   • Fecha fin: {inscripcion.fechaFin}")
                
                if inscripcion.observaciones:
                    print(f"\n OBSERVACIONES:")
                    print(f"   {inscripcion.observaciones}")
                
                print("=" * 60)
                return inscripcion
                
        except Exception as e:
            print(f"❌ Error al consultar detalle: {str(e)}")
            return None
    
    def filtrar_inscripciones_por_estado(self, estado):
        """
        Filtra inscripciones por estado específico
        """
        try:
            with db.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT 
                        i.idInscripcion,
                        i.fechaInscripcion,
                        i.estado,
                        e.nombres + ' ' + e.apellidos as estudiante,
                        e.cedula,
                        c.nombreCarrera
                    FROM Inscripciones i
                    JOIN Estudiantes e ON i.idEstudiante = e.idEstudiante
                    JOIN Carreras c ON i.idCarrera = c.idCarrera
                    WHERE i.estado = :estado
                    ORDER BY i.fechaInscripcion DESC
                """), {'estado': estado})
                
                inscripciones = result.fetchall()
                
                if not inscripciones:
                    print(f"\n📭 No hay inscripciones con estado '{estado}'")
                    return []
                
                print(f"\n INSCRIPCIONES CON ESTADO '{estado.upper()}':")
                print("=" * 80)
                print(f"{'ID':<4} {'FECHA':<12} {'ESTUDIANTE':<25} {'CÉDULA':<12} {'CARRERA':<20}")
                print("=" * 80)
                
                for insc in inscripciones:
                    fecha = insc.fechaInscripcion.strftime('%Y-%m-%d')
                    print(f"{insc.idInscripcion:<4} {fecha:<12} {insc.estudiante:<25} {insc.cedula:<12} {insc.nombreCarrera:<20}")
                
                print(f"\n Total: {len(inscripciones)} inscripción(es)")
                return inscripciones
                
        except Exception as e:
            print(f"❌ Error al filtrar inscripciones: {str(e)}")
            return []
    
    def generar_reporte_estadisticas(self):
        """
        Genera un reporte estadístico de las inscripciones
        """
        try:
            with db.engine.connect() as conn:
                # Total de inscripciones
                result = conn.execute(text("SELECT COUNT(*) as total FROM Inscripciones"))
                total = result.fetchone().total
                
                # Por estado
                result = conn.execute(text("""
                    SELECT estado, COUNT(*) as cantidad
                    FROM Inscripciones
                    GROUP BY estado
                    ORDER BY cantidad DESC
                """))
                por_estado = result.fetchall()
                
                # Por carrera
                result = conn.execute(text("""
                    SELECT c.nombreCarrera, COUNT(*) as cantidad
                    FROM Inscripciones i
                    JOIN Carreras c ON i.idCarrera = c.idCarrera
                    GROUP BY c.nombreCarrera
                    ORDER BY cantidad DESC
                """))
                por_carrera = result.fetchall()
                
                # Última semana
                result = conn.execute(text("""
                    SELECT COUNT(*) as ultima_semana
                    FROM Inscripciones
                    WHERE fechaInscripcion >= DATEADD(day, -7, GETDATE())
                """))
                ultima_semana = result.fetchone().ultima_semana
                
                print(f"\n📊 REPORTE ESTADÍSTICO DE INSCRIPCIONES")
                print("=" * 60)
                print(f"📈 TOTAL DE INSCRIPCIONES: {total}")
                print(f"📅 ÚLTIMA SEMANA: {ultima_semana} nueva(s) inscripción(es)")
                
                print(f"\n📋 DISTRIBUCIÓN POR ESTADO:")
                print("-" * 40)
                for estado in por_estado:
                    porcentaje = (estado.cantidad / total * 100) if total > 0 else 0
                    print(f"   • {estado.estado}: {estado.cantidad} ({porcentaje:.1f}%)")
                
                print(f"\n🎓 DISTRIBUCIÓN POR CARRERA:")
                print("-" * 40)
                for carrera in por_carrera:
                    porcentaje = (carrera.cantidad / total * 100) if total > 0 else 0
                    print(f"   • {carrera.nombreCarrera}: {carrera.cantidad} ({porcentaje:.1f}%)")
                
                print("=" * 60)
                
        except Exception as e:
            print(f"❌ Error al generar reporte: {str(e)}")