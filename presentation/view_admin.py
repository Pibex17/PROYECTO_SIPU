import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from application.services import AdminService, EvaluacionService

class DashboardAdmin(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("PANEL ADMINISTRADOR - SIPU")
        self.geometry("1250x850")
        self.service = AdminService()
        self.parent = parent
        self.protocol("WM_DELETE_WINDOW", self.cerrar_sesion)
        self._setup_ui()

    def cerrar_sesion(self):
        self.destroy()
        self.parent.deiconify()

    def _setup_ui(self):
        header = tk.Frame(self, bg="#2c3e50", height=60)
        header.pack(fill="x")
        tk.Label(header, text="ADMINISTRACIÓN ACADÉMICA", fg="white", bg="#2c3e50", font=("Arial", 16, "bold")).pack(side="left", padx=20)
        tk.Button(header, text="Cerrar Sesión", command=self.cerrar_sesion, bg="#c0392b", fg="white").pack(side="right", padx=20, pady=10)
        
        # --- SISTEMA DE PESTAÑAS CON EVENTOS ---
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_estructura = tk.Frame(self.nb)
        self.nb.add(self.tab_estructura, text="1. Gestión Periodos/Ofertas")
        self._ui_estructura_academica(self.tab_estructura)

        self.tab_inscripciones = tk.Frame(self.nb)
        self.nb.add(self.tab_inscripciones, text="2. Validar Inscripciones")
        self._ui_inscripciones(self.tab_inscripciones)

        self.tab_calificar = tk.Frame(self.nb)
        self.nb.add(self.tab_calificar, text="3. Cargar Notas (Excel)")
        self._ui_calificar(self.tab_calificar)

        self.tab_matriz = tk.Frame(self.nb)
        self.nb.add(self.tab_matriz, text="4. Matriz de Méritos")
        self._ui_matriz(self.tab_matriz)

        self.tab_stats = tk.Frame(self.nb)
        self.nb.add(self.tab_stats, text="5. Estadísticas")
        self._ui_estadisticas(self.tab_stats)

        # EVENTO: Recargar datos automáticamente al cambiar de pestaña
        self.nb.bind("<<NotebookTabChanged>>", self.al_cambiar_pestana)

    def al_cambiar_pestana(self, event):
        """Detecta qué pestaña se abrió y refresca su tabla automáticamente."""
        tab_actual = self.nb.index(self.nb.select())
        
        if tab_actual == 1: # Validar Inscripciones
            self.recargar_inscripciones()
        elif tab_actual == 2: # Cargar Notas
            self.recargar_notas_pendientes()
        elif tab_actual == 3: # Matriz Méritos
            self.recargar_matriz_final()
        elif tab_actual == 4: # Estadísticas
            self.recargar_stats()

    # ---------------------------------------------------------
    # 1. GESTIÓN ESTRUCTURA
    # ---------------------------------------------------------
    def _ui_estructura_academica(self, frame):
        paned = tk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        f_left = tk.Frame(paned, width=350, bg="#ecf0f1")
        paned.add(f_left)
        
        tk.Label(f_left, text="PERIODOS ACADÉMICOS", font=("Arial", 12, "bold"), bg="#ecf0f1").pack(pady=10)
        tk.Button(f_left, text="+ Nuevo Periodo", bg="#27ae60", fg="white", 
                  command=self.modal_crear_periodo).pack(fill="x", padx=10, pady=5)
        
        self.tree_periodos = ttk.Treeview(f_left, columns=("ID", "Nombre"), show="headings", height=15)
        self.tree_periodos.heading("ID", text="ID"); self.tree_periodos.column("ID", width=40)
        self.tree_periodos.heading("Nombre", text="Periodo"); self.tree_periodos.column("Nombre", width=150)
        self.tree_periodos.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree_periodos.bind("<<TreeviewSelect>>", self.cargar_detalle_periodo)

        def eliminar_periodo_sel():
            sel = self.tree_periodos.selection()
            if not sel: return
            item = self.tree_periodos.item(sel[0])
            id_p = item['values'][0]
            if messagebox.askyesno("Confirmar", f"¿Eliminar periodo {item['values'][1]}?"):
                ok, msg = self.service.eliminar_periodo(id_p)
                if ok: 
                    messagebox.showinfo("Éxito", msg)
                    self.cargar_periodos()
                    for w in self.f_right.winfo_children(): w.destroy()
                else: 
                    messagebox.showerror("Error", msg)

        tk.Button(f_left, text="🗑️ Eliminar Periodo", bg="#c0392b", fg="white", command=eliminar_periodo_sel).pack(fill="x", padx=10, pady=5)
        tk.Button(f_left, text="⚙️ Gestionar Carreras", bg="#7f8c8d", fg="white", command=self.modal_gestion_carreras).pack(side="bottom", fill="x", padx=10, pady=10)

        self.f_right = tk.Frame(paned, bg="white", width=800)
        paned.add(self.f_right)
        
        self.lbl_periodo_sel = tk.Label(self.f_right, text="Seleccione un periodo para gestionar", font=("Arial", 14), fg="gray", bg="white")
        self.lbl_periodo_sel.pack(expand=True)
        self.cargar_periodos()

    def cargar_periodos(self):
        for i in self.tree_periodos.get_children(): self.tree_periodos.delete(i)
        for p in self.service.obtener_lista_periodos():
            self.tree_periodos.insert("", "end", values=(p.idPeriodo, p.nombrePeriodo))

    def cargar_detalle_periodo(self, event):
        for w in self.f_right.winfo_children(): w.destroy()
        sel = self.tree_periodos.selection()
        if not sel: return
        item = self.tree_periodos.item(sel[0])
        self.id_periodo_actual = item['values'][0] 
        nom_periodo = item['values'][1]

        header = tk.Frame(self.f_right, bg="white")
        header.pack(fill="x", padx=20, pady=20)
        tk.Label(header, text=f"Periodo: {nom_periodo}", font=("Arial", 18, "bold"), bg="white", fg="#2980b9").pack(side="left")
        tk.Button(header, text="🔄 Actualizar Panel", command=lambda: self.cargar_detalle_periodo(None), bg="#f1c40f").pack(side="right")

        nb_p = ttk.Notebook(self.f_right)
        nb_p.pack(fill="both", expand=True, padx=20, pady=10)

        t_ofertas = tk.Frame(nb_p); nb_p.add(t_ofertas, text="Oferta Académica")
        self._ui_ofertas_periodo(t_ofertas, self.id_periodo_actual)

        t_evals = tk.Frame(nb_p); nb_p.add(t_evals, text="Evaluaciones")
        self._ui_evaluaciones_periodo(t_evals, self.id_periodo_actual)

    def _ui_ofertas_periodo(self, frame, id_periodo):
        frm_add = tk.LabelFrame(frame, text="Agregar Nueva Oferta", padx=10, pady=10)
        frm_add.pack(fill="x", padx=10, pady=10)
        tk.Label(frm_add, text="Carrera Activa:").pack(side="left")
        self.cb_carreras = ttk.Combobox(frm_add, state="readonly", width=30)
        self.cb_carreras.pack(side="left", padx=5)
        
        def refrescar_combo_carreras():
            self.cb_carreras.set('')
            carreras = self.service.obtener_lista_carreras_activas()
            self.mapa_carreras_activas = {c.nombreCarrera: c.idCarrera for c in carreras}
            self.cb_carreras['values'] = list(self.mapa_carreras_activas.keys())
        refrescar_combo_carreras()
        self.cb_carreras.bind("<Button-1>", lambda e: refrescar_combo_carreras())

        tk.Label(frm_add, text="Cupos:").pack(side="left", padx=5)
        e_cupos = tk.Entry(frm_add, width=10); e_cupos.pack(side="left"); e_cupos.insert(0, "50")

        def agregar_oferta():
            nom_c = self.cb_carreras.get()
            if not nom_c: return
            if self.service.crear_oferta_en_periodo(self.mapa_carreras_activas[nom_c], id_periodo, e_cupos.get()):
                messagebox.showinfo("Éxito", "Oferta agregada.")
                cargar_lista_ofertas()
            else: messagebox.showerror("Error", "Oferta ya existe.")
        tk.Button(frm_add, text="+ Agregar", bg="#2ecc71", fg="white", command=agregar_oferta).pack(side="left", padx=20)

        tree = ttk.Treeview(frame, columns=("ID", "Carrera", "Cupos", "Estado"), show="headings", height=8)
        tree.heading("ID", text="ID"); tree.column("ID", width=40)
        tree.heading("Carrera", text="Carrera"); tree.heading("Cupos", text="Cupos"); tree.heading("Estado", text="Estado")
        tree.pack(fill="both", expand=True, padx=10, pady=5)

        def cargar_lista_ofertas():
            for i in tree.get_children(): tree.delete(i)
            for o in self.service.obtener_ofertas_del_periodo(id_periodo):
                tree.insert("", "end", values=(o.idOferta, o.nombreCarrera, o.cupos, o.estado))
        
        def borrar_oferta():
            sel = tree.selection()
            if not sel: return
            oid = tree.item(sel[0])['values'][0]
            if messagebox.askyesno("Borrar", "¿Eliminar esta oferta? \n¡Se borrarán también las inscripciones!"):
                ok, msg = self.service.eliminar_oferta(oid)
                if ok: cargar_lista_ofertas()
                else: messagebox.showerror("Error", msg)
        tk.Button(frame, text="🗑️ Eliminar Oferta Seleccionada", command=borrar_oferta, bg="red", fg="white").pack(pady=5)
        cargar_lista_ofertas()

    def _ui_evaluaciones_periodo(self, frame, id_periodo):
        tk.Label(frame, text="Asignación de Examen de Admisión", font=("Arial", 12, "bold")).pack(pady=15)
        frm = tk.Frame(frame); frm.pack(pady=20)
        tk.Label(frm, text="Fecha (YYYY-MM-DD):").grid(row=0, column=0); e_fecha = tk.Entry(frm); e_fecha.grid(row=0, column=1)
        tk.Label(frm, text="Hora (HH:MM):").grid(row=1, column=0); e_hora = tk.Entry(frm); e_hora.grid(row=1, column=1)
        def asignar():
            if not e_fecha.get(): return
            cant = self.service.asignar_horarios_evaluacion(id_periodo, e_fecha.get(), e_hora.get())
            if cant >= 0: messagebox.showinfo("Listo", f"Horarios asignados a {cant} estudiantes.\nAhora aparecerán en la lista para cargar notas.")
            else: messagebox.showerror("Error", "Fallo al asignar.")
        tk.Button(frame, text="📅 Asignar Horarios Masivos", bg="#e67e22", fg="white", command=asignar).pack(pady=20)

    # ---------------------------------------------------------
    # 2. VALIDAR INSCRIPCIONES
    # ---------------------------------------------------------
    def _ui_inscripciones(self, frame):
        self.tree_insc = ttk.Treeview(frame, columns=("ID", "Estudiante", "Carrera"), show="headings")
        self.tree_insc.heading("ID", text="ID"); self.tree_insc.heading("Estudiante", text="Estudiante"); self.tree_insc.heading("Carrera", text="Carrera")
        self.tree_insc.pack(fill="both", expand=True)
        
        btn_f = tk.Frame(frame); btn_f.pack(pady=10)
        
        def procesar(accion):
            sel = self.tree_insc.selection()
            if not sel: return
            id_ins = self.tree_insc.item(sel[0])['values'][0]
            if accion == "ACEPTAR": ok, msg = self.service.aceptar_inscripcion(id_ins)
            else: ok, msg = self.service.rechazar_inscripcion(id_ins)
            if ok: 
                messagebox.showinfo("Info", msg)
                self.recargar_inscripciones()
            else: messagebox.showerror("Error", msg)
        
        tk.Button(btn_f, text="✅ Aceptar", command=lambda: procesar("ACEPTAR"), bg="green", fg="white", width=15).pack(side="left", padx=10)
        tk.Button(btn_f, text="❌ Rechazar", command=lambda: procesar("RECHAZAR"), bg="red", fg="white", width=15).pack(side="left", padx=10)
        tk.Button(frame, text="Refrescar", command=self.recargar_inscripciones).pack()

    def recargar_inscripciones(self):
        for i in self.tree_insc.get_children(): self.tree_insc.delete(i)
        for r in self.service.obtener_inscripciones_pendientes():
            self.tree_insc.insert("", "end", values=(r.idInscripcion, r.Estudiante, r.nombreCarrera))

    # ---------------------------------------------------------
    # 3. CARGAR NOTAS
    # ---------------------------------------------------------
    def _ui_calificar(self, frame):
        def subir_excel():
            path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
            if path:
                ok, msg = self.service.cargar_notas_excel(path)
                if ok: 
                    messagebox.showinfo("Carga Exitosa", f"{msg}\n\nLos estudiantes aprobados/reprobados se han movido a la MATRIZ DE MÉRITOS.")
                    self.recargar_notas_pendientes() # Limpia la lista de pendientes
                    self.recargar_matriz_final()     # Actualiza la matriz
                else: 
                    messagebox.showerror("Error de Carga", msg)

        frm_top = tk.Frame(frame); frm_top.pack(fill="x", pady=20)
        tk.Label(frm_top, text="Cargar Matriz de Notas (Masiva)", font=("Arial", 12)).pack(side="left", padx=20)
        tk.Button(frm_top, text="📂 Seleccionar Excel", command=subir_excel, bg="#8e44ad", fg="white", height=2, width=20).pack(side="left")

        # Tabla de Pendientes
        self.tree_notas = ttk.Treeview(frame, columns=("ID", "Cedula", "Estudiante", "Examen"), show="headings")
        self.tree_notas.heading("ID", text="ID"); self.tree_notas.column("ID", width=30)
        self.tree_notas.heading("Cedula", text="Cédula"); self.tree_notas.column("Cedula", width=100)
        self.tree_notas.heading("Estudiante", text="Estudiante"); self.tree_notas.column("Estudiante", width=250)
        self.tree_notas.heading("Examen", text="Examen Pendiente")
        self.tree_notas.pack(fill="both", expand=True)
        
        tk.Button(frame, text="🔄 Refrescar Lista Pendientes", command=self.recargar_notas_pendientes).pack(pady=10)

    def recargar_notas_pendientes(self):
        for i in self.tree_notas.get_children(): self.tree_notas.delete(i)
        # Aquí DEBEN aparecer los estudiantes que ya tienen horario asignado pero no nota
        for r in self.service.obtener_pendientes_calificacion():
            self.tree_notas.insert("", "end", values=(r.idAsignacion, r.cedula, r.Estudiante, r.nombreEvaluacion))

    # ---------------------------------------------------------
    # 4. MATRIZ MÉRITOS
    # ---------------------------------------------------------
    def _ui_matriz(self, frame):
        self.tree_matriz = ttk.Treeview(frame, columns=("Cedula", "Estudiante", "Carrera", "Puntaje", "Estado"), show="headings")
        for c in ("Cedula", "Estudiante", "Carrera", "Puntaje", "Estado"): 
            self.tree_matriz.heading(c, text=c)
        self.tree_matriz.pack(fill="both", expand=True)
        
        tk.Button(frame, text="Refrescar Matriz", command=self.recargar_matriz_final).pack(pady=10)

    def recargar_matriz_final(self):
        for i in self.tree_matriz.get_children(): self.tree_matriz.delete(i)
        for r in self.service.obtener_matriz():
            # Si el estado es reprobado, lo pintamos de rojo (opcional)
            self.tree_matriz.insert("", "end", values=(r.cedula, r.Estudiante, r.nombreCarrera, r.puntajeObtenido, r.estado))

    # ---------------------------------------------------------
    # 5. ESTADÍSTICAS
    # ---------------------------------------------------------
    def _ui_estadisticas(self, frame):
        tk.Label(frame, text="Indicadores de Rendimiento", font=("Arial", 16, "bold")).pack(pady=20)
        self.container_stats = tk.Frame(frame); self.container_stats.pack()
        tk.Button(frame, text="🔄 Actualizar Estadísticas", command=self.recargar_stats).pack(pady=20)

    def recargar_stats(self):
        stats = self.service.obtener_dashboard_stats()
        for w in self.container_stats.winfo_children(): w.destroy()
        
        def card(padre, titulo, valor, color):
            f = tk.Frame(padre, bg=color, width=200, height=120); f.pack_propagate(False); f.pack(side="left", padx=10, pady=10)
            tk.Label(f, text=titulo, bg=color, fg="white", font=("Arial", 10, "bold")).pack(pady=10)
            tk.Label(f, text=str(valor), bg=color, fg="white", font=("Arial", 26, "bold")).pack()
        
        r1 = tk.Frame(self.container_stats); r1.pack()
        card(r1, "Total Estudiantes", stats['estudiantes'], "#3498db")
        card(r1, "Carreras Activas", stats['carreras_activas'], "#9b59b6")
        r2 = tk.Frame(self.container_stats); r2.pack()
        card(r2, "Inscripciones Pend.", stats['pendientes'], "#f39c12")
        card(r2, "Aceptadas", stats['aceptadas'], "#27ae60")
        card(r2, "Evaluados", stats['evaluados'], "#e67e22")

    # --- MODALES (CÓDIGO EXISTENTE RESUMIDO) ---
    def modal_crear_periodo(self):
        top = tk.Toplevel(self); top.title("Nuevo Periodo"); top.geometry("300x250")
        tk.Label(top, text="Año:").pack(); e_anio = tk.Entry(top); e_anio.pack()
        tk.Label(top, text="Semestre:").pack(); cb_sem = ttk.Combobox(top, values=["1", "2"]); cb_sem.pack()
        tk.Label(top, text="Inicio:").pack(); e_fi = tk.Entry(top); e_fi.pack()
        tk.Label(top, text="Fin:").pack(); e_ff = tk.Entry(top); e_ff.pack()
        def guardar():
            if self.service.crear_periodo_semestral(e_anio.get(), cb_sem.get(), e_fi.get(), e_ff.get()):
                messagebox.showinfo("Ok", "Creado"); self.cargar_periodos(); top.destroy()
        tk.Button(top, text="Guardar", command=guardar).pack(pady=10)

    def modal_gestion_carreras(self):
        top = tk.Toplevel(self); top.title("Gestión Carreras"); top.geometry("600x400")
        tree = ttk.Treeview(top, columns=("ID", "Nombre", "Estado"), show="headings")
        tree.heading("ID", text="ID"); tree.heading("Nombre", text="Carrera"); tree.heading("Estado", text="Estado")
        tree.pack(fill="both", expand=True)
        def cargar():
            [tree.delete(i) for i in tree.get_children()]
            [tree.insert("", "end", values=(c.idCarrera, c.nombreCarrera, c.estado)) for c in self.service.obtener_todas_carreras_admin()]
        cargar()
        f = tk.Frame(top); f.pack()
        tk.Label(f, text="Nombre:").pack(side="left"); e = tk.Entry(f); e.pack(side="left")
        def acc(tipo):
            sel = tree.selection()
            if tipo=="ADD": self.service.crear_carrera(e.get())
            elif sel and tipo=="UPD": self.service.actualizar_carrera(tree.item(sel[0])['values'][0], e.get())
            elif sel and tipo=="TOG": self.service.toggle_estado_carrera(tree.item(sel[0])['values'][0])
            elif sel and tipo=="DEL": self.service.eliminar_carrera(tree.item(sel[0])['values'][0])
            cargar()
        tk.Button(f, text="Agregar", command=lambda: acc("ADD")).pack(side="left")
        tk.Button(f, text="Actualizar", command=lambda: acc("UPD")).pack(side="left")
        tk.Button(f, text="Estado", command=lambda: acc("TOG")).pack(side="left")
        tk.Button(f, text="Eliminar", command=lambda: acc("DEL")).pack(side="left")