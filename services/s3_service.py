import os
import uuid
from pathlib import Path
from flask import current_app
from werkzeug.utils import secure_filename

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


class S3Service:
    """Service handling file uploads to AWS S3 using boto3, with automatic local fallback."""

    @classmethod
    def get_s3_client(cls):
        """Initializes and returns a boto3 S3 client using IAM role or configured credentials."""
        if not BOTO3_AVAILABLE:
            return None

        bucket = current_app.config.get('S3_BUCKET_NAME')
        if not bucket:
            return None

        region = current_app.config.get('AWS_REGION', 'us-east-1')
        aws_key = current_app.config.get('AWS_ACCESS_KEY_ID')
        aws_secret = current_app.config.get('AWS_SECRET_ACCESS_KEY')

        try:
            # If explicit credentials provided (e.g. local dev testing)
            if aws_key and aws_secret:
                return boto3.client(
                    's3',
                    region_name=region,
                    aws_access_key_id=aws_key,
                    aws_secret_access_key=aws_secret
                )
            # Otherwise use default provider chain (IAM Instance Role on EC2)
            return boto3.client('s3', region_name=region)
        except Exception as e:
            current_app.logger.warning(f"Failed to initialize S3 client: {e}")
            return None

    @classmethod
    def is_s3_configured(cls):
        """Checks if S3 bucket name is specified and client can be initialized."""
        return bool(cls.get_s3_client())

    @classmethod
    def upload_file(cls, file_obj, original_filename, folder='documents'):
        """
        Uploads a file to AWS S3 if configured; otherwise saves to local upload directory.
        Returns tuple: (s3_key_or_relative_path, storage_backend)
        """
        sec_name = secure_filename(original_filename) or 'file'
        unique_prefix = uuid.uuid4().hex[:10]
        s3_key = f"{folder}/{unique_prefix}_{sec_name}"

        s3_client = cls.get_s3_client()
        bucket = current_app.config.get('S3_BUCKET_NAME')

        if s3_client and bucket:
            try:
                # Guess Content-Type or let boto3 handle it
                file_obj.seek(0)
                s3_client.upload_fileobj(
                    file_obj,
                    bucket,
                    s3_key,
                    ExtraArgs={'ServerSideEncryption': 'AES256'}  # S3 Server-side encryption standard
                )
                return s3_key, 'S3'
            except Exception as e:
                current_app.logger.error(f"Error uploading file to S3: {e}. Falling back to local storage.")

        # Local Fallback
        upload_dir = Path(current_app.config['UPLOAD_FOLDER']) / folder
        upload_dir.mkdir(parents=True, exist_ok=True)
        local_path = upload_dir / f"{unique_prefix}_{sec_name}"
        
        file_obj.seek(0)
        file_obj.save(str(local_path))
        
        # Save relative storage key
        relative_key = f"{folder}/{unique_prefix}_{sec_name}"
        return relative_key, 'Local'

    @classmethod
    def generate_download_url(cls, s3_key, storage_backend='S3', expires_in=3600):
        """
        Generates an authorized AWS S3 presigned URL for secure download,
        or returns None if stored locally (served via Flask route).
        """
        if storage_backend == 'S3':
            s3_client = cls.get_s3_client()
            bucket = current_app.config.get('S3_BUCKET_NAME')
            if s3_client and bucket:
                try:
                    url = s3_client.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': bucket, 'Key': s3_key},
                        ExpiresIn=expires_in
                    )
                    return url
                except Exception as e:
                    current_app.logger.error(f"Error generating S3 presigned URL: {e}")
        return None

    @classmethod
    def get_local_file_path(cls, s3_key):
        """Returns the absolute path to a locally stored file."""
        return Path(current_app.config['UPLOAD_FOLDER']) / s3_key

    @classmethod
    def delete_file(cls, s3_key, storage_backend='S3'):
        """Deletes file from S3 or local filesystem."""
        if storage_backend == 'S3':
            s3_client = cls.get_s3_client()
            bucket = current_app.config.get('S3_BUCKET_NAME')
            if s3_client and bucket:
                try:
                    s3_client.delete_object(Bucket=bucket, Key=s3_key)
                    return True
                except Exception as e:
                    current_app.logger.error(f"Failed to delete S3 object {s3_key}: {e}")
                    return False
        else:
            local_path = cls.get_local_file_path(s3_key)
            if local_path.exists():
                try:
                    local_path.unlink()
                    return True
                except Exception as e:
                    current_app.logger.error(f"Failed to delete local file {local_path}: {e}")
                    return False
        return True
