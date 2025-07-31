# app.py
import streamlit as st
from PIL import Image
import pytesseract
import pandas as pd

st.set_page_config(page_title="Buscador de Imagens", layout="wide")
st.title("📦 Buscador de Imagens (OCR)")

st.markdown("""
Este app permite:
- Fazer upload de várias imagens;
- Ler o texto de cada imagem (OCR);
- Buscar por uma palavra ou termo específico;
- Baixar os resultados em CSV.
""")

uploaded_files = st.file_uploader(
    "Faça upload das imagens (pode selecionar várias)",
    type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"{len(uploaded_files)} imagens carregadas.")

    dados = []
    with st.spinner("Lendo o texto das imagens... Pode levar um tempo se forem muitas imagens."):
        for uploaded_file in uploaded_files:
            image = Image.open(uploaded_file)
            texto = pytesseract.image_to_string(image, lang='por')
            dados.append({
                'Nome da Imagem': uploaded_file.name,
                'Texto Extraído': texto
            })

    df = pd.DataFrame(dados)

    st.subheader("Texto extraído de cada imagem")
    st.dataframe(df)

    termo = st.text_input("🔍 Digite uma palavra ou termo para buscar nas imagens:")

    if termo:
        termo_lower = termo.lower()
        resultado = df[df['Texto Extraído'].str.lower().str.contains(termo_lower)]

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
