import os
from flask import Flask
from resources.utilities import create_logger
from resources import setup

app = setup(os.getenv('FLASK_CONFIG') or 'default')
logger = create_logger('main')

if __name__ == '__main__':
    logger.info("Starting main app")
    app.run()
