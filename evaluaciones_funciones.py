# Funciones para gestión de evaluaciones en main.py
from Evaluacion import Evaluacion
from Estudiante import Aspirante
import datetime

def menu_gestion_evaluaciones_admin():
    """Menú completo de gestión de evaluaciones para administrador"""
    while True:
        print("\n" + "=" * 50)
        print("📋 GESTIÓN DE EVALUACIONES - ADMINISTRADOR")
        print("=" * 50)
        print("1. Crear nueva evaluación")
        print("2. Ver evaluaciones disponibles")
        print("3. Asignar evaluación a estudiante")
        print("4. Ver evaluaciones asignadas")
        print("5. Registrar puntaje de evaluación")
        print("6. Eliminar evaluación")
        print("7. Volver al menú principal")
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == "1":
            crear_evaluacion_interactivo()
        elif opcion == "2":
            Evaluacion.ver_evaluaciones_disponibles()
        elif opcion == "3":
            asignar_evaluacion_interactivo()
        elif opcion == "4":
            Evaluacion.ver_evaluaciones_asignadas_admin()
        elif opcion == "5":
            registrar_puntaje_interactivo()
        elif opcion == "6":
            eliminar_evaluacion_interactivo()
        elif opcion == "7":
            break
        else:
            print("❌ Opción inválida")

def crear_evaluacion_interactivo():
    """Interfaz para crear una nueva evaluación"""
    print("\n✏️  CREAR NUEVA EVALUACIÓN")
    print("-" * 50)
    
    nombre = input("Nombre de la evaluación: ").strip()
    if not nombre:
        print("❌ El nombre no puede estar vacío")
        return
    
    descripcion = input("Descripción (qué evaluará): ").strip()
    
    print("\n📊 TIPOS DE EVALUACIÓN DISPONIBLES:")
    tipos = ['Examen', 'Taller', 'Proyecto', 'Parcial', 'Final', 'Tareas', 'Quiz', 'Otro']
    for i, tipo in enumerate(tipos, 1):
        print(f"  {i}. {tipo}")
    
    try:
        tipo_opcion = int(input("\nSeleccione el tipo (1-8): "))
        if 1 <= tipo_opcion <= len(tipos):
            tipo = tipos[tipo_opcion - 1]
        else:
            print("❌ Opción inválida")
            return
    except ValueError:
        print("❌ Debe ingresar un número válido")
        return
    
    try:
        puntaje_maximo = float(input("Puntaje máximo (ej: 100): "))
        if puntaje_maximo <= 0:
            print("❌ El puntaje debe ser mayor a 0")
            return
    except ValueError:
        print("❌ El puntaje debe ser un número válido")
        return
    
    resultado = Evaluacion.crear_evaluacion(nombre, descripcion, tipo, puntaje_maximo)
    if resultado:
        print(f"\n✅ Evaluación creada exitosamente con ID: {resultado}")

def asignar_evaluacion_interactivo():
    """Interfaz para asignar una evaluación a un estudiante"""
    print("\n📌 ASIGNAR EVALUACIÓN A ESTUDIANTE")
    print("-" * 50)
    
    evaluaciones = Evaluacion.ver_evaluaciones_disponibles()
    if not evaluaciones:
        return
    
    try:
        id_evaluacion = int(input("\n🔢 ID de la evaluación a asignar: "))
        
        if not any(ev.idEvaluacion == id_evaluacion for ev in evaluaciones):
            print("❌ Evaluación no encontrada")
            return
        
        print("\n👤 BUSCAR ESTUDIANTE:")
        cedula = input("Ingrese la cédula del estudiante: ").strip()
        
        estudiante = Aspirante.buscar_estudiante_por_identificacion(cedula)
        if not estudiante:
            print("❌ Estudiante no encontrado")
            return
        
        print(f"\n✅ Estudiante encontrado: {estudiante.nombres} {estudiante.apellidos}")
        
        fecha_vencimiento = input("\n📅 Fecha de vencimiento (YYYY-MM-DD): ").strip()
        
        try:
            datetime.datetime.strptime(fecha_vencimiento, '%Y-%m-%d')
        except ValueError:
            print("❌ Formato de fecha inválido. Use YYYY-MM-DD")
            return
        
        confirmar = input(f"\n✅ ¿Confirmar asignación? (s/n): ").strip().lower()
        if confirmar == 's':
            resultado = Evaluacion.asignar_evaluacion_a_estudiante(
                id_evaluacion,
                estudiante.idEstudiante,
                fecha_vencimiento
            )
            if resultado:
                print(f"\n🎉 ¡Evaluación asignada exitosamente!")
        else:
            print("❌ Asignación cancelada")
            
    except ValueError:
        print("❌ ID debe ser un número")
    except Exception as e:
        print(f"❌ Error: {e}")

def registrar_puntaje_interactivo():
    """Interfaz para registrar puntaje de una evaluación"""
    print("\n✏️  REGISTRAR PUNTAJE DE EVALUACIÓN")
    print("-" * 50)
    
    asignaciones = Evaluacion.ver_evaluaciones_asignadas_admin()
    if not asignaciones:
        return
    
    try:
        id_asignacion = int(input("\n🔢 ID de la asignación a calificar: "))
        
        asignacion = None
        for asig in asignaciones:
            if asig.idAsignacion == id_asignacion:
                asignacion = asig
                break
        
        if not asignacion:
            print("❌ Asignación no encontrada")
            return
        
        if asignacion.estado == 'Completada':
            print(f"⚠️  Esta evaluación ya fue calificada con {asignacion.puntajeObtenido} puntos")
            return
        
        try:
            puntaje = float(input(f"\n📊 Ingrese el puntaje obtenido (máximo {asignacion.puntajeMaximo}): "))
            
            if puntaje < 0 or puntaje > asignacion.puntajeMaximo:
                print(f"❌ El puntaje debe estar entre 0 y {asignacion.puntajeMaximo}")
                return
            
        except ValueError:
            print("❌ El puntaje debe ser un número válido")
            return
        
        observaciones = input("Observaciones (opcional): ").strip()
        
        confirmar = input(f"\n✅ ¿Confirmar puntaje de {puntaje}/{asignacion.puntajeMaximo}? (s/n): ").strip().lower()
        if confirmar == 's':
            resultado = Evaluacion.registrar_puntaje(id_asignacion, puntaje, observaciones)
            if resultado:
                print(f"\n🎉 ¡Puntaje registrado exitosamente!")
        else:
            print("❌ Operación cancelada")
            
    except ValueError:
        print("❌ ID debe ser un número")
    except Exception as e:
        print(f"❌ Error: {e}")

def eliminar_evaluacion_interactivo():
    """Interfaz para eliminar una evaluación (admin)"""
    print("\n🗑️  ELIMINAR EVALUACIÓN")
    print("-" * 50)

    evaluaciones = Evaluacion.ver_evaluaciones_disponibles()
    if not evaluaciones:
        return

    try:
        id_evaluacion = int(input("\n🔢 ID de la evaluación a eliminar: "))

        # Validar existencia
        if not any(ev.idEvaluacion == id_evaluacion for ev in evaluaciones):
            print("❌ Evaluación no encontrada")
            return

        # Verificar si tiene asignaciones
        with_ea = False
        try:
            from DataBase import db
            from sqlalchemy import text
            with db.engine.connect() as conn:
                cnt = conn.execute(text("SELECT COUNT(1) as cnt FROM EvaluacionesAsignadas WHERE idEvaluacion = :id"), {"id": id_evaluacion}).fetchone()[0]
                with_ea = cnt and cnt > 0
        except Exception:
            with_ea = False

        if with_ea:
            print("⚠️  Esta evaluación tiene asignaciones relacionadas.")
            confirmar = input("¿Eliminar igualmente y todas las asignaciones? (s/n): ").strip().lower()
            if confirmar != 's':
                print("❌ Operación cancelada")
                return
            force = True
        else:
            confirmar = input("¿Confirmar eliminación de la evaluación? (s/n): ").strip().lower()
            if confirmar != 's':
                print("❌ Operación cancelada")
                return
            force = False

        resultado = Evaluacion.eliminar_evaluacion(id_evaluacion, force=force)
        if resultado:
            print("\n✅ Eliminación completada")

    except ValueError:
        print("❌ ID debe ser un número")
    except Exception as e:
        print(f"❌ Error: {e}")
