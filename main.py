
from DataBase import db
from sqlalchemy import text
from Periodos import Periodos
from Carreras import Carreras

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
    
    # Paso 3: Mostrar menú principal
    menu_principal()

def menu_principal():
    """Menú principal del sistema"""
    while True:
        print("\n" + "=" * 50)
        print("MENÚ PRINCIPAL - SISTEMA UNIVERSITARIO")
        print("=" * 50)
        print("1. Ver tablas existentes")
        print("2. Gestionar períodos académicos")
        print("3. Gestionar carreras")
        print("4. Salir")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            ver_tablas()
        elif opcion == "2":
            menu_periodos()
        elif opcion == "3":
            menu_carreras()
        elif opcion == "4":
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

if __name__ == "__main__":
    main()