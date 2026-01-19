import sys
import os

# Agregamos la ruta actual al sistema para asegurar que encuentre los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- CORRECCIÓN AQUÍ ---
# Antes era: from DataBase import db
# Ahora es: importamos desde la carpeta 'config'
from config.database import db 
from sqlalchemy import text

def resetear_base_datos():
    print("⚠️  INICIANDO RESETEO TOTAL DE LA BASE DE DATOS...")
    
    # Intentar conectar
    if not db.conectar():
        print("❌ Error: No se pudo conectar a la base de datos.")
        return

    try:
        with db.get_connection() as conn:
            # Borramos las tablas en orden inverso para evitar errores de llaves foraneas
            print("1. Eliminando tablas dependientes...")
            conn.execute(text("DROP TABLE IF EXISTS EvaluacionesAsignadas"))
            conn.execute(text("DROP TABLE IF EXISTS EvaluacionesAsignadas")) # Por si acaso
            conn.execute(text("DROP TABLE IF EXISTS Evaluaciones"))
            conn.execute(text("DROP TABLE IF EXISTS Postulaciones"))
            conn.execute(text("DROP TABLE IF EXISTS Inscripciones"))
            
            print("2. Eliminando tablas principales...")
            conn.execute(text("DROP TABLE IF EXISTS OfertasAcademicas"))
            conn.execute(text("DROP TABLE IF EXISTS Estudiantes"))
            conn.execute(text("DROP TABLE IF EXISTS Carreras"))
            conn.execute(text("DROP TABLE IF EXISTS Periodos"))
            conn.execute(text("DROP TABLE IF EXISTS RegistroNacionalPersonas"))
            
            conn.commit()
            print("✅ ¡BASE DE DATOS LIMPIA! Ahora ejecuta main.py para recrear todo.")
            
    except Exception as e:
        print(f"❌ Error durante el reseteo: {e}")

if __name__ == "__main__":
    resetear_base_datos()