import os


def get_env_value(key):
    if key in os.environ:
        return os.environ[key]
    raise KeyError(f"Environment variable '{key}' not found")

API_TOKEN = get_env_value('API_TOKEN')

# Дані проксі
USE_PROXY_1 = get_env_value('USE_PROXY_1') == 'True'
PROXY_IP_1 = get_env_value('PROXY_IP_1')
PROXY_PORT_1 = get_env_value('PROXY_PORT_1')
PROXY_LOGIN_1 = get_env_value('PROXY_LOGIN_1')
PROXY_PASSWORD_1 = get_env_value('PROXY_PASSWORD_1')

USE_PROXY_2 = get_env_value('USE_PROXY_2') == 'True'
PROXY_IP_2 = get_env_value('PROXY_IP_2')
PROXY_PORT_2 = get_env_value('PROXY_PORT_2')
PROXY_LOGIN_2 = get_env_value('PROXY_LOGIN_2')
PROXY_PASSWORD_2 = get_env_value('PROXY_PASSWORD_2')

USE_PROXY_3 = get_env_value('USE_PROXY_3') == 'True'
PROXY_IP_3 = get_env_value('PROXY_IP_3')
PROXY_PORT_3 = get_env_value('PROXY_PORT_3')
PROXY_LOGIN_3 = get_env_value('PROXY_LOGIN_3')
PROXY_PASSWORD_3 = get_env_value('PROXY_PASSWORD_3')
