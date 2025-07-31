# app.py
import streamlit as st
from PIL import Image
from google.cloud import vision
from google.oauth2 import service_account
import pandas as pd
import re

st.set_page_config(page_title="Buscador de Imagens", layout="wide")
st.title("📦 Buscador de Imagens (OCR com Google Cloud Vision API)")

st.markdown("""
Este app permite:
- Fazer upload de várias imagens;
- Ler nomes de medicamentos usando a Google Cloud Vision API;
- Buscar por uma palavra ou termo específico;
- Baixar os resultados em CSV.

## ✅ Passo a passo para criar conta e configurar Google Cloud Vision API:
1️⃣ Crie uma conta no [Google Cloud Platform](https://console.cloud.google.com/);
2️⃣ Crie um novo projeto;
3️⃣ Vá até **APIs & Services > Library** e ative a **Cloud Vision API**;
4️⃣ Em **APIs & Services > Credentials**, clique em **Create Credentials > Service Account**;
5️⃣ Dê um nome, prossiga e, na aba final, selecione "Owner" (ou outra permissão adequada);
6️⃣ Depois de criar, clique na conta de serviço criada, vá em **Keys > Add Key > Create new key**;
7️⃣ Selecione **JSON** e baixe o arquivo (guarde com segurança);
8️⃣ Copie o conteúdo desse arquivo e cole como dicionário no seu código Python.

⚠️ **Observação importante:** guardar a chave dentro do código não é seguro para produção. Use apenas para testes.
""")

# Cole aqui o conteúdo JSON da sua chave, exemplo:
service_account_info = {
  "type": "service_account",
  "project_id": "dulcet-pilot-467615-k8",
  "private_key_id": "451f638fe9c34e442cec3ef3d93a25e8984e5add",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDVgu/M9B6eKsn/\n7+80aXQnihCWcCGNV3hkxjhM7Ps5ZyM95zGleCQ0w4a4XbK9hd01Bs7AXOyYOnP8\naQ5+gn4dg2WSUpdHtio3aPEMpyizAEI1ORXGQ7jOBvgPvqEoTCTPEwUiIhvvbB9a\nQCvHDmVc8AW5ibeO+Hn29RHCqousccU8zvRIvhwoz5Ic8/MVnJEmUotoia3JM2D9\nLZIvsydTpyf1V3m7JuXv2T9K7Umc39+U94BfgrFbOZ13GML7l68ncelMIcpcAuAJ\nvufDGlWI10w8yloDQBeGHKynKAxAkMaTCJzXBfNSUY4G0iho74QVPSYIswY5O9Pp\nQgHyM9TtAgMBAAECggEACTggqPhniWEunLsHA1EvCfVdDFSQ1lIPFEbiL8wnIuOQ\nXYAUoDZPqz7qxnOL9WwI0QfXY0NVQf4le6IrqoxxlqOm/fT2rErc3XdOD+5N2cDV\nRbK5J85NILRN/3FgnbqqojhfhzRILC6T11P1r/WFV0h+mXQtYA0xnazCVLtZfEYk\nayM6atK4WsurzZlgixxpD6WHB3lhjumsc0/Ebz98laJp9wgLVXJWmKgTa9H1oMZk\nIWVLqp91O640wz5SCrwgE1SA2r9LFzoJjgjXiHA5HS8D2VXD09ESpCqTN1ZQrDmC\n1Drcbv6zdHmvAUO8RTBJqEF2Lo5nGBIgkCfqrYwUsQKBgQD+mFyQGf+8GNR8SZ+B\nmcSKsHYmrIHg3wV4OHYlOUHE7Yny8I6r3WDKmFX2EkJNkbfckB/9NbdkMAgIvcVv\nz0JwS3eoXelvGx5V+UuJMXJ2vRu0LpOI8OqOkB0AOuYLKxeN4M8chu5xYuUWJinT\nYYAhEDEOY1tBzAvJiRSQtDjI+QKBgQDWsIpvVdO5Ucqh6nE+T93691plGKETKgbD\n9zipjrt1v1PWurFmrVRb0ECm2L2rkbDNjvkZattuqIXeeOg4EvFIvTKFY8Akvyef\nojLYzoAPo98VVSDN0pSjT0xHEKyw/SbshKiP3uiH3/jLvjbH3aKaj6S6HmwT/htu\nwDUlmhC8lQKBgC+Xlb4OTiMAVUBClwGoF/iBEiUanFDIAALAMz20HVpNuTrjwxfX\nk09r+K2+LgzID6G4g3JXB0hAPlA8AVtsWBQb12tu2sM9Q4d4yakEyEvv/+zHxCaW\nOpKZ2AICAJzX2lhYTP8dLheeEAr66VitYkFMAI+a/SUomo97A5AlUHQpAoGAFJNc\n4Si/nu441mXKrqcm5iuYrUG8BkMr3NIvywhT7QgGN/kykV2hTR9bYuI4412WLU07\nkHUOTL+3/MdnsiAWodsIIYKa4qqzWHhKGT9JRLZ25et/tlotRq2N6O2vL1NDzL02\nDnvVm1ga1yQGygby049awT+zKgNbi7S+IzltyzUCgYEA1Vq4r+71VycZrcyMOCjn\nyvbMA0RjDSuUYYw4U313bTNMBMItPETwBZ9RxzQwqOAouIdEwoUCmWa7JJolDhh6\n7wNyxGOoOH4El9yTj/knhtoe+mZ0k0wTF7jRdjW/yZuHPJ/HP3501SxWyELVWF5j\nCDFom3E9ojz7PPbJ7u2/RaU=\n-----END PRIVATE KEY-----\n",
  "client_email": "buscadorocr@dulcet-pilot-467615-k8.iam.gserviceaccount.com",
  "client_id": "103067743247926721037",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/buscadorocr%40dulcet-pilot-467615-k8.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

credentials = service_account.Credentials.from_service_account_info(service_account_info)
client = vision.ImageAnnotatorClient(credentials=credentials)

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
            try:
                content = uploaded_file.read()
                image_vision = vision.Image(content=content)
                response = client.text_detection(image=image_vision)
                texto_completo = response.text_annotations[0].description if response.text_annotations else ""
                texto_limpo = re.sub(r'[^A-Za-zÁÉÍÓÚÇÑáéíóúçñ\s]', '', texto_completo)
                nomes_possiveis = re.findall(r'\b[A-ZÁÉÍÓÚÇÑ]{3,}\b', texto_limpo.upper())
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

    st.subheader("Nomes de medicamentos extraídos de cada imagem (Google Vision)")
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
    st.markdown("App feito com ❤️ usando Streamlit e Google Cloud Vision API.")
else:
    st.info("Por favor, faça upload de pelo menos uma imagem para começar.")
