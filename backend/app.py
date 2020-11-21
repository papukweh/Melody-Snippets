from subprocess import run
from flask import Flask, request, send_file
from audio_to_midi import audio_to_midi_crepe, audio_to_midi_melodia
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_PATH = 'user_files/'

@app.route('/')
def main_page():  
  return 'Please use the /convert route for automatic music transcription'

@app.route('/get_midi/<filename>', methods=['GET'])
def get_midi(filename):
  filename = filename if filename else 'input_song.mid'
  midi_path = f'{BASE_PATH}{filename}'
  try:
    return send_file(midi_path, mimetype='audio/midi')
  except:
    abort(404)

@app.route('/get_pdf/<filename>', methods=['GET'])
def get_pdf(filename):
  filename = filename if filename else 'input_song.pdf'
  pdf_path = f'{BASE_PATH}{filename}'
  try:
    return send_file(pdf_path, mimetype='application/pdf')
  except:
    abort(404)

@app.route('/convert', methods=['POST'])
def convert():
  # Gets query arguments
  algorithm = request.args.get('algorithm', default='crepe', type=str)
  smooth = request.args.get('smooth', default=0.25, type=float)
  minduration = request.args.get('minduration', default=0.1, type=float)
  confidence = request.args.get('confidence', default=0.9, type=float)
  output_format = request.args.get('format', default='pdf', type=str)
  filename = request.args.get('filename', default='input_song', type=str)

  # Gets audio file and saves
  song = request.files['file']
  path = f'{BASE_PATH}{filename}'
  song.save(path)
  
  # Converts to MIDI
  midi_path = path+'.mid'

  if algorithm == 'crepe':
    converted = audio_to_midi_crepe(path, midi_path, minduration=minduration, threshold=confidence)
  elif algorithm == 'melodia':
    converted = audio_to_midi_melodia(path, midi_path, minduration=minduration, smooth=smooth)
  else:
    abort(400)

  # Returns MIDI
  if output_format == 'midi':
    return send_file(midi_path, mimetype='audio/midi')

  # Converts to PDF
  pdf_path = path+'.pdf'
  bashCommand = './MuseScore.AppImage -O {} -o {} --debug'.format(midi_path, pdf_path)
  process = run(bashCommand.split())

  # Returns PDF
  return send_file(pdf_path, mimetype='application/pdf')

if __name__ == '__main__':
  app.run(host='0.0.0.0')
