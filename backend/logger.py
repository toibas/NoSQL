# IMPORTS
import time
import os
import logging

# MAIN CODE
def create_logger(name, level, stream: bool = True, file: bool = True,
                  format: str = '%(msecs)dms at %(asctime)s -> %(name)s:%(levelname)s:  %(message)s'):
    """Erstellt und konfiguriert einen Logger mit optionaler Ausgabe in die Konsole und/oder Datei.

    Args:
        name (str): Name des Loggers.
        level (int/str): Logging-Level (z. B. logging.DEBUG, logging.INFO).
        stream (bool, optional): Gibt an, ob Logs in der Konsole ausgegeben werden. Standard: True.
        file (bool, optional): Gibt an, ob Logs in einer Datei gespeichert werden. Standard: True.
        format (str, optional): Log-Formatierung. Standard: '%(msecs)dms at %(asctime)s -> %(name)s:%(levelname)s:  %(message)s'.

    Returns:
        logging.Logger: Der konfigurierte Logger.
        
    Autor Florian 
    """
    if not os.path.exists('./logs/'):
        os.mkdir('./logs/')
    file_location = f'./logs/{time.strftime("%Y%m%d")}.log'

    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(format)
    if stream:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    if file:
        file_handler = logging.FileHandler(filename=file_location, mode='a')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    logger.info('Logger created.')
    return logger