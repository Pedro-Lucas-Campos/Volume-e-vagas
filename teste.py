
import streamlit as st
import cv2
from pyzbar import pyzbar
import numpy as np
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import queue
import av
import pandas as pd

config_servidor_stun = {
    'iceServers': [{'urls': ['stun:stun.l.google.com:19302']}]
}

result_queue: "queue.Queue[str]" = queue.Queue()

class QRCodeVideoTransformer(VideoTransformerBase):
    def __init__(self):
        self.last_qr_data = None

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")

        decoded_objects = pyzbar.decode(img)
        if decoded_objects:
            qr_data = decoded_objects[0].data.decode("utf-8")
            if qr_data != self.last_qr_data:
                self.last_qr_data = qr_data
                result_queue.put(qr_data)
        else:
            self.last_qr_data = None

        for obj in decoded_objects:
            points = obj.polygon
            if len(points) > 4:
                hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                cv2.polylines(img, [hull], True, (0, 255, 0), 3)
            else:
                cv2.polylines(img, [np.array(points, dtype=np.int32)], True, (0, 255, 0), 3)
            
            text = f"Data: {obj.data.decode('utf-8')}"
            cv2.putText(img, text, (obj.rect.left, obj.rect.top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        return av.VideoFrame.from_ndarray(img, format="bgr24")

st.set_page_config(page_title='Registro de HC',layout='wide')

st.title("LEITOR DE QR CODE")
st.write("Aponte a câmera para o QR CODE")

ctx = webrtc_streamer(
    key='qrcode-reader',
    video_transformer_factory=QRCodeVideoTransformer,
    rtc_configuration=config_servidor_stun,
    media_stream_constraints={'video':True, 'audio':False}
)

if "records" not in st.session_state:
    st.session_state.records = []
if "scan_step" not in st.session_state:
    st.session_state.scan_step = "veiculo"
if "current_vin" not in st.session_state:
    st.session_state.current_vin = None

if ctx.state.playing:
    new_qr_data = None
    while not result_queue.empty():
        new_qr_data = result_queue.get_nowait()

    if new_qr_data:
        if st.session_state.scan_step == "veiculo":
            st.session_state.current_vin = new_qr_data
            st.session_state.scan_step = "localizacao"
            st.rerun()

        elif st.session_state.scan_step == "localizacao":
            if new_qr_data != st.session_state.current_vin:
                st.session_state.records.append({
                    "Veículo (VIN)": st.session_state.current_vin,
                    "Localização": new_qr_data
                })
                st.session_state.current_vin = None
                st.session_state.scan_step = "veiculo"
                st.rerun()


st.markdown("---")

if st.session_state.scan_step == "veiculo":
    st.info("➡️ **Passo 1:** Aponte a câmera para o QR Code do **VEÍCULO**.")
else:
    st.success(f"✅ **Veículo Lido:** `{st.session_state.current_vin}`")
    st.info("➡️ **Passo 2:** Agora, aponte para o QR Code da **LOCALIZAÇÃO**.")
    
    if st.button("❌ Cancelar Leitura do Veículo"):
        st.session_state.current_vin = None
        st.session_state.scan_step = "veiculo"
        st.rerun()

st.markdown("---")

st.header("Histórico de Registros")
if not st.session_state.records:
    st.warning("Nenhum registro foi feito ainda.")
else:
    df = pd.DataFrame(st.session_state.records)
    st.dataframe(df, use_container_width=True)
    
    @st.cache_data
    def convert_df_to_csv(df_to_convert):
        return df_to_convert.to_csv(index=False).encode('utf-8')

    csv = convert_df_to_csv(df)

    st.download_button(
        label="📥 Exportar para CSV",
        data=csv,
        file_name='registros_qr_code.csv',
        mime='text/csv',
    )

if image:
  st.image(image)