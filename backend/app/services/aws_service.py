import os
from venv import logger

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError

from ..core.config_settings import settings


class AwsService:
    s3_client = boto3.client('s3')

    def __init__(self):
        self.aws_access_key = settings.AWS_ACCESS_KEY_ID
        self.aws_secret_key = settings.AWS_SECRET_ACCESS_KEY
        self.bucket_name = settings.S3_BUCKET_NAME
        self.is_s3_connected()

    # Upload the file
    def is_s3_connected(self):
        """
            Check if the AWS S3 service is connected by attempting to list the objects in the specified bucket.

            :param bucket_name: Name of the S3 bucket to check connectivity.
            :return: True if connected, False otherwise.
            """
        try:

            # Try to access the bucket by listing its contents (limited to 1 item)
            self.s3_client.list_objects_v2(Bucket=self.bucket_name, MaxKeys=1)
            print(f"Successfully connected to the S3 bucket: {self.bucket_name}")
            logger.info(f"Successfully connected to the S3 bucket: {self.bucket_name}")
            return True
        except NoCredentialsError:
            print("AWS credentials not found.")
        except PartialCredentialsError:
            print("Incomplete AWS credentials configuration.")
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            print(f"Failed to connect to S3. Error: {error_code}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        return False

    def upload_file(self, file_name, object_name=None):
        """Upload a file to an S3 bucket

        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """

        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(file_name)

        try:
            response = self.s3_client.upload_file(file_name, self.bucket_name, object_name)

            if response is None:
                pre_signed_url = self.create_presigned_url(object_name, 900)
                return pre_signed_url

        except ClientError as e:
            # logging.error(e)
            raise ClientError(f"Failed to upload the file: {e}")

    def create_presigned_url(self, object_name, expiration=900):
        """Generate a pre-signed URL to share an S3 object

        :param object_name: string
        :param expiration: Time in seconds for the pre-signed URL to remain valid
        :return: Pre-signed URL as string. If error, returns None.
        """

        try:
            response = self.s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': self.bucket_name,
                                                                'Key': object_name},
                                                        ExpiresIn=expiration)
        except ClientError as e:
            # logging.error(e)
            raise ClientError(f"Failed to generate pre-signed url: {e}")

        # The response contains the pre-signed URL
        return response
