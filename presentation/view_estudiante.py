import tkinter as tk
from tkinter import ttk, messagebox
from application.services import StudentService
import os

class DashboardEstudiante(tk.Toplevel):
    def __init__(self, parent, estudiante):
        super().__init__(parent)
        self.estudiante = estudiante
        self.service = StudentService()
        self.parent = parent
        self.title(f"Portal Estudiante - {estudiante.nombres}")
        self.geometry("900x600")
        self.protocol("WM_DELETE_WINDOW", self.cerrar)
        self._ui()

    def cerrar(self):
        self.destroy()
        self.parent.deiconify()

    def _ui(self):
        # Barra superior
        bar = tk.Frame(self, bg="#0056b3", height=50)
        bar.pack(fill="x")
        tk.Label(bar, text=f"Estudiante: {self.estudiante.nombres} {self.estudiante.apellidos}", bg="#0056b3", fg="white", font=("Arial", 12)).pack(side="left", padx=10)
        tk.Button(bar, text="Cerrar Sesión", command=self.cerrar, bg="red", fg="white").pack(side="right", padx=5)

        # Pestañas
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        # ==========================================
        # PESTAÑA 1: INSCRIPCIÓN (OFERTAS)
        # ==========================================
        t_ins = tk.Frame(nb)
        nb.add(t_ins, text="Inscripción")
        
        tk.Label(t_ins, text="Ofertas Académicas Disponibles", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Tabla de Ofertas
        # Definimos las columnas visibles y ocultas
        cols = ("ID Oferta", "Carrera", "Periodo", "IDCarrera")
        self.tree_ofertas = ttk.Treeview(t_ins, columns=cols, show="headings", displaycolumns=("ID Oferta", "Carrera", "Periodo"))
        
        self.tree_ofertas.heading("ID Oferta", text="ID Oferta")
        self.tree_ofertas.column("ID Oferta", width=80, anchor="center")
        
        self.tree_ofertas.heading("Carrera", text="Carrera")
        self.tree_ofertas.column("Carrera", width=400)
        
        self.tree_ofertas.heading("Periodo", text="Periodo")
        self.tree_ofertas.column("Periodo", width=150, anchor="center")
        
        self.tree_ofertas.pack(fill="both", expand=True, padx=20, pady=5)

        # --- FUNCIÓN DE CARGA ---
        def cargar_ofertas():
            # 1. Limpiar tabla
            for i in self.tree_ofertas.get_children():
                self.tree_ofertas.delete(i)
            
            try:
                # 2. Obtener datos del servicio
                ofertas = self.service.ver_ofertas()
                
                # 3. Llenar tabla
                for of in ofertas:
                    # Se asume que 'of' tiene: idOferta, nombreCarrera, nombrePeriodo, idCarrera
                    self.tree_ofertas.insert("", "end", values=(of.idOferta, of.nombreCarrera, of.nombrePeriodo, of.idCarrera))
            except Exception as e:
                messagebox.showerror("Error de Conexión", f"No se pudieron cargar las ofertas:\n{str(e)}")

        # --- BOTONES ---
        f_btn = tk.Frame(t_ins)
        f_btn.pack(pady=10)
        
        tk.Button(f_btn, text="🔄 Actualizar Lista", command=cargar_ofertas, bg="#17a2b8", fg="white").pack(side="left", padx=5)

        def inscribirse():
            sel = self.tree_ofertas.selection()
            if not sel: 
                messagebox.showwarning("Aviso", "Seleccione una carrera de la lista.")
                return
            
            val = self.tree_ofertas.item(sel[0])['values']
            id_oferta = val[0]
            nombre = val[1]
            id_carrera = val[3] # ID Oculto
            
            if messagebox.askyesno("Confirmar", f"¿Desea inscribirse en {nombre}?"):
                ok, msg = self.service.inscribirse(self.estudiante, id_oferta, id_carrera) 
                if ok: 
                    messagebox.showinfo("Éxito", msg)
                    refresh_estado() # Actualizar la otra pestaña
                else: 
                    messagebox.showerror("Error", msg)

        tk.Button(f_btn, text="📝 Inscribirse", command=inscribirse, bg="green", fg="white", font=("Arial", 10, "bold"), width=15).pack(side="left", padx=5)

        # Carga automática inicial
        cargar_ofertas()


        # ==========================================
        # PESTAÑA 2: ESTADO Y NOTAS
        # ==========================================
        t_proc = tk.Frame(nb)
        nb.add(t_proc, text="Estado y Notas")
        
        cols_ex = ("Evaluacion", "Fecha/Hora", "Puntaje", "Estado")
        tree_ex = ttk.Treeview(t_proc, columns=cols_ex, show="headings")
        for c in cols_ex: tree_ex.heading(c, text=c)
        tree_ex.column("Evaluacion", width=250)
        tree_ex.pack(fill="both", expand=True, padx=20, pady=10)

        def refresh_estado():
            for i in tree_ex.get_children(): tree_ex.delete(i)
            data = self.service.ver_mis_procesos(self.estudiante)
            
            # Inscripciones
            for i in data['inscripciones']:
                if i.estado == 'Pendiente':
                    # Evitar duplicados si ya tiene examen
                    tiene_examen = any(e.estado == 'Pendiente' for e in data['examenes'])
                    if not tiene_examen:
                        tree_ex.insert("", "end", values=("Proceso de Admisión", "Esperando Asignación", "-", "INSCRIPCION PENDIENTE"))
            
            # Exámenes
            for e in data['examenes']:
                puntaje = str(e.puntajeObtenido) if e.puntajeObtenido is not None else "Pendiente"
                fecha = f"{e.fechaVencimiento} {e.observaciones}" if e.fechaVencimiento else "Por definir"
                tree_ex.insert("", "end", values=(e.nombreEvaluacion, fecha, puntaje, e.estado))

        def descargar_pdf():
            sel = tree_ex.selection()
            if not sel: return
            
            valores = tree_ex.item(sel[0])['values']
            if valores[3] == "INSCRIPCION PENDIENTE":
                messagebox.showwarning("Aviso", "Aún no se ha generado su comprobante de examen/notas.")
                return
            
            ok, ruta = self.service.descargar_comprobante_examen(
                self.estudiante, valores[0], valores[2], valores[3], valores[1]
            )
            if ok:
                messagebox.showinfo("PDF Generado", f"Guardado en:\n{ruta}")
                try: os.startfile(ruta)
                except: pass

        tk.Button(t_proc, text="🔄 Actualizar Estado", command=refresh_estado).pack(pady=5)
        tk.Button(t_proc, text="📄 Descargar Comprobante", command=descargar_pdf, bg="#17a2b8", fg="white").pack(pady=10)
        
        refresh_estado()