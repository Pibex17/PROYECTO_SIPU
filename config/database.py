from sqlalchemy import create_engine
import pyodbc

class DatabaseSingleton:
    """
    Gestiona una única instancia de conexión a la base de datos (Patrón Singleton).
    Maneja la detección automática del driver ODBC disponible.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseSingleton, cls).__new__(cls)
            cls._instance.engine = None
            # Ajustar según el nombre del servidor SQL local
            cls._instance.server_name = "localhost\\SQLEXPRESS" 
        return cls._instance

    def conectar(self):
        """Establece la conexión con SQL Server usando SQLAlchemy."""
        if self.engine: return True
        try:
            # Detección dinámica de drivers para compatibilidad entre entornos
            drivers = pyodbc.drivers()
            driver_name = "ODBC Driver 17 for SQL Server"
            if "ODBC Driver 18 for SQL Server" in drivers:
                driver_name = "ODBC Driver 18 for SQL Server"
            elif "SQL Server" in drivers:
                driver_name = "SQL Server"

            conn_str = (
                f"mssql+pyodbc://@{self.server_name}/RegistroNacional?"
                f"driver={driver_name}&trusted_connection=yes&"
                f"Encrypt=no&TrustServerCertificate=yes"
            )
            self.engine = create_engine(conn_str)
            
            # Validación de conectividad (Heartbeat)
            with self.engine.connect() as conn:
                pass 
            return True
        except Exception as e:
            print(f"[CRITICAL] Error de conexión a BD: {e}")
            return False

    def get_connection(self):
        """Retorna un objeto de conexión activo."""
        return self.engine.connect()

db = DatabaseSingleton()