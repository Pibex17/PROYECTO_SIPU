import tkinter as tk
from tkinter import messagebox
from application.services import AuthService

class RegistroView(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("SIPU - Crear Cuenta")
        self.geometry("550x650")
        self.service = AuthService()
        self.parent = parent
        self._center_window()
        self._setup_ui()

    def _center_window(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f'{w}x{h}+{x}+{y}')

    def _setup_ui(self):
        tk.Label(self, text="Registro Oficial de Estudiantes", font=("Arial", 18, "bold")).pack(pady=20)
        
        frm = tk.Frame(self)
        frm.pack(pady=10)

        # 1. Cédula con Buscador
        tk.Label(frm, text="Cédula de Identidad:", font=("Arial", 10, "bold")).pack(anchor="w")
        frm_ced = tk.Frame(frm)
        frm_ced.pack(fill="x", pady=5)
        
        self.entry_cedula = tk.Entry(frm_ced, width=30)
        self.entry_cedula.pack(side="left")
        
        tk.Button(frm_ced, text="🔍 Buscar en Registro Civil", bg="#3498db", fg="white", 
                  command=self.buscar_datos).pack(side="left", padx=10)

        # 2. Datos Personales (Bloqueados)
        self.entries = {}
        
        tk.Label(frm, text="Nombres (Automático):").pack(anchor="w", pady=(10,0))
        self.entries["nombres"] = tk.Entry(frm, width=45, state="disabled")
        self.entries["nombres"].pack(pady=5)

        tk.Label(frm, text="Apellidos (Automático):").pack(anchor="w")
        self.entries["apellidos"] = tk.Entry(frm, width=45, state="disabled")
        self.entries["apellidos"].pack(pady=5)

        # 3. Datos de Contacto y Cuenta
        for label, key in [("Correo Electrónico:", "email"), ("Teléfono:", "telefono")]:
            tk.Label(frm, text=label).pack(anchor="w", pady=(5,0))
            e = tk.Entry(frm, width=45)
            e.pack(pady=5)
            self.entries[key] = e

        tk.Label(frm, text="Contraseña:").pack(anchor="w", pady=(5,0))
        self.entries["pass"] = tk.Entry(frm, width=45, show="*")
        self.entries["pass"].pack(pady=5)

        tk.Label(frm, text="Confirmar Contraseña:").pack(anchor="w", pady=(5,0))
        self.entries["confirm"] = tk.Entry(frm, width=45, show="*")
        self.entries["confirm"].pack(pady=5)

        # Botones
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Registrar Usuario", bg="green", fg="white", 
                  font=("bold"), width=20, height=2, command=self.accion_registrar).pack(pady=5)
        tk.Button(btn_frame, text="Cancelar", command=self.destroy).pack()

    def buscar_datos(self):
        cedula = self.entry_cedula.get().strip()
        if not cedula:
            messagebox.showwarning("Aviso", "Ingrese una cédula para buscar.")
            return

        datos = self.service.consultar_datos_ciudadano(cedula)
        
        if datos:
            # Rellenar y bloquear
            self._set_entry("nombres", datos["nombres"])
            self._set_entry("apellidos", datos["apellidos"])
            messagebox.showinfo("Encontrado", f"Datos verificados correctamente:\n{datos['nombres']} {datos['apellidos']}")
        else:
            # Limpiar
            self._set_entry("nombres", "")
            self._set_entry("apellidos", "")
            messagebox.showerror("Error", "La cédula no existe en el Registro Nacional.\nNo puede registrarse.")

    def _set_entry(self, key, value):
        self.entries[key].config(state="normal")
        self.entries[key].delete(0, tk.END)
        self.entries[key].insert(0, value)
        self.entries[key].config(state="disabled") # Volver a bloquear para que no editen

    def accion_registrar(self):
        cedula = self.entry_cedula.get().strip()
        nombres = self.entries["nombres"].get()
        
        # Validar que ya haya buscado
        if not nombres:
            messagebox.showwarning("Aviso", "Primero debe BUSCAR y validar su cédula.")
            return

        data = {k: v.get().strip() for k, v in self.entries.items() if k not in ["nombres", "apellidos"]}
        
        try:
            # Los nombres y apellidos se envían, pero el servicio los ignorará y usará los oficiales por seguridad
            exito, msg = self.service.registrar_estudiante(
                cedula, 
                nombres, 
                self.entries["apellidos"].get(), 
                data["email"], 
                data["telefono"], 
                data["pass"], 
                data["confirm"]
            )
            
            if exito:
                messagebox.showinfo("Bienvenido", "Cuenta creada exitosamente.\nInicie sesión.")
                self.destroy()
            else:
                messagebox.showerror("Error", msg)
        except Exception as e:
            messagebox.showerror("Error Crítico", str(e))