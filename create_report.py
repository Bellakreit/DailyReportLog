import streamlit as st
import pandas as pd
import sqlite3
from report_form import show_report_form
from audio_transcriber import transcribe_audio
from pathlib import Path
import tempfile
from split_text import classify_text

# setting the session state so the user will be brought to all reports page after their report is created
if st.session_state.get("report_saved"):
    st.switch_page("all_reports.py")

# streamlit page designing
st.title("Create Report", text_alignment="center")
st.header("Create a new report")
st.subheader("upload or record an audio to create your report")
st.logo("Designer.png", size='large')
st.markdown("""
Your report should consist on the following information:
- A short description of the day's work.
- The safety equipment used (PPE).
- The hours worked by each worker.

Record or upload an audio and press submit audio to create your report. You can also enter the report manually by clicking the 'Enter Report Manually' button.
we recommend that the audio is clear and concise. The audio should not be longer than 1 minute, the longer it is the longer it will take to create the report.
""")

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

# adding a session state variable for audio to keep track of what audio will be used
if "saved_audio" not in st.session_state:
    st.session_state.saved_audio = None

saved_audio = st.session_state.saved_audio

# sample audio implementation
sample_btn = st.button("Use Sample Audio")
# add a sample audio to be used
sample_audio_path = Path("sample_audio.mp3")
if sample_btn:
    if sample_audio_path.exists():
        with open(sample_audio_path, "rb") as f:
            st.session_state.saved_audio = f.read()
    else:
        st.error("Sample audio file not found.")

# upload audio implementation
uploaded_file = st.file_uploader(
    "Upload an audio file",
    type=["audio/mpeg", "audio/mp4", "audio/wav", "audio/x-wav"],
    help="Audio files are supported in mpeg, mp4, wav, and x-wav formats.",
)
if uploaded_file is not None:
    st.session_state.saved_audio = uploaded_file.getvalue()


# record audio implementation
audio = st.audio_input("Record your report")

if audio:
    st.session_state.saved_audio = audio.read()

saved_audio = st.session_state.saved_audio

btn_submit_audio = st.button("Submit Audio")
# if the button was pressed do the following
if btn_submit_audio or sample_btn:
    if saved_audio is not None:
        # using a spinner but also added check boxes to see progress of the report being made
        with st.spinner(text="Creating report...this will take a few minutes"):
            transcription = transcribe_audio(saved_audio)
            st.checkbox("audio transcribed", value=True, disabled=True)
            if not transcription or not transcription.strip():
                st.error("The audio did not produce usable text. Please try a clearer recording or enter the report manually.")
            else:
                st.session_state._prefilled = False
                st.session_state._worker_df = pd.DataFrame(columns=["Worker Name", "Hours Worked"])
                st.markdown("classifying text...")
                dict_result = classify_text(transcription)
                st.checkbox("text classified", value=True, disabled=True)
                st.markdown("filling report form...")
                # error handling if the model output was not a dict or if it was a dict with an error key
                if isinstance(dict_result, dict) and dict_result.get("error"):
                    st.warning("The AI output was not usable, so the form was left empty for you to complete manually.")
                    show_report_form(None, selected_project_id)
                else:
                    st.success("Audio submitted successfully!")
                    show_report_form(dict_result, selected_project_id)

    # if no audio was uploaded or recorded, show an error message
    else:
        st.error("Please upload or record audio before submitting.")

btnshow = st.button("Enter Report Manually")
if btnshow:
    show_report_form(None, selected_project_id)
