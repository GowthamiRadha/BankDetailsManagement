import streamlit as st
import streamlit_authenticator as stauth
import user_database as db
import bank_database as bank_db
import yaml
import time

# Define the clear_form_fields function at the global scope
def clear_form_fields():
    # Clear form fields after submission
    st.experimental_rerun()

st.title("Bank Details Management System")
st.sidebar.header("")
st.sidebar.info(
    '''Web Application For Bank Details Management'''
)

# Initialize the authenticator outside the main function
authenticator = None

def get_authenticator():
    with open('.streamlit/config.yaml') as file:
        config = yaml.load(file, Loader=yaml.SafeLoader)

    users = db.fetch_all_users()

    credentials = {}
    credentials['usernames'] = {}

    for user in users:
        username = user.get('username', None)
        name = user.get('name', None)
        password = user.get('password', None)
        role = user.get('role', '')  # Assuming 'role' attribute exists

        # Skip if any value is None
        if username is None or name is None or password is None:
            continue

        # Convert to string to be safe
        username = str(username)
        name = str(name)
        password = str(password)

        credentials['usernames'][username] = {}
        credentials['usernames'][username]['email'] = username
        credentials['usernames'][username]['name'] = name
        credentials['usernames'][username]['password'] = password
        credentials['usernames'][username]['role'] = role  # Store the 'role' attribute

    authenticator = stauth.Authenticate(
                credentials,
                config['cookie']['name'],
                config['cookie']['key'],
                config['cookie']['expiry_days'],
                config['preauthorized']
            )

    return authenticator

def login(authenticator):
    name, authentication_status, username = authenticator.login("Login", "main")
    return username, authentication_status
    
def main():
    global authenticator  # Use the global authenticator variable

    if authenticator is None:
        authenticator = get_authenticator()

    username, authentication_status = login(authenticator)

    if authentication_status is None:
        st.warning("Please enter username and password")

    elif authentication_status is False:
        st.error("Username/Password is incorrect")

    if authentication_status == True:  # Authentication successful
        user_role = db.get_user_role(username)

        if user_role == "admin":

            # Sidebar navigation options for all users
            menu = ["Add User", "Add Bank Details", "Get Bank Details","Update Bank Details"]
            selected_option = st.sidebar.selectbox("NavigationOptions", menu,key="unique")
            st.sidebar.markdown("---")  # Separator line
            if selected_option == "Add User":
                st.subheader("Add New User")
                with st.form("userForm", clear_on_submit=True):
                    email = st.text_input("UserName(Email)")
                    name = st.text_input("Name")
                    password = st.text_input("Password",type='password')
                    role = st.selectbox("Role",('user','admin'))
                    submitted = st.form_submit_button("Register")
                    if submitted:
                        if name=="" or name is None:
                            st.error("Name cannot be empty")
                        elif username=="" or username is None:
                            st.error("Username cannot be empty")
                        elif len(password)<6:
                            st.error("Password must have atleast 6 characters.")
                        else:
                            details = db.save_user(email, name, password, role)
                            success_message = st.empty()
                            success_message.success(details)
                            time.sleep(5)
                            success_message.empty()
            elif selected_option== "Add Bank Details":
                st.subheader("Add Bank Details")
                with st.form("bankForm", clear_on_submit=True):
                    username = st.text_input("Username (Email)")
                    account_no = st.text_input("Account Number")
                    ifsc_code = st.text_input("IFSC Code")
                    company_name = st.text_input("Company Name")
                    bank_name = st.text_input("Bank Name")
                    
                    transaction_type = st.selectbox("Transaction Type", ("", "Yes", "No"))
                    amount = st.number_input("Amount")
                    narration = st.text_area("Narration")
                    beneficiary_name = st.text_input("Beneficiary Name")
                    email = st.text_input("Email (Optional)")
                    
                    submitted = st.form_submit_button("Submit")
                    if submitted:
                        # Validate and save bank details here
                        if not username or not account_no or not ifsc_code or not company_name or not bank_name:
                            st.error("Please fill in all required fields.")
                        # Check if 'amount' is a valid number (you can add additional validation if needed)
                        elif not isinstance(amount, (int, float)):
                            st.error("Amount must be a valid number.")
                        else:
                            # Save the bank details to the database (you need to implement this)
                            details = bank_db.save_bank_details(
                                username, account_no, ifsc_code, company_name, bank_name,
                                transaction_type, amount, narration, beneficiary_name, email
                            )
                            success_message = st.empty()
                            success_message.success(details)
                            time.sleep(5)
                            success_message.empty()
            elif selected_option=="Get Bank Details":
                st.subheader("Get Bank Details")

                # Retrieve all unique Company Names and Bank Names from the database
                unique_company_names = bank_db.get_unique_company_names()
                unique_bank_names = bank_db.get_unique_bank_names()

                # Create a form for searching by Company Name and Bank Name
                with st.form("searchForm", clear_on_submit=False):
                    search_company_name = st.selectbox("Company Name", [""] + unique_company_names)
                    search_bank_name = st.selectbox("Bank Name", [""] + unique_bank_names)
                    search_submitted = st.form_submit_button("Search")

                if search_submitted:
                    # Remove the empty string ("") from the selected options
                    if search_company_name == "":
                        search_company_name = None
                    if search_bank_name == "":
                        search_bank_name = None

                    # Query DynamoDB to retrieve bank details based on Company Name and Bank Name
                    matching_bank_details = bank_db.get_matching_bank_details(search_company_name, search_bank_name)

                    if matching_bank_details:
                        # Display a table of matching bank details
                        st.write("Matching Bank Details:")
                        st.table(matching_bank_details)

                    else:
                        st.warning("No matching bank details found.")
            elif selected_option == "Update Bank Details":
                st.subheader("Update Bank Details")

                if 'update_mode' not in st.session_state:
                    st.session_state.update_mode = False
                    st.session_state.matching_bank_details = []

                if not st.session_state.update_mode:
                    with st.form("updateSearchForm"):
                        unique_company_names = bank_db.get_unique_company_names()
                        unique_bank_names = bank_db.get_unique_bank_names()
                        update_search_company_name = st.selectbox("Company Name", [""] + unique_company_names)
                        update_search_bank_name = st.selectbox("Bank Name", [""] + unique_bank_names)
                        update_search_submitted = st.form_submit_button("Search")

                        if update_search_submitted:
                            matching_bank_details = bank_db.get_matching_bank_details(update_search_company_name, update_search_bank_name)
                            if matching_bank_details:
                                st.session_state.update_mode = True
                                st.session_state.matching_bank_details = matching_bank_details
                            else:
                                st.warning("No matching records found.")

                if st.session_state.update_mode:
                    with st.form("updateForm"):
                        bank_records = [f"{detail['username']}({detail['account_no']})" for detail in st.session_state.matching_bank_details]
                        selected_record = st.selectbox("Select Record", bank_records, key='recordSelect')
                        transaction_type = st.selectbox("Transaction Type", ("", "Yes", "No"))
                        amount = st.number_input("Amount", value=0.0, key='amount')
                        narration = st.text_area("Narration", key='narration')
                        email = st.text_input("Email (Optional)", key='email')
                        update_submitted = st.form_submit_button("Update")

                        if update_submitted:
                            selected_detail = next((detail for detail in st.session_state.matching_bank_details if f"{detail['username']}({detail['account_no']})" == selected_record), None)
                            if selected_detail:
                                company_name = selected_detail['company_name']
                                bank_name = selected_detail['bank_name']
                                account_no = selected_detail['account_no']

                                updated_details = {}
                                if transaction_type != "":
                                    updated_details['transaction_type'] = transaction_type
                                if amount != 0.0:  # assuming 0.0 means no input
                                    updated_details['amount'] = str(amount)
                                if narration != "":
                                    updated_details['narration'] = narration
                                if email != "":
                                    updated_details['email'] = email

                                update_status = ""
                                if updated_details == {}:
                                    update_status = "Nothing to Update"
                                else:
                                    update_status = bank_db.update_bank_details(company_name, bank_name, account_no, updated_details)
                                
                                st.session_state.update_mode = False  # Reset the form state
                                success_message = st.empty()
                                success_message.success(update_status)
                                time.sleep(5)
                                success_message.empty()
                                st.experimental_rerun()
                            else:
                                st.error("Selected record details not found.")
        else:
            menu = ["Add Bank Details", "Get Bank Details","Update Bank Details"]
            selected_option = st.sidebar.selectbox("NavigationOptions", menu,key="unique")
            st.sidebar.markdown("---")  # Separator line
            if selected_option== "Add Bank Details":
                st.subheader("Add Bank Details")
                with st.form("bankForm", clear_on_submit=True):
                    username = st.text_input("Username (Email)")
                    account_no = st.text_input("Account Number")
                    ifsc_code = st.text_input("IFSC Code")
                    company_name = st.text_input("Company Name")
                    bank_name = st.text_input("Bank Name")
                    
                    transaction_type = st.selectbox("Transaction Type", ("", "Yes", "No"))
                    amount = st.number_input("Amount")
                    narration = st.text_area("Narration")
                    beneficiary_name = st.text_input("Beneficiary Name")
                    email = st.text_input("Email (Optional)")
                    
                    submitted = st.form_submit_button("Submit")
                    if submitted:
                        # Validate and save bank details here
                        if not username or not account_no or not ifsc_code or not company_name or not bank_name:
                            st.error("Please fill in all required fields.")
                        # Check if 'amount' is a valid number (you can add additional validation if needed)
                        elif not isinstance(amount, (int, float)):
                            st.error("Amount must be a valid number.")
                        else:
                            # Save the bank details to the database (you need to implement this)
                            details = bank_db.save_bank_details(
                                username, account_no, ifsc_code, company_name, bank_name,
                                transaction_type, amount, narration, beneficiary_name, email
                            )
                            success_message = st.empty()
                            success_message.success(details)
                            time.sleep(5)
                            success_message.empty()
            elif selected_option=="Get Bank Details":
                st.subheader("Get Bank Details")

                # Retrieve all unique Company Names and Bank Names from the database
                unique_company_names = bank_db.get_unique_company_names()
                unique_bank_names = bank_db.get_unique_bank_names()

                # Create a form for searching by Company Name and Bank Name
                with st.form("searchForm", clear_on_submit=False):
                    search_company_name = st.selectbox("Company Name", [""] + unique_company_names)
                    search_bank_name = st.selectbox("Bank Name", [""] + unique_bank_names)
                    search_submitted = st.form_submit_button("Search")

                if search_submitted:
                    # Remove the empty string ("") from the selected options
                    if search_company_name == "":
                        search_company_name = None
                    if search_bank_name == "":
                        search_bank_name = None

                    # Query DynamoDB to retrieve bank details based on Company Name and Bank Name
                    matching_bank_details = bank_db.get_matching_bank_details(search_company_name, search_bank_name)

                    if matching_bank_details:
                        # Display a table of matching bank details
                        st.write("Matching Bank Details:")
                        st.table(matching_bank_details)

                    else:
                        st.warning("No matching bank details found.")
            elif selected_option == "Update Bank Details":
                st.subheader("Update Bank Details")

                if 'update_mode' not in st.session_state:
                    st.session_state.update_mode = False
                    st.session_state.matching_bank_details = []

                if not st.session_state.update_mode:
                    with st.form("updateSearchForm"):
                        unique_company_names = bank_db.get_unique_company_names()
                        unique_bank_names = bank_db.get_unique_bank_names()
                        update_search_company_name = st.selectbox("Company Name", [""] + unique_company_names)
                        update_search_bank_name = st.selectbox("Bank Name", [""] + unique_bank_names)
                        update_search_submitted = st.form_submit_button("Search")

                        if update_search_submitted:
                            matching_bank_details = bank_db.get_matching_bank_details(update_search_company_name, update_search_bank_name)
                            if matching_bank_details:
                                st.session_state.update_mode = True
                                st.session_state.matching_bank_details = matching_bank_details
                            else:
                                st.warning("No matching records found.")

                if st.session_state.update_mode:
                    with st.form("updateForm"):
                        bank_records = [f"{detail['username']}({detail['account_no']})" for detail in st.session_state.matching_bank_details]
                        selected_record = st.selectbox("Select Record", bank_records, key='recordSelect')
                        transaction_type = st.selectbox("Transaction Type", ("", "Yes", "No"))
                        amount = st.number_input("Amount", value=0.0, key='amount')
                        narration = st.text_area("Narration", key='narration')
                        email = st.text_input("Email (Optional)", key='email')
                        update_submitted = st.form_submit_button("Update")

                        if update_submitted:
                            selected_detail = next((detail for detail in st.session_state.matching_bank_details if f"{detail['username']}({detail['account_no']})" == selected_record), None)
                            if selected_detail:
                                company_name = selected_detail['company_name']
                                bank_name = selected_detail['bank_name']
                                account_no = selected_detail['account_no']

                                updated_details = {}
                                if transaction_type != "":
                                    updated_details['transaction_type'] = transaction_type
                                if amount != 0.0:  # assuming 0.0 means no input
                                    updated_details['amount'] = str(amount)
                                if narration != "":
                                    updated_details['narration'] = narration
                                if email != "":
                                    updated_details['email'] = email

                                update_status = ""
                                if updated_details == {}:
                                    update_status = "Nothing to Update"
                                else:
                                    update_status = bank_db.update_bank_details(company_name, bank_name, account_no, updated_details)
                                
                                st.session_state.update_mode = False  # Reset the form state
                                success_message = st.empty()
                                success_message.success(update_status)
                                time.sleep(5)
                                success_message.empty()
                                st.experimental_rerun()
                            else:
                                st.error("Selected record details not found.")
        authenticator.logout("Logout","sidebar")

        
if __name__ == "__main__":
    main()