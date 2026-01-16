import os
from pathlib import Path

import environ

# Initialize environ
env = environ.Env()

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Read .env file if it exists
env_file = BASE_DIR.parent / '.env'
if env_file.exists():
    env.read_env(str(env_file))
