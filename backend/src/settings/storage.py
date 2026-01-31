from settings.environment import env

# File storage settings
USE_S3 = env.bool('USE_S3', default=False)

if USE_S3:
    # S3 / R2 / MinIO compatible storage
    _s3_options = {
        'access_key': env('AWS_ACCESS_KEY_ID', default=''),
        'secret_key': env('AWS_SECRET_ACCESS_KEY', default=''),
        'bucket_name': env('AWS_STORAGE_BUCKET_NAME', default='flower-shop-media'),
        'region_name': env('AWS_S3_REGION_NAME', default='us-east-1'),
        'file_overwrite': False,
        'default_acl': env('AWS_DEFAULT_ACL', default='public-read'),
    }

    # Optional settings
    if env('AWS_S3_ENDPOINT_URL', default=''):
        _s3_options['endpoint_url'] = env('AWS_S3_ENDPOINT_URL')

    if env('AWS_S3_CUSTOM_DOMAIN', default=''):
        _s3_options['custom_domain'] = env('AWS_S3_CUSTOM_DOMAIN')

    if env('AWS_LOCATION', default=''):
        _s3_options['location'] = env('AWS_LOCATION')

    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
            'OPTIONS': _s3_options,
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
        },
    }
else:
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
        },
    }

# Image settings
MAX_UPLOAD_SIZE = env.int('MAX_UPLOAD_SIZE', default=10 * 1024 * 1024)  # 10MB
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']
