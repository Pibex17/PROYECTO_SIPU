import tkinter as tk
from tkinter import messagebox
from presentation.view_registro import RegistroView
from presentation.view_estudiante import DashboardEstudiante
from presentation.view_admin import DashboardAdmin
from application.services import AuthService

class LoginView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SIPU - Acceso al Sistema")
        self.geometry("400x550")
        self.resizable(False, False)
        self.service = AuthService()
        self._setup_ui()
        self.eval('tk::PlaceWindow . center')

    def _setup_ui(self):
        tk.Label(self, text="Bienvenido al SIPU", font=("Arial", 20, "bold")).pack(pady=40)
        
        tk.Label(self, text="Cédula / Usuario:", font=("Arial", 11)).pack(anchor="w", padx=50)
        self.ent_user = tk.Entry(self, font=("Arial", 12))
        self.ent_user.pack(pady=5, padx=50, fill="x")

        tk.Label(self, text="Contraseña:", font=("Arial", 11)).pack(anchor="w", padx=50)
        self.ent_pass = tk.Entry(self, font=("Arial", 12), show="*")
        self.ent_pass.pack(pady=5, padx=50, fill="x")

        tk.Button(self, text="Iniciar Sesión", bg="#007bff", fg="white", 
                  command=self.login, font=("Arial", 11, "bold"), height=2).pack(pady=30, padx=50, fill="x")
        
        tk.Label(self, text="¿No tienes cuenta?").pack()
        tk.Button(self, text="Registrarse como Estudiante", bg="#28a745", fg="white", 
                  command=self.abrir_registro).pack(pady=5, padx=50, fill="x")

    def login(self):
        u = self.ent_user.get().strip()
        p = self.ent_pass.get().strip()
        
        resultado = self.service.login(u, p)
        
        if resultado == "ADMIN":
            self.withdraw()
            DashboardAdmin(self) # Abre panel Admin
            
        elif resultado:
            self.withdraw() 
            DashboardEstudiante(self, resultado) # Abre panel Estudiante
        else:
            messagebox.showerror("Error", "Credenciales incorrectas o usuario no encontrado.")

    def abrir_registro(self):
        RegistroView(self)