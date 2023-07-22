from time import sleep
from prefect_aws import S3Bucket, AwsCredentials
import os

def create_aws_creds_block():
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    if aws_secret_access_key is None:
        raise Exception("You didn't assign the environment variable 'AWS_ACCESS_KEY_ID'")

    if aws_secret_access_key is None:
        raise Exception("You didn't assign the environment variable 'AWS_SECRET_ACCESS_KEY'")

    my_aws_creds_obj = AwsCredentials(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    my_aws_creds_obj.save(name="my-aws-creds", overwrite=True)

def create_s3_bucket_block():
    
    bucket_name = os.getenv("S3_BUCKET_NAME")
    
    if bucket_name is None:
        raise Exception("You didn't assign the environment variable 'S3_BUCKET_NAME'")

    aws_creds = AwsCredentials.load("my-aws-creds")
    my_s3_bucket_obj = S3Bucket(
        bucket_name=bucket_name, credentials=aws_creds
    )
    my_s3_bucket_obj.save(name="s3-final-pj", overwrite=True)

if __name__ == "__main__":
    create_aws_creds_block()
    sleep(5)
    create_s3_bucket_block()