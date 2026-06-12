import streamlit as st
from audiorecorder import audiorecorder

st.title("Create Report", text_alignment="center")
st.header("Create a new report")
st.subheader("upload or record an audio to create your report")

uploaded_file = st.file_uploader(
    "Upload an audio file",
    type=["mpeg", "mp4", "wav", "x-wav"],
    help="Audio files are supported in mpeg, mp4, wav, and x-wav formats.",
)


st.title("Audio Recorder")
audio = audiorecorder("Click to record", "Click to stop recording")

if len(audio) > 0:
    # To play audio in frontend:
    st.audio(audio.export().read())  

    # To save audio to a file, use pydub export method:
    audio.export("audio.wav", format="wav")