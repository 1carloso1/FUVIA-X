import base64
import os
import tempfile
from fpdf import FPDF
from typing import Optional
from constants import TRADUCCIONES_MATERIALES
from schemas import ReporteRequest

class ReportePDF(FPDF):
    def header(self):
        # 1. BARRA SUPERIOR DORADA
        self.set_fill_color(212, 175, 55)
        self.rect(0, 0, self.w, 1.5, style="F")

        # 2. LOGOS Y DIVISOR
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        ruta_public = os.path.join(BASE_DIR, "..", "frontend", "public")
        logo_uni = os.path.join(ruta_public, "logo-universidad.png")
        logo_lab = os.path.join(ruta_public, "logo-laboratorio.png")
        
        try:
            if os.path.exists(logo_uni):
                self.image(logo_uni, x=15, y=7, h=14)
            if os.path.exists(logo_lab):
                self.image(logo_lab, x=48, y=7, h=14)
            if os.path.exists(logo_uni) and os.path.exists(logo_lab):
                self.set_draw_color(226, 232, 240)
                self.line(43, 9, 43, 19)
        except Exception: pass

# 3. TÍTULO Y STATUS
        self.set_y(9)
        self.set_font("helvetica", "B", 18)
        self.set_text_color(10, 46, 92) # Corresponde a #0a2e5c
        
        # TRUCO DE TRACKING: Usamos espacios dobles entre letras para simular el tracking-[0.4em]
        self.cell(0, 6, "F  U  V  I  A", align="R", ln=True)
        
        self.set_font("helvetica", "B", 8)
        self.set_text_color(100, 116, 139) # Corresponde a text-slate-500
        
        # TRUCO UPPERCASE: Escribimos el texto directamente en mayúsculas
        self.cell(0, 5, "EVALUACIÓN PREDICTIVA DE DISEÑOS DE MEZCLA", align="R")

        # 4. BARRA AZUL MARINO
        self.set_fill_color(0, 53, 122)
        self.rect(0, 26, self.w, 1.5, style="F")
        self.set_y(35)

    def footer(self):
        self.set_draw_color(226, 232, 240)
        self.line(15, self.h - 15, self.w - 15, self.h - 15)
        self.set_y(-12)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(148, 163, 184)
        v = self.version_software if hasattr(self, 'version_software') else "0.0.0"
        self.cell(0, 10, f"FUVIA v.{v}  |  LIAI  |  Página {self.page_no()}", align="C")

    def create_section_header(self, title):
        self.set_fill_color(248, 250, 252)
        self.set_text_color(30, 41, 59)
        self.set_font("helvetica", "B", 10)
        self.cell(0, 8, f"  {title.upper()}", ln=True, fill=True)
        self.ln(2)

def generar_pdf_bytes(datos: ReporteRequest, is_valid: bool, error_abs: Optional[float], error_rel: Optional[float]) -> bytes:
    pdf = ReportePDF()
    pdf.version_software = getattr(datos, 'version', '0.0.0')
    pdf.add_page()
    
    # ==========================================
    # --- 1. PARÁMETROS DE DISEÑO DE MEZCLA ---
    # ==========================================
    pdf.create_section_header("1. Parámetros de Diseño de Mezcla")
    
    pdf.set_font("helvetica", "B", 9)
    pdf.set_fill_color(241, 245, 249)
    pdf.cell(90, 8, " Componente", border=1, fill=True)
    pdf.cell(50, 8, " Cantidad", border=1, fill=True, align="C")
    pdf.cell(40, 8, " Unidad", border=1, fill=True, align="C", ln=True)
    
    pdf.set_font("helvetica", "", 9)

    peso_total = 0
    inputs_dict = datos.inputs.model_dump()
    for material, cantidad in inputs_dict.items():
        traduccion = TRADUCCIONES_MATERIALES.get(material, {"nombre": material.capitalize(), "unidad": "N/A"})
        nombre = traduccion["nombre"]
        unidad = traduccion["unidad"]

        pdf.cell(90, 7, f" {nombre}", border=1)
        pdf.cell(50, 7, f" {cantidad:,.2f}", border=1, align="C")
        pdf.cell(40, 7, f" {unidad}", border=1, align="C", ln=True)

        # Sumamos solo si la unidad es kg/m³ (ignoramos 'age' que son días)
        if material.lower() != "age":
            peso_total += float(cantidad)
    
    # --- FILA DE PESO TOTAL ---
    pdf.set_font("helvetica", "B", 9)
    # Fondo gris sutil para que destaque como en tu frontend (bg-slate-50)
    pdf.set_fill_color(248, 250, 252) 
    pdf.cell(90, 8, "Densidad Total", border=1, fill=True)
    pdf.cell(50, 8, f" {peso_total:,.2f}", border=1, align="C", fill=True)
    pdf.cell(40, 8, " kg/m³", border=1, align="C", fill=True, ln=True)
    
    pdf.ln(8)

    # ==================================================
    # --- 2. RESULTADOS DEL SISTEMA DE INFERENCIA ---
    # ==================================================
    pdf.create_section_header("2. Resultados del Sistema de Inferencia")
    
    pdf.set_font("helvetica", "B", 9)
    pdf.set_fill_color(241, 245, 249)
    pdf.cell(90, 8, " Parámetro Analizado", border=1, fill=True)
    pdf.cell(90, 8, " Resultado Obtenido", border=1, fill=True, align="C", ln=True)
    
    pdf.set_font("helvetica", "", 9)
    metrics = [
        ("Resistencia Real (Laboratorio)", f"{datos.resistencia_real} MPa" if is_valid else "No registrada"),
        ("Resistencia Inferida (IA)", f"{datos.prediccion.resistencia_estimada} MPa"),
        ("Relación Agua/Cemento", f"{datos.prediccion.relacion_agua_cemento} ({datos.prediccion.clase_ac})"),
        ("Relación Grava/Arena", f"{datos.prediccion.relacion_grava_arena} ({datos.prediccion.clase_ga})")
    ]
    
    for label, val in metrics:
        pdf.cell(90, 7, f" {label}", border=1)
        pdf.cell(90, 7, f" {val}", border=1, align="C", ln=True)

    pdf.ln(8)

    # ===================================
    # --- 3. CÁLCULO DE LOS ERRORES ---
    # ===================================
    pdf.create_section_header("3. Cálculo de los Errores")

    if is_valid and error_abs is not None and error_rel is not None:
        str_error_abs = f" {error_abs:.3f} MPa"
        str_error_rel = f" {error_rel:.3f} %"
    else:
        str_error_abs = " N/A"
        str_error_rel = " N/A"
    
    pdf.set_font("helvetica", "B", 9)
    pdf.set_fill_color(241, 245, 249)
    pdf.cell(60, 8, " Métrica de Desviación", border=1, fill=True)
    pdf.cell(60, 8, " Valor Calculado", border=1, fill=True, align="C")
    pdf.cell(60, 8, " Meta del Sistema", border=1, fill=True, align="C", ln=True)
    
    pdf.set_font("helvetica", "", 9)
    
    # Fila de Error Absoluto
    pdf.cell(60, 7, " Error Absoluto", border=1)
    pdf.cell(60, 7, str_error_abs, border=1, align="C")
    pdf.cell(60, 7, " < 10.00 MPa", border=1, align="C", ln=True)
    
    # Fila de Error Relativo
    pdf.cell(60, 7, " Error Relativo", border=1)
    pdf.cell(60, 7, str_error_rel, border=1, align="C")
    pdf.cell(60, 7, " N/A", border=1, align="C", ln=True)
    
    # =========================================================
    # --- CONCLUSIÓN Y DICTAMEN TÉCNICO (Sin uso de colores) ---
    # =========================================================
    pdf.ln(4)
    
    # Título del dictamen en negritas
    pdf.set_font("helvetica", "B", 9)
    pdf.cell(0, 6, "Dictamen de Confiabilidad Predictiva:", ln=True)
    
    # Texto del dictamen en fuente normal justificada
    pdf.set_font("helvetica", "", 9)
    
# 1. EVALUAMOS PRIMERO SI EXISTEN DATOS DE LABORATORIO
    if is_valid and error_abs is not None:
        
        # 2. Si hay datos, evaluamos si el error es aceptable (< 10 MPa)
        if error_abs < 10:
            texto_conclusion = (
                f"El sistema de inferencia demuestra un alto nivel de precisión. El error absoluto "
                f"registrado de **{error_abs:.3f} MPa** se encuentra estrictamente dentro del margen de "
                f"tolerancia admisible (< 10.00 MPa). Este resultado certifica la confiabilidad algorítmica "
                f"del modelo para estimar el comportamiento mecánico de esta dosificación específica, "
                f"validando su uso como herramienta de soporte técnico."
            )
        # 3. Si hay datos, pero el error es muy alto (>= 10 MPa)
        else:
            texto_conclusion = (
                f"Se ha detectado una divergencia técnica significativa en la predicción. El error absoluto "
                f"calculado de **{error_abs:.3f} MPa** excede el umbral máximo de tolerancia establecido "
                f"(< 10.00 MPa) para este proyecto. Se determina que la estimación de la IA no es "
                f"suficientemente precisa en este caso, por lo que se recomienda una validación tradicional "
                f"de laboratorio o una futura recalibración del modelo base."
            )
            
    # 4. EL CAMINO DE "OMITIR": No hay datos de laboratorio
    else:
        texto_conclusion = (
            "Dado que no se proporcionó un valor empírico de resistencia real en laboratorio, "
            "el sistema ha omitido la validación cruzada algorítmica. Los resultados aquí presentados representan "
            "una estimación teórica fundamentada exclusivamente en el modelo de Inteligencia Artificial. "
            "Se recomienda encarecidamente someter esta dosificación a pruebas físicas de compresión "
            "para certificar normativamente su viabilidad estructural en obra."
        )

    # Imprimimos el párrafo (multi_cell hace el salto de línea automático)
    # align="J" es para justificar el texto como en un documento formal de Word
    pdf.multi_cell(0, 5, texto_conclusion, align="J", markdown=True)

    # ===============================
    # --- 4. EVIDENCIA GRÁFICA ---
    # ===============================
    if pdf.get_y() > 180:
        pdf.add_page()
    
    pdf.create_section_header("4. Evidencia Gráfica e Inferencial")
    
    if datos.graficas_base64:
        base64_data = datos.graficas_base64.split("base64,")[1] if "base64," in datos.graficas_base64 else datos.graficas_base64
        imagen_bytes = base64.b64decode(base64_data)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_img:
            temp_img.write(imagen_bytes)
            temp_img_path = temp_img.name
            
        try:
            pdf.image(temp_img_path, x=20, w=170)
        finally:
            os.remove(temp_img_path)

    return bytes(pdf.output())