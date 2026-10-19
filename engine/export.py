from fpdf import FPDF

def export_analysis(question, code, result_text, explanation, fig=None):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(31, 78, 121)
    pdf.cell(0, 12, "Local AI Data Analyst Report", ln=True)
    pdf.ln(5)

    # Question
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Question", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, question)
    pdf.ln(4)

    # Explanation
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Explanation", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, explanation)
    pdf.ln(4)

    # Code
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Generated Code", ln=True)
    pdf.set_font("Courier", "", 9)
    pdf.multi_cell(0, 5, code[:1500])
    pdf.ln(4)

    # Result
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Result", ln=True)
    pdf.set_font("Courier", "", 9)
    pdf.multi_cell(0, 5, result_text[:1500])

    return bytes(pdf.output())