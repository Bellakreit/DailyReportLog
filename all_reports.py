import streamlit as st

def btnSeeAllReports_Click():
    st.session_state.show_all_reports = True

see_all = st.button("See All Reports", type="primary", on_click=btnSeeAllReports_Click)
search_query = st.text_input("Search by username or date (YYYY-MM-DD)", help="Enter a username or date to search for specific reports.")    