from dotenv import dotenv_values


def load_db_URL() -> str:
    """
    Функция получения данных о бд из переменных окружения и составления из них шаблон URL базы данных.

    Аргументы:
        None: функция ничего не принимает.

    Возвращает:
        str: шаблон URL базы данных.
    """
    env_vars = dotenv_values(".env")
    database = env_vars['DATABASE']
    db_user = env_vars['DB_USER']
    db_password = env_vars['DB_PASSWORD']
    db_host = env_vars['DB_HOST']
    db_port = env_vars['DB_PORT']
    return (f"://{db_user}:{db_password}@"
            f"{db_host}:{db_port}/{database}")