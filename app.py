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
  "private_key_id": "783549a255269c375f6aee9975e3201af16d5abc",
  "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCQpWBrEO236xOJ\\nK8VTmTyBX8Sd0Koik+VifadcFY3aMJKm0+zcirSREKhNRTBdsLexLf5tAdTinXKW\\nuaBT4Tfh8jqdsBRAXKgqJVq0JFpShkEZ7/dCtNS4ZTxKC/+251AKyWYEkzv+QHIm\\njnqVYN9GlWU4U9+Z82Yjajy0pqbW0/aDXG2r8Ktp4C9jMorLVMGb7JIgU00kn8Sr\\nQfLeWa9G+dJm0zT24YtJfX07IluYPwyt7dv1MRiKt6KLQqauDLkusNR1hg6Owm4b\\nsVDvgTPwcA1AA07+t8KpvWhzWndNzY9V3ad5FhWaX12jQYugiP7HFUeXPqha6X1n\\ng7mNv4tTAgMBAAECggEACbZZBYdi9tz9eFHsk4LwCZ3VFWWr7ttwZQ8b3DaESljF\\nmBcVye80VaNBMcMKDthtVSPJ+CbN1ROOXKmFJuyx9GVv4yOuEG5ISmAsuXjRacYi\\n++tddmiu+dyuUiiBGJZqjPbd90OtnRJVt9oMSBhzlYk1fTVAh9VMj+czwUuJW1ZR\\nWD8lpmKQfs4wbxiHkg2lUECDdozwTfVIMcKtwD3CENIBYZUdy3bdsotn0wkSTa3y\\nqAlow+nyEpTv3PyxKzwwDmggT//NlRXCkl/dawncH9ZbEJZlcSVh2EUSLdi9Vpnb\\nqqRmH3W0FQyae+8I01l8hP4VaJ8vP43lxJF8wcoc0QKBgQDDfOa49jp8ZX1ILFsK\\nC0ju2ZK5jh8fgfZAy/69yOgfgIhK6fz7tsDp/KnaY3Hye+K8+58l7A2AlQykzZve\\n0Autt0b+p0bv9OLxWoOlxdoJhdtGQJDmqutsznYbEyP7gMq1WNvsh3Le2depunLV\\n97QL+ffy1z70hqF/CwpA3Ctb0QKBgQC9a5kNqGf5W6rhjf2KMuaKbJxbWGIlJdec\\nL9ey6+B73+uKPvBDoUy/Hr72YrRvHgh2F9HDIqpqWUNp1bQm5pBuAn/t0yBl9Z/d\\nFb1fmUZpLQhvcox/VUq4t2scsB8HOht5IGcOWKWYu8crg/WsAlhnJyJ8PS+70H3J\\nc+7v90BR4wKBgBwD2kzHfLo3ES02rhVSaLFSHOTaqTsqtM+0bF1mXV2mXeHehpLM\\nLflabD0P41SMzIGozbXxjj3PHnC/xoa36fSLP3FfJ5tbzOopvpQTNpwGwtXeiuWD\\nuRluvR5EL/PrESHMCjhrcNre/Tklry9awEK3IAF9N1hzstEyE9YXt18BAoGBAKd8\\naEynR6g44ZOm1TRJZYeoGWi7cayfFVJJC1RtNITTrZUDqbZi/VVQflGlXR2TVK/2\\nx8be9Ags/WqrRyvOWo6rLyq+r7r3wG7gNh49jQCajQbeJlTAud0ycUdgg08Elh44\\nBGevAl1WS/myKJv7RueOtvNbtsU+yLpEBFWyLfE5AoGAVH0qofMrIvikfkRRax3N\\nPdMg8YxcnsOZigAnCZ99b33tbN8aoGI1n3cg/YnJygbmzF0OPDUEcg8lJyLHWhJO\\nHYy1RHcGAAW8tSo3fBMYIeSM0E+9wj1HJRLa7gId0gc0rUNZgGicvjR9TzgwMmNW\\ncLKxVnz60lUoot/ExEWC5pQ=\\n-----END PRIVATE KEY-----\\n",
  "client_email": "buscadorocracripel@dulcet-pilot-467615-k8.iam.gserviceaccount.com",
  "client_id": "114628444313258940435",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/buscadorocracripel%40dulcet-pilot-467615-k8.iam.gserviceaccount.com",
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
