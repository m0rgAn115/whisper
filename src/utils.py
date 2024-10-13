import os

SUPPORTED_FORMATS = ['flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm']

def is_valid_audio_format(filename):
    """Check if the audio file format is supported."""
    _, extension = os.path.splitext(filename)
    extension = extension.lower().lstrip('.')
    return extension in SUPPORTED_FORMATS