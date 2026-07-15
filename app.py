import streamlit as st
# streamlit run app.py to run app

st.set_page_config(page_title="Daily Report Log")  # keep browser consistent

# remember if a user is logged in
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "UserID" not in st.session_state:
    st.session_state.UserID = None

if "UserName" not in st.session_state:
    st.session_state.UserName = None

if "FirstName" not in st.session_state:
    st.session_state.FirstName = None

if "LastName" not in st.session_state:
    st.session_state.LastName = None


def LogoutUser():  # log the user out and clear their information
    st.session_state.logged_in = False
    st.session_state.UserID = None
    st.session_state.UserName = None
    st.session_state.FirstName = None
    st.session_state.LastName = None
    st.session_state.show_form = False
    st.session_state.customer_type = None
    st.rerun()


def logout_page():  # logout page
    st.title("Logout")

    st.write(
        f"You are logged in as "
        f"{st.session_state.FirstName} {st.session_state.LastName}."
    )

    if st.button("Logout", type="primary"):
        LogoutUser()


Home_page = st.Page("home.py", title="Home Page")  # create home page
# create page for creating reports
create_report_page = st.Page("create_report.py", title="Create Report Page")
all_reports_page = st.Page("all_reports.py", title="All Reports")  # create report page
project_page = st.Page("project_page.py", title="Projects")  # create project page
feedback_page = st.Page("feedback.py", title="Feedback")  # create feedback page
logout_page = st.Page(logout_page, title="Logout")  # create logout page


if st.session_state.logged_in:
    pg = st.navigation([
        create_report_page,
        all_reports_page,
        project_page,
        feedback_page,
        logout_page
    ])  # show all pages when the user is logged in

else:
    pg = st.navigation([
        Home_page
    ])  # only show the home page until the user logs in


pg.run()