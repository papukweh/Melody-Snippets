# Melody-Snippets

Simple PoC for an automatic transcription system based on short melodic recordings.

This projects uses two approaches for tackling this problem:

1. The feature extraction/MIR approach, using the [melodia algorithm](https://github.com/justinsalamon/audio_to_midi_melodia). You can get the vamp plugin for this algorithm [here](https://www.upf.edu/web/mtg/melodia?p=Download%20and%20installation).
2. The machine learning approach, using the pre-trained network [CREPE: A Convolutional REpresentation for Pitch Estimation](https://github.com/marl/crepe). It can be installed with pip like a normal package.

Other softwares:
- [MusesScore](https://musescore.org/en) is used to render the sheet music based on the MIDI file.
- [Librosa](https://librosa.org/doc/latest/index.html) is used to load the audio, get BPM information and removing silent parts.

### Backend

#### Usage

Needs the [conda package manager](https://docs.conda.io/projects/conda/en/latest/user-guide/install/) installed.

Install dependencies with:
```bash
make setup-frontend
```

Then, activate the environment with:
```bash
conda activate Melody-Snippets
```

Run locally with:
```bash
make start-backend
```

#### API Reference

`POST /convert`
Form data:
```python
file: 'Blob with the raw content of the audio file. Can be any format (.mp3, .ogg, .wav, etc).'
```

Query string parameters:
```python
algorithm: 'Algorithm to use. Valid types are melodia and crepe.', default='crepe', type=str
format: 'Output format type. Valid types are midi and pdf.', default='pdf', type=str
minduration: 'Minimum allowed duration for note (in seconds). Shorter notes will be removed.' default=0.1, type=float
smooth: 'Smooth the pitch sequence with a median filter of the provided duration (in seconds).', default=0.25, type=float (melodia only)
confidence: 'Minimum allowed confidence for note. Notes with confidence lower than this threshold will be removed.', default=0.9, type=float (crepe only)
```

#### Testing the API

Here are some samples commands using cURL:
```bash
curl -F "file=@FILENAME" "localhost:5000/convert?algorithm=melodia&minduration=0.05" --output FILENAME.pdf
curl -F "file=@FILENAME" "localhost:5000/convert?algorithm=melodia&smooth=0.15&format=midi" --output FILENAME.mid
curl -F "file=@FILENAME" "localhost:5000/convert?algorithm=crepe&confidence=0.75" --output FILENAME.pdf
```

### Frontend

#### Usage
Needs [NodeJS](https://nodejs.org/en/) + [Yarn](https://yarnpkg.com/) installed.

Install dependencies with:
```bash
make setup-frontend
```

Run locally with:
```bash
make start-frontend
```

You can then access your app on `localhost:3000`

#### Screenshots

WIP

### References
```
J. Salamon and E. Gómez, "Melody Extraction from Polyphonic Music Signals using Pitch Contour Characteristics", IEEE Transactions on Audio, Speech and Language Processing, 20(6):1759-1770, Aug. 2012.
CREPE: A Convolutional Representation for Pitch Estimation
Jong Wook Kim, Justin Salamon, Peter Li, Juan Pablo Bello.
Proceedings of the IEEE International Conference on Acoustics, Speech, and Signal Processing (ICASSP), 2018.
```