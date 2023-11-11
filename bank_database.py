import boto3
import decimal
import streamlit as st
import streamlit_authenticator as stauth

# Initialize AWS credentials
AWS_ACCESS_KEY_ID = st.secrets["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = st.secrets["AWS_SECRET_ACCESS_KEY"]
AWS_REGION = 'ap-south-1'  # Replace with your desired AWS region

# Initialize a DynamoDB client
dynamodb = boto3.client('dynamodb', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

def save_bank_details(username, account_no, ifsc_code, company_name, bank_name,
                                transaction_type, amount, narration, beneficiary_name, email):
        
    # DynamoDB table name for bank details
    dynamodb_table_name = 'bank_details'

    # Ensure that 'amount' is stored as a string with 'N' type annotation
    amount_str = str(amount)

    # Create an item dictionary with non-null attributes
    item = {
        'username': {'S': username},
        'transaction_type': {'S': transaction_type},
        'account_no': {'S': account_no},
        'amount': {'N': amount_str},  # Store 'amount' as a string with 'N' type annotation
        'bank_name': {'S': bank_name},
        'company_name': {'S': company_name},
        'beneficiary_name': {'S': beneficiary_name},
        'ifsc_code': {'S': ifsc_code},
    }

    # Only add 'narration' and 'email' if they are not null
    if narration:
        item['narration'] = {'S': narration}
    if email:
        item['email'] = {'S': email}

    try:
        # Save the bank details to DynamoDB
        dynamodb.put_item(
            TableName=dynamodb_table_name,
            Item=item
        )

        return "Bank details saved successfully."
    except Exception as e:
        return "Bank details are not saved due to an error: " + str(e)    

def update_bank_details(company_name, bank_name, account_no, updated_details):
    dynamodb_table_name = 'bank_details'
    print(company_name)
    print(bank_name)
    print(account_no)
    print(updated_details)

    # Prepare the key for identifying the record
    key = {
        'company_name': {'S': company_name},
        'account_no': {'S': account_no}
    }

    # Prepare the expression for updating the record
    update_expression = "SET "
    expression_attribute_values = {}
    for detail_key, value in updated_details.items():
        # Ensure the attribute name in the update expression does not conflict with primary key attribute names
        if detail_key not in key:
            update_expression += f"{detail_key} = :{detail_key}, "
            expression_attribute_values[f":{detail_key}"] = {'S': value if isinstance(value, str) else str(value)}

    # Remove the trailing comma and space from the update expression
    update_expression = update_expression.rstrip(", ")

    try:
        # Update the bank details in DynamoDB
        dynamodb.update_item(
            TableName=dynamodb_table_name,
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
        return "Bank details updated successfully."
    except Exception as e:
        return f"Failed to update bank details: {e}"


def get_unique_company_names():
    dynamodb_table_name = 'bank_details'

    try:
        response = dynamodb.scan(
            TableName=dynamodb_table_name,
            ProjectionExpression="company_name"
        )

        items = response.get("Items", [])

        # Extract unique company names from DynamoDB items
        unique_company_names = set()
        for item in items:
            company_name = item.get("company_name", {}).get("S", "")
            if company_name:
                unique_company_names.add(company_name)

        return sorted(list(unique_company_names))

    except Exception as e:
        return []

def get_unique_bank_names():
    dynamodb_table_name = 'bank_details'

    try:
        response = dynamodb.scan(
            TableName=dynamodb_table_name,
            ProjectionExpression="bank_name"
        )

        items = response.get("Items", [])

        # Extract unique bank names from DynamoDB items
        unique_bank_names = set()
        for item in items:
            bank_name = item.get("bank_name", {}).get("S", "")
            if bank_name:
                unique_bank_names.add(bank_name)

        return sorted(list(unique_bank_names))

    except Exception as e:
        return []

def get_matching_bank_details(company_name, bank_name):
    dynamodb_table_name = 'bank_details'

    try:
        if company_name and bank_name:
            response = dynamodb.scan(
                TableName=dynamodb_table_name,
                FilterExpression="company_name = :company_name AND bank_name = :bank_name",
                ExpressionAttributeValues={
                    ":company_name": {"S": company_name},
                    ":bank_name": {"S": bank_name}
                }
            )
        elif company_name:
            response = dynamodb.scan(
                TableName=dynamodb_table_name,
                FilterExpression="company_name = :company_name",
                ExpressionAttributeValues={
                    ":company_name": {"S": company_name}
                }
            )
        elif bank_name:
            response = dynamodb.scan(
                TableName=dynamodb_table_name,
                FilterExpression="bank_name = :bank_name",
                ExpressionAttributeValues={
                    ":bank_name": {"S": bank_name}
                }
            )
        else:
            # Return an empty list if both company_name and bank_name are None
            return get_all_bank_details()

        items = response.get("Items", [])

        # Convert DynamoDB items to a list of dictionaries
        matching_bank_details = []
        for item in items:
            bank_detail = {
                "username": item.get("username", {}).get("S", ""),
                "transaction_type": item.get("transaction_type", {}).get("S", ""),
                "account_no": item.get("account_no", {}).get("S", ""),
                "amount": float(item.get("amount", {}).get("N", 0.0)),
                "bank_name": item.get("bank_name", {}).get("S", ""),
                "company_name": item.get("company_name", {}).get("S", ""),
                "narration": item.get("narration", {}).get("S", ""),
                "beneficiary_name": item.get("beneficiary_name", {}).get("S", ""),
                "ifsc_code": item.get("ifsc_code", {}).get("S", ""),
                "email": item.get("email", {}).get("S", "")
            }
            matching_bank_details.append(bank_detail)

        return matching_bank_details

    except Exception as e:
        return []

def get_all_bank_details():
    dynamodb_table_name = 'bank_details'

    try:
        response = dynamodb.scan(TableName=dynamodb_table_name)
        items = response.get("Items", [])

        # Convert DynamoDB items to a list of dictionaries
        all_bank_details = []
        for item in items:
            print(item)
            bank_detail = {
                "username": item.get("username", {}).get("S", ""),
                "transaction_type": item.get("transaction_type", {}).get("S", ""),
                "account_no": item.get("account_no", {}).get("S", ""),
                "amount": float(item.get("amount", {}).get("N", item.get("amount", {}).get("S", "0.0"))),
                "bank_name": item.get("bank_name", {}).get("S", ""),
                "company_name": item.get("company_name", {}).get("S", ""),
                "narration": item.get("narration", {}).get("S", ""),
                "beneficiary_name": item.get("beneficiary_name", {}).get("S", ""),
                "ifsc_code": item.get("ifsc_code", {}).get("S", ""),
                "email": item.get("email", {}).get("S", "")
            }
            all_bank_details.append(bank_detail)

        return all_bank_details

    except Exception as e:
        return None
