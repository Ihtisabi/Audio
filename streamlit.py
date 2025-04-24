import streamlit as st
import librosa
import soundfile as sf
import os
import tempfile
import librosa.display
import matplotlib.pyplot as plt
from pydub import AudioSegment
import numpy as np

# Judul aplikasi
st.title("Visualisasi dan Manipulasi Audio")

# Upload file audio (MP3/WAV)
uploaded_file = st.file_uploader("Upload file audio (MP3/WAV)", type=["mp3", "wav"])

# Pilih kecepatan playback
playback_rate = st.selectbox("Pilih kecepatan playback:", [0.5, 0.75, 1.0, 1.25, 1.5], index=2)

# Input durasi efek fade in dan fade out (dalam detik)
fade_in_duration = st.number_input("Durasi Fade In (detik)", min_value=0, max_value=10, value=2, step=1)
fade_out_duration = st.number_input("Durasi Fade Out (detik)", min_value=0, max_value=10, value=2, step=1)


if uploaded_file is not None:
    try:
        # Simpan sementara file yang diupload dengan ekstensi aslinya
        file_extension = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_input:
            temp_input.write(uploaded_file.read())
            input_path = temp_input.name
            
        # Konversi ke WAV terlebih dahulu menggunakan pydub (untuk menangani MP3)
        audio = AudioSegment.from_file(input_path)
        wav_path = os.path.join(tempfile.gettempdir(), "temp_audio.wav")
        audio.export(wav_path, format="wav")
        
        # Load audio menggunakan librosa dari file WAV
        y, sr = librosa.load(wav_path)

        # Visualisasi waveform asli
        st.subheader("Waveform Audio Asli")
        plt.figure(figsize=(10, 4))
        librosa.display.waveshow(y, sr=sr)
        plt.title("Waveform Audio Asli")
        plt.xlabel("Waktu (detik)")
        plt.ylabel("Amplitudo")
        st.pyplot(plt)
        plt.close()

        if st.button("Terapkan Efek Fade In/Out dan Kecepatan Playback"):
            # Menambahkan efek fade in dan fade out menggunakan pydub
            audio = AudioSegment.from_file(wav_path)
            
            # Ubah kecepatan playback menggunakan pydub
            if playback_rate != 1.0:
                speed_changed_audio = audio._spawn(audio.raw_data, overrides={
                    "frame_rate": int(audio.frame_rate * playback_rate)
                })
                # Kembalikan ke sample rate asli untuk mempertahankan pitch tapi mengubah tempo
                speed_changed_audio = speed_changed_audio.set_frame_rate(audio.frame_rate)
            else:
                speed_changed_audio = audio
                
            # Terapkan fade hanya jika durasinya > 0
            processed_audio = speed_changed_audio
            
            if fade_in_duration > 0:
                fade_in_ms = fade_in_duration * 1000  # Konversi ke milidetik
                processed_audio = processed_audio.fade_in(fade_in_ms)
                
            if fade_out_duration > 0:
                fade_out_ms = fade_out_duration * 1000  # Konversi ke milidetik
                processed_audio = processed_audio.fade_out(fade_out_ms)

            # Simpan hasil audio
            output_path = os.path.join(tempfile.gettempdir(), f"processed_audio_{playback_rate}.wav")
            processed_audio.export(output_path, format="wav")

            # Visualisasi waveform audio yang telah diproses
            y_processed, sr_processed = librosa.load(output_path)
            st.subheader(f"Waveform Audio Setelah Efek (Kecepatan {playback_rate}x, Fade In/Out)")
            plt.figure(figsize=(10, 4))
            librosa.display.waveshow(y_processed, sr=sr_processed)
            plt.title(f"Waveform Audio Setelah Efek")
            plt.xlabel("Waktu (detik)")
            plt.ylabel("Amplitudo")
            st.pyplot(plt)
            plt.close()

            # Putar audio yang sudah diproses
            st.audio(output_path, format="audio/wav")
            
            # Tampilkan pesan sukses yang menjelaskan efek yang diterapkan
            effects_applied = []
            if playback_rate != 1.0:
                effects_applied.append(f"kecepatan {playback_rate}x")
            if fade_in_duration > 0:
                effects_applied.append(f"fade in {fade_in_duration}s")
            if fade_out_duration > 0:
                effects_applied.append(f"fade out {fade_out_duration}s")
                
            if effects_applied:
                st.success(f"Audio diproses dengan: {', '.join(effects_applied)}")
            else:
                st.success(f"Audio diproses tanpa efek tambahan")
            
    except Exception as e:
        st.error(f"Terjadi kesalahan: {str(e)}")
        
    finally:
        # Bersihkan file sementara
        try:
            if 'input_path' in locals():
                os.unlink(input_path)
            if 'wav_path' in locals():
                os.unlink(wav_path)
            if 'output_path' in locals():
                pass
        except:
            pass
else:
    st.info("Silakan upload file terlebih dahulu.")