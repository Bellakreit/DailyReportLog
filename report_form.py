from datetime import datetime

import streamlit as st
import sqlite3
import pandas as pd

import streamlit as st
import sqlite3
import pandas as pd


@st.dialog("Report Form")
def show_report_form(dict_result=None, selected_project_id=None, report_id=None):
    # Pre-fill BEFORE any widget renders
    if dict_result and not st.session_state.get("_prefilled"):
        st.session_state.selected_project_id = selected_project_id
        raw_date = dict_result.get("Date", pd.Timestamp.today().date())
        st.session_state.date = (
            datetime.strptime(raw_date, "%Y-%m-%d").date()
            if isinstance(raw_date, str) else raw_date
        )
        st.session_state.description = dict_result.get("Description", "")
        st.session_state.hard_hat_used = bool(dict_result.get("HardHatUsed", False))
        st.session_state.gloves_used = bool(dict_result.get("GlovesUsed", False))
        st.session_state.eye_protection_used = bool(dict_result.get("EyeProtectionUsed", False))
        st.session_state.ear_protection_used = bool(dict_result.get("EarProtectionUsed", False))
        st.session_state.footware_used = bool(dict_result.get("FootwearUsed", False))
        st.session_state.dust_mask_used = bool(dict_result.get("DustMaskUsed", False))
        st.session_state.other_ppe_used = str(dict_result.get("OtherPPEUsed", "") or "")
       # In pre-fill block, use a different key
        workers = dict_result.get("WorkerHours", {})
        st.session_state._worker_df = pd.DataFrame(
            [(k, v) for k, v in workers.items()],
            columns=["Worker Name", "Hours Worked"]
        ) if workers else pd.DataFrame(columns=["Worker Name", "Hours Worked"])
        st.session_state._prefilled = True

    # if report_id is provided, fetch the report data from the database and pre-fill the form
    if report_id and not st.session_state.get("_prefilled"):
        conn = sqlite3.connect('report_log.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Reports WHERE ReportID = ?", (report_id,))
        report_data = cursor.fetchone()
        if report_data:
            st.session_state.selected_project_id = report_data[1]  # ProjectID
            raw_date = report_data[3]  # Date
            st.session_state.date = (
                datetime.strptime(raw_date, "%Y-%m-%d").date()
                if isinstance(raw_date, str) else raw_date
            )
            st.session_state.description = report_data[4]  # Description   
            st.session_state.hard_hat_used = bool(report_data[5])  # HardHatUsed
            st.session_state.gloves_used = bool(report_data[6])  # GlovesUsed
            st.session_state.eye_protection_used = bool(report_data[7])  # EyeProtection
            st.session_state.ear_protection_used = bool(report_data[8])  # EarProtectionUsed
            st.session_state.footware_used = bool(report_data[9])  # FootwearUsed
            st.session_state.dust_mask_used = bool(report_data[10])  # DustMaskUsed
            st.session_state.other_ppe_used = str(report_data[11] or "")

            # Fetch worker hours for this report
            cursor.execute("SELECT WorkerName, WorkerHours FROM ProjectWorkers WHERE ReportID = ?", (report_id,))
            worker_hours_data = cursor.fetchall()
            if worker_hours_data:
                st.session_state._worker_df = pd.DataFrame(worker_hours_data, columns=["Worker Name", "Hours Worked"])
            else:
                st.session_state._worker_df = pd.DataFrame(columns=["Worker Name", "Hours Worked"])

        conn.close()
        st.session_state._prefilled = True

    tab1, tab2, tab3 = st.tabs(["General", "Safety", "Worker Details"])

    with tab1:
        st.date_input("Date (YYYY-MM-DD):", key="date")
        st.text_area("Description of the day's work:", key="description", height=100)

    with tab2:
        st.write("Safety Equipment Used:")
        st.checkbox("Hard Hat Used", key="hard_hat_used")
        st.checkbox("Gloves Used", key="gloves_used")
        st.checkbox("Eye Protection Used", key="eye_protection_used")
        st.checkbox("Ear Protection Used", key="ear_protection_used")
        st.checkbox("Footwear Used", key="footware_used")
        st.checkbox("Dust Mask Used", key="dust_mask_used")
        st.text_input("Other PPE Used:", key="other_ppe_used")

    with tab3:
        st.write("Worker Hours:")
        edit_df = st.data_editor(
            st.session_state.get("_worker_df", pd.DataFrame(columns=["Worker Name", "Hours Worked"])),
            num_rows="dynamic"
        )

    if st.button("Submit"):
        conn = sqlite3.connect('report_log.db')
        submit_report(
            conn=conn,
            date=st.session_state.date,
            selected_project_id=st.session_state.selected_project_id,
            description=st.session_state.description,
            hard_hat_used=st.session_state.hard_hat_used,
            gloves_used=st.session_state.gloves_used,
            eye_protection_used=st.session_state.eye_protection_used,
            ear_protection_used=st.session_state.ear_protection_used,
            footware_used=st.session_state.footware_used,
            dust_mask_used=st.session_state.dust_mask_used,
            other_ppe_used=st.session_state.other_ppe_used,
            worker_hours=st.session_state.get("_worker_df", pd.DataFrame(columns=["Worker Name", "Hours Worked"]))
        )
        conn.close()
        st.session_state._prefilled = False  # reset for next open
        st.success("Report submitted successfully!")
        st.rerun()
        st.session_state.show_form = False  # Close the dialog after submission


def submit_report(conn, selected_project_id, date, description, hard_hat_used, gloves_used, eye_protection_used, ear_protection_used, footware_used, dust_mask_used, other_ppe_used, worker_hours):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Reports (ProjectID, Date, Description, HardHatUsed, GlovesUsed, EyeProtectionUsed, EarProtectionUsed, FootwearUsed, DustMaskUsed, OtherPPEUsed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (selected_project_id, date, description, hard_hat_used, gloves_used, eye_protection_used, ear_protection_used, footware_used, dust_mask_used, other_ppe_used))
    cursor.execute("Insert INTO ProjectWorkers (ReportID, WorkerName, WorkerHours) VALUES (?, ?, ?)", (cursor.lastrowid, "", 0))  # Insert a dummy row to get the ReportID
    report_id = cursor.lastrowid  # Get the ReportID of the newly inserted report

    for _, row in worker_hours.iterrows():
        name = row["Worker Name"]
        hours = row["Hours Worked"]

        if not name or pd.isna(hours):
            continue  # skip blank rows

        cursor.execute('''
            INSERT INTO ProjectWorkers (ReportID, WorkerName, WorkerHours)
            VALUES (?, ?, ?)
        ''', (report_id, name.strip(), float(hours)))
    conn.commit()

# @st.dialog("Report Form")
# def show_report_form():
#     tab1, tab2, tab3 = st.tabs(["General", "Safety", "Worker Details"])

#     with tab1:
#         date = st.date_input("Date (YYYY-MM-DD):", key="date")
#         description = st.text_area("Description of the day's work:", key="description", height=100)


#     with tab2:
#         st.write("Safety Equipment Used:")
#         hard_hat_used = st.checkbox("Hard Hat Used", key="hard_hat_used")
#         gloves_used = st.checkbox("Gloves Used", key="gloves_used")
#         eye_protection_used = st.checkbox("Eye Protection Used", key="eye_protection_used")
#         ear_protection_used = st.checkbox("Ear Protection Used", key="ear_protection_used")
#         footware_used = st.checkbox("Footwear Used", key="footware_used")
#         dust_mask_used = st.checkbox("Dust Mask Used", key="dust_mask_used")
#         other_ppe_used = st.text_input("Other PPE Used:", key="other_ppe_used")

#     with tab3:
#         st.write("Worker Hours:")
#         df = pd.DataFrame(columns=["Worker Name", "Hours Worked"])
#         edit_df = st.data_editor(df, num_rows="dynamic", key="worker_hours_df")

#     if st.button("Submit"):
#         # access values via st.session_state.date, st.session_state.title, etc.
#         conn = sqlite3.connect('report_log.db')  # replace with actual database connection
#         submit_report(
#             conn=conn,  # replace with actual database connection
#             date=st.session_state.date,
#             description=st.session_state.description,
#             hard_hat_used=st.session_state.hard_hat_used,
#             gloves_used=st.session_state.gloves_used,
#             eye_protection_used=st.session_state.eye_protection_used,
#             ear_protection_used=st.session_state.ear_protection_used,
#             footware_used=st.session_state.footware_used,
#             dust_mask_used=st.session_state.dust_mask_used,
#             other_ppe_used=st.session_state.other_ppe_used
#         )
#         conn.close()
#         st.success("Report submitted successfully!")
#         st.session_state.show_form = False
#         st.rerun()

# def submit_report(conn, date, description, hard_hat_used, gloves_used, eye_protection_used, ear_protection_used, footware_used, dust_mask_used, other_ppe_used):
#     cursor = conn.cursor()
#     cursor.execute('''
#         INSERT INTO Reports (Date, Description, HardHatUsed, GlovesUsed, EyeProtectionUsed, EarProtectionUsed, FootwareUsed, DustMaskUsed, OtherPPEUsed)
#         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
#     ''', (date, description, hard_hat_used, gloves_used, eye_protection_used, ear_protection_used, footware_used, dust_mask_used, other_ppe_used))
#     conn.commit()

# def fill_report_form(dict_result):
#     st.session_state.date = pd.to_datetime("today").date()  # default to today's date
#     st.session_state.description = dict_result.get("Description", "")
#     st.session_state.hard_hat_used = dict_result.get("HardHatUsed", False)
#     st.session_state.gloves_used = dict_result.get("GlovesUsed", False)
#     st.session_state.eye_protection_used = dict_result.get("EyeProtectionUsed", False)
#     st.session_state.ear_protection_used = dict_result.get("EarProtectionUsed", False)
#     st.session_state.footware_used = dict_result.get("FootwearUsed", False)
#     st.session_state.dust_mask_used = dict_result.get("DustMaskUsed", False)
#     st.session_state.other_ppe_used = dict_result.get("OtherPPEUsed", False)
#     st.session_state.worker_hours_df = pd.DataFrame.from_dict(dict_result.get("WorkerHours", {}), orient="index", columns=["Hours Worked"])
