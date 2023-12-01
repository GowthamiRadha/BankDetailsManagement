import streamlit as st
import streamlit_authenticator as stauth
import user_database as db
import bank_company_database as bank_db
import yaml
import time
import pandas as pd

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


def get_user_credentials():
    # Fetch and return user credentials from the database
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
    return credentials


def get_authenticator():
    with open('.streamlit/config.yaml') as file:
        config = yaml.load(file, Loader=yaml.SafeLoader)

    credentials = get_user_credentials()

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
        # Initialize session state to store selected company and bank names
        if 'selected_company' not in st.session_state:
            st.session_state.selected_company = None

        if 'bank_names' not in st.session_state:
            st.session_state.bank_names = []
        user_role = db.get_user_role(username)

        if user_role == "admin":

            # Sidebar navigation options for all users
            menu = ["Add User", "Get User Details","Add Company Details","Get Company Details","Add Employee Details", "Get Employee Details","Update Employee Details"]
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
                        print("Submitted User Form")
                        if name=="" or name is None:
                            st.error("Name cannot be empty")
                        elif username=="" or username is None:
                            st.error("Username cannot be empty")
                        elif len(password)<6:
                            st.error("Password must have atleast 6 characters.")
                        else:
                            print("Going to call Save User Details")
                            details = db.save_user(email, name, password, role)
                            print("Response from DB Call", details)
                            success_message = st.empty()
                            success_message.success(details)
                            time.sleep(5)
                            success_message.empty()
            elif selected_option == "Get User Details":
                st.subheader("User Details")
                
                print("Before Calling Fetch all Users")
                # Fetch all user details using db.fetch_all_users
                user_details = db.fetch_all_users()
                print("Response from Get All Users ", user_details)

                if user_details:
                    # Create a DataFrame from the fetched data
                    user_df = pd.DataFrame(user_details)
                    
                    # Exclude the "password" column if it exists
                    if "password" in user_df.columns:
                        user_df = user_df.drop(columns=["password"])
                    
                    # Display the user details in a table
                    st.dataframe(user_df, height=len(user_details)*40)  # Adjust the height based on the number of rows
                    # Add a download button to allow users to download the DataFrame as a CSV file
                    st.download_button(
                        label="Download User Details (CSV)",
                        data=user_df.to_csv(index=False),
                        file_name="user_details.csv",
                        key="download_user_details"
                    )
                else:
                    st.warning("No user details found.")
            elif selected_option == "Add Company Details":
                st.subheader("Add Company Details")

                with st.form("companyForm", clear_on_submit=True):
                    company_name = st.text_input("Company Name*")
                    company_bank_name = st.text_input("Company Bank Name*")
                    company_account_number = st.text_input("Company Account Number*")
                    company_mail_id = st.text_input("Company Mail ID")
                    company_phone_number = st.text_input("Company Phone Number")

                    submitted = st.form_submit_button("Submit")
                    if submitted:
                        print("Submitted Company form with Details")
                        # Validate and save company details here
                        if not company_name or not company_bank_name or not company_account_number:
                            st.error("Please fill in all required fields.")
                        else:
                            # Save the company details to the database
                            # You need to implement the database interaction code here
                            # Use the provided input values for database insertion
                            # For example, you can use a function like 'save_company_details' in your 'bank_db' module
                            # Make sure to handle database errors and provide appropriate feedback to the user
                            success_message = st.empty()
                            try:
                                print("Before Calling Save Company details")
                                details = bank_db.save_company_details(
                                    company_name,
                                    company_bank_name,
                                    company_account_number,
                                    company_mail_id,
                                    company_phone_number
                                )
                                print("Response from save_company_details ", details)
                                success_message.success("Company details saved successfully.")
                            except Exception as e:
                                st.error(f"An error occurred while saving company details: {str(e)}")
                            # Clear the success message after 5 seconds
                            time.sleep(5)
                            success_message.empty()
            elif selected_option == "Get Company Details":
                st.subheader("Get Company Details")

                # Retrieve and display company details here
                # You need to implement the database query to fetch company details
                # For example, you can use a function like 'get_company_details' in your 'bank_db' module
                # Handle any potential errors when fetching data from the database

                try:
                    # Fetch company details from the database using a function like 'get_company_details'
                    company_details = bank_db.get_company_details()
                    
                    if company_details:
                        # Display company details in a tabular format
                        company_df = pd.DataFrame(company_details, columns=["Company Name", "Company Bank Name", "Company Account Number", "Company Mail ID", "Company Phone Number"])
                        st.dataframe(company_df, height=len(company_details) * 40)  # Adjust the height based on the number of rows
                        st.download_button(
                            label="Download Company Details (CSV)",
                            data=company_df.to_csv(index=False),
                            file_name="company_details.csv",
                            key="download_company_details"
                        )
                    else:
                        st.warning("No company details found.")

                except Exception as e:
                    st.error(f"An error occurred while fetching company details: {str(e)}")
            elif selected_option == "Add Employee Details":
                st.subheader("Add Employee Details")

                company_names = bank_db.fetch_company_names()

                # Display a dropdown for selecting the company
                selected_company = st.selectbox("Select Company", company_names)

                with st.form("employeeForm", clear_on_submit=True):
                    beneficiary_name = st.text_input("Beneficiary Name*")
                    account_number = st.text_input("Account Number*")
                    beneficiary_ifsc_code = st.text_input("IFSC Code*")
                    beneficiary_bank_name = st.selectbox("Select Beneficiary's Bank*", ["BankA","BankB","BankC"])
                    transaction_type = st.selectbox("Transaction Type", ("", "NEFT","RTGS", "FT", "N","I"))
                    amount = st.number_input("Amount")
                    narration = st.text_area("Narration")
                    email = st.text_input("Email (Optional)")
                    # Store the selected company in session state
                    st.session_state.selected_company = selected_company
                    bank_names = bank_db.fetch_bank_names(st.session_state.selected_company)
                    # Display a dropdown for selecting the bank name
                    selected_bank = st.selectbox("Select Company's Bank", bank_names)

                    submitted = st.form_submit_button("Submit")
                    if submitted:
                        print("After submitting Employee Form")
                        # Validate and save employee details here
                        if not beneficiary_name or not account_number or not beneficiary_ifsc_code:
                            st.error("Please fill in all required fields.")
                        # Check if 'amount' is a valid number (you can add additional validation if needed)
                        elif not isinstance(amount, (int, float)):
                            st.error("Amount must be a valid number.")
                        else:
                            # Save the employee details to the database using selected_company and selected_bank
                            # You need to implement the database interaction code here
                            # You can use selected_company and selected_bank for database operations
                            print("Before Calling Save Employee Details")
                            success_message = st.empty()
                            details = bank_db.save_employee_details(beneficiary_name, account_number, beneficiary_bank_name, beneficiary_ifsc_code,
                                        transaction_type, amount, narration, selected_company, selected_bank)
                            print("Response from Save employee Details ", details)
                            success_message.success("Employee details saved successfully.")
                            # Clear the success message after 5 seconds
                            st.experimental_set_query_params()
                            time.sleep(5)
                            success_message.empty()
            elif selected_option == "Get Employee Details":
                st.subheader("Get Employee Details")

                # Create a form for searching by Company Name and Company Bank Name
                with st.form("searchForm", clear_on_submit=False):
                    # Retrieve all unique Company Names and Bank Names from the database
                    unique_company_names = bank_db.get_unique_company_names()
                    unique_bank_names = bank_db.get_unique_bank_names()

                    # Display dropdowns for selecting Company Name and Company Bank Name
                    search_company_name = st.selectbox("Company Name", [""] + unique_company_names)
                    search_company_bank_name = st.selectbox("Company Bank Name", [""] + unique_bank_names)
                    search_submitted = st.form_submit_button("Search")

                if search_submitted:
                    # Remove the empty string ("") from the selected options
                    if search_company_name == "":
                        search_company_name = None
                    if search_company_bank_name == "":
                        search_company_bank_name = None

                    # Query the database to retrieve employee details and additional columns from the Company database
                    matching_employee_details = bank_db.get_matching_employee_details(search_company_name, search_company_bank_name)

                    if matching_employee_details:
                        # Display a table of matching employee details
                        df = pd.DataFrame(matching_employee_details, columns=["BeneficiaryName", "AccountNumber", "BeneficiaryBankName", "BeneficiaryIFSCCode", 
                            "TypeOfTransfer", "Amount", "Narration", "CompanyName", "CompanyBankName","CompanyAccountNumber",
                            "CompanyMailID", "CompanyPhoneNumber"])
                        st.write("Matching Employee Details:")
                        st.dataframe(df)
                        st.download_button(
                            label="Download Employee Details (CSV)",
                            data=df.to_csv(index=False),
                            file_name="employee_details.csv",
                            key="download_employee_details"
                        )
                    else:
                        st.warning("No matching employee details found.")
            elif selected_option == "Update Employee Details":
                st.subheader("Update Employee Details")

                if 'update_mode' not in st.session_state:
                    st.session_state.update_mode = False
                    st.session_state.matching_employee_details = []

                if not st.session_state.update_mode:
                    with st.form("updateSearchForm"):
                        unique_company_names = bank_db.get_unique_company_names()
                        unique_bank_names = bank_db.get_unique_bank_names()
                        update_search_company_name = st.selectbox("Company Name", [""] + unique_company_names)
                        update_search_company_bank_name = st.selectbox("Company Bank Name", [""] + unique_bank_names)
                        update_search_submitted = st.form_submit_button("Search")

                        if update_search_submitted:
                            if update_search_company_name == "":
                                update_search_company_name = None
                            if update_search_company_bank_name == "":
                                update_search_company_bank_name = None
                            matching_employee_details = bank_db.get_only_matching_employee_details(update_search_company_name, update_search_company_bank_name)
                            if matching_employee_details:
                                st.session_state.update_mode = True
                                st.session_state.matching_employee_details = matching_employee_details
                            else:
                                st.warning("No matching records found.")

                if st.session_state.update_mode:
                    with st.form("updateForm"):
                        df = pd.DataFrame(st.session_state.matching_employee_details, columns=["BeneficiaryName", "AccountNumber", "BeneficiaryBankName", "BeneficiaryIFSCCode", 
                            "TypeOfTransfer", "Amount", "Narration", "CompanyName", "CompanyBankName"])
                        

                        # Define the columns that cannot be edited
                        non_editable_columns = ["BeneficiaryName", "AccountNumber", "BeneficiaryBankName", "BeneficiaryIFSCCode","CompanyName", "CompanyBankName"]
                        
                        # Create a dictionary to define column configurations
                        column_config = {
                            "Amount": st.column_config.NumberColumn(
                                "Amount",
                                help="The amount of the transfer",
                                min_value=0.0,
                                step = 1.0,
                                format="%.2f"
                            ),
                            "TypeOfTransfer": st.column_config.SelectboxColumn(
                                "TypeOfTransfer",
                                help="Type of transfer",
                                options=["NEFT", "RTGS", "FT", "N", "I"]
                            )
                        }

                        updated_details = st.data_editor(df, disabled = non_editable_columns,column_config = column_config)

                        update_submitted = st.form_submit_button("Update")

                        if update_submitted:
                            if not updated_details.empty:
                                updated_details = updated_details.reset_index()  # Reset the index
                                updated_details = updated_details.to_dict(orient='records')
                                print(updated_details)
                                update_status = bank_db.bulk_update_employee_details(updated_details)
                                st.session_state.update_mode = False  # Reset the form state
                                success_message = st.empty()
                                success_message.success(update_status)
                                time.sleep(5)
                                success_message.empty()
                                st.experimental_rerun()
                            else:
                                st.error("No changes to update.")
        else:
            menu = ["Add Employee Details", "Get Employee Details","Update Employee Details"]
            selected_option = st.sidebar.selectbox("NavigationOptions", menu,key="unique")
            st.sidebar.markdown("---")  # Separator line
            if selected_option == "Add Employee Details":
                st.subheader("Add Employee Details")

                company_names = bank_db.fetch_company_names()

                # Display a dropdown for selecting the company
                selected_company = st.selectbox("Select Company", company_names)

                with st.form("employeeForm", clear_on_submit=True):
                    beneficiary_name = st.text_input("Beneficiary Name*")
                    account_number = st.text_input("Account Number*")
                    beneficiary_ifsc_code = st.text_input("IFSC Code*")
                    beneficiary_bank_name = st.selectbox("Select Beneficiary's Bank*", ["BankA","BankB","BankC"])
                    transaction_type = st.selectbox("Transaction Type", ("", "NEFT","RTGS", "FT", "N","I"))
                    amount = st.number_input("Amount")
                    narration = st.text_area("Narration")
                    email = st.text_input("Email (Optional)")
                    # Store the selected company in session state
                    st.session_state.selected_company = selected_company
                    bank_names = bank_db.fetch_bank_names(st.session_state.selected_company)
                    # Display a dropdown for selecting the bank name
                    selected_bank = st.selectbox("Select Company's Bank", bank_names)

                    submitted = st.form_submit_button("Submit")
                    if submitted:
                        # Validate and save employee details here
                        if not beneficiary_name or not account_number or not beneficiary_ifsc_code:
                            st.error("Please fill in all required fields.")
                        # Check if 'amount' is a valid number (you can add additional validation if needed)
                        elif not isinstance(amount, (int, float)):
                            st.error("Amount must be a valid number.")
                        else:
                            # Save the employee details to the database using selected_company and selected_bank
                            # You need to implement the database interaction code here
                            # You can use selected_company and selected_bank for database operations
                            details = bank_db.save_employee_details(beneficiary_name, account_number, beneficiary_bank_name, beneficiary_ifsc_code,
                                        transaction_type, amount, narration, selected_company, selected_bank)
                            success_message = st.empty()
                            success_message.success("Employee details saved successfully.")
                            # Clear the success message after 5 seconds
                            st.experimental_set_query_params()
                            time.sleep(5)
                            success_message.empty()
            elif selected_option == "Get Employee Details":
                st.subheader("Get Employee Details")

                # Create a form for searching by Company Name and Company Bank Name
                with st.form("searchForm", clear_on_submit=False):
                    # Retrieve all unique Company Names and Bank Names from the database
                    unique_company_names = bank_db.get_unique_company_names()
                    unique_bank_names = bank_db.get_unique_bank_names()

                    # Display dropdowns for selecting Company Name and Company Bank Name
                    search_company_name = st.selectbox("Company Name", [""] + unique_company_names)
                    search_company_bank_name = st.selectbox("Company Bank Name", [""] + unique_bank_names)
                    search_submitted = st.form_submit_button("Search")

                if search_submitted:
                    # Remove the empty string ("") from the selected options
                    if search_company_name == "":
                        search_company_name = None
                    if search_company_bank_name == "":
                        search_company_bank_name = None

                    # Query the database to retrieve employee details and additional columns from the Company database
                    matching_employee_details = bank_db.get_matching_employee_details(search_company_name, search_company_bank_name)

                    if matching_employee_details:
                        # Display a table of matching employee details
                        df = pd.DataFrame(matching_employee_details, columns=["BeneficiaryName", "AccountNumber", "BeneficiaryBankName", "BeneficiaryIFSCCode", 
                            "TypeOfTransfer", "Amount", "Narration", "CompanyName", "CompanyBankName","CompanyAccountNumber",
                            "CompanyMailID", "CompanyPhoneNumber"])
                        st.write("Matching Employee Details:")
                        st.dataframe(df)
                        st.download_button(
                            label="Download Employee Details (CSV)",
                            data=df.to_csv(index=False),
                            file_name="employee_details.csv",
                            key="download_employee_details"
                        )
                    else:
                        st.warning("No matching employee details found.")
            elif selected_option == "Update Employee Details":
                st.subheader("Update Employee Details")

                if 'update_mode' not in st.session_state:
                    st.session_state.update_mode = False
                    st.session_state.matching_employee_details = []

                if not st.session_state.update_mode:
                    with st.form("updateSearchForm"):
                        unique_company_names = bank_db.get_unique_company_names()
                        unique_bank_names = bank_db.get_unique_bank_names()
                        update_search_company_name = st.selectbox("Company Name", [""] + unique_company_names)
                        update_search_company_bank_name = st.selectbox("Company Bank Name", [""] + unique_bank_names)
                        update_search_submitted = st.form_submit_button("Search")

                        if update_search_submitted:
                            if update_search_company_name == "":
                                update_search_company_name = None
                            if update_search_company_bank_name == "":
                                update_search_company_bank_name = None
                            matching_employee_details = bank_db.get_only_matching_employee_details(update_search_company_name, update_search_company_bank_name)
                            if matching_employee_details:
                                st.session_state.update_mode = True
                                st.session_state.matching_employee_details = matching_employee_details
                            else:
                                st.warning("No matching records found.")

                if st.session_state.update_mode:
                    with st.form("updateForm"):
                        df = pd.DataFrame(st.session_state.matching_employee_details, columns=["BeneficiaryName", "AccountNumber", "BeneficiaryBankName", "BeneficiaryIFSCCode", 
                            "TypeOfTransfer", "Amount", "Narration", "CompanyName", "CompanyBankName"])
                        

                        # Define the columns that cannot be edited
                        non_editable_columns = ["BeneficiaryName", "AccountNumber", "BeneficiaryBankName", "BeneficiaryIFSCCode","CompanyName", "CompanyBankName"]
                        
                        # Create a dictionary to define column configurations
                        column_config = {
                            "Amount": st.column_config.NumberColumn(
                                "Amount",
                                help="The amount of the transfer",
                                min_value=0.0,
                                step = 1.0,
                                format="%.2f"
                            ),
                            "TypeOfTransfer": st.column_config.SelectboxColumn(
                                "TypeOfTransfer",
                                help="Type of transfer",
                                options=["NEFT", "RTGS", "FT", "N", "I"]
                            )
                        }

                        updated_details = st.data_editor(df, disabled = non_editable_columns,column_config = column_config)

                        update_submitted = st.form_submit_button("Update")

                        if update_submitted:
                            if not updated_details.empty:
                                updated_details = updated_details.reset_index()  # Reset the index
                                updated_details = updated_details.to_dict(orient='records')
                                print(updated_details)
                                update_status = bank_db.bulk_update_employee_details(updated_details)
                                st.session_state.update_mode = False  # Reset the form state
                                success_message = st.empty()
                                success_message.success(update_status)
                                time.sleep(5)
                                success_message.empty()
                                st.experimental_rerun()
                            else:
                                st.error("No changes to update.")
        authenticator.logout("Logout","sidebar")

        
if __name__ == "__main__":
    main()