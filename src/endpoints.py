import os
import logging
import tempfile
from flask import jsonify, request
from utils import is_valid_audio_format, SUPPORTED_FORMATS

def register_endpoints(app):
    """Register all endpoints to the Flask app."""

    @app.route('/audio-to-text', methods=['POST'])
    def transcribe_audio():
        """Endpoint to transcribe audio files."""
        if 'audio' not in request.files:
            logging.warning("No audio file found in the request.")
            return jsonify({'error': 'No se encontró el archivo de audio'}), 400

        audio_file = request.files['audio']
        logging.debug(f"Received file: {audio_file.filename}")

        if not is_valid_audio_format(audio_file.filename):
            logging.warning("Invalid audio file format.")
            return jsonify({'error': f'Formato de archivo no válido. Formatos soportados: {", ".join(SUPPORTED_FORMATS)}'}), 400

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.filename)[1]) as temp_file:
                audio_file.save(temp_file)
                temp_file_path = temp_file.name

            file_size = os.path.getsize(temp_file_path)
            if file_size == 0:
                logging.warning("Empty audio file.")
                return jsonify({'error': 'El archivo de audio está vacío'}), 400

            with open(temp_file_path, "rb") as audio_file:
                transcription = app.config['OPENAI_CLIENT'].audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="es"
                )

            os.unlink(temp_file_path)

            text = transcription.text
            logging.debug(f"Transcription obtained: {text}")

            return jsonify({'text': text}), 200
        except Exception as e:
            logging.error(f"Error during transcription: {str(e)}", exc_info=True)
            return jsonify({'error': f'Error al transcribir el audio: {str(e)}'}), 500


    @app.route('/test', methods=['GET'])
    def test():
        """Test endpoint to transcribe a predefined audio file."""
        try:
            audio_path = 'test.wav'
            with open(audio_path, "rb") as audio_file:
                transcription = app.config['OPENAI_CLIENT'].audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="es"
                )

            text = transcription.text
            logging.debug(f"Transcription obtained: {text}")
            return jsonify({'text': text}), 200
        except Exception as e:
            logging.error(f"Error during transcription: {str(e)}", exc_info=True)
            return jsonify({'error': f'Error al transcribir el audio: {str(e)}'}), 500
    
    @app.route('/speaker-verification', methods=['POST'])
    def verify_speaker():
        """Endpoint to verify speaker identity using two audio files."""
        if verification is None:
            return jsonify({'error': 'Modelo no inicializado correctamente'}), 500
            
        if 'audio1' not in request.files or 'audio2' not in request.files:
            return jsonify({'error': 'Se requieren dos archivos de audio'}), 400
            
        audio1 = request.files['audio1']
        audio2 = request.files['audio2']
        
        # Validate audio formats
        if not all(is_valid_audio_format(f.filename) for f in [audio1, audio2]):
            return jsonify({
                'error': f'Formato de archivo no válido. Formatos soportados: {", ".join(SUPPORTED_FORMATS)}'
            }), 400
            
        try:
            # Create temporary files for both audio files
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio1.filename)[1]) as temp1, \
                 tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio2.filename)[1]) as temp2:
                
                audio1.save(temp1)
                audio2.save(temp2)
                
                # Verify files aren't empty
                if any(os.path.getsize(f.name) == 0 for f in [temp1, temp2]):
                    return jsonify({'error': 'Uno o ambos archivos de audio están vacíos'}), 400
                
                # Perform verification
                score, prediction = verification.verify_files(temp1.name, temp2.name)
                
                # Clean up temporary files
                os.unlink(temp1.name)
                os.unlink(temp2.name)
                
                return jsonify({
                    'similarity_score': float(score),
                    'is_same_speaker': bool(prediction),
                    'threshold': VERIFICATION_THRESHOLD
                }), 200
                
        except Exception as e:
            logging.error(f"Error during speaker verification: {str(e)}", exc_info=True)
            return jsonify({'error': f'Error en la verificación: {str(e)}'}), 500
            
    @app.route('/test-verification', methods=['GET'])
    def test_verification():
        """Test endpoint using a predefined audio file against itself."""
        if verification is None:
            return jsonify({'error': 'Modelo no inicializado correctamente'}), 500
            
        try:
            test_file = 'test.wav'
            if not os.path.exists(test_file):
                return jsonify({'error': 'Archivo de prueba no encontrado'}), 404
                
            score, prediction = verification.verify_files(test_file, test_file)
            
            return jsonify({
                'similarity_score': float(score),
                'is_same_speaker': bool(prediction),
                'threshold': VERIFICATION_THRESHOLD
            }), 200
            
        except Exception as e:
            logging.error(f"Error during test verification: {str(e)}", exc_info=True)
            return jsonify({'error': f'Error en la verificación de prueba: {str(e)}'}), 500

    @app.route('/info', methods=['GET'])
    def home():
        return "whisper-1 microservice is running"