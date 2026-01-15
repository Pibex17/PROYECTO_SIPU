from sqlalchemy import text
from DataBase import db
from datetime import datetime

class Evaluacion:
    """Clase para gestionar evaluaciones de estudiantes"""
    
    @staticmethod
    def crear_tabla_evaluaciones():
        """Crea la tabla de evaluaciones si no existe"""
        try:
            with db.engine.connect() as conn:
                # Verificar si la tabla existe
                result = conn.execute(text("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME = 'Evaluaciones'
                """))
                
                if not result.fetchone():
                    print("📝 Creando tabla 'Evaluaciones'...")
                    conn.execute(text("""
                        CREATE TABLE Evaluaciones (
                            idEvaluacion INT IDENTITY(1,1) PRIMARY KEY,
                            nombreEvaluacion VARCHAR(200) NOT NULL,
                            descripcion VARCHAR(500),
                            tipoEvaluacion VARCHAR(50) NOT NULL,
                            puntajeMaximo DECIMAL(5,2) NOT NULL DEFAULT 100,
                            fechaCreacion DATETIME DEFAULT GETDATE(),
                            estado VARCHAR(20) DEFAULT 'Activa'
                        )
                    """))
                    print("✅ Tabla 'Evaluaciones' creada")
                else:
                    print("✅ Tabla 'Evaluaciones' ya existe")
                
                # Crear tabla de asignaciones de evaluaciones a estudiantes
                result = conn.execute(text("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME = 'EvaluacionesAsignadas'
                """))
                
                if not result.fetchone():
                    print("📝 Creando tabla 'EvaluacionesAsignadas'...")
                    conn.execute(text("""
                        CREATE TABLE EvaluacionesAsignadas (
                            idAsignacion INT IDENTITY(1,1) PRIMARY KEY,
                            idEvaluacion INT NOT NULL,
                            idEstudiante INT NOT NULL,
                            estado VARCHAR(20) DEFAULT 'Pendiente',
                            fechaAsignacion DATETIME DEFAULT GETDATE(),
                            fechaVencimiento DATE,
                            puntajeObtenido DECIMAL(5,2),
                            observaciones VARCHAR(500),
                            fechaCompletada DATETIME,
                            FOREIGN KEY (idEvaluacion) REFERENCES Evaluaciones(idEvaluacion),
                            FOREIGN KEY (idEstudiante) REFERENCES Estudiantes(idEstudiante)
                        )
                    """))
                    print("✅ Tabla 'EvaluacionesAsignadas' creada")
                else:
                    print("✅ Tabla 'EvaluacionesAsignadas' ya existe")
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"❌ Error al crear tablas de evaluaciones: {e}")
            return False
    
    @staticmethod
    def crear_evaluacion(nombre, descripcion, tipo, puntaje_maximo):
        """
        Crea una nueva evaluación (solo administrador)
        
        Args:
            nombre (str): Nombre de la evaluación
            descripcion (str): Descripción de qué evaluará
            tipo (str): Tipo de evaluación (Examen, Taller, Proyecto, etc.)
            puntaje_maximo (float): Puntaje máximo de la evaluación
        
        Returns:
            int: ID de la evaluación creada, o None si falla
        """
        try:
            with db.engine.connect() as conn:
                # Validar que el tipo sea válido
                tipos_validos = ['Examen', 'Taller', 'Proyecto', 'Parcial', 'Final', 'Tareas', 'Quiz', 'Otro']
                
                if tipo not in tipos_validos:
                    print(f"❌ Tipo de evaluación inválido. Tipos válidos: {', '.join(tipos_validos)}")
                    return None
                
                if puntaje_maximo <= 0:
                    print("❌ El puntaje máximo debe ser mayor a 0")
                    return None
                
                # Insertar evaluación
                conn.execute(text("""
                    INSERT INTO Evaluaciones (nombreEvaluacion, descripcion, tipoEvaluacion, puntajeMaximo)
                    VALUES (:nombre, :descripcion, :tipo, :puntaje)
                """), {
                    "nombre": nombre,
                    "descripcion": descripcion,
                    "tipo": tipo,
                    "puntaje": puntaje_maximo
                })

                # Obtener el ID generado de forma segura
                row = conn.execute(text("SELECT CAST(SCOPE_IDENTITY() AS INT) as id")).fetchone()
                evaluacion_id = row[0] if row is not None else None

                conn.commit()

                if evaluacion_id is None:
                    print("❌ No se pudo obtener el ID de la evaluación creada")
                    return None

                print(f"✅ Evaluación '{nombre}' creada exitosamente (ID: {int(evaluacion_id)})")
                return int(evaluacion_id)
                
        except Exception as e:
            print(f"❌ Error al crear evaluación: {e}")
            return None

    @staticmethod
    def eliminar_evaluacion(id_evaluacion, force=False):
        """
        Elimina una evaluación. Si hay asignaciones relacionadas, requiere force=True para eliminarlas también.

        Args:
            id_evaluacion (int): ID de la evaluación a eliminar
            force (bool): Si True, elimina también las asignaciones relacionadas

        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            with db.engine.connect() as conn:
                # Verificar existencia
                result = conn.execute(text("""
                    SELECT idEvaluacion, nombreEvaluacion FROM Evaluaciones WHERE idEvaluacion = :id
                """), {"id": id_evaluacion})
                ev = result.fetchone()
                if not ev:
                    print("❌ Evaluación no encontrada")
                    return False

                # Verificar asignaciones
                result = conn.execute(text("""
                    SELECT COUNT(1) as cnt FROM EvaluacionesAsignadas WHERE idEvaluacion = :id
                """), {"id": id_evaluacion})
                cnt = result.fetchone()[0]

                if cnt and cnt > 0 and not force:
                    print(f"⚠️  Hay {cnt} asignaciones relacionadas. Use force=True para eliminar todo.")
                    return False

                # Si force, eliminar asignaciones relacionadas
                if cnt and cnt > 0 and force:
                    conn.execute(text("""
                        DELETE FROM EvaluacionesAsignadas WHERE idEvaluacion = :id
                    """), {"id": id_evaluacion})

                # Eliminar la evaluación
                conn.execute(text("""
                    DELETE FROM Evaluaciones WHERE idEvaluacion = :id
                """), {"id": id_evaluacion})

                conn.commit()
                print(f"✅ Evaluación '{ev.nombreEvaluacion}' eliminada correctamente")
                return True

        except Exception as e:
            print(f"❌ Error al eliminar evaluación: {e}")
            return False
    
    @staticmethod
    def asignar_evaluacion_a_estudiante(id_evaluacion, id_estudiante, fecha_vencimiento):
        """
        Asigna una evaluación a un estudiante (admin)
        
        Args:
            id_evaluacion (int): ID de la evaluación
            id_estudiante (int): ID del estudiante
            fecha_vencimiento (str): Fecha de vencimiento (YYYY-MM-DD)
        
        Returns:
            bool: True si se asignó exitosamente
        """
        try:
            with db.engine.connect() as conn:
                # Validar que la evaluación existe
                result = conn.execute(text("""
                    SELECT idEvaluacion, nombreEvaluacion, puntajeMaximo
                    FROM Evaluaciones
                    WHERE idEvaluacion = :id
                """), {"id": id_evaluacion})
                
                evaluacion = result.fetchone()
                if not evaluacion:
                    print("❌ Evaluación no encontrada")
                    return False
                
                # Validar que el estudiante existe
                result = conn.execute(text("""
                    SELECT idEstudiante, nombres, apellidos
                    FROM Estudiantes
                    WHERE idEstudiante = :id
                """), {"id": id_estudiante})
                
                estudiante = result.fetchone()
                if not estudiante:
                    print("❌ Estudiante no encontrado")
                    return False
                
                # Verificar si ya tiene esta evaluación asignada
                result = conn.execute(text("""
                    SELECT idAsignacion
                    FROM EvaluacionesAsignadas
                    WHERE idEvaluacion = :id_eval AND idEstudiante = :id_est
                """), {
                    "id_eval": id_evaluacion,
                    "id_est": id_estudiante
                })
                
                if result.fetchone():
                    print("⚠️  Esta evaluación ya está asignada a este estudiante")
                    return False
                
                # Asignar evaluación
                conn.execute(text("""
                    INSERT INTO EvaluacionesAsignadas (idEvaluacion, idEstudiante, fechaVencimiento)
                    VALUES (:id_eval, :id_est, :fecha_venc)
                """), {
                    "id_eval": id_evaluacion,
                    "id_est": id_estudiante,
                    "fecha_venc": fecha_vencimiento
                })
                
                conn.commit()
                
                print(f"✅ Evaluación '{evaluacion.nombreEvaluacion}' asignada a {estudiante.nombres} {estudiante.apellidos}")
                print(f"   Fecha de vencimiento: {fecha_vencimiento}")
                return True
                
        except Exception as e:
            print(f"❌ Error al asignar evaluación: {e}")
            return False
    
    @staticmethod
    def ver_evaluaciones_disponibles():
        """Muestra todas las evaluaciones disponibles para asignar"""
        try:
            with db.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT 
                        idEvaluacion,
                        nombreEvaluacion,
                        tipoEvaluacion,
                        descripcion,
                        puntajeMaximo,
                        estado
                    FROM Evaluaciones
                    WHERE estado = 'Activa'
                    ORDER BY idEvaluacion
                """))
                
                evaluaciones = result.fetchall()
                
                if not evaluaciones:
                    print("ℹ️  No hay evaluaciones disponibles")
                    return evaluaciones
                
                print("\n📋 EVALUACIONES DISPONIBLES:")
                print("-" * 100)
                print(f"{'ID':<5} {'Nombre':<30} {'Tipo':<15} {'Puntaje Máx':<15} {'Descripción':<30}")
                print("-" * 100)
                
                for ev in evaluaciones:
                    descripcion = ev.descripcion[:27] + "..." if ev.descripcion and len(ev.descripcion) > 30 else (ev.descripcion or "N/A")
                    print(f"{ev.idEvaluacion:<5} {ev.nombreEvaluacion:<30} {ev.tipoEvaluacion:<15} {ev.puntajeMaximo:<15} {descripcion:<30}")
                
                print("-" * 100)
                return evaluaciones
                
        except Exception as e:
            print(f"❌ Error al ver evaluaciones: {e}")
            return []
    
    @staticmethod
    def ver_evaluaciones_asignadas_admin():
        """Muestra todas las evaluaciones asignadas (para admin)"""
        try:
            with db.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT 
                        ea.idAsignacion,
                        ea.idEvaluacion,
                        e.nombreEvaluacion,
                        e.tipoEvaluacion,
                        e.puntajeMaximo,
                        s.nombres,
                        s.apellidos,
                        ea.estado,
                        ea.fechaAsignacion,
                        ea.fechaVencimiento,
                        ea.puntajeObtenido
                    FROM EvaluacionesAsignadas ea
                    JOIN Evaluaciones e ON ea.idEvaluacion = e.idEvaluacion
                    JOIN Estudiantes s ON ea.idEstudiante = s.idEstudiante
                    ORDER BY ea.fechaAsignacion DESC
                """))
                
                asignaciones = result.fetchall()
                
                if not asignaciones:
                    print("ℹ️  No hay evaluaciones asignadas")
                    return asignaciones
                
                print("\n📋 EVALUACIONES ASIGNADAS:")
                print("-" * 140)
                print(f"{'ID':<5} {'Evaluación':<25} {'Estudiante':<25} {'Tipo':<12} {'Estado':<12} {'Puntaje':<12} {'Vencimiento':<15}")
                print("-" * 140)
                
                for asig in asignaciones:
                    puntaje_str = f"{asig.puntajeObtenido}/{asig.puntajeMaximo}" if asig.puntajeObtenido else "Pendiente"
                    vencimiento = asig.fechaVencimiento.strftime("%Y-%m-%d") if asig.fechaVencimiento else "Sin fecha"
                    estudiante = f"{asig.nombres} {asig.apellidos}"[:25]
                    
                    print(f"{asig.idAsignacion:<5} {asig.nombreEvaluacion:<25} {estudiante:<25} {asig.tipoEvaluacion:<12} {asig.estado:<12} {puntaje_str:<12} {vencimiento:<15}")
                
                print("-" * 140)
                return asignaciones
                
        except Exception as e:
            print(f"❌ Error al ver evaluaciones asignadas: {e}")
            return []
    
    @staticmethod
    def registrar_puntaje(id_asignacion, puntaje, observaciones=""):
        """
        Registra el puntaje obtenido en una evaluación (admin)
        
        Args:
            id_asignacion (int): ID de la asignación
            puntaje (float): Puntaje obtenido
            observaciones (str): Observaciones opcionales
        
        Returns:
            bool: True si se registró exitosamente
        """
        try:
            with db.engine.connect() as conn:
                # Obtener información de la asignación
                result = conn.execute(text("""
                    SELECT ea.idEvaluacion, e.puntajeMaximo
                    FROM EvaluacionesAsignadas ea
                    JOIN Evaluaciones e ON ea.idEvaluacion = e.idEvaluacion
                    WHERE ea.idAsignacion = :id
                """), {"id": id_asignacion})
                
                asignacion = result.fetchone()
                if not asignacion:
                    print("❌ Asignación de evaluación no encontrada")
                    return False
                
                # Validar puntaje
                if puntaje < 0 or puntaje > asignacion.puntajeMaximo:
                    print(f"❌ El puntaje debe estar entre 0 y {asignacion.puntajeMaximo}")
                    return False
                
                # Actualizar puntaje
                conn.execute(text("""
                    UPDATE EvaluacionesAsignadas
                    SET puntajeObtenido = :puntaje,
                        estado = 'Completada',
                        observaciones = :observaciones,
                        fechaCompletada = GETDATE()
                    WHERE idAsignacion = :id
                """), {
                    "puntaje": puntaje,
                    "observaciones": observaciones,
                    "id": id_asignacion
                })
                
                conn.commit()
                print(f"✅ Puntaje registrado: {puntaje}/{asignacion.puntajeMaximo}")
                return True
                
        except Exception as e:
            print(f"❌ Error al registrar puntaje: {e}")
            return False
    
    @staticmethod
    def obtener_evaluaciones_pendientes_estudiante(id_estudiante):
        """
        Obtiene las evaluaciones pendientes de un estudiante
        
        Args:
            id_estudiante (int): ID del estudiante
        
        Returns:
            list: Lista de evaluaciones pendientes
        """
        try:
            with db.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT 
                        ea.idAsignacion,
                        e.idEvaluacion,
                        e.nombreEvaluacion,
                        e.tipoEvaluacion,
                        e.descripcion,
                        e.puntajeMaximo,
                        ea.estado,
                        ea.fechaAsignacion,
                        ea.fechaVencimiento
                    FROM EvaluacionesAsignadas ea
                    JOIN Evaluaciones e ON ea.idEvaluacion = e.idEvaluacion
                    WHERE ea.idEstudiante = :id_est
                    AND ea.estado = 'Pendiente'
                    ORDER BY ea.fechaVencimiento ASC
                """), {"id_est": id_estudiante})
                
                return result.fetchall()
                
        except Exception as e:
            print(f"❌ Error al obtener evaluaciones pendientes: {e}")
            return []
    
    @staticmethod
    def obtener_evaluaciones_completadas_estudiante(id_estudiante):
        """
        Obtiene las evaluaciones completadas de un estudiante
        
        Args:
            id_estudiante (int): ID del estudiante
        
        Returns:
            list: Lista de evaluaciones completadas
        """
        try:
            with db.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT 
                        ea.idAsignacion,
                        e.idEvaluacion,
                        e.nombreEvaluacion,
                        e.tipoEvaluacion,
                        e.descripcion,
                        e.puntajeMaximo,
                        ea.puntajeObtenido,
                        ea.estado,
                        ea.fechaCompletada,
                        ea.observaciones
                    FROM EvaluacionesAsignadas ea
                    JOIN Evaluaciones e ON ea.idEvaluacion = e.idEvaluacion
                    WHERE ea.idEstudiante = :id_est
                    AND ea.estado = 'Completada'
                    ORDER BY ea.fechaCompletada DESC
                """), {"id_est": id_estudiante})
                
                return result.fetchall()
                
        except Exception as e:
            print(f"❌ Error al obtener evaluaciones completadas: {e}")
            return []
    
    @staticmethod
    def obtener_todas_evaluaciones_estudiante(id_estudiante):
        """
        Obtiene todas las evaluaciones (pendientes y completadas) de un estudiante
        
        Args:
            id_estudiante (int): ID del estudiante
        
        Returns:
            dict: Diccionario con evaluaciones pendientes y completadas
        """
        return {
            "pendientes": Evaluacion.obtener_evaluaciones_pendientes_estudiante(id_estudiante),
            "completadas": Evaluacion.obtener_evaluaciones_completadas_estudiante(id_estudiante)
        }
