from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

###################################################ACTIVATE ALL FOR PRODUCTION
class StaticStorage(S3Boto3Storage):
    location="ONLY ACTIVATE IF YOU WANT TO SERVE STATIC FILES FROM S3"
    # location = settings.AWS_STATIC_LOCATION

class PublicMediaStorage(S3Boto3Storage):
    location = settings.AWS_PUBLIC_MEDIA_LOCATION
    file_overwrite = False
    def __init__(self, acl=None, bucket=None, **settings):
        super(PublicMediaStorage, self).__init__(acl, bucket, **settings)

class PrivateMediaStorage(S3Boto3Storage):
    location = settings.AWS_PRIVATE_MEDIA_LOCATION
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False
    def __init__(self, acl=None, bucket=None, **settings):
        super(PrivateMediaStorage, self).__init__(acl, bucket, **settings)
