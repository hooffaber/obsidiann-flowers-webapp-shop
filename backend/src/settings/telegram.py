from settings.environment import env

# Telegram Bot settings
TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN', default='')
TELEGRAM_BOT_USERNAME = env('TELEGRAM_BOT_USERNAME', default='')

# Mini App settings
TELEGRAM_MINI_APP_URL = env('TELEGRAM_MINI_APP_URL', default='')

# Init data validation
TELEGRAM_AUTH_TIMEOUT = env.int('TELEGRAM_AUTH_TIMEOUT', default=86400)  # 24 hours
