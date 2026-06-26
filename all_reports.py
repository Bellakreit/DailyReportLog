import streamlit as st
import sqlite3
import pandas as pd

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
    st.subheader("All Reports")
    # Here you would typically fetch and display the reports from your database
    # For demonstration, we'll just show a placeholder message
    st.write("Displaying all reports")
    # Show all reports from database in dataframe, show only report id and date
    conn = sqlite3.connect("report_log.db")
    df = pd.read_sql_query("SELECT * FROM Reports", conn)
    edit_df = st.data_editor(df, num_rows="dynamic", key="report_df")
    conn.close()
