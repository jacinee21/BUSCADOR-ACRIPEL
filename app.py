# app.py
import streamlit as st
from PIL import Image
import pytesseract
import pandas as pd
import re
import os

st.set_page_config(page_title="Buscador de Imagens", layout="wide")
st.title("📦 Buscador de Imagens (OCR)")

st.markdown("""
Este app permite:
- Fazer upload de várias imagens;
- Ler apenas nomes de medicamentos (OCR);
- Buscar por uma palavra ou termo específico;
- Baixar os resultados em CSV.
""")

os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract-ocr/4.00/tessdata/'

uploaded_files = st.file_uploader(
    "Faça upload das imagens (pode selecionar várias)",
    type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"{len(uploaded_files)} imagens carregadas.")

    dados = []
    with st.spinner("Lendo os nomes de medicamentos nas imagens... Pode levar um tempo."):
        for uploaded_file in uploaded_files:
            image = Image.open(uploaded_file)
            try:
                texto_completo = pytesseract.image_to_string(image, lang='por')
                # Extrair apenas possíveis nomes de medicamentos (exemplo: palavras em maiúsculo com 3+ letras)
                nomes_medicamentos = re.findall(r'\b[A-ZÁÉÍÓÚÇÑ]{3,}\b', texto_completo)
                texto_filtrado = ', '.join(nomes_medicamentos)
            except Exception as e:
                st.error(f"❗ Erro ao processar OCR: {e}")
                texto_filtrado = "[Erro ao processar OCR]"
            dados.append({
                'Nome da Imagem': uploaded_file.name,
                'Nomes de Medicamentos Detectados': texto_filtrado
            })

    df = pd.DataFrame(dados)

    st.subheader("Nomes de medicamentos extraídos de cada imagem")
    st.dataframe(df)

    termo = st.text_input("🔍 Digite um nome ou termo para buscar nas imagens:")

    if termo:
        termo_upper = termo.upper()
        resultado = df[df['Nomes de Medicamentos Detectados'].str.upper().str.contains(termo_upper)]

        st.subheader(f"Resultados contendo: '{termo}'")
        st.dataframe(resultado)

        csv = resultado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar resultados como CSV",
            data=csv,
            file_name='resultados_busca.csv',
            mime='text/csv'
        )

    st.markdown("---")
    st.markdown("App feito com ❤️ usando Streamlit e pytesseract.")
else:
    st.info("Por favor, faça upload de pelo menos uma imagem para começar.")

# requirements.txt
# streamlit
# pytesseract
# pillow
# pandas

# packages.txt
# tesseract-ocr
# tesseract-ocr-por
