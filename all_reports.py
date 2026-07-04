import streamlit as st
import sqlite3
import pandas as pd

from report_form import show_report_form

st.logo("Designer.png", size='large')

def btnSeeAllReports_Click():
    st.session_state.show_all_reports = True

see_all = st.button("See All Reports", type="primary", on_click=btnSeeAllReports_Click)
search_query = st.text_input("Search by title or date (YYYY-MM-DD)", help="Enter a title or date to search for specific reports.")

btn_search = st.button("Search", type="primary")
if btn_search:
    st.success(f"Searching for reports matching: {search_query}")


if "show_all_reports" not in st.session_state:
    st.session_state.show_all_reports = False  

if st.session_state.show_all_reports:
    # show report id and date in a table, and allow the user to click on a report to view it
    st.write("Report ID | Date")
    st.write("--- | ---")
    conn = sqlite3.connect("report_log.db")
    df = pd.read_sql_query("SELECT ReportID, Date FROM Reports", conn)
    for index, row in df.iterrows():
        report_id = row["ReportID"]
        date = row["Date"]
        if st.button(f"View Report {report_id} - {date}", key=f"view_report_{report_id}"):
            st.session_state.selected_report_id = report_id
            st.session_state.show_all_reports = False  # Close the all reports view
            show_report_form(selected_project_id=None, report_id=st.session_state.selected_report_id)  # Call the function to show the report form with the selected report ID
            st.success(f"Viewing Report ID: {report_id}")
