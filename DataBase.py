from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import getpass

class DatabaseManager:
    """Gestiona la conexión a SQL Server Express y operaciones básicas de BD"""
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.Base = declarative_base()
    
    def conectar(self):
        """
        Conecta al servidor SQL Server Express
        Primero intenta con usuario 'sa', luego con autenticación Windows
        """
        print("\n" + "="*60)
        print("CONEXIÓN A SQL SERVER EXPRESS")
        print("="*60)
        
        # Solicita datos de conexión
        server = input("Nombre del servidor [localhost\\SQLEXPRESS]: ") or "localhost\\SQLEXPRESS"
        database = "RegistroNacional"
        username = "sa"
        password = getpass.getpass("Contraseña de SQL Server: ")
        
        try:
            connection_string = (
                f"mssql+pyodbc://{username}:{password}"
                f"@{server}/{database}?"
                f"driver=ODBC Driver 17 for SQL Server&"
                f"encrypt=no&"
                f"trust_server_certificate=yes"
            )
            
            print(f"Conectando a: {server}...")
            
            self.engine = create_engine(connection_string)
            self.SessionLocal = sessionmaker(bind=self.engine)
            
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT DB_NAME() as db, @@SERVERNAME as server"))
                info = result.fetchone()
                
                print("Conexión exitosa!")
                print(f"Servidor: {info.server}")
                print(f"Base de datos: {info.db}\n")
                return True
                
        except Exception as e:
            print(f"Error: {str(e)}\n")
            print("Intentando con autenticación Windows...")
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
            
            print("Conectando con autenticación Windows...")
            
            self.engine = create_engine(connection_string)
            self.SessionLocal = sessionmaker(bind=self.engine)
            
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT suser_name() as usuario"))
                usuario = result.fetchone()[0]
                
                print("Conexión exitosa con Windows Auth!")
                print(f"Usuario: {usuario}\n")
                return True
                
        except Exception as e:
            print(f"Error con Windows Auth: {e}\n")
            return False
    
    def verificar_base_datos(self):
        """Verifica si la base de datos existe, si no la crea"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT name FROM sys.databases 
                    WHERE name = 'RegistroNacional'
                """))
                
                if not result.fetchone():
                    print("La base de datos 'RegistroNacional' no existe.")
                    crear = input("¿Crearla? (s/n): ").lower()
                    
                    if crear == 's':
                        conn.execute(text("CREATE DATABASE RegistroNacional"))
                        print("Base de datos 'RegistroNacional' creada!\n")
                    else:
                        print("Necesitas la base de datos para continuar\n")
                        return False
                else:
                    print("Base de datos 'RegistroNacional' encontrada\n")
                
                return True
                    
        except Exception as e:
            print(f"Error al verificar base de datos: {e}\n")
            return False

db = DatabaseManager()