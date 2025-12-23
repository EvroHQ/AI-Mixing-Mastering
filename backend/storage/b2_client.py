"""
Backblaze B2 Storage Client
Handles file upload/download with signed URLs
"""

from b2sdk.v2 import B2Api, InMemoryAccountInfo
from config.settings import settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class B2Client:
    """Backblaze B2 storage client"""
    
    def __init__(self):
        """Initialize B2 API client"""
        info = InMemoryAccountInfo()
        self.b2_api = B2Api(info)
        
        # Authorize
        self.b2_api.authorize_account(
            "production",
            settings.B2_APPLICATION_KEY_ID,
            settings.B2_APPLICATION_KEY
        )
        
        logger.info("B2 client initialized successfully")
    
    def upload_file(
        self, 
        file_content: bytes, 
        file_name: str, 
        bucket_name: str
    ) -> str:
        """
        Upload file to B2 bucket
        
        Args:
            file_content: File bytes
            file_name: Name/path for the file in bucket
            bucket_name: Target bucket name
            
        Returns:
            File path in bucket
        """
        try:
            bucket = self.b2_api.get_bucket_by_name(bucket_name)
            
            # Upload file
            file_info = bucket.upload_bytes(
                file_content,
                file_name
            )
            
            logger.info(f"Uploaded {file_name} to {bucket_name}")
            return file_name
            
        except Exception as e:
            logger.error(f"Error uploading file to B2: {e}")
            raise
    
    def download_file(
        self, 
        file_name: str, 
        bucket_name: str
    ) -> bytes:
        """
        Download file from B2 bucket
        
        Args:
            file_name: Name/path of the file in bucket
            bucket_name: Source bucket name
            
        Returns:
            File content as bytes
        """
        try:
            bucket = self.b2_api.get_bucket_by_name(bucket_name)
            
            logger.info(f"Downloading file: {file_name} from bucket: {bucket_name}")
            
            # Download file
            downloaded_file = bucket.download_file_by_name(file_name)
            
            # Save to bytes
            import io
            buffer = io.BytesIO()
            downloaded_file.save(buffer)
            file_content = buffer.getvalue()
            
            logger.info(f"Downloaded {len(file_content)} bytes")
            return file_content
            
        except Exception as e:
            logger.error(f"Error downloading file from B2: {e}")
            raise
    
    def get_download_url(
        self, 
        file_name: str, 
        bucket_name: str, 
        expiry_seconds: int = 86400
    ) -> str:
        """
        Generate signed download URL
        
        Args:
            file_name: Name/path of the file in bucket
            bucket_name: Source bucket name
            expiry_seconds: URL expiry time (default 24 hours)
            
        Returns:
            Signed download URL
        """
        try:
            bucket = self.b2_api.get_bucket_by_name(bucket_name)
            
            # Get download authorization token
            auth_token = bucket.get_download_authorization(
                file_name_prefix=file_name,
                valid_duration_in_seconds=expiry_seconds
            )
            
            # Get the download URL from bucket info
            download_url = self.b2_api.get_download_url_for_file_name(
                bucket_name, 
                file_name
            )
            
            # Add authorization token
            signed_url = f"{download_url}?Authorization={auth_token}"
            
            logger.info(f"Generated signed URL for {file_name}")
            return signed_url
            
        except Exception as e:
            logger.error(f"Error generating download URL: {e}")
            raise
    
    def delete_file(
        self, 
        file_name: str, 
        bucket_name: str
    ):
        """
        Delete file from B2 bucket
        
        Args:
            file_name: Name/path of the file in bucket
            bucket_name: Source bucket name
        """
        try:
            bucket = self.b2_api.get_bucket_by_name(bucket_name)
            
            # List file versions
            file_versions = bucket.ls(file_name, latest_only=True)
            
            # Delete each version
            for file_version, _ in file_versions:
                self.b2_api.delete_file_version(
                    file_version.id_,
                    file_version.file_name
                )
            
            logger.info(f"Deleted {file_name} from {bucket_name}")
            
        except Exception as e:
            logger.error(f"Error deleting file from B2: {e}")
            raise
    
    def list_files(
        self, 
        bucket_name: str, 
        prefix: Optional[str] = None
    ) -> list:
        """
        List files in B2 bucket
        
        Args:
            bucket_name: Bucket name
            prefix: Optional prefix filter
            
        Returns:
            List of file names
        """
        try:
            bucket = self.b2_api.get_bucket_by_name(bucket_name)
            
            files = []
            for file_version, _ in bucket.ls(prefix or "", latest_only=True):
                files.append(file_version.file_name)
            
            logger.info(f"Listed {len(files)} files from {bucket_name}")
            return files
            
        except Exception as e:
            logger.error(f"Error listing files from B2: {e}")
            raise
