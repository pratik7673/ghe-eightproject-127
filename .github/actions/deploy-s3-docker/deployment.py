import os
import boto3
import mimetypes
from botocore.config import Config
from botocore.exceptions import NoCredentialsError

def run():
    try:
        bucket = os.environ['INPUT_BUCKET']
        bucket_region = os.environ['INPUT_BUCKET-REGION']
        dist_folder = os.environ['INPUT_DIST-FOLDER']

        # Ensure AWS credentials are set
        if not os.getenv("AWS_ACCESS_KEY_ID") or not os.getenv("AWS_SECRET_ACCESS_KEY"):
            raise NoCredentialsError

        configuration = Config(region_name=bucket_region)
        s3_client = boto3.client('s3', config=configuration)

        for root, subdirs, files in os.walk(dist_folder):
            for file in files:
                s3_client.upload_file(
                    os.path.join(root, file),
                    bucket,
                    os.path.join(root, file).replace(dist_folder + '/', ''),
                    ExtraArgs={"ContentType": mimetypes.guess_type(file)[0]}
                )

        website_url = f'http://{bucket}.s3-website-{bucket_region}.amazonaws.com'
        
        # Save output for GitHub Actions
        with open(os.environ['GITHUB_OUTPUT'], 'a') as gh_output:
            print(f'website-url={website_url}', file=gh_output)

    except NoCredentialsError:
        print("Error: AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.")

if __name__ == '__main__':
    run()
