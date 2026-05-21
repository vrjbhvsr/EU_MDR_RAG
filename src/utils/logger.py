import logging
import os
from pathlib import Path
import inspect
from colorlog import ColoredFormatter
import inspect

class log:
    def __init__(self):
        

        # Create log directory if it doesn't exist
        self.log_dir = Path("Bug_Tracker/logs")   # All the logs will be saved in logs directory
        self.log_dir.mkdir(exist_ok=True)

        # Define the log file name
        self.file_path= self.log_dir / "app.log" # Log file will be named app.log
        filename = inspect.stack()[1].filename   # Gtting the filename from which .py file the logger is called
        module_name = Path(filename).stem

        self.logger = self._make_logger(self.file_path, module_name)
    # defining a method to create logger
    def _make_logger(self, filepath, logger):
        logger = logging.getLogger(logger)
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.FileHandler(filepath)
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s",datefmt="%Y-%m-%d %H:%M:%S")   # Setting log format how it should be written
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            # 
            console_handler = logging.StreamHandler()

            # Below lines will set the  color for different log levels warning yellow, error red etc.
            color_formatter = ColoredFormatter(
                "%(log_color)s%(asctime)s %(lineno)d %(name)s - %(levelname)s - %(message)s",
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'bold_red',
                }
            )
            console_handler.setFormatter(color_formatter)
            logger.addHandler(console_handler)
        return logger
    
    # defining methods for different log levels
    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

            
    def exception(self, message: str):
        self.logger.exception(message)

    def critical(self, message: str):
        self.logger.critical(message)