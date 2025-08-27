import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import re
# ===== CSS PARA ESTILO =====
st.markdown(
    """
    <style>
    /* Fondo rosa de la app */
    .stApp {
        background-color: #ffe6f2;
    }

    /* Forzar todos los textos en negro */
    body, .stApp, h1, h2, h3, h4, h5, h6, p, div, span, a {
        color: black !important;
    }

    /* Estilo y tamaño del título */
    .streamlit-expanderHeader, .reportview-container .main .block-container h1 {
        color: black !important;
    }

    /* Botón grande (aplica a botones de Streamlit) */
    div.stButton > button {
        background-color: #ff66b2;
        color: white;
        font-size: 28px;
        padding: 12px 36px;
        border-radius: 14px;
        border: none;
        cursor: pointer;
        transition: transform 0.15s ease-in-out, background-color 0.15s ease-in-out;
    }
    div.stButton > button:hover {
        transform: scale(1.05);
        background-color: #cc0066;
    }

    /* Animación heartbeat para el texto */
    @keyframes heartbeat {
        0% { transform: scale(1); }
        25% { transform: scale(1.18); }
        50% { transform: scale(1); }
        75% { transform: scale(1.12); }
        100% { transform: scale(1); }
    }
    .heartbeat {
        animation: heartbeat 1s ease-in-out infinite;
        font-size: 22px;
        font-weight: 700;
        text-align: center;
        color: black !important; /* texto animado también negro */
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ===== TITULO =====
st.title("😼 App para vaguitas 😼")

# ===== Estado toggle en session_state =====
if "heart_on" not in st.session_state:
    st.session_state.heart_on = False

# ===== Botón centrado (usamos columnas para centrar de forma robusta) =====
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Cuando se hace click, toggleeamos el estado
    if st.button("💖", key="heart_button"):
        st.session_state.heart_on = not st.session_state.heart_on

# ===== Texto animado o mensaje alternativo =====
if st.session_state.heart_on:
    st.markdown("<p class='heartbeat'>yo tambien te amo 😻</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align:center; font-size:18px;'>😿</p>", unsafe_allow_html=True)

# ===== IMAGEN REDUCIDA (centrada) =====
img_url = "https://2.bp.blogspot.com/-H-mgyhPyol8/TfJsfL9qusI/AAAAAAAAADM/gbZ3hRKdxnw/s1600/gato+bebiendo+vino.jpg"
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(img_url, caption="Ponete a laburar loco", width=280)

# ===== GIF (centrado) =====
gif_url = "https://gifdb.com/images/high/working-cat-doing-fast-typing-or3mww33tjy9zu5y.gif"
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(gif_url, caption="Modo vago activado 🐱💻", width=320)
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






