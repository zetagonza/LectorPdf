import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import re
from PyPDF2 import PdfMerger
merger = PdfMerger()
import io

# =====================================================
# 📌 SECCIÓN UNIR PDFS
# =====================================================
st.title("Unir varios PDFs en uno solo")

uploaded_files = st.file_uploader(
    "Unir PDF's",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("Unir PDFs"):
        merger = PdfMerger()

        for uploaded_file in uploaded_files:
            merger.append(uploaded_file)

        # Guardar en buffer
        merged_pdf = io.BytesIO()
        merger.write(merged_pdf)
        merger.close()
        merged_pdf.seek(0)

        st.success("✅ PDFs unidos correctamente")
        st.download_button(
            label="📥 Descargar PDF unido",
            data=merged_pdf,
            file_name="pdf_unido.pdf",
            mime="application/pdf"
        )

# =====================================================
# 📌 SECCIÓN EXTRACCIÓN CUIT (con filtro > 99.999,00)
# =====================================================
st.title("Extracción de CUIT, Jurisdicción y saldos mayores a $99.999,00")

# Subir PDF
uploaded_file_2 = st.file_uploader("Poner aca el PDF para filtrar saldos altos", type=["pdf"])

if uploaded_file_2 is not None:
    # Leer PDF con PyMuPDF
    doc = fitz.open(stream=uploaded_file_2.read(), filetype="pdf")

    # Extraer texto crudo
    lines = []
    for i, page in enumerate(doc):
        text = page.get_text()
        lines.append(f"--- Página {i+1} ---")
        lines.extend(text.splitlines())

    # Limpiar líneas vacías
    lines = [line.strip() for line in lines if line.strip()]

    # Procesar bloques
    rows = []
    i = 0
    cuit = None

    while i < len(lines):
        line = lines[i]

        if line.startswith("--- Página"):
            cuit = None
            i += 1
            continue

        if not cuit:
            cuit_match = re.match(r'\d{2}-\d{8}-\d', line)
            if cuit_match:
                cuit = cuit_match.group()
                i += 1
                continue

        if re.match(r'^\d{3}$', line):
            codigo = line
            valores = []
            j = i + 1
            while j < len(lines) and len(valores) < 6:
                if lines[j].startswith("$"):
                    valores.append(lines[j])
                j += 1

            provincia = lines[j] if j < len(lines) else ""

            if len(valores) >= 4:
                valor_4 = valores[3]
                rows.append([cuit, provincia, valor_4])

            i = j + 1
            continue

        i += 1

    # Crear DataFrame
    df_altos = pd.DataFrame(rows, columns=["CUIT", "Jurisdiccion", "A favor Contribuyente"])

    # Quitar guiones del CUIT
    df_altos["CUIT"] = df_altos["CUIT"].str.replace("-", "", regex=False)

    # 🔹 Convertir a número y filtrar mayores a 99.999,00
    df_altos["Monto_num"] = df_altos["A favor Contribuyente"].str.replace("$", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float)
    df_altos = df_altos[df_altos["Monto_num"] > 99999]

    # Eliminar la columna auxiliar
    df_altos = df_altos.drop(columns=["Monto_num"])

    st.subheader("Datos extraídos (solo saldos > $99.999,00)")
    st.dataframe(df_altos)

    # Botón para descargar CSV
    csv_altos = df_altos.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        label="Descargar CSV (saldos altos)",
        data=csv_altos,
        file_name="resultado_saldos_altos.csv",
        mime="text/csv"
    )









