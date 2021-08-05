import logging
import os
import sys
from logger import configs as cfg

__all__ = [
    'get_custom_logger'
]


class CustomFormatter(logging.Formatter):
    """
    A custom formatter class which set colors and format.
    """

    FORMATS = {
        logging.DEBUG: cfg.LEVEL_FORMATS["DEBUG"],
        logging.INFO: cfg.LEVEL_FORMATS["INFO"],
        logging.WARNING: cfg.LEVEL_FORMATS["WARNING"],
        logging.ERROR: cfg.LEVEL_FORMATS["ERROR"],
        logging.CRITICAL: cfg.LEVEL_FORMATS["CRITICAL"],
    }

    def format(self, record) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt=cfg.DATE_FORMAT)
        return formatter.format(record)


def _get_valid_filepath(file_name: str, file_path: str) -> str:
    """
    This function creates the directory and file (if not exist) for log file.
    """

    if not file_name.endswith('.log'):
        # Checks and put the relevant extension for log files
        file_name: str = f"{file_name}.log"

    full_path: str = os.path.join(file_path, file_name)

    try:
        if os.path.exists(full_path):
            # If path is valid, means file is already there, return path
            return full_path

        if not os.path.exists(file_path):
            # This block creates folder (if specified and not exist).
            os.makedirs(file_path)

        if not os.path.exists(full_path):
            # This block create empty log file by given name in specified directory.
            open(full_path, 'w').close()

        return full_path
    except (OSError, PermissionError):
        return os.path.join(cfg.BACKUP_FILE_PATH, file_name)


def _get_local_file_handler(valid_file_path, level, formatter) -> logging.FileHandler:
    local_file_handler = logging.FileHandler(valid_file_path)
    local_file_handler.setLevel(level)
    local_file_handler.setFormatter(formatter)

    return local_file_handler


def _get_global_file_handler(valid_file_path, level, formatter) -> logging.FileHandler:
    global_file_handler = logging.FileHandler(valid_file_path)
    global_file_handler.setLevel(level)
    global_file_handler.setFormatter(formatter)

    return global_file_handler


class _Logger(logging.Logger):
    def __init__(self, name):
        super().__init__(name)

    def tlog(self, msg, prefix="[LOG]"):
        print(f"{cfg.high_green}{prefix} [{self.name}] : {msg}{cfg.reset}")


def get_custom_logger(name, level=logging.DEBUG, console_output: bool = True,
                      make_combined_logs: bool = cfg.COMBINED_LOGGING,
                      make_individual_logs: bool = cfg.INDIVIDUAL_LOGGING
                      ) -> logging.Logger:
    """
    This function is supposed to be called whenever you want to make a logger.
    :param name: name of the module, set it to __name__
    :param level: level of logging. default if debug.
    :param console_output: If true, will also display logs on console.
    :param make_combined_logs: If True, will make a single file to dump all logs from every module of project.
    :param make_individual_logs: if True, the log file name will be same as python modules which are logging it.
    :return: an instance of Logger class.
    """

    formatter = CustomFormatter()

    _logger = _Logger(name)

    log_file_path: str = cfg.LOG_FILE_PATH

    if log_file_path == '' or log_file_path is None or log_file_path == '.':
        # if absolute path is not given, File will be created in backup location specified.
        log_file_path = cfg.BACKUP_FILE_PATH

    # Adding file handlers

    if make_combined_logs:
        # Here, the name of the file is same for each instance
        combined_file_name: str = cfg.COMBINED_LOG_FILE_NAME

        valid_file_path: str = _get_valid_filepath(combined_file_name, log_file_path)
        global_file_handler = _get_global_file_handler(valid_file_path, level, formatter)

        _logger.addHandler(global_file_handler)

    if make_individual_logs:
        # Here, the name of the file is same as name of the python module logger is used in.
        individual_file_name: str = name

        valid_file_path: str = _get_valid_filepath(individual_file_name, log_file_path)
        local_file_handler = _get_local_file_handler(valid_file_path, level, formatter)

        _logger.addHandler(local_file_handler)

    if console_output:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(level)
        stream_handler.setFormatter(formatter)

        _logger.addHandler(stream_handler)

    return _logger
