import os
import boto3
import mimetypes
from botocore.config import Config
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def run():
    try:
        # Fetch credentials from environment
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        bucket = os.getenv("INPUT_BUCKET")
        bucket_region = os.getenv("INPUT_BUCKET-REGION")
        dist_folder = os.getenv("INPUT_DIST-FOLDER")

        if not aws_access_key or not aws_secret_key:
            raise NoCredentialsError("AWS credentials are missing!")

        # Debugging: Print credentials (mask for security)
        print(f"AWS_ACCESS_KEY_ID: {aws_access_key[:4]}****")
        print(f"AWS_SECRET_ACCESS_KEY: {aws_secret_key[:4]}****")

        # Set up AWS session manually
        session = boto3.Session(
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=bucket_region
        )
        s3_client = session.client('s3')

        # Upload files to S3
        for root, _, files in os.walk(dist_folder):
            for file in files:
                file_path = os.path.join(root, file)
                s3_client.upload_file(
                    file_path,
                    bucket,
                    file_path.replace(dist_folder + '/', ''),
                    ExtraArgs={"ContentType": mimetypes.guess_type(file)[0]}
                )

        website_url = f'http://{bucket}.s3-website-{bucket_region}.amazonaws.com'
        
        # Save output for GitHub Actions
        with open(os.environ['GITHUB_OUTPUT'], 'a') as gh_output:
            print(f'website-url={website_url}', file=gh_output)

    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    run()
