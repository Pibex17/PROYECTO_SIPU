
from DataBase import db
from sqlalchemy import text
from Periodos import Periodos
from Carreras import Carreras
from Estudiante import Aspirante
from Inscripciones import Inscripciones
import datetime

sistema_inscripciones = None

def main():
    print("🎓 SISTEMA DE INSCRIPCIÓN UNIVERSITARIA")
    print("=" * 50)
    print("🔧 Usando: SQL Server Express (localhost\\SQLEXPRESS)")
    print("=" * 50)
    
    # Paso 1: Conectar al servidor correcto
    if not db.conectar():
        print("No se puede continuar sin conexión a la base de datos.")
        return
    
    # Paso 2: Verificar/Crear base de datos
    if not db.verificar_base_datos():
        return
    
    # Paso 3: Reparar estructuras de tablas
    reparar_estructuras_tablas()

    # Inicializar sistema de inscripciones
    global sistema_inscripciones
    sistema_inscripciones = Inscripciones()
    sistema_inscripciones.crear_tablas_compatibles()
    
    # Paso 3: Mostrar menú principal
    menu_acceso()

def reparar_estructuras_tablas():
    """Repara todas las tablas agregando columnas faltantes"""
    print("\n🛠️  REPARANDO ESTRUCTURAS DE TABLAS")
    print("=" * 50)
    
    try:
        with db.engine.connect() as conn:
            # 1. Reparar tabla Carreras
            print("\n🔧 TABLA 'Carreras':")
            try:
                # Verificar si existe columna duracionSemestres
                result = conn.execute(text("""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'Carreras' AND COLUMN_NAME = 'duracionSemestres'
                """))
                
                if not result.fetchone():
                    print("  📝 Agregando columna 'duracionSemestres'...")
                    conn.execute(text("ALTER TABLE Carreras ADD duracionSemestres INT DEFAULT 10"))
                    print("  ✅ Columna 'duracionSemestres' agregada")
                else:
                    print("  ✅ Columna 'duracionSemestres' ya existe")
                    
                # Verificar si existe columna descripcion
                result = conn.execute(text("""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'Carreras' AND COLUMN_NAME = 'descripcion'
                """))
                
                if not result.fetchone():
                    print("  📝 Agregando columna 'descripcion'...")
                    conn.execute(text("ALTER TABLE Carreras ADD descripcion VARCHAR(500)"))
                    print("  ✅ Columna 'descripcion' agregada")
                else:
                    print("  ✅ Columna 'descripcion' ya existe")
                    
            except Exception as e:
                print(f"  ❌ Error al reparar Carreras: {e}")
            
            # 2. Reparar tabla Estudiantes
            print("\n🔧 TABLA 'Estudiantes':")
            try:
                columnas_estudiantes = ['email', 'telefono', 'fechaNacimiento']
                
                for columna in columnas_estudiantes:
                    result = conn.execute(text(f"""
                        SELECT COLUMN_NAME 
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME = 'Estudiantes' AND COLUMN_NAME = '{columna}'
                    """))
                    
                    if not result.fetchone():
                        print(f"  📝 Agregando columna '{columna}'...")
                        
                        if columna == 'email':
                            conn.execute(text("ALTER TABLE Estudiantes ADD email VARCHAR(100)"))
                        elif columna == 'telefono':
                            conn.execute(text("ALTER TABLE Estudiantes ADD telefono VARCHAR(20)"))
                        elif columna == 'fechaNacimiento':
                            conn.execute(text("ALTER TABLE Estudiantes ADD fechaNacimiento DATE"))
                            
                        print(f"  ✅ Columna '{columna}' agregada")
                    else:
                        print(f"  ✅ Columna '{columna}' ya existe")
                        
            except Exception as e:
                print(f"  ❌ Error al reparar Estudiantes: {e}")
            
            # 3. Reparar tabla Inscripciones
            print("\n🔧 TABLA 'Inscripciones':")
            try:
                columnas_inscripciones = ['observaciones', 'fechaActualizacion']
                
                for columna in columnas_inscripciones:
                    result = conn.execute(text(f"""
                        SELECT COLUMN_NAME 
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME = 'Inscripciones' AND COLUMN_NAME = '{columna}'
                    """))
                    
                    if not result.fetchone():
                        print(f"  📝 Agregando columna '{columna}'...")
                        
                        if columna == 'observaciones':
                            conn.execute(text("ALTER TABLE Inscripciones ADD observaciones VARCHAR(500)"))
                        elif columna == 'fechaActualizacion':
                            conn.execute(text("ALTER TABLE Inscripciones ADD fechaActualizacion DATETIME DEFAULT GETDATE()"))
                            
                        print(f"  ✅ Columna '{columna}' agregada")
                    else:
                        print(f"  ✅ Columna '{columna}' ya existe")
                        
            except Exception as e:
                print(f"  ❌ Error al reparar Inscripciones: {e}")
            
            # 4. Crear tabla OfertasAcademicas si no existe
            print("\n🔧 TABLA 'OfertasAcademicas':")
            try:
                result = conn.execute(text("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME = 'OfertasAcademicas'
                """))
                
                if not result.fetchone():
                    print("  📝 Creando tabla 'OfertasAcademicas'...")
                    conn.execute(text("""
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
                    print("  ✅ Tabla 'OfertasAcademicas' creada")
                else:
                    print("  ✅ Tabla 'OfertasAcademicas' ya existe")
                    
            except Exception as e:
                print(f"  ❌ Error al crear OfertasAcademicas: {e}")
            
            conn.commit()
            print("\n🎉 ¡TODAS LAS TABLAS REPARADAS EXITOSAMENTE!")
            return True
            
    except Exception as e:
        print(f"❌ Error general en reparación: {e}")
        return False

def menu_acceso():
    while True:
        print("\n" + "=" * 50)
        print("ACCESO AL SISTEMA UNIVERSITARIO")
        print("=" * 50)
        print("1. Administrador")
        print("2. Estudiante")
        print("3. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            menu_principal()   #ADMIN EXISTENTE
        elif opcion == "2":
            acceso_estudiante()
        elif opcion == "3":
            break
        else:
            print("❌ Opción inválida")

def acceso_estudiante():
    """Acceso para estudiantes/aspirantes"""
    print("\n" + "=" * 50)
    print("ACCESO DE ESTUDIANTE")
    print("=" * 50)
    
    # Pedir datos de identificación
    print("\n📋 VALIDACIÓN EN REGISTRO NACIONAL")
    print("-" * 40)
    
    tipo_documento = input("Tipo de documento (cédula/pasaporte): ").strip()
    numero_identificacion = input("Número de identificación: ").strip()
    
    # Validar en registro nacional
    registro_valido = Aspirante.validar_en_registro_nacional(tipo_documento, numero_identificacion)
    
    if registro_valido:
        print(f"\n✅ ACCESO PERMITIDO")
        print(f"   Nombre: {registro_valido.nombres} {registro_valido.apellidos}")
        print(f"   Documento: {registro_valido.tipoDocumento} {registro_valido.identificacion}")
        
        # Opciones después de validar
        print("\n📋 ¿Qué desea hacer?")
        print("1. Inscribirme en una carrera (Nuevo estudiante)")
        print("2. Ver mis inscripciones (Estudiante registrado)")
        print("3. Salir")
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == "1":
            # Proceso de inscripción usando el sistema de inscripciones
            registrar_estudiante_nuevo_sistema(registro_valido)
        elif opcion == "2":
            # Verificar inscripciones existentes usando el nuevo sistema
            sistema_inscripciones.ver_inscripciones_estudiante(numero_identificacion)
        elif opcion == "3":
            print("¡Hasta luego! 👋")
        else:
            print("❌ Opción inválida")
    else:
        print("\n❌ ACCESO DENEGADO")
        print("   No se encontró en el Registro Nacional o su estado no es activo")


def registrar_estudiante_nuevo_sistema(registro_aspirante):
    """
    Registra automáticamente al aspirante como estudiante
    usando el nuevo sistema de inscripciones
    """
    print("\n🎓 REGISTRO COMO ESTUDIANTE")
    print("=" * 50)
    
    # Mostrar datos obtenidos del registro nacional
    print("📋 DATOS OBTENIDOS DEL REGISTRO NACIONAL:")
    print("-" * 40)
    print(f"• Cédula: {registro_aspirante.identificacion}")
    print(f"• Nombres: {registro_aspirante.nombres}")
    print(f"• Apellidos: {registro_aspirante.apellidos}")
    print("-" * 40)
    
    # Solicitar información adicional opcional
    print("\n📝 INFORMACIÓN ADICIONAL (Opcional):")
    email = input("Correo electrónico (opcional): ").strip()
    telefono = input("Teléfono (opcional): ").strip()
    
    # Mostrar carreras disponibles
    print("\n🎯 CARRERAS DISPONIBLES:")
    print("-" * 40)
    
    carreras = Carreras()
    carreras.ver_carreras_para_inscripcion()
    
    # Seleccionar carrera
    while True:
        try:
            carrera_id = int(input("\n🔢 Ingrese el ID de la carrera a la que desea inscribirse: "))
            
            # Validar que la carrera existe
            try:
                with db.engine.connect() as conn:
                    result = conn.execute(text("""
                        SELECT idCarrera, nombreCarrera 
                        FROM Carreras 
                        WHERE idCarrera = :id AND estado = 'Activa'
                    """), {"id": carrera_id})
                    carrera = result.fetchone()
                    
                    if not carrera:
                        print("❌ Carrera no encontrada o inactiva")
                        continue
                    
                    print(f"\n📋 CONFIRMACIÓN DE INSCRIPCIÓN:")
                    print("-" * 40)
                    print(f"• Estudiante: {registro_aspirante.nombres} {registro_aspirante.apellidos}")
                    print(f"• Cédula: {registro_aspirante.identificacion}")
                    print(f"• Carrera: {carrera.nombreCarrera}")
                    
                    # Confirmar registro
                    confirmar = input(f"\n✅ ¿Confirmar inscripción? (s/n): ").strip().lower()
                    
                    if confirmar == 's':
                        # Registrar estudiante usando el nuevo sistema
                        resultado_registro = sistema_inscripciones.registrar_estudiante_compatible(
                            registro_aspirante=registro_aspirante,
                            id_carrera=carrera_id,
                            email=email,
                            telefono=telefono
                        )
                        
                        if resultado_registro:
                            # Crear inscripción automática
                            resultado_inscripcion = sistema_inscripciones.crear_inscripcion_automatica(
                                cedula_estudiante=registro_aspirante.identificacion,
                                id_carrera=carrera_id
                            )
                            
                            if resultado_inscripcion:
                                print(f"\n🎉 ¡INSCRIPCIÓN COMPLETADA EXITOSAMENTE!")
                                print(f"   Tu solicitud está en estado: Pendiente")
                                print(f"   Recibirás una notificación cuando sea revisada")
                            else:
                                print("\n⚠️  Estudiante registrado pero no se pudo crear la inscripción")
                                print("   Por favor contacta con administración")
                        return
                    else:
                        print("❌ Inscripción cancelada")
                        return
                        
            except Exception as e:
                print(f"❌ Error al validar carrera: {e}")
                continue
                
        except ValueError:
            print("❌ Por favor ingrese un número válido")
            continue
    """Acceso para estudiantes/aspirantes"""
    print("\n" + "=" * 50)
    print("ACCESO DE ESTUDIANTE")
    print("=" * 50)
    
    # Pedir datos de identificación
    print("\n📋 VALIDACIÓN EN REGISTRO NACIONAL")
    print("-" * 40)
    
    tipo_documento = input("Tipo de documento (cédula/pasaporte): ").strip()
    numero_identificacion = input("Número de identificación: ").strip()
    
    # Validar en registro nacional
    registro_valido = Aspirante.validar_en_registro_nacional(tipo_documento, numero_identificacion)
    
    if registro_valido:
        print(f"\n✅ ACCESO PERMITIDO")
        print(f"   Nombre: {registro_valido.nombres} {registro_valido.apellidos}")
        print(f"   Documento: {registro_valido.tipoDocumento} {registro_valido.identificacion}")
        
        # Opciones después de validar
        print("\n📋 ¿Qué desea hacer?")
        print("1. Registrarme como estudiante")
        print("2. Ver mis inscripciones")
        print("3. Salir")
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == "1":
            # Proceso de registro como estudiante
            registrar_estudiante_desde_aspirante(registro_valido)
        elif opcion == "2":
            # Verificar si ya está registrado como estudiante
            estudiante = Aspirante.buscar_estudiante_por_identificacion(numero_identificacion)
            if estudiante:
                # Obtener nombre de la carrera
                try:
                    with db.engine.connect() as conn:
                        result = conn.execute(text("""
                            SELECT nombreCarrera 
                            FROM Carreras 
                            WHERE idCarrera = :id
                        """), {"id": estudiante.carreraId})
                        carrera = result.fetchone()
                        nombre_carrera = carrera.nombreCarrera if carrera else "Desconocida"
                except Exception as e:
                    nombre_carrera = "Error al obtener"
                
                print(f"\n👤 Ya está registrado como estudiante")
                print(f"   Carrera: {nombre_carrera} (ID: {estudiante.carreraId})")
                print(f"   Estado: {estudiante.estado}")
            else:
                print("\n⚠️  No está registrado como estudiante aún")
        elif opcion == "3":
            print("¡Hasta luego! 👋")
        else:
            print("❌ Opción inválida")
    else:
        print("\n❌ ACCESO DENEGADO")
        print("   No se encontró en el Registro Nacional o su estado no es activo")

def registrar_estudiante_desde_aspirante(registro_aspirante):
    """Registra a un aspirante como estudiante"""
    print("\n🎓 REGISTRO COMO ESTUDIANTE")
    print("-" * 40)
    
    # Obtener información del aspirante
    nombres = registro_aspirante.nombres
    apellidos = registro_aspirante.apellidos
    cedula = registro_aspirante.identificacion
    
    # Verificar si ya está registrado
    estudiante_existente = Aspirante.buscar_estudiante_por_identificacion(cedula)
    if estudiante_existente:
        print("⚠️  Ya está registrado como estudiante")
        return
    
    # Solicitar información adicional
    fecha_nacimiento = input("Fecha de nacimiento (YYYY-MM-DD): ").strip()
    
    # Validar formato de fecha
    try:
        datetime.datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
    except ValueError:
        print("❌ Formato de fecha inválido. Use YYYY-MM-DD")
        return
    
    # Mostrar carreras disponibles
    carreras = Carreras()
    carreras.ver_carreras()
    
    # Seleccionar carrera
    carrera_id = input("\nID de la carrera a inscribirse: ").strip()
    
    # Validar que la carrera existe y está activa
    try:
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT idCarrera, nombreCarrera 
                FROM Carreras 
                WHERE idCarrera = :id AND estado = 'Activa'
            """), {"id": carrera_id})
            carrera = result.fetchone()
            if not carrera:
                print("❌ Carrera no encontrada o inactiva")
                return
            nombre_carrera = carrera.nombreCarrera
    except Exception as e:
        print(f"❌ Error al validar carrera: {e}")
        return
    
    # Confirmar registro
    confirmar = input(f"\n¿Confirmar registro de {nombres} {apellidos} en la carrera '{nombre_carrera}'? (s/n): ").strip().lower()
    
    if confirmar == 's':
        # Registrar estudiante
        resultado = Aspirante.registrar_estudiante(cedula, nombres, apellidos, fecha_nacimiento, int(carrera_id))
        if resultado:
            print("🎉 ¡Registro completado exitosamente!")
    else:
        print("❌ Registro cancelado")

def registrar_estudiante_desde_aspirante(registro_aspirante):
    """
    Registra automáticamente al aspirante como estudiante
    usando el nuevo sistema de inscripciones
    """
    print("\n🎓 REGISTRO COMO ESTUDIANTE")
    print("=" * 50)
    
    # Mostrar datos obtenidos del registro nacional
    print("📋 DATOS OBTENIDOS DEL REGISTRO NACIONAL:")
    print("-" * 40)
    print(f"• Cédula: {registro_aspirante.identificacion}")
    print(f"• Nombres: {registro_aspirante.nombres}")
    print(f"• Apellidos: {registro_aspirante.apellidos}")
    print("-" * 40)
    
    # Solicitar información adicional opcional
    print("\n📝 INFORMACIÓN ADICIONAL (Opcional):")
    email = input("Correo electrónico (opcional): ").strip()
    telefono = input("Teléfono (opcional): ").strip()
    
    # Mostrar carreras disponibles
    print("\n🎯 CARRERAS DISPONIBLES:")
    print("-" * 40)
    
    carreras = Carreras()
    carreras.ver_carreras_para_inscripcion()
    
    # Seleccionar carrera
    while True:
        try:
            carrera_id = int(input("\n🔢 Ingrese el ID de la carrera a la que desea inscribirse: "))
            
            # Validar que la carrera existe
            try:
                with db.engine.connect() as conn:
                    result = conn.execute(text("""
                        SELECT idCarrera, nombreCarrera 
                        FROM Carreras 
                        WHERE idCarrera = :id AND estado = 'Activa'
                    """), {"id": carrera_id})
                    carrera = result.fetchone()
                    
                    if not carrera:
                        print("❌ Carrera no encontrada o inactiva")
                        continue
                    
                    print(f"\n📋 CONFIRMACIÓN DE INSCRIPCIÓN:")
                    print("-" * 40)
                    print(f"• Estudiante: {registro_aspirante.nombres} {registro_aspirante.apellidos}")
                    print(f"• Cédula: {registro_aspirante.identificacion}")
                    print(f"• Carrera: {carrera.nombreCarrera}")
                    
                    # Confirmar registro
                    confirmar = input(f"\n✅ ¿Confirmar inscripción? (s/n): ").strip().lower()
                    
                    if confirmar == 's':
                        # Registrar estudiante usando el nuevo sistema
                        resultado_registro = sistema_inscripciones.registrar_estudiante_compatible(
                            registro_aspirante=registro_aspirante,
                            id_carrera=carrera_id,
                            email=email,
                            telefono=telefono
                        )
                        
                        if resultado_registro:
                            # Crear inscripción automática
                            resultado_inscripcion = sistema_inscripciones.crear_inscripcion_automatica(
                                cedula_estudiante=registro_aspirante.identificacion,
                                id_carrera=carrera_id
                            )
                            
                            if resultado_inscripcion:
                                print(f"\n🎉 ¡INSCRIPCIÓN COMPLETADA EXITOSAMENTE!")
                                print(f"   Tu solicitud está en estado: Pendiente")
                                print(f"   Recibirás una notificación cuando sea revisada")
                            else:
                                print("\n⚠️  Estudiante registrado pero no se pudo crear la inscripción")
                                print("   Por favor contacta con administración")
                        return
                    else:
                        print("❌ Inscripción cancelada")
                        return
                        
            except Exception as e:
                print(f"❌ Error al validar carrera: {e}")
                continue
                
        except ValueError:
            print("❌ Por favor ingrese un número válido")
            continue

def menu_principal():
    """Menú principal del sistema - VERSIÓN ACTUALIZADA"""
    while True:
        print("\n" + "=" * 50)
        print("MENÚ PRINCIPAL - SISTEMA UNIVERSITARIO")
        print("=" * 50)
        print("1. Ver tablas existentes")
        print("2. Gestionar períodos académicos")
        print("3. Gestionar carreras")
        print("4. GESTIÓN DE INSCRIPCIONES")  # ← NUEVA OPCIÓN DESTACADA
        print("5. Salir")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            ver_tablas()
        elif opcion == "2":
            menu_periodos()
        elif opcion == "3":
            menu_carreras()
        elif opcion == "4":
            menu_gestion_inscripciones_admin()  # ← NUEVA FUNCIÓN
        elif opcion == "5":
            print("¡Hasta pronto! 👋")
            break
        else:
            print("❌ Opción inválida")

def ver_tablas():
    """Muestra las tablas existentes"""
    try:
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """))
            
            tablas = result.fetchall()
            
            print(f"\n📋 TABLAS EN 'RegistroNacional':")
            print("-" * 40)
            if tablas:
                for tabla in tablas:
                    print(f"  • {tabla.TABLE_NAME}")
            else:
                print("  No hay tablas en la base de datos")
                
    except Exception as e:
        print(f"❌ Error: {e}")

def ver_estructura():
    """Muestra la estructura completa de la base de datos"""
    try:
        with db.engine.connect() as conn:
            # Información general
            result = conn.execute(text("""
                SELECT 
                    DB_NAME() as database_name,
                    @@SERVERNAME as server_name,
                    suser_name() as current_user,
                    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE') as table_count
            """))
            
            info = result.fetchone()
            print(f"\n🏢 INFORMACIÓN DE LA BASE DE DATOS:")
            print(f"  Servidor: {info.server_name}")
            print(f"  Base de datos: {info.database_name}")
            print(f"  Usuario: {info.current_user}")
            print(f"  Tablas: {info.table_count}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def menu_periodos():
    """Menú para gestionar períodos académicos"""
    periodos = Periodos()
    
    while True:
        print("\n" + "=" * 50)
        print("MENÚ DE PERÍODOS ACADÉMICOS")
        print("=" * 50)
        print("1. Crear tabla de períodos")
        print("2. Insertar nuevo período")
        print("3. Ver períodos activos")
        print("4. Desactivar período")
        print("5. Volver al menú principal")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            periodos.crear_tabla_periodos()
        if opcion == "2":
            nombre = input("Nombre del período: ")
            inicio = input("Fecha de inicio (YYYY-MM-DD): ")
            fin = input("Fecha de fin (YYYY-MM-DD): ")
            estado = input("Estado (Activo/Cerrado/Planeado): ")
            periodos.insertar_periodo(nombre, inicio, fin, estado)
        if opcion == "3":
            periodos.ver_periodos()
        if opcion == "4":
            id_periodo = input("ID del período a desactivar: ")
            periodos.desactivar_periodo(id_periodo)
        if opcion == "5":
            break

def menu_carreras():
    """Menú para gestionar carreras académicas"""
    carreras = Carreras()
    
    while True:
        print("\n" + "=" * 50)
        print("MENÚ DE CARRERAS ACADÉMICAS")
        print("=" * 50)
        print("1. Crear tabla de carreras")
        print("2. Insertar nueva carrera")
        print("3. Ver carreras")
        print("4. Actualizar carrera")
        print("5. Eliminar carrera")
        print("6. Volver al menú principal")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            carreras.crear_tabla_carreras()
        elif opcion == "2":
            nombre = input("Nombre de la carrera: ")
            descripcion = input("Descripción: ")
            duracion = int(input("Duración en semestres: "))
            estado = input("Estado (Activa/Inactiva) [Activa]: ") or "Activa"
            carreras.insertar_carrera(nombre, descripcion, duracion, estado)
        elif opcion == "3":
            carreras.ver_carreras()
        elif opcion == "4":
            id_carrera = int(input("ID de la carrera a actualizar: "))
            nuevo_nombre = input("Nuevo nombre (dejar vacío para no cambiar): ") or None
            nueva_descripcion = input("Nueva descripción (dejar vacío para no cambiar): ") or None
            nueva_duracion_str = input("Nueva duración (dejar vacío para no cambiar): ")
            nueva_duracion = int(nueva_duracion_str) if nueva_duracion_str else None
            nuevo_estado = input("Nuevo estado (Activa/Inactiva, dejar vacío para no cambiar): ") or None
            carreras.actualizar_carrera(id_carrera, nuevo_nombre, nueva_descripcion, nueva_duracion, nuevo_estado)
        elif opcion == "5":
            id_carrera = int(input("ID de la carrera a eliminar: "))
            carreras.eliminar_carrera(id_carrera)
        elif opcion == "6":
            break
        else:
            print("❌ Opción inválida")

def menu_gestion_inscripciones_admin():
    """Menú completo de gestión de inscripciones para administrador"""
    while True:
        print("\n" + "=" * 50)
        print("🎯 GESTIÓN DE INSCRIPCIONES - ADMINISTRADOR")
        print("=" * 50)
        print("1. Ver todas las inscripciones")
        print("2. Ver detalle de una inscripción")
        print("3. Filtrar inscripciones por estado")
        print("4. Actualizar estado de inscripción")
        print("5. Ver reporte estadístico")
        print("6. Volver al menú principal")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            sistema_inscripciones.ver_todas_inscripciones_detalladas()
        elif opcion == "2":
            ver_detalle_inscripcion_interactivo()
        elif opcion == "3":
            filtrar_inscripciones_por_estado_interactivo()
        elif opcion == "4":
            actualizar_estado_inscripcion_interactivo()
        elif opcion == "5":
            sistema_inscripciones.generar_reporte_estadisticas()
        elif opcion == "6":
            break
        else:
            print("❌ Opción inválida")

def ver_detalle_inscripcion_interactivo():
    """Interfaz para ver detalle de una inscripción"""
    print("\n🔍 VER DETALLE DE INSCRIPCIÓN")
    print("-" * 40)
    
    # Primero mostrar todas las inscripciones
    sistema_inscripciones.ver_todas_inscripciones_detalladas()
    
    try:
        id_inscripcion = int(input("\n🔢 Ingrese el ID de la inscripción a detallar: "))
        sistema_inscripciones.ver_detalle_inscripcion(id_inscripcion)
    except ValueError:
        print("❌ ID debe ser un número")
    except Exception as e:
        print(f"❌ Error: {e}")

def filtrar_inscripciones_por_estado_interactivo():
    """Interfaz para filtrar inscripciones por estado"""
    print("\n🔍 FILTRAR INSCRIPCIONES POR ESTADO")
    print("-" * 40)
    
    print("\n📊 ESTADOS DISPONIBLES PARA FILTRAR:")
    print("1. Pendiente")
    print("2. Aprobada")
    print("3. Rechazada")
    print("4. Cancelada")
    
    try:
        opcion = input("\nSeleccione el estado a filtrar (1-4): ").strip()
        
        estados = {
            '1': 'Pendiente',
            '2': 'Aprobada',
            '3': 'Rechazada',
            '4': 'Cancelada'
        }
        
        if opcion in estados:
            estado = estados[opcion]
            sistema_inscripciones.filtrar_inscripciones_por_estado(estado)
        else:
            print("❌ Opción inválida")
    except Exception as e:
        print(f"❌ Error: {e}")

def actualizar_estado_inscripcion_interactivo():
    """Interfaz para actualizar estado de inscripción"""
    print("\n🔄 ACTUALIZAR ESTADO DE INSCRIPCIÓN")
    print("-" * 40)
    
    # Primero mostrar todas las inscripciones
    sistema_inscripciones.ver_todas_inscripciones_detalladas()
    
    try:
        id_inscripcion = int(input("\n🔢 ID de la inscripción a actualizar: "))
        
        # Ver detalle primero para confirmar
        print("\n📄 CONFIRMACIÓN - DATOS DE LA INSCRIPCIÓN:")
        inscripcion = sistema_inscripciones.ver_detalle_inscripcion(id_inscripcion)
        
        if not inscripcion:
            return
        
        print("\n📊 ESTADOS DISPONIBLES:")
        print("1. Pendiente (por defecto)")
        print("2. Aprobada (inscripción aceptada)")
        print("3. Rechazada (inscripción rechazada)")
        print("4. Cancelada (cancelada por estudiante)")
        
        opcion = input("\nSeleccione el nuevo estado (1-4): ").strip()
        
        estados = {
            '1': 'Pendiente',
            '2': 'Aprobada',
            '3': 'Rechazada',
            '4': 'Cancelada'
        }
        
        if opcion in estados:
            nuevo_estado = estados[opcion]
            
            if nuevo_estado == inscripcion.estado:
                print(f"⚠️  La inscripción ya tiene estado '{nuevo_estado}'")
                return
            
            observaciones = input("\n📝 Observaciones/reason (opcional): ").strip()
            
            confirmar = input(f"\n✅ ¿Confirmar cambio de estado de '{inscripcion.estado}' a '{nuevo_estado}'? (s/n): ").strip().lower()
            
            if confirmar == 's':
                # Actualizar estado
                resultado = sistema_inscripciones.actualizar_estado_inscripcion(id_inscripcion, nuevo_estado, observaciones)
                if resultado:
                    print(f"\n🎉 Estado actualizado exitosamente!")
                    print(f"   Inscripción #{id_inscripcion} ahora está: {nuevo_estado}")
            else:
                print("❌ Operación cancelada")
        else:
            print("❌ Estado no válido")
            
    except ValueError:
        print("❌ ID debe ser un número")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()