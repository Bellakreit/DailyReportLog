import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
#from audiorecorder import audiorecorder
from report_form import show_report_form
# from report_form import fill_report_form
from audio_transcriber import transcribe_audio
from pathlib import Path
import torch

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


uploaded_file = st.file_uploader(
    "Upload an audio file",
    type=["audio/mpeg", "audio/mp4", "audio/wav", "audio/x-wav"],
    help="Audio files are supported in mpeg, mp4, wav, and x-wav formats.",
)
if uploaded_file is not None:
    saved_audio = uploaded_file.getvalue()

# st.title("Audio Recorder")
# audio = audiorecorder("Click to record", "Click to stop recording")

# if len(audio) > 0:
#     # save audio as torch tensor DOES NOT WORK
#     saved_audio = torch.from_numpy(np.array(audio))
#     st.audio(saved_audio)
    

btn_submit_audio = st.button("Submit Audio")
if btn_submit_audio:
    # Transcribe the audio
    with st.spinner("Creating report...this will take a few minutes"):
        transcription = transcribe_audio(saved_audio)
        dict_result = classify_text(transcription)
        # transform the string dictionary to an actual Python dictionary
        st.success("Audio submitted successfully!")
        show_report_form(dict_result, selected_project_id)
        #fill_report_form(dict_result)

btnshow = st.button("Enter Report Manually")
if btnshow:
    show_report_form()
