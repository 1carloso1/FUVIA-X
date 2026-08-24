import base64
import os
import tempfile
from fpdf import FPDF
from typing import Optional
from constants import TRADUCCIONES_MATERIALES
from schemas import ReporteRequest

class ReportePDF(FPDF):
    def header(self):
        self.set_fill_color(212, 175, 55)
        self.rect(0, 0, self.w, 1.5, style="F")

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
        except Exception:
            pass

        self.set_y(9)
        self.set_font("helvetica", "B", 18)
        self.set_text_color(10, 46, 92)
        self.cell(0, 6, "F  U  V  I  A", align="R", ln=True)

        self.set_font("helvetica", "B", 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 5, "PREDICTIVE EVALUATION OF MIX DESIGNS", align="R")

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
        self.cell(0, 10, f"FUVIA v.{v}  |  LIAI  |  Page {self.page_no()}", align="C")

    def create_section_header(self, title):
        self.set_fill_color(248, 250, 252)
        self.set_text_color(30, 41, 59)
        self.set_font("helvetica", "B", 10)
        self.cell(0, 8, f"  {title.upper()}", ln=True, fill=True)
        self.ln(2)


def _limpiar_texto(texto: str) -> str:
    return texto.replace('—', '-').replace('-', '-').replace('"', '"').replace('"', '"')


def _insertar_imagen_base64(pdf: FPDF, base64_str: str, x: int = 20, w: int = 170) -> None:
    data = base64_str.split("base64,")[1] if "base64," in base64_str else base64_str
    imagen_bytes = base64.b64decode(data)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(imagen_bytes)
        tmp_path = tmp.name
    try:
        pdf.image(tmp_path, x=x, w=w)
    finally:
        os.remove(tmp_path)


def generar_pdf_bytes(
    datos:     ReporteRequest,
    is_valid:  bool,
    error_abs: Optional[float],
    error_rel: Optional[float]
) -> bytes:
    pdf = ReportePDF()
    pdf.version_software = getattr(datos, 'version', '0.0.0')
    pdf.add_page()

    # ==========================================
    # --- 1. MIX DESIGN PARAMETERS ---
    # ==========================================
    pdf.create_section_header("1. Mix Design Parameters")

    pdf.set_font("helvetica", "B", 9)
    pdf.set_fill_color(241, 245, 249)
    pdf.cell(90, 8, " Component", border=1, fill=True)
    pdf.cell(50, 8, " Quantity",  border=1, fill=True, align="C")
    pdf.cell(40, 8, " Unit",      border=1, fill=True, align="C", ln=True)

    pdf.set_font("helvetica", "", 9)
    peso_total  = 0
    inputs_dict = datos.inputs.model_dump()

    for material, cantidad in inputs_dict.items():
        traduccion = TRADUCCIONES_MATERIALES.get(material, {"nombre": material.capitalize(), "unidad": "N/A"})
        pdf.cell(90, 7, f" {traduccion['nombre']}", border=1)
        pdf.cell(50, 7, f" {cantidad:,.2f}",         border=1, align="C")
        pdf.cell(40, 7, f" {traduccion['unidad']}",  border=1, align="C", ln=True)
        if material.lower() != "age":
            peso_total += float(cantidad)

    pdf.set_font("helvetica", "B", 9)
    pdf.set_fill_color(248, 250, 252)
    pdf.cell(90, 8, "Total Density",       border=1, fill=True)
    pdf.cell(50, 8, f" {peso_total:,.2f}", border=1, align="C", fill=True)
    pdf.cell(40, 8, " kg/m3",              border=1, align="C", fill=True, ln=True)
    pdf.ln(8)

    # ==================================================
    # --- 2. INFERENCE SYSTEM RESULTS ---
    # ==================================================
    pdf.create_section_header("2. Inference System Results")

    pdf.set_font("helvetica", "B", 9)
    pdf.set_fill_color(241, 245, 249)
    pdf.cell(90, 8, " Analyzed Parameter", border=1, fill=True)
    pdf.cell(90, 8, " Obtained Result",    border=1, fill=True, align="C", ln=True)

    pdf.set_font("helvetica", "", 9)
    metrics = [
        ("Real Strength (Laboratory)", f"{datos.resistencia_real} MPa" if is_valid else "Not recorded"),
        ("Inferred Strength (AI)",     f"{datos.prediccion.resistencia_estimada} MPa"),
        ("Water/Cement Ratio",         f"{datos.prediccion.relacion_agua_cemento} ({datos.prediccion.clase_ac})"),
        ("Coarse/Fine Aggregate Ratio",f"{datos.prediccion.relacion_grava_arena} ({datos.prediccion.clase_ga})")
    ]
    for label, val in metrics:
        pdf.cell(90, 7, f" {label}", border=1)
        pdf.cell(90, 7, f" {val}",   border=1, align="C", ln=True)
    pdf.ln(8)

    # ===================================
    # --- 3. ERROR CALCULATION ---
    # ===================================
    pdf.create_section_header("3. Error Calculation")

    str_error_abs = f" {error_abs:.3f} MPa" if (is_valid and error_abs is not None) else " N/A"
    str_error_rel = f" {error_rel:.3f} %"   if (is_valid and error_rel is not None) else " N/A"

    pdf.set_font("helvetica", "B", 9)
    pdf.set_fill_color(241, 245, 249)
    pdf.cell(60, 8, " Deviation Metric", border=1, fill=True)
    pdf.cell(60, 8, " Calculated Value", border=1, fill=True, align="C")
    pdf.cell(60, 8, " System Target",    border=1, fill=True, align="C", ln=True)

    pdf.set_font("helvetica", "", 9)
    pdf.cell(60, 7, " Absolute Error", border=1)
    pdf.cell(60, 7, str_error_abs,      border=1, align="C")
    pdf.cell(60, 7, " < 10.00 MPa",    border=1, align="C", ln=True)

    pdf.cell(60, 7, " Relative Error", border=1)
    pdf.cell(60, 7, str_error_rel,      border=1, align="C")
    pdf.cell(60, 7, " N/A",             border=1, align="C", ln=True)

    pdf.ln(4)
    pdf.set_font("helvetica", "B", 9)
    pdf.cell(0, 6, "Predictive Reliability Assessment:", ln=True)
    pdf.set_font("helvetica", "", 9)

    if is_valid and error_abs is not None:
        if error_abs < 10:
            texto_conclusion = _limpiar_texto(
                f"The inference system demonstrates a high level of accuracy. The recorded absolute error "
                f"of **{error_abs:.3f} MPa** falls strictly within the admissible tolerance margin "
                f"(< 10.00 MPa). This result certifies the algorithmic reliability of the model for "
                f"estimating the mechanical behavior of this specific mix design, validating its use "
                f"as a technical support tool."
            )
        else:
            texto_conclusion = _limpiar_texto(
                f"A significant technical divergence has been detected in the prediction. The calculated "
                f"absolute error of **{error_abs:.3f} MPa** exceeds the maximum established tolerance "
                f"threshold (< 10.00 MPa). It is determined that the AI estimation is not sufficiently "
                f"accurate in this case; traditional laboratory validation or future model recalibration "
                f"is recommended."
            )
    else:
        texto_conclusion = _limpiar_texto(
            "Since no empirical compressive strength value from laboratory testing was provided, "
            "the system has omitted the algorithmic cross-validation. The results presented here represent "
            "a theoretical estimate based exclusively on the Artificial Intelligence model. "
            "It is strongly recommended to subject this mix design to physical compression tests "
            "to normatively certify its structural viability in construction."
        )

    pdf.multi_cell(0, 5, texto_conclusion, align="J", markdown=True)

    # ===============================
    # --- 4. GRAPHICAL AND INFERENTIAL EVIDENCE ---
    # ===============================
    if pdf.get_y() > 180:
        pdf.add_page()

    pdf.create_section_header("4. Graphical and Inferential Evidence")

    if datos.graficas_base64:
        _insertar_imagen_base64(pdf, datos.graficas_base64)

    # ===============================
    # --- 5. EXPLAINABILITY ANALYSIS (SHAP - XAI) ---
    # ===============================
    if datos.shap_graficas_base64:
        pdf.add_page()
        pdf.create_section_header("5. Explainability Analysis (SHAP - XAI)")

        pdf.set_font("helvetica", "", 9)
        pdf.set_text_color(100, 116, 139)
        pdf.multi_cell(
            0, 5,
            _limpiar_texto(
                "The SHAP (SHapley Additive exPlanations) analysis quantifies the individual contribution "
                "of each ingredient to the predicted compressive strength. Green bars indicate that the "
                "ingredient increases strength relative to the model base value; red bars indicate reduction. "
                "The sum of all contributions plus the base value equals the predicted compressive strength."
            ),
            align="J"
        )
        pdf.ln(4)
        pdf.set_text_color(30, 41, 59)
        _insertar_imagen_base64(pdf, datos.shap_graficas_base64)

    return bytes(pdf.output())