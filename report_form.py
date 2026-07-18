from datetime import datetime
import streamlit as st
import sqlite3
import pandas as pd

@st.dialog("Report Form")
def show_report_form(dict_result=None, selected_project_id=None):

    if selected_project_id is not None:
        st.session_state.selected_project_id = selected_project_id

    if dict_result is None:
        st.session_state._prefilled = False
        st.session_state.edit_report_id = None
        st.session_state._worker_df = pd.DataFrame(columns=["Worker Name", "Hours Worked"])
        st.session_state.date = pd.Timestamp.today().date()
        st.session_state.description = ""
        st.session_state.hard_hat_used = False
        st.session_state.gloves_used = False
        st.session_state.eye_protection_used = False
        st.session_state.ear_protection_used = False
        st.session_state.footware_used = False
        st.session_state.dust_mask_used = False
        st.session_state.other_ppe_used = ""

    elif not st.session_state.get("_prefilled"):
        st.session_state.edit_report_id = dict_result.get("ReportID")

        date_value = dict_result.get("Date", pd.Timestamp.today().date())

        if isinstance(date_value, str):
            date_value = pd.to_datetime(date_value).date()

        st.session_state.date = date_value
        st.session_state.description = dict_result.get("Description", "")
        st.session_state.hard_hat_used = bool(dict_result.get("HardHatUsed", False))
        st.session_state.gloves_used = bool(dict_result.get("GlovesUsed", False))
        st.session_state.eye_protection_used = bool(dict_result.get("EyeProtectionUsed", False))
        st.session_state.ear_protection_used = bool(dict_result.get("EarProtectionUsed", False))
        st.session_state.footware_used = bool(dict_result.get("FootwearUsed", False))
        st.session_state.dust_mask_used = bool(dict_result.get("DustMaskUsed", False))
        st.session_state.other_ppe_used = str(dict_result.get("OtherPPEUsed", "") or "")

        workers = dict_result.get("WorkerHours", {})
        st.session_state._worker_df = pd.DataFrame(
            [(k, v) for k, v in workers.items()],
            columns=["Worker Name", "Hours Worked"],
        ) if workers else pd.DataFrame(columns=["Worker Name", "Hours Worked"])
        st.session_state._prefilled = True

    if "_worker_df" not in st.session_state:
        st.session_state._worker_df = pd.DataFrame(columns=["Worker Name", "Hours Worked"])

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

        edited_worker_df = st.data_editor(
            st.session_state._worker_df,
            num_rows="dynamic",
            key="worker_hours_editor"
        )

    edit_report_id = st.session_state.get("edit_report_id")

    if st.button("Save Changes" if edit_report_id else "Submit"):
        conn = sqlite3.connect("report_log.db")

        if edit_report_id:
            update_report(
                conn=conn,
                report_id=edit_report_id,
                date=st.session_state.date,
                description=st.session_state.description,
                hard_hat_used=st.session_state.hard_hat_used,
                gloves_used=st.session_state.gloves_used,
                eye_protection_used=st.session_state.eye_protection_used,
                ear_protection_used=st.session_state.ear_protection_used,
                footware_used=st.session_state.footware_used,
                dust_mask_used=st.session_state.dust_mask_used,
                other_ppe_used=st.session_state.other_ppe_used,
                worker_hours=edited_worker_df
            )
        else:
            submit_report(
                conn=conn,
                user_id=st.session_state.UserID,
                selected_project_id=st.session_state.get("selected_project_id"),
                date=st.session_state.date,
                description=st.session_state.description,
                hard_hat_used=st.session_state.hard_hat_used,
                gloves_used=st.session_state.gloves_used,
                eye_protection_used=st.session_state.eye_protection_used,
                ear_protection_used=st.session_state.ear_protection_used,
                footware_used=st.session_state.footware_used,
                dust_mask_used=st.session_state.dust_mask_used,
                other_ppe_used=st.session_state.other_ppe_used,
                worker_hours=edited_worker_df
            )

        conn.close()

        st.session_state._prefilled = False
        st.session_state.show_form = False
        st.session_state.edit_report_id = None

        if "worker_hours_editor" in st.session_state:
            del st.session_state["worker_hours_editor"]

        if "_worker_df" in st.session_state:
            del st.session_state["_worker_df"]

        st.session_state.report_saved = True
        st.rerun()


def submit_report(
    conn,
    user_id,
    selected_project_id,
    date,
    description,
    hard_hat_used,
    gloves_used,
    eye_protection_used,
    ear_protection_used,
    footware_used,
    dust_mask_used,
    other_ppe_used,
    worker_hours
):
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO Reports (
            UserID,
            ProjectID,
            Date,
            Description,
            HardHatUsed,
            GlovesUsed,
            EyeProtectionUsed,
            EarProtectionUsed,
            FootwearUsed,
            DustMaskUsed,
            OtherPPEUsed
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        selected_project_id,
        date,
        description,
        hard_hat_used,
        gloves_used,
        eye_protection_used,
        ear_protection_used,
        footware_used,
        dust_mask_used,
        other_ppe_used
    ))

    # This MUST happen immediately after inserting into Reports
    report_id = cursor.lastrowid

    for _, row in worker_hours.iterrows():
        name = row.get("Worker Name")
        hours = row.get("Hours Worked")

        if pd.isna(name) or str(name).strip() == "":
            continue

        if pd.isna(hours) or str(hours).strip() == "":
            continue

        cursor.execute('''
            INSERT INTO ProjectWorkers (
                ReportID,
                WorkerName,
                WorkerHours
            )
            VALUES (?, ?, ?)
        ''', (
            report_id,
            str(name).strip(),
            float(hours)
        ))

    conn.commit()


def update_report(
    conn,
    report_id,
    date,
    description,
    hard_hat_used,
    gloves_used,
    eye_protection_used,
    ear_protection_used,
    footware_used,
    dust_mask_used,
    other_ppe_used,
    worker_hours
):
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE Reports
        SET Date = ?,
            Description = ?,
            HardHatUsed = ?,
            GlovesUsed = ?,
            EyeProtectionUsed = ?,
            EarProtectionUsed = ?,
            FootwearUsed = ?,
            DustMaskUsed = ?,
            OtherPPEUsed = ?
        WHERE ReportID = ?
    ''', (
        date,
        description,
        hard_hat_used,
        gloves_used,
        eye_protection_used,
        ear_protection_used,
        footware_used,
        dust_mask_used,
        other_ppe_used,
        report_id
    ))

    # replace the old worker rows with the edited table
    cursor.execute('DELETE FROM ProjectWorkers WHERE ReportID = ?', (report_id,))

    for _, row in worker_hours.iterrows():
        name = row.get("Worker Name")
        hours = row.get("Hours Worked")

        if pd.isna(name) or str(name).strip() == "":
            continue

        if pd.isna(hours) or str(hours).strip() == "":
            continue

        cursor.execute('''
            INSERT INTO ProjectWorkers (
                ReportID,
                WorkerName,
                WorkerHours
            )
            VALUES (?, ?, ?)
        ''', (
            report_id,
            str(name).strip(),
            float(hours)
        ))

    conn.commit()