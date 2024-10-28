import streamlit as st
import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError, ClientError

# Load environment variables for AWS credentials
load_dotenv()

# AWS credentials from environment variables (if needed)
# aws_access_key_id = os.getenv('YOUR_ACCESS_KEY_ID')
# aws_secret_access_key = os.getenv('YOUR_SECRET_ACCESS_KEY')
region_name = 'eu-north-1'

# S3 Bucket names
order_bucket = 'order-data-bucket-final-one'
returns_bucket = 'returns-data-bucket-final-one'

def assume_role(role_arn):
    """Assumes an IAM role and returns temporary credentials."""
    sts_client = boto3.client('sts', region_name=region_name)
    try:
        assumed_role = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName='StreamlitSession'
        )
        return assumed_role['Credentials']
    except ClientError as e:
        st.error(f"Failed to assume role: {e}")
        return None

def upload_to_s3(file_data, bucket_name, file_name):
    """Uploads a file to the specified S3 bucket."""
    try:
        # Assume the role to get temporary credentials
        role_arn = 'arn:aws:iam::975049989132:role/final'  # Update with your role ARN
        credentials = assume_role(role_arn)

        if credentials:
            # Create S3 client with temporary credentials
            s3 = boto3.client(
                's3',
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken'],
                region_name=region_name
            )
            s3.upload_fileobj(file_data, bucket_name, file_name)
            return f"Upload successful: {file_name}"
        else:
            return "Failed to obtain credentials."
    except NoCredentialsError:
        return "Credentials not available."
    except ClientError as e:
        return f"Error uploading file: {e}"

# Streamlit app title
st.title('Upload Order and Returns Data')

# File uploader widget
uploaded_file = st.file_uploader("Upload your order or returns file", type=["csv", "xlsx"])

# Select the team (Order or Returns)
team_option = st.selectbox("Select the team", ["Order Team", "Returns Team"])

if uploaded_file is not None:
    # Display the file name
    st.write(f"Uploaded file: {uploaded_file.name}")

    # Select the correct bucket based on the team
    bucket_name = order_bucket if team_option == "Order Team" else returns_bucket

    # Button to upload file to S3
    if st.button("Upload to S3"):
        try:
            # Upload the file to the selected S3 bucket
            result = upload_to_s3(uploaded_file, bucket_name, uploaded_file.name)
            st.success(result)
        except Exception as e:
            st.error(f"Error uploading file: {e}")
