import streamlit as st
import google.generativeai as genai
import pandas as pd
from PIL import Image
import io

# Sayfa ayarları
st.set_page_config(page_title="Sihirli Tarayıcı", page_icon="✨")

st.title("Sihirli Liste Tarayıcı ✨")
st.write("Sadece fotoğrafı çekin, gerisini yapay zeka halletsin. Tık diye Excel'iniz hazır!")

# API anahtarını güvenli kasadan alıyoruz (Müşteri bunu asla göremez)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.warning("Lütfen sistem yöneticisi ile iletişime geçin (API Anahtarı eksik).")

# Kamera modülü
resim = st.camera_input("📷 Listeyi Çek")

if resim:
    with st.spinner("Yapay zeka el yazısını okuyor ve Excel'i diziyor... (Yaklaşık 5-10 saniye)"):
        try:
            # Fotoğrafı hazırlıyoruz
            img = Image.open(resim)
            
            # Gemini zekasını çağırıyoruz
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            # Gemini'ye verdiğimiz kesin talimat (Prompt)
            prompt = """
            Bu resimdeki el yazısı listeyi oku. Çok kargacık burgacık olsa bile tahmin et.
            Sadece iki sütunlu virgülle ayrılmış (CSV) formatında çıktı ver. Başlıklar 'Ürün' ve 'Miktar' olsun. 
            Ekstra hiçbir açıklama, markdown veya kod bloğu yazma. Sadece saf veriyi ver.
            Örnek:
            Ürün,Miktar
            Elma,5 kg
            Ekmek,2 adet
            """
            
            cevap = model.generate_content([prompt, img])
            
            # Gemini'nin verdiği metni anında tabloya çeviriyoruz
            satirlar = cevap.text.strip().split('\n')
            veri = [satir.split(',') for satir in satirlar if ',' in satir]
            
            df = pd.DataFrame(veri[1:], columns=veri[0])

            # Tabloyu ekranda şık bir şekilde göster
            st.success("✅ Waw! İşlem Başarılı. İşte verileriniz:")
            st.dataframe(df, use_container_width=True)

            # Tabloyu Excel formatına dönüştür
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sihirli_Liste')
            excel_data = output.getvalue()

            # Tek tıkla indirme butonu
            st.download_button(
                label="📥 Excel Olarak İndir",
                data=excel_data,
                file_name="Sihirli_Liste.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except Exception as e:
            st.error(f"Bir hata oluştu, lütfen fotoğrafı daha net çekmeyi deneyin. Detay: {e}")
