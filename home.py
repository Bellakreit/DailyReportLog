import streamlit as st
import sqlite3
# home page

# remember who is logged in
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

# logic/functions:


def AddUser(conn, UserName, Password, FirstName, LastName, Email, Phone):
    if not UserName or not Password or not FirstName or not LastName or not Email or not Phone:  # checking all fields are filled
        raise ValueError("All fields must be filled in.")  # raise error so the button code can catch it
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO Users (UserName, Password, FirstName, LastName, Email, Phone)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (UserName, Password, FirstName, LastName, Email, Phone))
    conn.commit()

    # return the id of the user we just created
    return cur.lastrowid


def LoginUser(conn, UserName, Password):
    if not UserName or not Password:  # check if fields are empty
        raise ValueError("All fields must be filled in.")  # raise error so the button code can catch it
    # look up user in database
    cur = conn.cursor()

    # first check if username exists
    cur.execute("SELECT * FROM Users WHERE UserName = ?", (UserName,))
    user = cur.fetchone()

    if not user:
        raise ValueError("Username not found.")

    # check password and return the user information
    cur.execute("""
        SELECT UserID, FirstName, LastName
        FROM Users
        WHERE UserName = ? AND Password = ?
    """, (UserName, Password))

    customer = cur.fetchone()

    if not customer:
        raise ValueError("Incorrect password.")

    return customer


# streamlit page:
with st.container(horizontal_alignment="center"):
    st.image("Designer.png", width=350)

st.title("Voice Report PRO", text_alignment="center")  # setting title, header and subheader for home page
st.header("Welcome to the Voice Report Pro", text_alignment="center")
st.subheader("Make your daily report log easy and efficient", text_alignment="center")
st.logo('Designer.png', size='large')


def btnNewUser_Click():  # when the new user button is clicked function
    st.session_state.show_form = True
    st.session_state.customer_type = "new"  # remember which button was clicked


def btnOldUser_Click():  # when the old user button is clicked function
    st.session_state.show_form = True
    st.session_state.customer_type = "existing"  # keep track that the user is existing one


testuser = st.text("Test User:  test-user\nPassword: testpass", text_alignment="center")

btnNewUser = st.button("New User", type="primary", on_click=btnNewUser_Click)
btnOldUser = st.button("Existing User", type="primary", on_click=btnOldUser_Click)

if "show_form" not in st.session_state:  # default for the form is false until the button is clicked
    st.session_state.show_form = False

if "customer_type" not in st.session_state:  # keep track of customer type so we can use correct form
    st.session_state.customer_type = None

if st.session_state.show_form:

    if st.session_state.customer_type == "new":  # if customer is new bring the form so they can be added to database
        customerForm = st.form('Profile')
        customerForm.subheader("New User Profile")  # form subheader
        UserName = customerForm.text_input('User Name')  # form txt boxes to be filled by the user
        # make password stars
        Password = customerForm.text_input('Password', type='password')
        FirstName = customerForm.text_input('First Name')
        LastName = customerForm.text_input('Last Name')
        Email = customerForm.text_input('Email')
        Phone = customerForm.text_input('Phone Number')

        if customerForm.form_submit_button("Save"):
            try:
                conn2 = sqlite3.connect('report_log.db')  # open connection

                # save the new user and get their id
                UserID = AddUser(
                    conn2,
                    UserName,
                    Password,
                    FirstName,
                    LastName,
                    Email,
                    Phone
                )

                conn2.close()  # close connection
                st.session_state.show_form = False  # closes form after saved

                # remember who is logged in
                st.session_state.logged_in = True
                st.session_state.UserID = UserID
                st.session_state.UserName = UserName
                st.session_state.FirstName = FirstName
                st.session_state.LastName = LastName

                st.success("Profile saved!")

                # refresh app so the navigation updates
                st.rerun()

            except ValueError as e:  # if addcustomer found an error because the fields werent all filled
                st.error(str(e))

    elif st.session_state.customer_type == "existing":  # if the customer is existing then bring the form up
        loginForm = st.form('Login')
        loginForm.subheader("Existing User")  # form subheader
        UserName = loginForm.text_input('User Name')  # inputs the username and password and then will be looked up
        Password = loginForm.text_input('Password', type='password')

        if loginForm.form_submit_button("Login"):
            try:
                conn2 = sqlite3.connect('report_log.db')  # open connection
                customer = LoginUser(conn2, UserName, Password)  # retrieve data from db
                conn2.close()  # close connection
                st.session_state.show_form = False  # closes form after pressing login

                # remember who is logged in
                st.session_state.logged_in = True
                st.session_state.UserID = customer[0]
                st.session_state.UserName = UserName
                st.session_state.FirstName = customer[1]
                st.session_state.LastName = customer[2]

                st.success(f"Welcome back {customer[1]} {customer[2]}!")
                # customer[0] = UserID
                # customer[1] = FirstName
                # customer[2] = LastName

                # refresh app so the navigation updates
                st.rerun()

            except ValueError as e:  # if customer was not found print error message
                st.error(str(e))