import pyodbc

# Script para verificar si los drivers ODBC necesarios están instalados
# Ejecutar ANTES de correr main.py

def verificar_drivers_odbc():
    # Intenta obtener lista de drivers disponibles
    print("Buscando drivers ODBC disponibles...")
    print("=" * 50)
    
    try:
        # Obtiene todos los drivers ODBC instalados
        drivers = pyodbc.drivers()
        
        if drivers:
            print("Drivers ODBC encontrados:\n")
            for driver in drivers:
                print(f"  - {driver}")
            
            # Busca específicamente el ODBC Driver 17 (necesario para SQL Server)
            odbc_17 = any('17' in driver for driver in drivers)
            
            print("\n" + "=" * 50)
            if odbc_17:
                print("ODBC Driver 17 for SQL Server: INSTALADO")
                print("El sistema está listo para conectar a SQL Server.")
            else:
                print("ODBC Driver 17 for SQL Server: NO ENCONTRADO")
                print("Debes instalar 'ODBC Driver 17 for SQL Server' para continuar.")
                
        else:
            print("No se encontraron drivers ODBC en el sistema.")
            
    except Exception as e:
        # Si hay error al acceder a los drivers
        print(f"Error al verificar drivers: {e}")

if __name__ == "__main__":
    verificar_drivers_odbc()