import logging

from os import getenv


def check_log_level():
    log_level_str = getenv("LOG_LEVEL", "3")

    try:
        log_level_int = int(log_level_str)
    except ValueError:
        log_level_int = 3  

    levels = {
        4: logging.DEBUG,
        3: logging.INFO,
        2: logging.WARNING,
        1: logging.ERROR,
        0: logging.CRITICAL
    }

    log_level = levels.get(log_level_int, logging.INFO)

    return log_level


def create_logger():
    return logging.getLogger(__name__)


def configure_log():
    
    nivel_log = check_log_level()

    logging.basicConfig(
        level=nivel_log,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S"
    )
    logger = create_logger()
    logger.log(nivel_log, f"Nível de log configurado: {logging.getLevelName(nivel_log)}")
    return
