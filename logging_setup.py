# logging_setup.py
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def get_logger():
    return logging.getLogger()