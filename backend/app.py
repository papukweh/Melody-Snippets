from subprocess import run
from flask import Flask, request, send_file
from audio_to_midi import audio_to_midi_melodia as audio2midi
from io import BytesIO
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def main_page():  
  return 'Please use the /convert route for automatic music transcription'

@app.route('/convert', methods=['POST'])
def convert():

  # Gets audio file and saves
  song = request.files['file']
  path = 'user_files/input_song'
  song.save(path)
  
  # Converts to MIDI
  midi_path = path+'.mid'
  converted = audio2midi(path, midi_path, smooth=0.25, minduration=0.05)

  # Converts to PDF
  pdf_path = path+'.pdf'
  bashCommand = './MuseScore.AppImage -O {} -o {} --debug'.format(midi_path, pdf_path)
  process = run(bashCommand.split())

  # Returns PDF
  return send_file(pdf_path, mimetype='application/pdf')

if __name__ == '__main__':
  app.run(host='0.0.0.0')
