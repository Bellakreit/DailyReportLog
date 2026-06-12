import streamlit as st
# streamlit run OraWigs_app.py to run app
Home_page = st.Page("home.py", title="Home Page")  # creat home page
create_report_page = st.Page("create_report.py", title="Create Report Page")  # create page for creating reports
all_reports_page = st.Page("all_reports.py", title="All Reports")  #  create report page

pg = st.navigation([Home_page, create_report_page, all_reports_page])  # make a navigation for the pages
st.set_page_config(page_title="Daily Report Log")  # keep browser consistent
pg.run()