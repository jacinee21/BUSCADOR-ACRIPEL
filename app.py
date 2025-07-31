# app.py
import streamlit as st
from PIL import Image
import easyocr
import pandas as pd
import re

st.set_page_config(page_title="Buscador de Imagens", layout="wide")
st.title("📦 Buscador de Imagens (OCR mais preciso)")

st.markdown("""
Este app permite:
- Fazer upload de várias imagens;
- Ler nomes de medicamentos (OCR) de forma mais precisa;
- Buscar por uma palavra ou termo específico;
- Baixar os resultados em CSV.
""")

# Inicializar leitor do easyocr (suporta português)
reader = easyocr.Reader(['pt'])

# Lista de palavras comuns a ignorar
palavras_ignorar = {'COMPRIMIDOS', 'CAPSULAS', 'MG', 'ML', 'USO', 'ADULTO', 'INFANTIL', 'SOLUCAO', 'XAROPE'}

uploaded_files = st.file_uploader(
    "Faça upload das imagens (pode selecionar várias)",
    type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"{len(uploaded_files)} imagens carregadas.")

    dados = []
    with st.spinner("Processando imagens e filtrando nomes de medicamentos..."):
        for uploaded_file in uploaded_files:
            image = Image.open(uploaded_file)
            try:
                # Realizar OCR usando easyocr
                resultados = reader.readtext(image, detail=0, paragraph=True)
                texto_completo = ' '.join(resultados)
                # Limpeza: remover caracteres especiais e números
                texto_limpo = re.sub(r'[^A-Za-zÁÉÍÓÚÇÑáéíóúçñ\s]', '', texto_completo)
                # Extrair palavras em maiúsculo (3+ letras)
                nomes_possiveis = re.findall(r'\b[A-ZÁÉÍÓÚÇÑ]{3,}\b', texto_limpo.upper())
                # Remover palavras da lista de ignorar
                nomes_filtrados = [nome for nome in nomes_possiveis if nome not in palavras_ignorar]
                nomes_unicos = list(dict.fromkeys(nomes_filtrados))
                texto_final = ', '.join(nomes_unicos)
            except Exception as e:
                st.error(f"❗ Erro ao processar OCR: {e}")
                texto_final = "[Erro ao processar OCR]"
            dados.append({
                'Nome da Imagem': uploaded_file.name,
                'Nomes de Medicamentos Detectados': texto_final
            })

    df = pd.DataFrame(dados)

    st.subheader("Nomes de medicamentos extraídos de cada imagem (OCR mais preciso)")
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
    st.markdown("App feito com ❤️ usando Streamlit e easyocr.")
else:
    st.info("Por favor, faça upload de pelo menos uma imagem para começar.")

# requirements.txt
# streamlit
# easyocr
# pillow
# pandas
