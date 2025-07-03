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

def extrair_vin():
    img_file_buffer_vin = st.camera_input("Tire a foto do QR CODE")

    if img_file_buffer_vin is not None:
        bytes_data = img_file_buffer_vin.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        st.info("ANALISANDO O QR CODE")
        texto_extraido = ler_qr_code(cv2_img)
        
        if texto_extraido:
            try:
                qr_data_vin = texto_extraido[0].data.decode("utf-8")
                qr_data_vin = qr_data_vin[41:58]
            except Exception as e:
                st.error(f"Erro ao extrair VIN: {e}")
    return qr_data_vin

def extrair_loc():
    img_file_buffer_loc = st.camera_input("Tire a foto do QR CODE")

    if img_file_buffer_loc is not None:
        bytes_data = img_file_buffer_loc.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        st.info("ANALISANDO O QR CODE")
        texto_extraido = ler_qr_code(cv2_img)
        
        if texto_extraido:
            try:
                qr_data_loc = texto_extraido[0].data.decode("utf-8")
            except Exception as e:
                st.error(f"Erro ao extrair VIN: {e}")
    return qr_data_loc

st.set_page_config(page_title="Cadastro de volume",layout='wide')

st.title("Leia o QR CODE")
st.write("Aponte a câmera para o QR CODE")

extrair_vin()
extrair_loc()