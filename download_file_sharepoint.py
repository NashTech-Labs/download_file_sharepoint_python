from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
import boto3
import json
import os

# retrieve sharepoint password from AWS Secret Manager
def retrieve_password_secret_manager(secretID):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(
        SecretID = secretID
    )
    sharepoint_secrets = json.loads(response['SecretString'])
    password = sharepoint_secrets['password']
    return password

#download file from sharepoint
def download_file_sharepoint(url, username, password, file_url, local_path):
    print("Authenticating with SharePoint")
    #Authentication
    ctx_auth = AuthenticationContext(url)
    if ctx_auth.acquire_token_for_user(username, password):
        ctx = ClientContext(url, ctx_auth)
        web = ctx.web
        ctx.load(web)
        ctx.execute_query()
        print("Authentication Successful")
        print("Web Title: {0}".format(web.properties['Title']))
        
    try:
        download_path = os.path.join(local_path, os.path.basename(file_url))
        with open(download_path, "wb") as local_file:
            file = ctx.web.get_file_by_server_relative_url(file_url).download(local_file).execute_query()
        print("[OK] file has been downloaded into: {0}".format(download_path))
        
    except Exception as E:
        print("File not found in SharePoint Location.")
            

if __name__ == "__main__":
    
    sharepoint_url = os.environ["SHAREPOINT_URL"] #SharePoint URL from where you want to download the file.
    username = os.environ["SHAREPOINT_USERNAME"] #SharePoint Username for authentication
    secretID = os.environ["SECRET_ID"] #SecretID for retrieving the SharePoint password from AWS Secret Manager
    password = retrieve_password_secret_manager(secretID)
    file_url = os.environ["FILE_URL"] #Filepath in SharePoint Loccation
    local_path = os.environ["LOCAL_PATH"] #Local Path where you want to download the file
    
    
    download_file_sharepoint(sharepoint_url, username, password, file_url, local_path)
    