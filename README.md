# Daily Report Log

This project is a simple Streamlit app for creating and managing daily construction reports. It lets users log in, create reports from audio or manually, view past reports, manage projects, and leave feedback.

## What this app does

The app is built to make daily reporting easier by helping users:

- sign up or log in as a user
- create a daily report with details like date, description, safety equipment used, and worker with hours
- upload or record audio and turn it into a report draft
- view reports that were created by the logged-in user only
- manage project information
- submit feedback

## Main features

- User login and account creation
- Audio-based report creation
- Manual report entry
- Report viewing and review
- Project management page
- Feedback form

## Tech stack

- Python
- Streamlit
- SQLite
- pandas
- Hugging Face models for audio transcription and text classification

## Getting started

1. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

2. Set up the database:

   ```bash
   python database/init_db.py
   ```

3. Start the app:

   ```bash
   streamlit run app.py
   ```

4. Open the local Streamlit URL in your browser.

## Project files

- app.py - main app entry point and navigation
- home.py - login and user registration page
- create_report.py - report creation page
- all_reports.py - view saved reports
- report_form.py - report submission form logic
- audio_transcriber.py - audio transcription helper
- split_text.py - AI-based report classification logic
- database/init_db.py - database setup

## Notes

- The app uses a local SQLite database file named report_log.db.
- Audio transcription depends on model downloads and may take some time on first run.
- A sample audio file can be used if present as sample_audio.mp3.

## Example user

For quick testing, the home page includes a sample test user:

- Username: test-user
- Password: testpass
