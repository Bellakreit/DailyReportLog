import streamlit as st
import sqlite3
# home page

# logic/functions:


def AddCustomer(conn, UserName, Password, FirstName, LastName, Email, Phone):
    if not UserName or not Password or not FirstName or not LastName or not Email or not Phone:  # checking all fields are filled
        raise ValueError("All fields must be filled in.")  # raise error so the button code can catch it
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO Customers (UserName, Password, FirstName, LastName, Email, Phone)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (UserName, Password, FirstName, LastName, Email, Phone))
    conn.commit()


def LoginCustomer(conn, UserName, Password):
    if not UserName or not Password:  # check if fields are empty
        raise ValueError("All fields must be filled in.")  # raise error so the button code can catch it
    # look up user in database
    cur = conn.cursor()
    # first check if username exists
    cur.execute("SELECT * FROM Customers WHERE UserName = ?", (UserName,))
    user = cur.fetchone()
    if not user:
        raise ValueError("Username not found.")
    
    # then check if password matches and just select the first and last name to return
    cur.execute("SELECT FirstName, LastName FROM Customers WHERE UserName = ? AND Password = ?", (UserName, Password))
    customer = cur.fetchone()
    if not customer:
        raise ValueError("Incorrect password.")
    
    return customer


# streamlit page:

st.title("Daily Report Log", text_alignment="center")  # setting title, header and subheader for home page
st.header("Welcome to the Daily Report Log", text_alignment="center")
st.subheader("Make your daily report log easy and efficient", text_alignment="center")

def btnNewCustomer_Click():  # when the new customer button is clicked function
    st.session_state.show_form = True
    st.session_state.customer_type = "new"  # remember which button was clicked

def btnOldCustomer_Click():  # when the old customer button is clicked function
    st.session_state.show_form = True
    st.session_state.customer_type = "existing"  # keep track that the customer is existing one

btnNewCustomer = st.button("New Customer", type="primary", on_click=btnNewCustomer_Click)
btnOldCustomer = st.button("Existing Customer", type="primary", on_click=btnOldCustomer_Click)

if "show_form" not in st.session_state:  # default for the form is false until the button is clicked
    st.session_state.show_form = False

if "customer_type" not in st.session_state:  # keep track of customer type so we can use correct form
    st.session_state.customer_type = None

if st.session_state.show_form:

    if st.session_state.customer_type == "new":  # if customer is new bring the form so they can be added to database
        customerForm = st.form('Profile')
        customerForm.subheader("New Customer Profile")  # form subheader
        UserName = customerForm.text_input('User Name')  # form txt boxes to be filled by the user
        Password = customerForm.text_input('Password')
        FirstName = customerForm.text_input('First Name')
        LastName = customerForm.text_input('Last Name')
        Email = customerForm.text_input('Email')
        Phone = customerForm.text_input('Phone Number')
        if customerForm.form_submit_button("Save"):
            try:
                conn2 = sqlite3.connect('OraWigs.db')  # open connection
                AddCustomer(conn2, UserName, Password, FirstName, LastName, Email, Phone)  # uses function to add customer to db
                conn2.close()  # close connection
                st.success("Profile saved!")
                st.session_state.show_form = False  # closes form after saved
            except ValueError as e:  # if addcustomer found an error because the fields werent all filled
                 st.error(str(e))

    elif st.session_state.customer_type == "existing":  # if the customer is existing then bring the form up
        loginForm = st.form('Login')
        loginForm.subheader("Existing Customer")  # form subheader
        UserName = loginForm.text_input('User Name')  # inputs the username and password and then will be looked up
        Password = loginForm.text_input('Password')
        if loginForm.form_submit_button("Login"):
            try:
                conn2 = sqlite3.connect('OraWigs.db')  # open connection
                customer = LoginCustomer(conn2, UserName, Password)  # retrieve data from db
                conn2.close()  # close connection
                st.success(f"Welcome back {customer[0]} {customer[1]}!")
                    # customer[0] = FirstName
                    # customer[1] = LastName
                st.session_state.show_form = False  # closes form  after pressing login
            except ValueError as e:  # if customer was not found print error message
                st.error(str(e))
        