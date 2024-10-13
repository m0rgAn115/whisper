import os
import logging
import tempfile
from flask import jsonify, request
from utils import is_valid_audio_format, SUPPORTED_FORMATS
from speechbrain.pretrained import SpeakerRecognition
import torch


# Initialize SpeechBrain model globally
try:
    verification = SpeakerRecognition.from_hparams(
        source="speechbrain/spkrec-ecapa-voxceleb",
        savedir="pretrained_models/spkrec-ecapa-voxceleb"
    )
except Exception as e:
    logging.error(f"Error initializing SpeechBrain model: {str(e)}")
    verification = None

# Default threshold for speaker verification (this is the typical value used in ECAPA-TDNN)
VERIFICATION_THRESHOLD = 0.50

def register_endpoints2(app):
    """Register all endpoints to the Flask app."""
    
    @app.route('/speaker-verification', methods=['POST'])
    def verify_speaker():
        """Endpoint to verify speaker identity using two audio files."""
        if verification is None:
            return jsonify({'error': 'Modelo no inicializado correctamente'}), 500

        if 'audio' not in request.files:
            return jsonify({'error': 'Se requieren dos archivos de audio'}), 400

        audio1 = request.files['audio']
        audio2_path = 'p2.wav'  # Ruta al archivo local

        # Validate audio formats
        if not is_valid_audio_format(audio1.filename) or not is_valid_audio_format(audio2_path):
            return jsonify({
                'error': f'Formato de archivo no válido. Formatos soportados: {", ".join(SUPPORTED_FORMATS)}'
            }), 400

        try:
            # Create temporary files for both audio files
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio1.filename)[1]) as temp1:
                audio1.save(temp1)
                temp1_path = temp1.name

            temp2_path = audio2_path  # Usamos el archivo local directamente

            # Verify files aren't empty
            if any(os.path.getsize(f) == 0 for f in [temp1_path, temp2_path]):
                return jsonify({'error': 'Uno o ambos archivos de audio están vacíos'}), 400

            # Perform verification
            score, prediction = verification.verify_files(temp1_path, temp2_path)

            # Clean up temporary files
            os.unlink(temp1_path)

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
            test_file = 'p2.wav'
            test_file2 = 'p3.wav'
            if not os.path.exists(test_file):
                return jsonify({'error': 'Archivo de prueba no encontrado'}), 404
                
            score, prediction = verification.verify_files(test_file2, test_file)
            
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
        """Info endpoint with model status."""
        return jsonify({
            'status': 'running',
            'model': 'speechbrain/spkrec-ecapa-voxceleb',
            'model_loaded': verification is not None,
            'verification_threshold': VERIFICATION_THRESHOLD
        })