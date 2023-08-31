with open("/run/secrets/app_secret", "r") as fp:
    app_secret = fp.readline()[:-1]

with open("/run/secrets/db_password", "r") as fp:
    db_password = fp.readline()[:-1]


SECRET_KEY = app_secret
CONTENT_ORIGIN = "http://pulp_content:24816"
DATABASES = {"default": {"HOST": "postgres", "ENGINE": "django.db.backends.postgresql", "NAME": "pulp", "USER": "pulp", "PASSWORD": db_password, "PORT": "5432", "CONN_MAX_AGE": 0, "OPTIONS": {"sslmode": "prefer"}}}
DB_ENCRYPTION_KEY = "/run/secrets/db_encryption_key"
CACHE_ENABLED = True
REDIS_HOST = "redis"
REDIS_PORT = 6379
REDIS_PASSWORD = ""
ANSIBLE_API_HOSTNAME = "http://pulp_api:24817"
ANSIBLE_CONTENT_HOSTNAME = "http://pulp_content:24816/pulp/content"
ALLOWED_IMPORT_PATHS = ["/tmp"]
ALLOWED_EXPORT_PATHS = ["/tmp"]
TOKEN_SERVER = "http://pulp_api:24817/token/"
TOKEN_AUTH_DISABLED = False
TOKEN_SIGNATURE_ALGORITHM = "ES256"
PUBLIC_KEY_PATH = "/etc/pulp/keys/container_auth_public_key.pem"
PRIVATE_KEY_PATH = "/etc/pulp/keys/container_auth_private_key.pem"
ANALYTICS = False
STATIC_ROOT = "/var/lib/operator/static/"
