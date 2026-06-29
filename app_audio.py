import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy import signal
import os

st.set_page_config(page_title="Procesamiento de Audio DSP", page_icon="🎵", layout="wide")
st.title("🎵 Ecualizador Digital y Analizador de Frecuencias (DSP)")
st.markdown("Herramienta para cargar archivos `.wav`, aplicar filtros digitales en tiempo real y analizar el espectro.")

# 1. FUNCIÓN DE FILTRADO
def aplicar_filtro(datos, fs, tipo_filtro, f_corte, orden=5):
    # Nyquist
    nyq = 0.5 * fs
    f_normalizada = f_corte / nyq
    
    # Validar que la frecuencia de corte no supere Nyquist
    if f_normalizada >= 1.0:
        f_normalizada = 0.99
        
    # Se diseña el filtro Butterworth digital (b, a son los coeficientes de la función de transferencia)
    b, a = signal.butter(orden, f_normalizada, btype=tipo_filtro, analog=False)
    
    # Se aplica el filtro a los datos de audio
    datos_filtrados = signal.lfilter(b, a, datos)
    return np.int16(datos_filtrados) # Se devuelve en formato de 16 bits para el WAV

# 2. INTERFAZ WEB
st.sidebar.header("🎛️ Configuración del Filtro")
tipo = st.sidebar.selectbox("Tipo de Filtro", ["lowpass", "highpass"], format_func=lambda x: "Pasa-Bajos (Cortar Agudos)" if x=="lowpass" else "Pasa-Altos (Cortar Graves)")

# Subida del archivo por el usuario
archivo_subido = st.file_uploader("Sube un archivo de audio .wav de prueba", type=["wav"])

if archivo_subido is not None:
    # Leer el archivo WAV
    fs, datos = wavfile.read(archivo_subido)
    
    # Si el audio es estéreo (2 canales), nos quedamos con el canal izquierdo para simplificar el gráfico
    if len(datos.shape) > 1:
        datos_mono = datos[:, 0]
    else:
        datos_mono = datos

    # El slider de frecuencia de corte se adapta dinámicamente a la frecuencia de Nyquist del audio cargado
    f_max = int(fs / 2)
    f_corte = st.sidebar.slider("Frecuencia de Corte (Hz)", min_value=20, max_value=f_max, value=1000, step=50)

    # Procesar el audio mediante el filtro
    audio_filtrado = aplicar_filtro(datos_mono, fs, tipo, f_corte)

    # Guardar temporalmente el audio filtrado para que Streamlit pueda reproducirlo
    nombre_temporal = "temp_filtrado.wav"
    wavfile.write(nombre_temporal, fs, audio_filtrado)

    # --- REPRODUCTORES DE AUDIO ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔊 Audio Original")
        st.audio(archivo_subido)
    with col2:
        st.subheader("🎚️ Audio Filtrado")
        st.audio(nombre_temporal)

    # --- GRÁFICOS (Dominio del Tiempo y Frecuencia) ---
    st.header("📊 Análisis de Señal")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
    fig.tight_layout(pad=4.0)

    # Gráfico 1: Dominio del Tiempo (Forma de onda)
    tiempo = np.linspace(0, len(datos_mono) / fs, num=len(datos_mono))
    ax1.plot(tiempo[:20000], datos_mono[:20000], label="Original", color="gray", alpha=0.7) # Graficamos solo los primeros puntos para que vaya rápido
    ax1.plot(tiempo[:20000], audio_filtrado[:20000], label="Filtrado", color="#1DB954")
    ax1.set_title("Forma de Onda (Dominio del Tiempo - Zoom de los primeros puntos)")
    ax1.set_xlabel("Tiempo (segundos)")
    ax1.set_ylabel("Amplitud")
    ax1.legend()
    ax1.grid(True)

    # Gráfico 2: Dominio de la Frecuencia (Espectrograma / FFT rápida)
    # Usamos la función integrada de matplotlib para calcular la densidad espectral
    ax2.specgram(audio_filtrado, Fs=fs, cmap="viridis", NFFT=1024)
    ax2.set_title("Espectrograma de la Señal Filtrada (Dominio de la Frecuencia)")
    ax2.set_xlabel("Tiempo (segundos)")
    ax2.set_ylabel("Frecuencia (Hz)")
    ax2.set_ylim(0, f_max) # Limitamos hasta la frecuencia de Nyquist

    st.pyplot(fig)

    # Limpieza del archivo temporal
    if os.path.exists(nombre_temporal):
        os.remove(nombre_temporal)
else:
    st.info("Por favor, sube un archivo `.wav` para empezar el análisis. (Intenta que no sea un archivo gigante, con unos pocos segundos basta).")
