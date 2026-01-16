from celery.schedules import crontab

from settings.environment import env

# Celery Configuration
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/1')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'default'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Moscow'
CELERY_ENABLE_UTC = True

CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes

# Celery Beat (scheduled tasks)
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Периодические задачи
CELERY_BEAT_SCHEDULE = {
    # Очистка старых записей избранного каждое воскресенье в 4:00 ночи
    'cleanup-old-favorite-actions': {
        'task': 'products.cleanup_old_favorite_actions',
        'schedule': crontab(hour=4, minute=0, day_of_week='sunday'),
        'kwargs': {'days': 90},
    },
    # Агрегация дневной статистики каждый день в 1:00 ночи
    'aggregate-daily-stats': {
        'task': 'analytics.aggregate_daily_stats',
        'schedule': crontab(hour=1, minute=0),
    },
    # Очистка старых событий аналитики каждое воскресенье в 3:00 ночи
    'cleanup-old-analytics-events': {
        'task': 'analytics.cleanup_old_events',
        'schedule': crontab(hour=3, minute=0, day_of_week='sunday'),
        'kwargs': {'days': 90},
    },
}
