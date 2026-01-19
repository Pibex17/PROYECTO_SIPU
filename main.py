from config.database import db
from presentation.view_login import LoginView

if __name__ == "__main__":
    print("🚀 Iniciando Sistema SIPU con Arquitectura N-Tier...")
    
    # Inicializar Singleton de DB
    if db.conectar():
        app = LoginView()
        app.mainloop()
    else:
        print("❌ No se pudo iniciar el sistema por fallo en BD.")