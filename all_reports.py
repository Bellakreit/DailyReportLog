import streamlit as st
import sqlite3
import pandas as pd

from report_form import show_report_form

st.logo("Designer.png", size='large')


def btnSeeAllReports_Click():
    st.session_state.show_all_reports = True


def get_report_dict(report_id):
    conn = sqlite3.connect("report_log.db")
    cursor = conn.cursor()

    report_df = pd.read_sql_query(
        "SELECT * FROM Reports WHERE ReportID = ?",
        conn,
        params=(report_id,)
    )

    if report_df.empty:
        conn.close()
        return None

    report = report_df.iloc[0].to_dict()

    cursor.execute(
        """
        SELECT WorkerName, WorkerHours 
        FROM ProjectWorkers 
        WHERE ReportID = ?
        """,
        (report_id,)
    )

    worker_hours_data = cursor.fetchall()

    report["WorkerHours"] = {
        worker_name: worker_hours
        for worker_name, worker_hours in worker_hours_data
        if worker_name
    }

    conn.close()
    return report


see_all = st.button("See All Reports", type="primary", on_click=btnSeeAllReports_Click)

search_query = st.text_input(
    "Search by title or date (YYYY-MM-DD)",
    help="Enter a title or date to search for specific reports."
)

btn_search = st.button("Search", type="primary")
if btn_search:
    st.success(f"Searching for reports matching: {search_query}")


if "show_all_reports" not in st.session_state:
    st.session_state.show_all_reports = False

if st.session_state.show_all_reports:
    st.write("Report ID | Date")

    conn = sqlite3.connect("report_log.db")
    df = pd.read_sql_query("SELECT ReportID, Date FROM Reports", conn)
    conn.close()

    for index, row in df.iterrows():
        report_id = row["ReportID"]
        date = row["Date"]

        if st.button(f"View Report {report_id} - {date}", key=f"view_report_{report_id}"):
            dict_result = get_report_dict(report_id)

            if dict_result:
                st.session_state.selected_report_id = report_id
                st.session_state.show_all_reports = False
                st.session_state._prefilled = False
                show_report_form(dict_result)
                st.success(f"Viewing Report ID: {report_id}")
            else:
                st.error("Report not found.")
