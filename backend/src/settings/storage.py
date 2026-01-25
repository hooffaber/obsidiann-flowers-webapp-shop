from settings.environment import env

# File storage settings
USE_S3 = env.bool('USE_S3', default=False)

if USE_S3:
    # S3 / R2 / MinIO compatible storage
    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
            'OPTIONS': {
                'access_key': env('AWS_ACCESS_KEY_ID', default=''),
                'secret_key': env('AWS_SECRET_ACCESS_KEY', default=''),
                'bucket_name': env('AWS_STORAGE_BUCKET_NAME', default='flower-shop-media'),
                'endpoint_url': env('AWS_S3_ENDPOINT_URL', default=None),
                'region_name': env('AWS_S3_REGION_NAME', default='us-east-1'),
                'custom_domain': env('AWS_S3_CUSTOM_DOMAIN', default=None),
                'file_overwrite': False,
                'default_acl': 'public-read',
            },
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }
else:
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }

# Image settings
MAX_UPLOAD_SIZE = env.int('MAX_UPLOAD_SIZE', default=10 * 1024 * 1024)  # 10MB
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']
