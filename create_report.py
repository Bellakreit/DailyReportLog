import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from report_form import show_report_form
from audio_transcriber import transcribe_audio
from pathlib import Path
import streamlit as st
import tempfile
from split_text import classify_text

st.title("Create Report", text_alignment="center")
st.header("Create a new report")
st.subheader("upload or record an audio to create your report")
st.logo("Designer.png", size='large')

# select project from dropdown from querying the database, no default value
conn = sqlite3.connect("report_log.db")
projects_df = pd.read_sql_query("SELECT * FROM Projects", conn)

# map Name -> ProjectID
project_map = dict(zip(projects_df["Name"], projects_df["ProjectID"]))
project_names = projects_df["Name"].tolist()

selected_project_name = st.selectbox(
    "Select Project", project_names, key="selected_project", placeholder=None
)
selected_project_id = project_map.get(selected_project_name)


# sample audio implementation
sample_btn = st.button("Use Sample Audio")
# add a sample audio to be used
sample_audio_path = Path("sample_audio.mp3")
if sample_btn:
    if sample_audio_path.exists():
        with open(sample_audio_path, "rb") as f:
            saved_audio = f.read()
    else:
        st.error("Sample audio file not found.")

# upload audio implementation
uploaded_file = st.file_uploader(
    "Upload an audio file",
    type=["audio/mpeg", "audio/mp4", "audio/wav", "audio/x-wav"],
    help="Audio files are supported in mpeg, mp4, wav, and x-wav formats.",
)
if uploaded_file is not None:
    saved_audio = uploaded_file.getvalue()


# record audio implementation
audio = st.audio_input("Record your report")

if audio:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio.read())
        saved_audio = f.name

btn_submit_audio = st.button("Submit Audio")
if btn_submit_audio or sample_btn:
    # Transcribe the audio

    with st.spinner(text="Creating report...this will take a few minutes"):
        transcription = transcribe_audio(saved_audio)
        dict_result = classify_text(transcription)
        # transform the string dictionary to an actual Python dictionary
        st.success("Audio submitted successfully!")
        show_report_form(dict_result, selected_project_id)


btnshow = st.button("Enter Report Manually")
if btnshow:
    show_report_form(None, selected_project_id)
