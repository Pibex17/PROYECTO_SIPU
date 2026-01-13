
import pyodbc

def verificar_drivers_odbc():
    print("🔍 BUSCANDO DRIVERS ODBC DISPONIBLES:")
    print("=" * 50)
    
    try:
        drivers = pyodbc.drivers()
        
        if drivers:
            print("✅ Drivers ODBC encontrados:")
            for driver in drivers:
                print(f"  - {driver}")
                
            # Buscar específicamente ODBC Driver 17
            odbc_17 = any('17' in driver for driver in drivers)
            if odbc_17:
                print("\n🎉 ODBC Driver 17 for SQL Server: ✅ INSTALADO")
            else:
                print("\n❌ ODBC Driver 17 for SQL Server: NO ENCONTRADO")
                
        else:
            print("❌ No se encontraron drivers ODBC")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verificar_drivers_odbc()