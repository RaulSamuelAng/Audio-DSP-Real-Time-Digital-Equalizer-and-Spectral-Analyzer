# Audio-DSP-Real-Time-Digital-Equalizer-and-Spectral-Analyzer
A web-based engineering tool built with Python and Streamlit to upload .wav files, apply digital filters (Butterworth), and analyze signals in time and frequency domains.
For optimal real-time performance and to avoid memory/CPU bottlenecks during the Fast Fourier Transform (FFT) calculation, it is highly recommended to upload short audio clips (ideally under 15–20 seconds). Processing full-length tracks may slow down the spectrogram rendering.
