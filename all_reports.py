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

    # get the report only if it belongs to the logged-in user
    report_df = pd.read_sql_query(
        """
        SELECT *
        FROM Reports
        WHERE ReportID = ? AND UserID = ?
        """,
        conn,
        params=(report_id, st.session_state.UserID)
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


def build_text_content(report):
    if not report:
        return ""

    lines = [
        "Daily Report Log",
        f"Report ID: {report.get('ReportID', '')}",
        f"Date: {report.get('Date', '')}",
        "",
        "Description:",
        str(report.get("Description", "")) or "No description provided.",
        "",
        "Safety Equipment:",
    ]

    safety_items = []
    if report.get("HardHatUsed"):
        safety_items.append("Hard Hat")
    if report.get("GlovesUsed"):
        safety_items.append("Gloves")
    if report.get("EyeProtectionUsed"):
        safety_items.append("Eye Protection")
    if report.get("EarProtectionUsed"):
        safety_items.append("Ear Protection")
    if report.get("FootwearUsed"):
        safety_items.append("Footwear")
    if report.get("DustMaskUsed"):
        safety_items.append("Dust Mask")
    other_ppe = str(report.get("OtherPPEUsed", "") or "").strip()
    if other_ppe:
        safety_items.append(other_ppe)

    lines.append(", ".join(safety_items) if safety_items else "None listed")
    lines.append("")
    lines.append("Worker Hours:")

    worker_hours = report.get("WorkerHours", {}) or {}
    if worker_hours:
        for worker_name, hours in worker_hours.items():
            lines.append(f"- {worker_name}: {hours} hours")
    else:
        lines.append("No worker hours listed.")

    return "\n".join(lines)


see_all = st.button("See All Reports created by you", type="primary", on_click=btnSeeAllReports_Click)



if "show_all_reports" not in st.session_state:
    st.session_state.show_all_reports = False

if st.session_state.show_all_reports:
    st.write("Report ID | Date")

    conn = sqlite3.connect("report_log.db")

    # show only reports that belong to the logged-in user
    df = pd.read_sql_query(
        """
        SELECT ReportID, Date
        FROM Reports
        WHERE UserID = ?
        """,
        conn,
        params=(st.session_state.UserID,)
    )

    conn.close()

    for index, row in df.iterrows():
        report_id = row["ReportID"]
        date = row["Date"]
        report_data = get_report_dict(report_id)

        col1, col2 = st.columns([4, 1.4])

        with col1:
            if st.button(f"View Report {report_id} - {date}", key=f"view_report_{report_id}"):
                if report_data:
                    st.session_state.selected_report_id = report_id
                    st.session_state.show_all_reports = False
                    st.session_state._prefilled = False
                    show_report_form(report_data)
                    st.success(f"Viewing Report ID: {report_id}")
                else:
                    st.error("Report not found.")

        with col2:
            if report_data:
                st.download_button(
                    label="Download TXT",
                    data=build_text_content(report_data),
                    file_name=f"report_{report_id}.txt",
                    mime="text/plain",
                    key=f"download_report_{report_id}",
                )
