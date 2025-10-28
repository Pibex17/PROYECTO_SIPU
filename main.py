from DataBase import db
from sqlalchemy import text
from Periodos import Periodos
from Carreras import Carreras
from OfertasAcademicas import OfertasAcademicas

def input_int(mensaje):
    while True:
        valor = input(mensaje)
        if valor.isdigit():
            return int(valor)
        print("❌ Debe ingresar un número válido.")

def input_text(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("❌ Este campo no puede estar vacío.")

def input_estado(mensaje, opciones):
    opciones = [o.lower() for o in opciones]
    while True:
        valor = input(mensaje).strip()
        if not valor:
            print("❌ Debe ingresar un estado.")
            continue
        if valor.lower() in opciones:
            return valor.capitalize()
        print(f"❌ Estado inválido. Opciones válidas: {', '.join(opciones)}")

def menu_principal():
    while True:
        print("\n" + "=" * 50)
        print("MENÚ PRINCIPAL - SISTEMA UNIVERSITARIO")
        print("=" * 50)
        print("1. Ver tablas existentes")
        print("2. Gestionar períodos académicos")
        print("3. Gestionar carreras")
        print("4. Gestionar ofertas académicas")
        print("5. Salir")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            ver_tablas()
        elif opcion == "2":
            menu_periodos()
        elif opcion == "3":
            menu_carreras()
        elif opcion == "4":
            menu_ofertasAcademicas()
        elif opcion == "5":
            print("¡Hasta pronto! 👋")
            return
        else:
            print("❌ Opción inválida")

def menu_ofertasAcademicas():
    while True:
        print("\n" + "=" * 50)
        print("MENÚ - OFERTAS ACADÉMICAS")
        print("=" * 50)
        print("1. Crear tabla de ofertas")
        print("2. Crear oferta académica")
        print("3. Ver ofertas")
        print("4. Modificar oferta")
        print("5. Eliminar oferta")
        print("6. Volver")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            OfertasAcademicas.crear_tablas_ofertas()

        elif opcion == "2":
            nombre = input_text("Nombre de la oferta: ")
            id_periodo = input_int("ID del período: ")
            estado = input_estado("Estado (Activa/Inactiva): ", ["activa", "inactiva"])
            
            carreras_oferta = []
            while True:
                id_carrera = input_int("ID Carrera a agregar: ")
                jornada = input_text("Jornada: ")
                modalidad = input_text("Modalidad: ")
                tipo_cupo = input_text("Tipo de cupo: ")
                total_cupos = input_int("Total de cupos: ")

                carreras_oferta.append({
                    "idCarrera": id_carrera,
                    "jornada": jornada,
                    "modalidad": modalidad,
                    "tipoCupo": tipo_cupo,
                    "totalCupos": total_cupos
                })

                agregar_mas = input("¿Agregar otra carrera? (s/n): ").lower()
                if agregar_mas != "s":
                    break

            OfertasAcademicas.crear_oferta(nombre, id_periodo, estado, carreras_oferta)

        elif opcion == "3":
            periodo = input("Filtrar por ID periodo (Enter = todos): ")
            OfertasAcademicas.ver_ofertas(id_periodo=int(periodo) if periodo.isdigit() else None)

        elif opcion == "4":
            id_oferta = input_int("ID de la oferta: ")
            nuevo_nombre = input("Nuevo nombre (Enter para omitir): ") or None
            nuevo_periodo = input("Nuevo periodo (Enter para omitir): ")
            nuevo_periodo = int(nuevo_periodo) if nuevo_periodo.isdigit() else None
            nuevo_estado = input("Nuevo estado (Activa/Inactiva) (Enter para omitir): ") or None

            OfertasAcademicas.modificar_oferta(id_oferta, nuevo_nombre, nuevo_periodo, nuevo_estado)

        elif opcion == "5":
            id_oferta = input_int("ID de la oferta a eliminar: ")
            OfertasAcademicas.eliminar_oferta(id_oferta)

        elif opcion == "6":
            break

        else:
            print("❌ Opción inválida")

def menu_carreras():
    carreras = Carreras()
    
    while True:
        print("\n" + "=" * 50)
        print("MENÚ - CARRERAS")
        print("=" * 50)
        print("1. Crear tabla carreras")
        print("2. Insertar carrera")
        print("3. Ver carreras")
        print("4. Actualizar carrera")
        print("5. Eliminar carrera")
        print("6. Volver")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            carreras.crear_tabla_carreras()
        elif opcion == "2":
            nombre = input_text("Nombre de la carrera: ")
            descripcion = input_text("Descripción: ")
            duracion = input_int("Duración en semestres: ")
            estado = input_estado("Estado (Activo/Cerrado/Planeado): ", ["activo", "cerrado", "planeado"])
            carreras.insertar_carrera(nombre, descripcion, duracion, estado)
        elif opcion == "3":
            carreras.ver_carreras()
        elif opcion == "4":
            id_carrera = input_int("ID de la carrera: ")
            nuevo_nombre = input_text("Nuevo nombre: ")
            nueva_descripcion = input_text("Nueva descripción: ")
            nueva_duracion = input_int("Nueva duración: ")
            nuevo_estado = input_estado("Nuevo estado: ", ["activo", "cerrado", "planeado"])
            carreras.actualizar_carrera(id_carrera, nuevo_nombre, nueva_descripcion, nueva_duracion, nuevo_estado)
        elif opcion == "5":
            id_carrera = input_int("ID de la carrera a eliminar: ")
            carreras.eliminar_carrera(id_carrera)
        elif opcion == "6":
            break
        else:
            print("❌ Opción inválida")

def menu_periodos():
    periodos = Periodos()
    
    while True:
        print("\n" + "=" * 50)
        print("MENÚ - PERÍODOS ACADÉMICOS")
        print("=" * 50)
        print("1. Crear tabla períodos")
        print("2. Insertar período")
        print("3. Ver períodos activos")
        print("4. Desactivar período")
        print("5. Volver")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            periodos.crear_tabla_periodos()
        elif opcion == "2":
            nombre = input_text("Nombre del período: ")
            inicio = input_text("Fecha inicio (YYYY-MM-DD): ")
            fin = input_text("Fecha fin (YYYY-MM-DD): ")
            estado = input_estado("Estado (Activo/Cerrado/Planeado): ", ["activo", "cerrado", "planeado"])
            periodos.insertar_periodo(nombre, inicio, fin, estado)
        elif opcion == "3":
            periodos.ver_periodos()
        elif opcion == "4":
            id_periodo = input_int("ID del período: ")
            periodos.desactivar_periodo(id_periodo)
        elif opcion == "5":
            return
        else:
            print("❌ Opción inválida")

def main():
    print("🎓 SISTEMA DE INSCRIPCIÓN UNIVERSITARIA")
    print("=" * 50)
    print("🔧 Conectando a SQL Server...")
    print("=" * 50)
    
    if not db.conectar():
        print("❌ Sin conexión a la base.")
        return
    
    if not db.verificar_base_datos():
        return
    
    menu_principal()

if __name__ == "__main__":
    main()