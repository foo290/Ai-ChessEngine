import os

# This should be absolute path of a directory.
# If LOG_FILE_PATH = None, OR '' OR '.' :
#   BACKUP_FILE_PATH will be used to store log files
LOG_FILE_PATH = ''

INDIVIDUAL_LOGGING = False  # If True, the log file name will be same as python modules which are logging it.
COMBINED_LOGGING = False  # If True, will make a single file to dump all logs from every module of project.

COMBINED_LOG_FILE_NAME = 'logfile.log'

LOG_ON_CONSOLE = True  # If true, will also display logs on console.

FULL_FILE_PATH = os.path.join(LOG_FILE_PATH, COMBINED_LOG_FILE_NAME)

# Backup location is set to this very directory.
# Use :
#   In "Permission Denied" Exception
#   If LOG_FILE_PATH is empty or relative
BACKUP_FILE_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/Logs"

# Color formats for log text
Black = "\033[0;30m"
Red = "\033[0;31m"
Green = "\033[0;32m"
Yellow = "\033[0;33m"
Blue = "\033[0;34m"
Purple = "\033[0;35m"
Cyan = "\033[1;36m"
White = "\033[0;37m"
Bold_red = "\x1b[31;21m"
reset = "\033[0m"
high_green = '\033[1;93m'

#  Log Formats
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOGGING_FORMAT = '[%(levelname)s] - |%(asctime)s| - [%(name)s : LN : %(lineno)d] - %(message)s'

# Level Formats configurations
LEVEL_FORMATS = {
    "DEBUG": Purple + LOGGING_FORMAT + reset,
    "INFO": Green + LOGGING_FORMAT + reset,
    "WARNING": Yellow + LOGGING_FORMAT + reset,
    "ERROR": Red + LOGGING_FORMAT + reset,
    "CRITICAL": Bold_red + LOGGING_FORMAT + reset,
}
