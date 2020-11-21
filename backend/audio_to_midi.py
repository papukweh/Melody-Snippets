import os
import argparse
import numpy as np
import librosa
import resampy
import vamp
import crepe
from midi_utils import hz2midi, save_midi, midi_to_notes, midi_to_notes_with_confidence

'''
Extract the melody from an audio file and convert it to MIDI.

The script extracts the melody from an audio file using the Melodia algorithm,
and then segments the continuous pitch sequence into a series of quantized
notes, and exports to MIDI using the provided BPM.

Usage: audio_to_midi_melodia.py [-h] [--smooth SMOOTH]
                                [--minduration MINDURATION]
                                infile outfile


Examples:
python audio_to_midi_melodia.py --smooth 0.25 --minduration 0.1 song.wav song.mid
'''

def audio_to_midi_melodia(infile, outfile, smooth=0.25, minduration=0.1):
    # define analysis parameters
    fs = 44100
    hop = 128

    # load audio using librosa
    print('Loading audio...')
    signal, sr = librosa.load(infile)
    signal, index = librosa.effects.trim(signal)
    # estimate bpm
    bpm, _ = librosa.beat.beat_track(signal)
    # mixdown to mono if needed
    if len(signal.shape) > 1 and signal.shape[1] > 1:
        signal = signal.mean(axis=1)
    # resample to 44100 if needed
    if sr != fs:
        signal = resampy.resample(signal, sr, fs)
        sr = fs

    # extract melody using melodia vamp plugin
    print('Extracting melody f0 with MELODIA...')
    melody = vamp.collect(signal, sr, 'mtg-melodia:melodia',
                          parameters={'voicing': 0.2})

    pitch = melody['vector'][1]

    # impute missing 0's to compensate for starting timestamp
    pitch = np.insert(pitch, 0, [0]*8)

    # convert f0 to midi notes
    print('Converting Hz to MIDI notes...')
    midi_pitch = hz2midi(pitch)
    print(midi_pitch)

    # segment sequence into individual midi notes
    notes = midi_to_notes(midi_pitch, fs, hop, smooth, minduration)

    # save note sequence to a midi file
    print('Saving MIDI to disk...')
    save_midi(outfile, notes, bpm)

    print('Conversion complete.')

def audio_to_midi_crepe(infile, outfile, minduration=0.1, threshold=0.9):
    # define analysis parameters
    fs = 16000

    # load audio using librosa
    print('Loading audio...')
    signal, sr = librosa.load(infile)
    signal, index = librosa.effects.trim(signal)
    
    # estimate bpm
    bpm, _ = librosa.beat.beat_track(signal)
    # mixdown to mono if needed
    if len(signal.shape) > 1 and signal.shape[1] > 1:
        signal = signal.mean(axis=1)
    # resample to 16000 if needed
    if sr != fs:
        signal = resampy.resample(signal, sr, fs)
        sr = fs

    # extract melody using CREPE
    print('Extracting melody f0 with CREPE...')
    time, frequency, confidence, activation = crepe.predict(signal, sr, viterbi=True)
    
    print('Converting Hz to MIDI notes...')
    midi = hz2midi(frequency)
    midi_pitch = [(t, f, c) for t, f, c in zip(time, midi, confidence)]
    
    print(midi_pitch)

    # segment sequence into individual midi notes
    notes = midi_to_notes_with_confidence(midi_pitch, fs, minduration, threshold)

    # save note sequence to a midi file
    print('Saving MIDI to disk...')
    save_midi(outfile, notes, bpm)

    print('Conversion complete.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help='Path to input audio file.')
    parser.add_argument('outfile', help='Path for saving output MIDI file.')
    parser.add_argument('--smooth', type=float, default=0.25,
                        help='Smooth the pitch sequence with a median filter '
                             'of the provided duration (in seconds).')
    parser.add_argument('--minduration', type=float, default=0.1,
                        help='Minimum allowed duration for note (in seconds). '
                             'Shorter notes will be removed.')
    parser.add_argument('--algorithm', default='melodia',
                        help='Algorithm to use. Valid types are melodia and crepe')
    parser.add_argument('--confidence', default=0.9,
                        help='Minimum allowed confidence for note. '
                        'Notes with confidence lower than this threshold will be removed.')
    args = parser.parse_args()

    if args.algorithm == 'melodia':
        audio_to_midi_melodia(args.infile, args.outfile, smooth=args.smooth, minduration=args.minduration)
    elif args.algorithm == 'crepe':
        audio_to_midi_crepe(args.infile, args.outfile, minduration=args.minduration)
    else:
        raise InvalidArgumentException('Algorithm parameter is invalid. Valid types are melodia and crepe')