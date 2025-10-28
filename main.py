from DataBase import db
from sqlalchemy import text
from Periodos import Periodos
from Carreras import Carreras
from OfertasAcademicas import OfertasAcademicas
from Inscripciones import Inscripciones
from Evaluaciones import Evaluaciones
from datetime import datetime
import re

def main():
    """Función principal - Inicializa el sistema"""
    print("\n" + "="*60)
    print("SISTEMA DE INSCRIPCIÓN UNIVERSITARIA")
    print("Base de datos: SQL Server Express (localhost\\SQLEXPRESS)")
    print("="*60 + "\n")
    
    # Intenta conectar a SQL Server
    if not db.conectar():
        print("No se puede continuar sin conexión a la base de datos.")
        return
    
    # Verifica que la base de datos exista
    if not db.verificar_base_datos():
        return
    
    # Muestra el menú principal
    menu_principal()

def menu_principal():
    """Menú principal - Punto de entrada a todas las funciones del sistema"""
    while True:
        try:
            print("\n" + "="*50)
            print("MENU PRINCIPAL - SISTEMA UNIVERSITARIO")
            print("="*50)
            print("1. Ver tablas existentes")
            print("2. Gestionar períodos académicos")
            print("3. Gestionar carreras")
            print("4. Gestionar ofertas académicas")
            print("5. Gestionar inscripciones")
            print("6. Gestionar evaluaciones")
            print("7. Salir")
            
            opcion = input("\nSeleccione una opción: ")
            
            # Redirige a cada módulo según la opción
            if opcion == "1":
                try:
                    ver_tablas()
                except Exception as e:
                    print(f"Error al ver tablas: {e}")
            
            elif opcion == "2":
                try:
                    menu_periodos()
                except Exception as e:
                    print(f"Error en menú de períodos: {e}")
            
            elif opcion == "3":
                try:
                    menu_carreras()
                except Exception as e:
                    print(f"Error en menú de carreras: {e}")
            
            elif opcion == "4":
                try:
                    menu_ofertasAcademicas()
                except Exception as e:
                    print(f"Error en menú de ofertas académicas: {e}")
            
            elif opcion == "5":
                try:
                    menu_inscripciones()
                except Exception as e:
                    print(f"Error en menú de inscripciones: {e}")
            
            elif opcion == "6":
                try:
                    menu_evaluaciones()
                except Exception as e:
                    print(f"Error en menú de evaluaciones: {e}")
            
            elif opcion == "7":
                print("\nHasta luego!")
                break
            
            else:
                print("Opción no válida, intente de nuevo.")
        
        except KeyboardInterrupt:
            print("\n\nOperación cancelada.")
            confirmacion = input("¿Desea salir del sistema? (s/n): ")
            if confirmacion.lower() == 's':
                print("Hasta luego!")
                break
        
        except Exception as e:
            print(f"Error inesperado: {e}")
            print("Por favor, intente de nuevo.")

def ver_tablas():
    """Consulta y muestra todas las tablas existentes en la BD"""
    try:
        with db.engine.connect() as conn:
            # Query que obtiene los nombres de todas las tablas
            result = conn.execute(text("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """))
            
            tablas = result.fetchall()
            
            print("\nTablas en 'RegistroNacional':")
            print("-" * 40)
            if tablas:
                for tabla in tablas:
                    print(f"  - {tabla.TABLE_NAME}")
            else:
                print("  No hay tablas en la base de datos")
                
    except Exception as e:
        print(f"Error: {e}")

def menu_inscripciones():
    """Gestiona todo lo relacionado con estudiantes e inscripciones"""
    inscripciones = Inscripciones()
    
    while True:
        print("\n" + "="*50)
        print("MENU DE INSCRIPCIONES")
        print("="*50)
        print("1. Crear tablas de inscripciones")
        print("2. Registrar estudiante")
        print("3. Ver estudiantes")
        print("4. Crear inscripción")
        print("5. Ver inscripciones")
        print("6. Actualizar estado de inscripción")
        print("7. Eliminar inscripción")
        print("8. Volver al menú principal")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            # Crea las tablas Estudiantes e Inscripciones
            inscripciones.crear_tablas_inscripciones()
        
        elif opcion == "2":
            try:
                print("\n--- REGISTRAR NUEVO ESTUDIANTE ---")
                nombres = input("Nombres: ")
                apellidos = input("Apellidos: ")
                cedula = input("Cédula: ")
                
                # Valida que el email tenga formato correcto
                while True:
                    email = input("Email: ")
                    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                        break
                    else:
                        print("Email inválido. Use formato: ejemplo@dominio.com")
                
                telefono = input("Teléfono: ")
                direccion = input("Dirección: ")
                
                # Valida que la fecha tenga formato YYYY-MM-DD
                while True:
                    fecha_nac = input("Fecha de nacimiento (YYYY-MM-DD): ")
                    try:
                        datetime.strptime(fecha_nac, "%Y-%m-%d")
                        break
                    except ValueError:
                        print("Formato de fecha inválido. Use YYYY-MM-DD")
                
                estado = input("Estado (Activo/Inactivo/Suspendido) [Enter=Activo]: ") or "Activo"
                inscripciones.registrar_estudiante(nombres, apellidos, cedula, email, telefono, direccion, fecha_nac, estado)
            
            except Exception as e:
                print(f"Error: {e}")
                continue
        
        elif opcion == "3":
            # Muestra todos los estudiantes
            filtro_estado = input("Filtrar por estado (Enter para todos): ") or None
            inscripciones.ver_estudiantes(estado=filtro_estado)
        
        elif opcion == "4":
            print("\n--- CREAR NUEVA INSCRIPCIÓN ---")

            # Valida que sea un número entero
            try:
                id_est = int(input("ID del estudiante: "))
            except ValueError:
                print("Debe ingresar un número válido para el ID del estudiante")
                continue

            try:
                id_oferta = int(input("ID de la oferta: "))
            except ValueError:
                print("Debe ingresar un número válido para el ID de la oferta")
                continue

            try:
                id_carrera = int(input("ID de la carrera: "))
            except ValueError:
                print("Debe ingresar un número válido para el ID de la carrera")
                continue

            obs = input("Observaciones (Enter para omitir): ") or None
            estado = input("Estado (Pendiente/Aprobada/Rechazada) [Enter=Pendiente]: ") or "Pendiente"
            inscripciones.crear_inscripcion(id_est, id_oferta, id_carrera, obs, estado)

        elif opcion == "5":
            print("\n--- FILTROS (Enter para omitir) ---")
            
            id_est = input("ID estudiante: ")
            id_oferta = input("ID oferta: ")
            estado = input("Estado: ")
            
            # Convierte los IDs a int si se proporcionan
            try:
                id_est_int = int(id_est) if id_est else None
                id_oferta_int = int(id_oferta) if id_oferta else None
            except ValueError:
                print("Los IDs deben ser números válidos")
                continue
            
            inscripciones.ver_inscripciones(
                id_estudiante=id_est_int,
                id_oferta=id_oferta_int,
                estado=estado if estado else None
            )
        
        elif opcion == "6":
            try:
                id_insc = int(input("ID de la inscripción a actualizar: "))
            except ValueError:
                print("Debe ingresar un número válido")
                continue
            
            nuevo_estado = input("Nuevo estado (Pendiente/Aprobada/Rechazada/Cancelada) [Enter para omitir]: ") or None
            nuevas_obs = input("Nuevas observaciones [Enter para omitir]: ") or None
            inscripciones.actualizar_inscripcion(id_insc, nuevo_estado, nuevas_obs)

        elif opcion == "7":
            try:
                id_insc = int(input("ID de la inscripción a eliminar: "))
            except ValueError:
                print("Debe ingresar un número válido")
                continue
            
            # Pide confirmación antes de eliminar
            confirmacion = input(f"¿Está seguro de eliminar la inscripción {id_insc}? (s/n): ")
            if confirmacion.lower() == 's':
                inscripciones.eliminar_inscripcion(id_insc)
        
        elif opcion == "8":
            print("Volviendo al menú principal...")
            break
        
        else:
            print("Opción no válida")

def menu_evaluaciones():
    """Gestiona materias, matrículas y calificaciones de estudiantes"""
    evaluaciones = Evaluaciones()
    
    while True:
        print("\n" + "="*50)
        print("MENU DE EVALUACIONES")
        print("="*50)
        print("1. Crear tablas de evaluaciones")
        print("2. Crear materia")
        print("3. Ver materias")
        print("4. Matricular estudiante en materia")
        print("5. Registrar calificación")
        print("6. Ver calificaciones")
        print("7. Ver promedio de estudiante")
        print("8. Actualizar calificación")
        print("9. Eliminar calificación")
        print("10. Volver al menú principal")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            # Crea tablas: Materias, Matriculas, Calificaciones
            evaluaciones.crear_tablas_evaluaciones()
        
        elif opcion == "2":
            try:
                print("\n--- CREAR NUEVA MATERIA ---")
                nombre = input("Nombre de la materia: ")
                codigo = input("Código: ")
                # Valida que los créditos sean número
                creditos = int(input("Créditos: "))
                id_carrera = int(input("ID de la carrera: "))
                semestre = int(input("Semestre: "))
                estado = input("Estado (Activa/Inactiva) [Enter=Activa]: ") or "Activa"
                evaluaciones.crear_materia(nombre, codigo, creditos, id_carrera, semestre, estado)
            except ValueError:
                print("Debe ingresar valores numéricos válidos")
                continue
        
        elif opcion == "3":
            try:
                filtro_carrera = input("Filtrar por ID de carrera (Enter para todas): ")
                evaluaciones.ver_materias(id_carrera=int(filtro_carrera) if filtro_carrera else None)
            except ValueError:
                print("Debe ingresar un número válido")
                continue
        
        elif opcion == "4":
            try:
                print("\n--- MATRICULAR ESTUDIANTE ---")
                id_est = int(input("ID del estudiante: "))
                id_mat = int(input("ID de la materia: "))
                id_per = int(input("ID del período: "))
                evaluaciones.matricular_estudiante(id_est, id_mat, id_per)
            except ValueError:
                print("Debe ingresar números válidos")
                continue
        
        elif opcion == "5":
            try:
                print("\n--- REGISTRAR CALIFICACIÓN ---")
                id_matricula = int(input("ID de la matrícula: "))
                print("\nTipos de evaluación: Parcial1, Parcial2, Examen Final, Proyecto, Tarea, Otro")
                tipo_eval = input("Tipo de evaluación: ")
                # Valida que la nota sea decimal entre 0-100
                nota = float(input("Nota (0-100): "))
                porcentaje = float(input("Porcentaje (0-100): "))
                obs = input("Observaciones (Enter para omitir): ") or None
                evaluaciones.registrar_calificacion(id_matricula, tipo_eval, nota, porcentaje, obs)
            except ValueError:
                print("Debe ingresar valores numéricos válidos")
                continue
        
        elif opcion == "6":
            try:
                print("\n--- FILTROS (Enter para omitir) ---")
                id_est = input("ID estudiante: ")
                id_mat = input("ID materia: ")
                id_per = input("ID período: ")
                evaluaciones.ver_calificaciones(
                    id_estudiante=int(id_est) if id_est else None,
                    id_materia=int(id_mat) if id_mat else None,
                    id_periodo=int(id_per) if id_per else None
                )
            except ValueError:
                print("Debe ingresar números válidos")
                continue
        
        elif opcion == "7":
            try:
                id_est = int(input("ID del estudiante: "))
            except ValueError:
                print("Debe ingresar un número válido")
                continue
            
            try:
                id_per = input("ID del período (Enter para todos): ")
                evaluaciones.ver_promedio_estudiante(id_est, int(id_per) if id_per else None)
            except ValueError:
                print("Debe ingresar un número válido")
                continue
        
        elif opcion == "8":
            try:
                id_cal = int(input("ID de la calificación a actualizar: "))
            except ValueError:
                print("Debe ingresar un número válido")
                continue
            
            try:
                nueva_nota = input("Nueva nota (Enter para omitir): ")
                nuevo_porc = input("Nuevo porcentaje (Enter para omitir): ")
                nuevas_obs = input("Nuevas observaciones (Enter para omitir): ") or None
                evaluaciones.actualizar_calificacion(
                    id_cal,
                    nueva_nota=float(nueva_nota) if nueva_nota else None,
                    nuevo_porcentaje=float(nuevo_porc) if nuevo_porc else None,
                    nuevas_observaciones=nuevas_obs
                )
            except ValueError:
                print("Debe ingresar valores numéricos válidos")
                continue
        
        elif opcion == "9":
            try:
                id_cal = int(input("ID de la calificación a eliminar: "))
            except ValueError:
                print("Debe ingresar un número válido")
                continue
            
            # Confirmación antes de eliminar
            confirmacion = input(f"¿Está seguro de eliminar la calificación {id_cal}? (s/n): ")
            if confirmacion.lower() == 's':
                evaluaciones.eliminar_calificacion(id_cal)
        
        elif opcion == "10":
            print("Volviendo al menú principal...")
            break
        
        else:
            print("Opción no válida")
            
def menu_ofertasAcademicas():
    """Gestiona las ofertas académicas por período"""
    ofertas = OfertasAcademicas()
    
    while True:
        print("\n" + "="*50)
        print("MENU DE GESTIÓN DE OFERTAS ACADÉMICAS")
        print("="*50)
        print("1. Crear tabla de ofertas académicas")
        print("2. Crear oferta académica")
        print("3. Ver ofertas académicas")
        print("4. Modificar oferta")
        print("5. Eliminar oferta")
        print("6. Volver al menu principal")
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            # Crea tablas OfertasAcademicas y OfertaDetalle
            ofertas.crear_tablas_ofertas()
        
        elif opcion == "2":
            try:
                nombre = input("Nombre de la oferta: ")
                id_periodo = int(input("ID del periodo: "))
                estado = input("Estado (Activa/Inactiva) [Enter=Activa]: ") or "Activa"
                
                carreras_oferta = []
                agregar_mas = "s"
                
                # Permite agregar múltiples carreras a la oferta
                while agregar_mas.lower() == "s":
                    try:
                        id_carrera = int(input("ID Carrera a agregar: "))
                    except ValueError:
                        print("Debe ingresar un número válido para el ID de carrera")
                        continue
                    
                    jornada = input("Jornada: ")
                    modalidad = input("Modalidad: ")
                    tipo_cupo = input("Tipo de cupo: ")
                    
                    try:
                        total_cupos = int(input("Total de cupos: "))
                    except ValueError:
                        print("Debe ingresar un número válido para los cupos")
                        continue
                    
                    # Almacena los datos de cada carrera
                    carreras_oferta.append({
                        "idCarrera": id_carrera,
                        "jornada": jornada,
                        "modalidad": modalidad,
                        "tipoCupo": tipo_cupo,
                        "totalCupos": total_cupos
                    })
                    
                    agregar_mas = input("¿Agregar otra carrera? (s/n): ")
                
                ofertas.crear_oferta(nombre, id_periodo, estado, carreras_oferta)
            
            except ValueError:
                print("Debe ingresar valores numéricos válidos")
                continue
        
        elif opcion == "3":
            try:
                periodo = input("Filtrar por ID de periodo (Enter para todos): ")
                ofertas.ver_ofertas(id_periodo=int(periodo) if periodo else None)
            except ValueError:
                print("Debe ingresar un número válido")
                continue
        
        elif opcion == "4":
            try:
                id_oferta = int(input("Ingrese ID de la oferta a modificar: "))
            except ValueError:
                print("Debe ingresar un número válido para el ID de oferta")
                continue
            
            try:
                nuevo_nombre = input("Nuevo nombre (Enter para omitir): ") or None
                
                nuevo_periodo = input("Nuevo periodo (Enter para omitir): ")
                nuevo_periodo = int(nuevo_periodo) if nuevo_periodo else None
                
                nuevo_estado = input("Nuevo estado (Activa/Inactiva) (Enter para omitir): ") or None
                
                ofertas.modificar_oferta(id_oferta, nuevo_nombre, nuevo_periodo, nuevo_estado)
            
            except ValueError:
                print("Debe ingresar valores numéricos válidos")
                continue
        
        elif opcion == "5":
            try:
                id_oferta = int(input("Ingrese ID de la oferta a eliminar: "))
            except ValueError:
                print("Debe ingresar un número válido")
                continue
            
            # Confirmación antes de eliminar
            confirmacion = input(f"¿Está seguro de eliminar la oferta {id_oferta}? (s/n): ")
            if confirmacion.lower() == 's':
                ofertas.eliminar_oferta(id_oferta)
        
        elif opcion == "6":
            print("Volviendo al menu principal...")
            break
        
        else:
            print("Opción no válida")
            
def menu_carreras():
    """Gestiona las carreras académicas del sistema"""
    carreras = Carreras()
    
    while True:
        print("\n" + "="*50)
        print("MENU DE GESTIÓN DE CARRERAS")
        print("="*50)
        print("1. Crear tabla de carreras")
        print("2. Insertar carrera")
        print("3. Ver lista de carreras")
        print("4. Actualizar carrera")
        print("5. Eliminar carrera")
        print("6. Volver al menu principal")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            # Crea la tabla Carreras en la BD
            carreras.crear_tabla_carreras()
        
        elif opcion == "2":
            try:
                nombre = input("Nombre de la carrera: ")
                descripcion = input("Descripcion de la carrera: ")
                # Valida que sea un número entero positivo
                duracion = int(input("Cuantos semestres dura la carrera: "))
                estado = input("Estado (Activa/Inactiva) [Enter=Activa]: ") or "Activa"
                carreras.insertar_carrera(nombre, descripcion, duracion, estado)
            except ValueError:
                print("La duración debe ser un número válido")
                continue
        
        elif opcion == "3":
            # Muestra todas las carreras registradas
            carreras.ver_carreras()
        
        elif opcion == "4":
            try:
                id_carrera = int(input("ID de la carrera a actualizar: "))
            except ValueError:
                print("Debe ingresar un número válido para el ID")
                continue
            
            try:
                nuevo_nombre = input("Nuevo nombre para la carrera (Enter para omitir): ") or None
                nueva_descripcion = input("Nueva descripcion para la carrera (Enter para omitir): ") or None
                
                nueva_duracion = input("Nueva duracion para la carrera en semestres (Enter para omitir): ")
                nueva_duracion = int(nueva_duracion) if nueva_duracion else None
                
                nuevo_estado = input("Nuevo estado de la carrera (Activa/Inactiva) (Enter para omitir): ") or None
                
                carreras.actualizar_carrera(id_carrera, nuevo_nombre, nueva_descripcion, nueva_duracion, nuevo_estado)
            except ValueError:
                print("La duración debe ser un número válido")
                continue
        
        elif opcion == "5":
            try:
                id_carrera = int(input("ID de la carrera a eliminar: "))
            except ValueError:
                print("Debe ingresar un número válido")
                continue
            
            # Confirmación antes de eliminar
            confirmacion = input(f"¿Está seguro de eliminar la carrera {id_carrera}? (s/n): ")
            if confirmacion.lower() == 's':
                carreras.eliminar_carrera(id_carrera)
        
        elif opcion == "6":
            print("Volviendo al menu principal...")
            break
        
        else:
            print("Opción no válida")

def menu_periodos():
    """Gestiona los períodos académicos del sistema"""
    periodos = Periodos()
    
    while True:
        print("\n" + "="*50)
        print("MENU DE PERÍODOS ACADÉMICOS")
        print("="*50)
        print("1. Crear tabla de períodos")
        print("2. Insertar nuevo período")
        print("3. Ver períodos activos")
        print("4. Desactivar período")
        print("5. Volver al menú principal")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            # Crea la tabla Periodos en la BD
            periodos.crear_tabla_periodos()
        
        elif opcion == "2":
            try:
                nombre = input("Nombre del período: ")
                
                # Valida que la fecha de inicio tenga formato correcto
                while True:
                    inicio = input("Fecha de inicio (YYYY-MM-DD): ")
                    try:
                        datetime.strptime(inicio, "%Y-%m-%d")
                        break
                    except ValueError:
                        print("Formato de fecha inválido. Use YYYY-MM-DD")
                
                # Valida que la fecha de fin tenga formato correcto
                while True:
                    fin = input("Fecha de fin (YYYY-MM-DD): ")
                    try:
                        datetime.strptime(fin, "%Y-%m-%d")
                        break
                    except ValueError:
                        print("Formato de fecha inválido. Use YYYY-MM-DD")
                
                estado = input("Estado (Activo/Cerrado/Planeado) [Enter=Activo]: ") or "Activo"
                periodos.insertar_periodo(nombre, inicio, fin, estado)
            
            except Exception as e:
                print(f"Error: {e}")
                continue
        
        elif opcion == "3":
            # Muestra los períodos activos
            periodos.ver_periodos()
        
        elif opcion == "4":
            try:
                id_periodo = int(input("ID del período a desactivar: "))
            except ValueError:
                print("Debe ingresar un número válido")
                continue
            
            # Confirmación antes de cambiar estado
            confirmacion = input(f"¿Está seguro de desactivar el período {id_periodo}? (s/n): ")
            if confirmacion.lower() == 's':
                periodos.desactivar_periodo(id_periodo)
        
        elif opcion == "5":
            print("Volviendo al menú principal...")
            break
        
        else:
            print("Opción no válida")

if __name__ == "__main__":
    main()