from dataclasses import dataclass
from environs import Env


@dataclass
class BotConfig:
    """Класс для хранения токена бота и списка идентификаторов админов."""
    token: str
    admin_ids: list[int]


@dataclass
class WebhookConfig:
    nginx_host: str
    webhook_host: str
    webhook_path: str
    webhook_url: str



def load_bot_config() -> BotConfig:
    """
    Функция получения токена бота и идентификаторов админов из переменных окружения.

    Аргументы:
        None: функция ничего не принимает.
    Возвращает:
        BotConfig: объект датакласса BotConfig, содержащий в себе токен бота и список идентификаторов админов.
    """
    env: Env = Env()
    env.read_env()

    return BotConfig(
            token=env('BOT_TOKEN'),
            admin_ids=list(map(int, env.list('ADMIN_IDS')))
        )


def load_webhook_config():
    env: Env = Env()
    env.read_env()
    return WebhookConfig(
        nginx_host=env('NGINX_HOST'),
        webhook_host=f'https://{env('NGINX_HOST')}',
        webhook_path='/webhook',
        webhook_url=f'https://{env('NGINX_HOST')}/webhook'
    )


def load_db_URL() -> str:
    """
    Функция получения данных о бд из переменных окружения и составления из них шаблон URL базы данных.

    Аргументы:
        None: функция ничего не принимает.

    Возвращает:
        str: шаблон URL базы данных.
    """
    env: Env = Env()
    env.read_env()
    database = env('DATABASE')
    db_user = env('DB_USER')
    db_password = env('DB_PASSWORD')
    db_host = env('DB_HOST')
    db_port = env('DB_PORT')
    return (f"://{db_user}:{db_password}@"
            f"{db_host}:{db_port}/{database}")