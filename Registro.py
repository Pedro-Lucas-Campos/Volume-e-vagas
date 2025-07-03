import streamlit as st
import cv2
from pyzbar import pyzbar
import numpy as np
import pandas as pd
import requests

API_ENDPOINT = "https://api-final-njr2.onrender.com/add_record"

def processar_qr_code(camera_key, step_message, process_function=None):
    st.info(step_message)
    img_file_buffer = st.camera_input("Tire a foto do QR CODE", key=camera_key)

    if img_file_buffer is None:
        return None

    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    
    try:
        decoded_objects = pyzbar.decode(cv2_img)
        if not decoded_objects:
            st.warning("Nenhum QR Code encontrado. Tente novamente.")
            return None

        # Extrai o dado do primeiro QR Code encontrado
        qr_data = decoded_objects[0].data.decode("utf-8")

        # Aplica a função de processamento se ela for fornecida
        if process_function:
            return process_function(qr_data)
        
        return qr_data

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar o QR Code: {e}")
        return None

st.set_page_config(page_title="Cadastro de volume",layout='wide')
st.title("Leia o QR CODE")

if "step" not in st.session_state:
    st.session_state.step = "vin"
if "vin" not in st.session_state:
    st.session_state.vin = None
if "records" not in st.session_state:
    st.session_state.records = []

if st.session_state.step == "vin":
    vin_processor = lambda data: data[41:58] if len(data) >= 58 else data
    vin_lido = processar_qr_code("camera_vin", "Leia o QR Code do VEÍCULO.", vin_processor)
    if vin_lido:
        st.session_state.vin = vin_lido
        st.session_state.step = "loc"
        st.rerun()

elif st.session_state.step == "loc":
    st.success(f"VIN Lido: **{st.session_state.vin}**")
    loc_lida = processar_qr_code("camera_loc", "Agora, leia o QR Code da LOCALIZAÇÃO.")
    if loc_lida:
        record = {"VIN": st.session_state.vin, "Localização": loc_lida}
        try:
            response = requests.post(API_ENDPOINT, json=record)
            response.raise_for_status()
            st.success(f"Registro enviado com sucesso para a base de dados!")
        except requests.exceptions.RequestException as e:
            st.error(f"Falha ao comunicar com a API: {e}")
            st.warning("O registro foi salvo apenas nesta sessão. Verifique se a API está online.")
        st.session_state.records.append(record)

        st.session_state.step = "vin"
        st.session_state.vin = None
        st.rerun()

st.markdown("---")
st.header("Registros Coletados")
if st.session_state.records:
    df = pd.DataFrame(st.session_state.records)
    st.dataframe(df, use_container_width=True)

else:
    st.warning("Nenhum registro coletado ainda.")
