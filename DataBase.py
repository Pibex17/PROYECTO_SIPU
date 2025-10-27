
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import getpass

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.Base = declarative_base()
    
    def conectar(self):
        """Conecta al servidor correcto: localhost\SQLEXPRESS"""
        print("🔌 CONEXIÓN A SQL SERVER EXPRESS")
        print("=" * 50)
        
        # Usar el servidor que SÍ funciona
        server = "PIBEX17PC\SQLEXPRESS"  # ← Este es el que funciona
        database = "RegistroNacional"
        username = "sa"
        password = getpass.getpass("Contraseña de SQL Server: ")
        
        try:
            # Cadena de conexión
            connection_string = (
                f"mssql+pyodbc://{username}:{password}"
                f"@{server}/{database}?"
                f"driver=ODBC Driver 17 for SQL Server&"
                f"encrypt=no&"
                f"trust_server_certificate=yes"
            )
            
            print(f"⏳ Conectando a: {server}...")
            
            self.engine = create_engine(connection_string)
            self.SessionLocal = sessionmaker(bind=self.engine)
            
            # Probar conexión
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT DB_NAME() as db, @@SERVERNAME as server"))
                info = result.fetchone()
                
                print("✅ CONEXIÓN EXITOSA!")
                print(f"📊 Servidor: {info.server}")
                print(f"🗃️ Base de datos: {info.db}")
                return True
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            
            # Si falla con sa, probar con autenticación Windows
            print("\n🔄 Probando con autenticación Windows...")
            return self.conectar_windows()
    
    def conectar_windows(self):
        """Intenta conectar con autenticación Windows"""
        try:
            server = "localhost\\SQLEXPRESS"
            database = "RegistroNacional"
            
            connection_string = (
                f"mssql+pyodbc://{server}/{database}?"
                f"driver=ODBC Driver 17 for SQL Server&"
                f"trusted_connection=yes"
            )
            
            print(f"⏳ Conectando con autenticación Windows...")
            
            self.engine = create_engine(connection_string)
            self.SessionLocal = sessionmaker(bind=self.engine)
            
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT suser_name() as usuario"))
                usuario = result.fetchone()[0]
                
                print("✅ CONEXIÓN EXITOSA con Windows Auth!")
                print(f"👤 Usuario: {usuario}")
                return True
                
        except Exception as e:
            print(f"❌ Error con Windows Auth: {e}")
            return False
    
    def verificar_base_datos(self):
        """Verifica si la base de datos existe, si no la crea"""
        try:
            with self.engine.connect() as conn:
                # Verificar si la base de datos existe
                result = conn.execute(text("""
                    SELECT name FROM sys.databases 
                    WHERE name = 'RegistroNacional'
                """))
                
                if not result.fetchone():
                    print("📦 La base de datos 'RegistroNacional' no existe.")
                    crear = input("¿Crearla? (s/n): ").lower()
                    
                    if crear == 's':
                        conn.execute(text("CREATE DATABASE RegistroNacional"))
                        print("✅ Base de datos 'RegistroNacional' creada!")
                    else:
                        print("❌ Necesitas la base de datos para continuar")
                        return False
                else:
                    print("✅ Base de datos 'RegistroNacional' encontrada")
                
                return True
                    
        except Exception as e:
            print(f"❌ Error al verificar base de datos: {e}")
            return False

# Instancia global
db = DatabaseManager()