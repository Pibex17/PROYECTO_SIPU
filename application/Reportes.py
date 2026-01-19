from fpdf import FPDF
import os
import random
from datetime import datetime

class GeneradorReportes:
    
    def generar_codigo_unico(self):
        caracteres = "0123456789AEIOU"
        return "".join(random.choices(caracteres, k=6))

    def generar_constancia_inscripcion(self, estudiante, inscripcion, carrera_nombre):
        try:
            pdf = FPDF()
            pdf.add_page()
            codigo = self.generar_codigo_unico()
            
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "SISTEMA DE ADMISION UNIVERSITARIA", ln=True, align="C")
            pdf.set_font("Arial", "I", 12)
            pdf.cell(0, 10, "Comprobante de Inscripcion", ln=True, align="C")
            pdf.line(10, 30, 200, 30)
            pdf.ln(20)

            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, f"Estudiante: {estudiante.nombres} {estudiante.apellidos}", ln=True)
            pdf.cell(0, 10, f"Cedula: {estudiante.cedula}", ln=True)
            pdf.ln(10)
            pdf.cell(0, 10, f"Carrera: {carrera_nombre}", ln=True)
            pdf.cell(0, 10, f"Fecha Inscripcion: {inscripcion.fechaInscripcion}", ln=True)
            pdf.cell(0, 10, f"Estado: {inscripcion.estado}", ln=True)
            pdf.cell(0, 10, f"Codigo Verificacion: {codigo}", ln=True)

            nombre_archivo = f"Inscripcion_{estudiante.cedula}_{codigo}.pdf"
            ruta = os.path.abspath(nombre_archivo)
            pdf.output(nombre_archivo)
            return True, ruta
        except Exception as e:
            return False, str(e)

    def generar_comprobante_evaluacion(self, estudiante, nombre_examen, puntaje, estado, fecha):
        try:
            pdf = FPDF()
            pdf.add_page()
            codigo = self.generar_codigo_unico()
            
            titulo = "RESULTADOS DE EVALUACION" if estado != "Pendiente" else "COMPROBANTE DE ASIGNACION DE EXAMEN"
            
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "SISTEMA DE ADMISION UNIVERSITARIA", ln=True, align="C")
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, titulo, ln=True, align="C")
            pdf.line(10, 30, 200, 30)
            pdf.ln(20)

            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Datos del Aspirante:", ln=True)
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, f"Nombre: {estudiante.nombres} {estudiante.apellidos}", ln=True)
            pdf.cell(0, 10, f"ID: {estudiante.cedula}", ln=True)
            pdf.ln(10)

            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Detalle de Evaluacion:", ln=True)
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, f"Examen: {nombre_examen}", ln=True)
            
            if estado == "Pendiente" or str(puntaje) == "Pendiente":
                pdf.ln(5)
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, "FECHA Y HORA ASIGNADA:", ln=True)
                pdf.set_font("Arial", "", 14)
                pdf.cell(0, 10, f"{fecha}", ln=True)
                pdf.ln(10)
                pdf.set_font("Arial", "I", 10)
                pdf.cell(0, 10, "Presentarse con este comprobante y su cedula original.", ln=True)
            else:
                pdf.cell(0, 10, f"Fecha de Evaluacion: {fecha}", ln=True)
                pdf.ln(10)
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, f"PUNTAJE OBTENIDO: {puntaje}", ln=True)
                color_estado = "APROBADO" if "Aprobado" in estado else "REPROBADO"
                pdf.cell(0, 10, f"ESTADO FINAL: {color_estado}", ln=True)

            pdf.ln(20)
            pdf.set_font("Arial", "I", 8)
            pdf.cell(0, 10, f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Cod: {codigo}", ln=True, align="C")

            nombre_archivo = f"Reporte_{estudiante.cedula}_{codigo}.pdf"
            ruta = os.path.abspath(nombre_archivo)
            pdf.output(nombre_archivo)
            return True, ruta
        except Exception as e:
            return False, str(e)