import os

from prefect_email import EmailServerCredentials


def create_email_block(email_username, email_password):
    """
    Create email block for automatic sending email by prefect
    Args:
        email_username (str): gmail (eg.example@gmail.com)
        email_password (str): password - app password
    """
    credentials = EmailServerCredentials(
        username=email_username,  ## must be your real email password
        password=email_password,  # must be an app password generated from google settings
    )
    credentials.save("email-block", overwrite=True)


if __name__ == "__main__":
    print("Getting username and password for gamil account")
    username = os.getenv("EMAIL_USERNAME")
    password = os.getenv("EMAIL_PASSWORD")
    create_email_block(email_username=username, email_password=password)
    print("Email block for prefect created successfully")
