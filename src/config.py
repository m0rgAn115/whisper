import os
import logging
from dotenv import load_dotenv
from openai import OpenAI

def configure_app(app):
    """Configure the Flask app with logging and OpenAI client."""
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv()
    app.config['OPENAI_CLIENT'] = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))