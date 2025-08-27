import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import re
# --- CSS personalizado ---
st.markdown("""
    <style>
    body {
        background-color: pink;
        color: black; /* todos los textos en negro */
    }
    .stButton button {
        display: block;
        margin: 0 auto; /* centrar el botón */
        background-color: white;
        color: black;
        font-weight: bold;
        border-radius: 12px;
        padding: 10px 20px;
    }
    .animated-text {
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        animation: fadeIn 2s infinite alternate;
        color: black;
    }
    @keyframes fadeIn {
        from { opacity: 0.2; }
        to { opacity: 1; }
    }
    </style>
""", unsafe_allow_html=True)

# --- Estado del botón ---
if "show_gif" not in st.session_state:
    st.session_state.show_gif = False

# --- Botón Toggle ---
if st.button("Mostrar / Ocultar GIF"):
    st.session_state.show_gif = not st.session_state.show_gif

# --- Texto animado ---
st.markdown('<p class="animated-text">Bienvenido a mi App 🎉</p>', unsafe_allow_html=True)

# --- Mostrar GIF si está activado ---
if st.session_state.show_gif:
    st.image("https://gifdb.com/images/high/working-cat-doing-fast-typing-or3mww33tjy9zu5y.gif",
             use_container_width=False, width=250)
st.title("Extracción de CUIT, Jurisdicción y nose que cosa")

# Subir PDF
uploaded_file = st.file_uploader("Poner aca el PDF", type=["pdf"])

if uploaded_file is not None:
    # Leer PDF con PyMuPDF
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")

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

        # Detectar inicio de página y resetear CUIT
        if line.startswith("--- Página"):
            cuit = None
            i += 1
            continue

        # Buscar CUIT
        if not cuit:
            cuit_match = re.match(r'\d{2}-\d{8}-\d', line)
            if cuit_match:
                cuit = cuit_match.group()
                i += 1
                continue

        # Buscar código de jurisdicción
        if re.match(r'^\d{3}$', line):
            codigo = line
            valores = []
            j = i + 1
            # Recorrer siguientes líneas hasta capturar 6 valores monetarios
            while j < len(lines) and len(valores) < 6:
                if lines[j].startswith("$"):
                    valores.append(lines[j])
                j += 1

            # La provincia es la línea siguiente al último valor
            provincia = lines[j] if j < len(lines) else ""

            # Tomar el 4º valor si hay al menos 4
            if len(valores) >= 4:
                valor_4 = valores[3]
                rows.append([cuit, provincia, valor_4])

            # Avanzar el índice al final del bloque
            i = j + 1
            continue

        i += 1

    # Crear DataFrame
    df = pd.DataFrame(rows, columns=["CUIT", "Jurisdiccion", "A favor Contribuyente"])

    # 🔹 Filtrar filas donde el 4º valor sea "$0,00"
    df = df[df["A favor Contribuyente"] != "$0,00"]

    st.subheader("Datos extraídos (sin valores $0,00)")
    st.dataframe(df)

    # Botón para descargar CSV
    csv = df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        label="Descargar CSV",
        data=csv,
        file_name="resultado.csv",
        mime="text/csv"
    )






