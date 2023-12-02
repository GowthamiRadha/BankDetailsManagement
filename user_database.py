import boto3
import streamlit as st
import streamlit_authenticator as stauth

# Initialize AWS credentials
AWS_ACCESS_KEY_ID = st.secrets["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = st.secrets["AWS_SECRET_ACCESS_KEY"]
AWS_REGION = 'ap-south-1'  # Replace with your desired AWS region

# Initialize a DynamoDB client
dynamodb = boto3.client('dynamodb', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

def fetch_all_users():
    dynamodb_table_name = 'users'  # Replace with your DynamoDB table name
    
    try:
        # Query the DynamoDB table to fetch all users
        response = dynamodb.scan(TableName=dynamodb_table_name)

        # Assuming your DynamoDB table has attributes like 'username', 'name', 'password', and 'role'
        users = []
        for item in response.get('Items', []):
            username = item.get('username', {}).get('S', '')
            name = item.get('name', {}).get('S', '')
            password = item.get('password', {}).get('S', '')
            role = item.get('role', {}).get('S', '')  # Add this line to fetch the 'role' attribute

            users.append({
                'username': username,
                'name': name,
                'password': password,
                'role': role  # Include 'role' in the user data dictionary
            })

        return users
    except Exception as e:
        st.error(f"An error occurred while fetching users from DynamoDB: {str(e)}")
        return []

def get_user_role(username):
    # Initialize DynamoDB client
    dynamodb = boto3.client('dynamodb', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    try:
        # Query the DynamoDB table to fetch the user's role
        response = dynamodb.get_item(
            TableName='users',
            Key={'username': {'S': username}}
        )

        # Check if the user exists
        if 'Item' in response:
            role = response['Item'].get('role', {}).get('S', '')
            return role
        else:
            return None  # User not found
    except Exception as e:
        print(f"An error occurred while fetching user role from DynamoDB: {str(e)}")
        return None  # Error occurred
    
def save_user(username, name, password, role):
    # DynamoDB table name
    dynamodb_table_name = 'users'

    try:
        # Check if the user already exists in the table
        existing_user = dynamodb.get_item(
            TableName=dynamodb_table_name,
            Key={'username': {'S': username}}
        )

        if 'Item' in existing_user:
            st.error("User with this username already exists.")
            return False

        # If the user doesn't exist, save the new user data to DynamoDB
        passwords = stauth.Hasher([password]).generate()
        dynamodb.put_item(
            TableName=dynamodb_table_name,
            Item={
                'username': {'S': username},
                'name': {'S': name},
                'password': {'S': passwords[0]},
                'role': {'S': role}  # Save the user's role
            }
        )

        return "User saved successfully."
    except Exception as e:
        return "User is not saved!!!!"
    
def delete_user(username):
    # DynamoDB table name
    dynamodb_table_name = 'users'

    try:
        # Check if the user exists in the table
        existing_user = dynamodb.get_item(
            TableName=dynamodb_table_name,
            Key={'username': {'S': username}}
        )

        if 'Item' not in existing_user:
            return False  # User not found

        # If the user exists, delete them from DynamoDB
        dynamodb.delete_item(
            TableName=dynamodb_table_name,
            Key={'username': {'S': username}}
        )

        return True  # User deleted successfully
    except Exception as e:
        return False  # Error occurred during deletion
