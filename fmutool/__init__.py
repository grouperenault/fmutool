from colorama import Fore, Style, init
import logging
import sys


def setup_logger():
    class CustomFormatter(logging.Formatter):
        def format(self, record):
            log_format = "%(levelname)-8s | %(message)s"
            format_per_level = {
                logging.DEBUG: str(Fore.BLUE) + log_format,
                logging.INFO: str(Fore.CYAN) + log_format,
                logging.WARNING: str(Fore.YELLOW) + log_format,
                logging.ERROR: str(Fore.RED) + log_format,
                logging.CRITICAL: str(Fore.RED + Style.BRIGHT) + log_format,
            }
            formatter = logging.Formatter(format_per_level[record.levelno])
            return formatter.format(record)
    init()
    logger = logging.getLogger("fmutool")
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(CustomFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger


setup_logger()
