from DataBase import db
from sqlalchemy import text

class Evaluaciones:
    """Gestiona materias, matrículas, calificaciones y promedios de estudiantes"""
    def __init__(self):
        pass

    def crear_tablas_evaluaciones(self):
        """
        Crea las tablas del módulo de evaluaciones:
        - Materias: cursos disponibles por carrera
        - Matriculas: relación estudiante-materia-período
        - Calificaciones: notas de cada evaluación
        - Vista vw_PromedioEstudiantes: cálculo de promedios
        """
        try:
            with db.engine.connect() as conn:
                conn.execute(text("""
                    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'Materias')
                    CREATE TABLE Materias (
                        idMateria INT IDENTITY(1,1) PRIMARY KEY,
                        nombreMateria VARCHAR(120) NOT NULL,
                        codigo VARCHAR(20) NOT NULL UNIQUE,
                        creditos INT NOT NULL CHECK (creditos > 0),
                        idCarrera INT NOT NULL,
                        semestre INT NOT NULL CHECK (semestre > 0),
                        estado VARCHAR(20) NOT NULL DEFAULT 'Activa'
                            CHECK (estado IN ('Activa','Inactiva')),
                        fechaCreacion DATETIME NOT NULL DEFAULT GETDATE(),
                        FOREIGN KEY (idCarrera) REFERENCES Carreras(idCarrera)
                    )
                """))

                conn.execute(text("""
                    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'Matriculas')
                    CREATE TABLE Matriculas (
                        idMatricula INT IDENTITY(1,1) PRIMARY KEY,
                        idEstudiante INT NOT NULL,
                        idMateria INT NOT NULL,
                        idPeriodo INT NOT NULL,
                        fechaMatricula DATETIME NOT NULL DEFAULT GETDATE(),
                        estado VARCHAR(20) NOT NULL DEFAULT 'Activa'
                            CHECK (estado IN ('Activa','Retirada','Completada')),
                        FOREIGN KEY (idEstudiante) REFERENCES Estudiantes(idEstudiante),
                        FOREIGN KEY (idMateria) REFERENCES Materias(idMateria),
                        FOREIGN KEY (idPeriodo) REFERENCES Periodos(idPeriodo),
                        UNIQUE (idEstudiante, idMateria, idPeriodo)
                    )
                """))

                conn.execute(text("""
                    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'Calificaciones')
                    CREATE TABLE Calificaciones (
                        idCalificacion INT IDENTITY(1,1) PRIMARY KEY,
                        idMatricula INT NOT NULL,
                        tipoEvaluacion VARCHAR(50) NOT NULL
                            CHECK (tipoEvaluacion IN ('Parcial1','Parcial2','Examen Final','Proyecto','Tarea','Otro')),
                        nota DECIMAL(5,2) NOT NULL CHECK (nota >= 0 AND nota <= 100),
                        porcentaje DECIMAL(5,2) NOT NULL CHECK (porcentaje >= 0 AND porcentaje <= 100),
                        fechaRegistro DATETIME NOT NULL DEFAULT GETDATE(),
                        observaciones VARCHAR(255),
                        FOREIGN KEY (idMatricula) REFERENCES Matriculas(idMatricula)
                    )
                """))

                conn.execute(text("""
                    CREATE OR ALTER VIEW vw_PromedioEstudiantes AS
                    SELECT 
                        m.idMatricula,
                        m.idEstudiante,
                        m.idMateria,
                        m.idPeriodo,
                        e.nombres,
                        e.apellidos,
                        mat.nombreMateria,
                        mat.creditos,
                        ISNULL(SUM(c.nota * c.porcentaje / 100), 0) as notaFinal,
                        CASE 
                            WHEN ISNULL(SUM(c.nota * c.porcentaje / 100), 0) >= 70 THEN 'Aprobado'
                            WHEN ISNULL(SUM(c.nota * c.porcentaje / 100), 0) > 0 THEN 'Reprobado'
                            ELSE 'Sin Calificar'
                        END as estadoAcademico
                    FROM Matriculas m
                    JOIN Estudiantes e ON m.idEstudiante = e.idEstudiante
                    JOIN Materias mat ON m.idMateria = mat.idMateria
                    LEFT JOIN Calificaciones c ON m.idMatricula = c.idMatricula
                    WHERE m.estado = 'Activa'
                    GROUP BY m.idMatricula, m.idEstudiante, m.idMateria, m.idPeriodo,
                             e.nombres, e.apellidos, mat.nombreMateria, mat.creditos
                """))

                conn.commit()
                print("Tablas de Evaluaciones creadas correctamente.")
        except Exception as e:
            print(f"Error al crear tablas de evaluaciones: {str(e)}")

    def crear_materia(self, nombre, codigo, creditos, id_carrera, semestre, estado="Activa"):
        """Crea una nueva materia."""
        try:
            with db.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO Materias (nombreMateria, codigo, creditos, idCarrera, semestre, estado)
                    VALUES (:nombre, :codigo, :creditos, :carrera, :semestre, :estado)
                """), {
                    'nombre': nombre,
                    'codigo': codigo,
                    'creditos': creditos,
                    'carrera': id_carrera,
                    'semestre': semestre,
                    'estado': estado
                })
                conn.commit()
                print(f"Materia '{nombre}' creada correctamente.")
        except Exception as e:
            print(f"Error al crear materia: {str(e)}")

    def ver_materias(self, id_carrera=None):
        """Muestra todas las materias, opcionalmente filtradas por carrera."""
        try:
            with db.engine.connect() as conn:
                query = """
                    SELECT m.idMateria, m.nombreMateria, m.codigo, m.creditos, 
                           m.semestre, m.estado, c.nombreCarrera
                    FROM Materias m
                    JOIN Carreras c ON m.idCarrera = c.idCarrera
                """
                params = {}
                
                if id_carrera:
                    query += " WHERE m.idCarrera = :carrera"
                    params['carrera'] = id_carrera
                
                query += " ORDER BY c.nombreCarrera, m.semestre, m.nombreMateria"

                result = conn.execute(text(query), params)
                materias = result.fetchall()

                if not materias:
                    print("No hay materias registradas.")
                    return

                print("\nListado de materias:")
                for mat in materias:
                    print(f"ID: {mat.idMateria} | Código: {mat.codigo} | Materia: {mat.nombreMateria} | Créditos: {mat.creditos} | Semestre: {mat.semestre} | Carrera: {mat.nombreCarrera} | Estado: {mat.estado}")
        except Exception as e:
            print(f"Error al consultar materias: {str(e)}")

    def matricular_estudiante(self, id_estudiante, id_materia, id_periodo):
        """Matricula un estudiante en una materia para un período específico."""
        try:
            with db.engine.connect() as conn:
                est = conn.execute(text("""
                    SELECT estado FROM Estudiantes WHERE idEstudiante = :id
                """), {'id': id_estudiante}).fetchone()
                
                if not est or est.estado != 'Activo':
                    print("El estudiante no existe o no está activo.")
                    return

                conn.execute(text("""
                    INSERT INTO Matriculas (idEstudiante, idMateria, idPeriodo, estado)
                    VALUES (:estudiante, :materia, :periodo, 'Activa')
                """), {
                    'estudiante': id_estudiante,
                    'materia': id_materia,
                    'periodo': id_periodo
                })
                conn.commit()
                print("Estudiante matriculado exitosamente en la materia.")
        except Exception as e:
            print(f"Error al matricular estudiante: {str(e)}")

    def registrar_calificacion(self, id_matricula, tipo_evaluacion, nota, porcentaje, observaciones=None):
        """Registra una calificación para una matrícula específica."""
        try:
            with db.engine.connect() as conn:
                suma_porcentajes = conn.execute(text("""
                    SELECT ISNULL(SUM(porcentaje), 0) 
                    FROM Calificaciones 
                    WHERE idMatricula = :id
                """), {'id': id_matricula}).scalar()
                
                if suma_porcentajes + porcentaje > 100:
                    print(f"Error: La suma de porcentajes excedería 100% (actual: {suma_porcentajes}%)")
                    return

                conn.execute(text("""
                    INSERT INTO Calificaciones (idMatricula, tipoEvaluacion, nota, porcentaje, observaciones)
                    VALUES (:matricula, :tipo, :nota, :porcentaje, :obs)
                """), {
                    'matricula': id_matricula,
                    'tipo': tipo_evaluacion,
                    'nota': nota,
                    'porcentaje': porcentaje,
                    'obs': observaciones
                })
                conn.commit()
                print("Calificación registrada correctamente.")
        except Exception as e:
            print(f"Error al registrar calificación: {str(e)}")

    def ver_calificaciones(self, id_estudiante=None, id_materia=None, id_periodo=None):
        """Muestra calificaciones con filtros opcionales."""
        try:
            with db.engine.connect() as conn:
                query = """
                    SELECT 
                        e.nombres, e.apellidos, e.cedula,
                        mat.nombreMateria, mat.codigo,
                        p.nombrePeriodo,
                        c.tipoEvaluacion, c.nota, c.porcentaje,
                        c.fechaRegistro, c.observaciones
                    FROM Calificaciones c
                    JOIN Matriculas m ON c.idMatricula = m.idMatricula
                    JOIN Estudiantes e ON m.idEstudiante = e.idEstudiante
                    JOIN Materias mat ON m.idMateria = mat.idMateria
                    JOIN Periodos p ON m.idPeriodo = p.idPeriodo
                    WHERE 1=1
                """
                params = {}
                
                if id_estudiante:
                    query += " AND m.idEstudiante = :estudiante"
                    params['estudiante'] = id_estudiante
                if id_materia:
                    query += " AND m.idMateria = :materia"
                    params['materia'] = id_materia
                if id_periodo:
                    query += " AND m.idPeriodo = :periodo"
                    params['periodo'] = id_periodo
                
                query += " ORDER BY e.apellidos, mat.nombreMateria, c.fechaRegistro"

                result = conn.execute(text(query), params)
                calificaciones = result.fetchall()

                if not calificaciones:
                    print("No hay calificaciones registradas.")
                    return

                print("\nListado de calificaciones:")
                estudiante_actual = None
                for cal in calificaciones:
                    if estudiante_actual != cal.cedula:
                        estudiante_actual = cal.cedula
                        print(f"\nEstudiante: {cal.nombres} {cal.apellidos} (CI: {cal.cedula})")
                        print(f"  Materia: {cal.nombreMateria} ({cal.codigo})")
                        print(f"  Período: {cal.nombrePeriodo}")
                    
                    print(f"  - {cal.tipoEvaluacion}: {cal.nota}/100 ({cal.porcentaje}%)")
                    if cal.observaciones:
                        print(f"    Obs: {cal.observaciones}")
        except Exception as e:
            print(f"Error al consultar calificaciones: {str(e)}")

    def ver_promedio_estudiante(self, id_estudiante, id_periodo=None):
        """Muestra el promedio general de un estudiante."""
        try:
            with db.engine.connect() as conn:
                query = """
                    SELECT * FROM vw_PromedioEstudiantes
                    WHERE idEstudiante = :estudiante
                """
                params = {'estudiante': id_estudiante}
                
                if id_periodo:
                    query += " AND idPeriodo = :periodo"
                    params['periodo'] = id_periodo

                result = conn.execute(text(query), params)
                registros = result.fetchall()

                if not registros:
                    print("No hay registros académicos para este estudiante.")
                    return

                print(f"\nReporte académico:")
                print(f"Estudiante: {registros[0].nombres} {registros[0].apellidos}")
                print("\nMaterias:")
                
                total_creditos = 0
                suma_ponderada = 0
                
                for reg in registros:
                    nota = reg.notaFinal if reg.notaFinal else 0
                    print(f"  - {reg.nombreMateria} ({reg.creditos} créditos)")
                    print(f"    Nota Final: {nota:.2f}/100 - {reg.estadoAcademico}")
                    
                    total_creditos += reg.creditos
                    suma_ponderada += nota * reg.creditos
                
                if total_creditos > 0:
                    promedio_general = suma_ponderada / total_creditos
                    print(f"\nPromedio General: {promedio_general:.2f}/100")
        except Exception as e:
            print(f"Error al consultar promedio: {str(e)}")

    def actualizar_calificacion(self, id_calificacion, nueva_nota=None, nuevo_porcentaje=None, nuevas_observaciones=None):
        """Actualiza una calificación existente."""
        try:
            with db.engine.connect() as conn:
                campos = []
                params = {'id': id_calificacion}

                if nueva_nota is not None:
                    campos.append("nota = :nota")
                    params['nota'] = nueva_nota
                if nuevo_porcentaje is not None:
                    campos.append("porcentaje = :porcentaje")
                    params['porcentaje'] = nuevo_porcentaje
                if nuevas_observaciones is not None:
                    campos.append("observaciones = :obs")
                    params['obs'] = nuevas_observaciones

                if not campos:
                    print("No se proporcionaron campos para actualizar.")
                    return

                query = f"UPDATE Calificaciones SET {', '.join(campos)} WHERE idCalificacion = :id"
                conn.execute(text(query), params)
                conn.commit()
                print(f"Calificación ID {id_calificacion} actualizada correctamente.")
        except Exception as e:
            print(f"Error al actualizar calificación: {str(e)}")

    def eliminar_calificacion(self, id_calificacion):
        """Elimina una calificación según su ID."""
        try:
            with db.engine.connect() as conn:
                conn.execute(text("""
                    DELETE FROM Calificaciones WHERE idCalificacion = :id
                """), {'id': id_calificacion})
                conn.commit()
                print(f"Calificación ID {id_calificacion} eliminada correctamente.")
        except Exception as e:
            print(f"Error al eliminar calificación: {str(e)}")