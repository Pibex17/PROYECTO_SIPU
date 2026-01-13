from sqlalchemy import text
from DataBase import db

class Aspirante:
    
    @staticmethod
    def validar_en_registro_nacional(tipo_documento, numero_identificacion):
        """
        Valida si una persona existe en la tabla RegistroNacionalPersonas
        mediante tipo de documento y número de identificación
        
        Args:
            tipo_documento (str): Tipo de documento (cédula, pasaporte, etc.)
            numero_identificacion (str): Número de identificación
        
        Returns:
            dict/None: Datos de la persona si existe, None si no existe
        """
        try:
            with db.engine.connect() as conn:
                # Normalizar valores para evitar problemas de formato
                tipo_doc_normalizado = tipo_documento.strip().lower()
                numero_normalizado = str(numero_identificacion).strip()
                
                # Consultar en la tabla de registro nacional
                result = conn.execute(text("""
                    SELECT idAspirante, tipoDocumento, identificacion, 
                        nombres, apellidos, estado
                    FROM RegistroNacionalPersonas
                    WHERE LOWER(tipoDocumento) = LOWER(:tipo_doc)
                    AND identificacion = :numero
                """), {
                    "tipo_doc": tipo_doc_normalizado,
                    "numero": numero_normalizado
                })
                
                registro = result.fetchone()
                
                if registro:
                    print(f"✅ Registro encontrado: {registro.nombres} {registro.apellidos}")
                    return registro
                else:
                    print(f"❌ No se encontró registro para {tipo_documento} {numero_identificacion}")
                    return None
                    
        except Exception as e:
            print(f"❌ ERROR en la validación: {str(e)}")
            return None
    
    @staticmethod
    def registrar_estudiante(cedula, nombres, apellidos, fecha_nacimiento, carrera_id):
        """Registra un nuevo estudiante en la tabla Estudiantes"""
        try:
            with db.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO Estudiantes (cedula, nombres, apellidos, fechaNacimiento, carreraId, estado)
                    VALUES (:cedula, :nombres, :apellidos, :fecha_nacimiento, :carrera_id, 'Activo')
                """), {
                    "cedula": cedula,
                    "nombres": nombres,
                    "apellidos": apellidos,
                    "fecha_nacimiento": fecha_nacimiento,
                    "carrera_id": carrera_id
                })
                conn.commit()
                print(f"✅ Estudiante '{nombres} {apellidos}' registrado exitosamente.")
                return True
        except Exception as e:
            print(f"❌ ERROR al registrar el estudiante: {str(e)}")
            return False
    
    @staticmethod
    def buscar_estudiante_por_identificacion(numero_identificacion):
        """
        Busca un estudiante por número de identificación
        """
        try:
            with db.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT idEstudiante, cedula, nombres, apellidos, 
                        fechaNacimiento, carreraId, estado
                    FROM Estudiantes
                    WHERE cedula = :cedula
                """), {"cedula": str(numero_identificacion).strip()})
                
                estudiante = result.fetchone()
                return estudiante
                
        except Exception as e:
            print(f"❌ ERROR al buscar estudiante: {str(e)}")
            return None