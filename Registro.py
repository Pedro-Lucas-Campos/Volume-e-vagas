import streamlit as st
import cv2
from pyzbar import pyzbar
import numpy as np

def ler_qr_code(image):
    try:
        texto_extraido = pyzbar.decode(image)
        return texto_extraido
    except Exception as e:
        print(f'{e}')

def contornar_imagem(image, texto_extraido):
    try:
        for texto in texto_extraido:
            points = texto.polygon
            if len(points) > 4:
                hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                cv2.polylines(image, [hull], True, (0,255,0),2)
            else:
                cv2.polylines(image, [np.array(points, dtype=np.int32)], True, (0,255,0),2)
            qr_data = texto.data.decode("utf-8")
            qr_type = texto.type

            text = f"Data: {qr_data} | Type: {qr_type}"
            cv2.putText(image, text, (points[0].x, points[0].y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0, 2))
        return image
    except Exception as e:
        print(f'{e}')

st.set_page_config(page_title="Cadastro de volume",layout='wide')

st.title("Leia o QR CODE")
st.write("Aponte a câmera para o QR CODE")

img_file_buffer = st.camera_input("Tire a foto do QR CODE")

if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    st.info("ANALISANDO O QR CODE")
    texto_extraido = ler_qr_code(cv2_img)
    
    if texto_extraido:
        texto_extraido = texto_extraido[19:48]
        st.success(f"O VIN {texto_extraido} foi extraido")