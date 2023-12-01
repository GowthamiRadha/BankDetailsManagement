import streamlit as st
import mysql.connector

# Function to establish a database connection
def create_db_connection():
    connection = mysql.connector.connect(
        host = st.secrets["AWS_HOSTNAME"],
        user= st.secrets["AWS_USERNAME"],
        password = st.secrets["AWS_PASSWORD"],
        database = st.secrets["AWS_DATABASE"],
    )
    return connection

# Function to save employee details to the MySQL database
def save_employee_details(beneficiary_name, account_number, beneficiary_bank_name, beneficiary_ifsc_code,
                          type_of_transfer, amount, narration, company_name, company_bank_name):
    try:
        # Create a database connection
        connection = create_db_connection()
        cursor = connection.cursor()
        print("connection ",connection)
        print("cursor ",cursor)

        # Define the SQL query to insert data into the Employee table
        insert_query = """
        INSERT INTO Employee (BeneficiaryName, AccountNumber, BeneficiaryBankName, BeneficiaryIFSCCode,
        TypeOfTransfer, Amount, Narration, CompanyName, CompanyBankName)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        BeneficiaryName = VALUES(BeneficiaryName),
        BeneficiaryBankName = VALUES(BeneficiaryBankName),
        BeneficiaryIFSCCode = VALUES(BeneficiaryIFSCCode),
        TypeOfTransfer = VALUES(TypeOfTransfer),
        Amount = VALUES(Amount),
        Narration = VALUES(Narration)
        """

        # Execute the SQL query with the provided data
        cursor.execute(insert_query, (beneficiary_name, account_number, beneficiary_bank_name, beneficiary_ifsc_code,
                                      type_of_transfer, amount, narration, company_name, company_bank_name))

        # Commit the transaction and close the connection
        connection.commit()
        cursor.close()
        connection.close()

        return "Employee details saved successfully."

    except Exception as e:
        return f"Employee details are not saved due to an error: {str(e)}"  


# Function to fetch unique company names from the Company Database
def fetch_company_names():
    try:
        # Create a database connection
        connection = create_db_connection()
        cursor = connection.cursor()

        # Define the SQL query to fetch unique company names
        select_query = """
        SELECT DISTINCT CompanyName FROM Company
        """

        # Execute the SQL query to fetch company names
        cursor.execute(select_query)
        
        # Fetch all company names
        company_names = [row[0] for row in cursor.fetchall()]

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return company_names

    except Exception as e:
        return []

# Function to fetch bank names based on the selected company
def fetch_bank_names(selected_company):
    try:
        # Create a database connection
        connection = create_db_connection()
        cursor = connection.cursor()

        print(selected_company)

        # Define the SQL query to fetch bank names based on the selected company
        select_query = """
        SELECT DISTINCT CompanyBankName FROM Company
        WHERE CompanyName= %s
        """

        # Execute the SQL query to fetch bank names
        cursor.execute(select_query, (selected_company,))
        #print("---", cursor.fetchall())
        
        # Fetch all bank names
        bank_names = [row[0] for row in cursor.fetchall()]

        # Close the cursor and connection
        cursor.close()
        connection.close()

        print("bank_names", bank_names)
        return bank_names

    except Exception as e:
        return [] 

# Function to fetch unique company names from the Company Database
def get_unique_company_names():
    try:
        # Create a database connection
        connection = create_db_connection()
        cursor = connection.cursor()

        # Define the SQL query to fetch unique company names
        select_query = """
        SELECT DISTINCT CompanyName FROM Company
        """

        # Execute the SQL query to fetch unique company names
        cursor.execute(select_query)

        # Fetch all unique company names
        unique_company_names = [row[0] for row in cursor.fetchall()]

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return unique_company_names

    except Exception as e:
        return []

# Function to fetch unique bank names from the Company Database
def get_unique_bank_names():
    try:
        # Create a database connection
        connection = create_db_connection()
        cursor = connection.cursor()

        # Define the SQL query to fetch unique bank names
        select_query = """
        SELECT DISTINCT CompanyBankName FROM Company
        """

        # Execute the SQL query to fetch unique bank names
        cursor.execute(select_query)

        # Fetch all unique bank names
        unique_bank_names = [row[0] for row in cursor.fetchall()]

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return unique_bank_names

    except Exception as e:
        return []

# Function to get matching employee details based on Company Name and Company Bank Name
def get_matching_employee_details(company_name=None, company_bank_name=None):
    try:
        # Create a database connection
        connection = create_db_connection()
        cursor = connection.cursor()

        # Define the SQL query to fetch employee details with additional columns from the Company table
        select_query = """
        SELECT E.BeneficiaryName, E.AccountNumber, E.BeneficiaryBankName, E.BeneficiaryIFSCCode, E.TypeOfTransfer, E.Amount, E.Narration,
               E.CompanyName, E.CompanyBankName, C.CompanyAccountNumber, C.CompanyMailID, C.CompanyPhoneNumber
        FROM Employee E
        LEFT JOIN Company C ON E.CompanyName = C.CompanyName AND E.CompanyBankName = C.CompanyBankName
        """

        # Create a list to store query conditions
        conditions = []

        # Create a list to store query parameters
        parameters = []

        # Add conditions based on provided criteria
        if company_name is not None:
            conditions.append("E.CompanyName = %s")
            parameters.append(company_name)
        if company_bank_name is not None:
            conditions.append("E.CompanyBankName = %s")
            parameters.append(company_bank_name)

        # Combine conditions into a WHERE clause
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)
            select_query += " " + where_clause

        # Execute the SQL query with parameters
        cursor.execute(select_query, parameters)

        # Fetch all matching employee details
        matching_employee_details = [row for row in cursor.fetchall()]

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return matching_employee_details

    except Exception as e:
        return []

# Function to bulk update employee details in the MySQL database
def bulk_update_employee_details(updated_employee_details):
    try:
        # Create a database connection
        connection = create_db_connection()
        cursor = connection.cursor()

        # Define the SQL query to update employee details
        update_query = """
        UPDATE Employee
        SET TypeOfTransfer = %s, Amount = %s, Narration = %s
        WHERE BeneficiaryName = %s AND AccountNumber = %s AND BeneficiaryBankName = %s
        """

        for employee in updated_employee_details:
            cursor.execute(update_query, (employee["TypeOfTransfer"], employee["Amount"], employee["Narration"],
                                          employee["BeneficiaryName"], employee["AccountNumber"], employee["BeneficiaryBankName"]))

        # Commit the transaction and close the connection
        connection.commit()
        cursor.close()
        connection.close()

        return "Employee details updated successfully."

    except Exception as e:
        return f"Employee details are not updated due to an error: {str(e)}"

# Function to get only matching employee details based on Company Name and Company Bank Name
def get_only_matching_employee_details(company_name=None, company_bank_name=None):
    try:
        # Create a database connection
        connection = create_db_connection()
        cursor = connection.cursor()

        # Define the SQL query to fetch only matching employee details
        select_query = """
        SELECT BeneficiaryName, AccountNumber, BeneficiaryBankName, BeneficiaryIFSCCode, TypeOfTransfer, Amount, Narration, CompanyName, CompanyBankName
        FROM Employee
        """

        # Create a list to store query conditions
        conditions = []

        # Create a list to store query parameters
        parameters = []

        # Add conditions based on provided criteria
        if company_name is not None:
            conditions.append("CompanyName = %s")
            parameters.append(company_name)
        if company_bank_name is not None:
            conditions.append("CompanyBankName = %s")
            parameters.append(company_bank_name)

        # Combine conditions into a WHERE clause
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)
            select_query += " " + where_clause

        # Execute the SQL query with parameters
        cursor.execute(select_query, parameters)

        # Fetch all matching employee details
        matching_employee_details = [row for row in cursor.fetchall()]

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return matching_employee_details

    except Exception as e:
        return []

def save_company_details(company_name, company_bank_name, company_account_number, company_mail_id, company_phone_number):
    try:
        # Create a database connection
        connection = create_db_connection()
        cursor = connection.cursor()
        print("connection in save company details ",connection)
        print("cursor in save company details ",cursor)

        # Define the SQL query to insert data into the Company table
        insert_query = """
        INSERT INTO Company (CompanyName, CompanyBankName, CompanyAccountNumber, CompanyMailID, CompanyPhoneNumber)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        CompanyName = VALUES(CompanyName),
        CompanyBankName = VALUES(CompanyBankName),
        CompanyAccountNumber = VALUES(CompanyAccountNumber),
        CompanyMailID = VALUES(CompanyMailID),
        CompanyPhoneNumber = VALUES(CompanyPhoneNumber)
        """

        # Execute the SQL query with the provided data
        cursor.execute(insert_query, (company_name, company_bank_name, company_account_number, company_mail_id, company_phone_number))

        # Commit the transaction and close the connection
        connection.commit()
        cursor.close()
        connection.close()

        return "Company details saved successfully."

    except Exception as e:
        return f"Company details are not saved due to an error: {str(e)}"

def get_company_details():
    try:
        # Create a database connection
        connection = create_db_connection()
        cursor = connection.cursor()

        # Define the SQL query to fetch company details
        select_query = """
        SELECT CompanyName, CompanyBankName, CompanyAccountNumber, CompanyMailID, CompanyPhoneNumber
        FROM Company
        """

        # Execute the SQL query to fetch company details
        cursor.execute(select_query)

        # Fetch all company details
        company_details = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return company_details

    except Exception as e:
        st.error(f"An error occurred while fetching company details: {str(e)}")
        return []

# def update_bank_details(company_name, bank_name, account_no, updated_details):
#     dynamodb_table_name = 'bank_details'
#     print(company_name)
#     print(bank_name)
#     print(account_no)
#     print(updated_details)

#     # Prepare the key for identifying the record
#     key = {
#         'company_name': {'S': company_name},
#         'account_no': {'S': account_no}
#     }

#     # Prepare the expression for updating the record
#     update_expression = "SET "
#     expression_attribute_values = {}
#     for detail_key, value in updated_details.items():
#         # Ensure the attribute name in the update expression does not conflict with primary key attribute names
#         if detail_key not in key:
#             update_expression += f"{detail_key} = :{detail_key}, "
#             expression_attribute_values[f":{detail_key}"] = {'S': value if isinstance(value, str) else str(value)}

#     # Remove the trailing comma and space from the update expression
#     update_expression = update_expression.rstrip(", ")

#     try:
#         # Update the bank details in DynamoDB
#         dynamodb.update_item(
#             TableName=dynamodb_table_name,
#             Key=key,
#             UpdateExpression=update_expression,
#             ExpressionAttributeValues=expression_attribute_values
#         )
#         return "Bank details updated successfully."
#     except Exception as e:
#         return f"Failed to update bank details: {e}"


# def get_unique_company_names():
#     dynamodb_table_name = 'bank_details'

#     try:
#         response = dynamodb.scan(
#             TableName=dynamodb_table_name,
#             ProjectionExpression="company_name"
#         )

#         items = response.get("Items", [])

#         # Extract unique company names from DynamoDB items
#         unique_company_names = set()
#         for item in items:
#             company_name = item.get("company_name", {}).get("S", "")
#             if company_name:
#                 unique_company_names.add(company_name)

#         return sorted(list(unique_company_names))

#     except Exception as e:
#         return []

# def get_unique_bank_names():
#     dynamodb_table_name = 'bank_details'

#     try:
#         response = dynamodb.scan(
#             TableName=dynamodb_table_name,
#             ProjectionExpression="bank_name"
#         )

#         items = response.get("Items", [])

#         # Extract unique bank names from DynamoDB items
#         unique_bank_names = set()
#         for item in items:
#             bank_name = item.get("bank_name", {}).get("S", "")
#             if bank_name:
#                 unique_bank_names.add(bank_name)

#         return sorted(list(unique_bank_names))

#     except Exception as e:
#         return []

# def get_matching_bank_details(company_name, bank_name):
#     dynamodb_table_name = 'bank_details'

#     try:
#         if company_name and bank_name:
#             response = dynamodb.scan(
#                 TableName=dynamodb_table_name,
#                 FilterExpression="company_name = :company_name AND bank_name = :bank_name",
#                 ExpressionAttributeValues={
#                     ":company_name": {"S": company_name},
#                     ":bank_name": {"S": bank_name}
#                 }
#             )
#         elif company_name:
#             response = dynamodb.scan(
#                 TableName=dynamodb_table_name,
#                 FilterExpression="company_name = :company_name",
#                 ExpressionAttributeValues={
#                     ":company_name": {"S": company_name}
#                 }
#             )
#         elif bank_name:
#             response = dynamodb.scan(
#                 TableName=dynamodb_table_name,
#                 FilterExpression="bank_name = :bank_name",
#                 ExpressionAttributeValues={
#                     ":bank_name": {"S": bank_name}
#                 }
#             )
#         else:
#             # Return an empty list if both company_name and bank_name are None
#             return get_all_bank_details()

#         items = response.get("Items", [])

#         # Convert DynamoDB items to a list of dictionaries
#         matching_bank_details = []
#         for item in items:
#             bank_detail = {
#                 "username": item.get("username", {}).get("S", ""),
#                 "transaction_type": item.get("transaction_type", {}).get("S", ""),
#                 "account_no": item.get("account_no", {}).get("S", ""),
#                 "amount": float(item.get("amount", {}).get("N", 0.0)),
#                 "bank_name": item.get("bank_name", {}).get("S", ""),
#                 "company_name": item.get("company_name", {}).get("S", ""),
#                 "narration": item.get("narration", {}).get("S", ""),
#                 "beneficiary_name": item.get("beneficiary_name", {}).get("S", ""),
#                 "ifsc_code": item.get("ifsc_code", {}).get("S", ""),
#                 "email": item.get("email", {}).get("S", "")
#             }
#             matching_bank_details.append(bank_detail)

#         return matching_bank_details

#     except Exception as e:
#         return []

# def get_all_bank_details():
#     dynamodb_table_name = 'bank_details'

#     try:
#         response = dynamodb.scan(TableName=dynamodb_table_name)
#         items = response.get("Items", [])

#         # Convert DynamoDB items to a list of dictionaries
#         all_bank_details = []
#         for item in items:
#             print(item)
#             bank_detail = {
#                 "username": item.get("username", {}).get("S", ""),
#                 "transaction_type": item.get("transaction_type", {}).get("S", ""),
#                 "account_no": item.get("account_no", {}).get("S", ""),
#                 "amount": float(item.get("amount", {}).get("N", item.get("amount", {}).get("S", "0.0"))),
#                 "bank_name": item.get("bank_name", {}).get("S", ""),
#                 "company_name": item.get("company_name", {}).get("S", ""),
#                 "narration": item.get("narration", {}).get("S", ""),
#                 "beneficiary_name": item.get("beneficiary_name", {}).get("S", ""),
#                 "ifsc_code": item.get("ifsc_code", {}).get("S", ""),
#                 "email": item.get("email", {}).get("S", "")
#             }
#             all_bank_details.append(bank_detail)

#         return all_bank_details

#     except Exception as e:
#         return None
