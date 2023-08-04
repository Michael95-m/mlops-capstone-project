from prefect_email import EmailServerCredentials
import os

def create_email_block(username, password):
    credentials = EmailServerCredentials(
        username=username, ## must be your real email password
        password=password,  # must be an app password generated from google settings
    )
    credentials.save("email-block", overwrite=True)

if __name__ == "__main__":
    print("Getting username and password for gamil account")
    username = os.getenv("EMAIL_USERNAME")
    password = os.getenv("EMAIL_PASSWORD")
    create_email_block(username=username, password=password)
    print("Email block for prefect created successfully")