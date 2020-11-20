import librosa
import resampy
import vamp
import argparse
import os
import numpy as np
from midiutil.MidiFile import MIDIFile
from scipy.signal import medfilt

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

def save_midi(outfile, notes, tempo):
    track = 0
    time = 0
    midifile = MIDIFile(1)

    # Add track name and tempo.
    midifile.addTrackName(track, time, 'MIDI TRACK')
    midifile.addTempo(track, time, tempo)

    channel = 0
    volume = 100

    for note in notes:
        print(note)
        onset = note[0] * (tempo/60.)
        duration = note[1] * (tempo/60.)
        pitch = note[2]
        midifile.addNote(track, channel, int(pitch), onset, duration, volume)

    # And write it to disk.
    binfile = open(outfile, 'wb')
    midifile.writeFile(binfile)
    binfile.close()


def midi_to_notes(midi, fs, hop, smooth, minduration):
    # smooth midi pitch sequence first
    if (smooth > 0):
        filter_duration = smooth  # in seconds
        filter_size = int(filter_duration * fs / float(hop))
        if filter_size % 2 == 0:
            filter_size += 1
        midi_filt = medfilt(midi, filter_size)
    else:
        midi_filt = midi

    notes = []
    p_prev = 0
    duration = 0
    onset = 0
    for n, p in enumerate(midi_filt):
        if p == p_prev:
            duration += 1
        else:
            # treat 0 as silence
            if p_prev > 0:
                # add note
                duration_sec = duration * hop / float(fs)
                # only add notes that are long enough
                if duration_sec >= minduration:
                    onset_sec = onset * hop / float(fs)
                    notes.append((onset_sec, duration_sec, p_prev))

            # start new note
            onset = n
            duration = 1
            p_prev = p

    # add last note
    if p_prev > 0:
        # add note
        duration_sec = duration * hop / float(fs)
        onset_sec = onset * hop / float(fs)
        notes.append((onset_sec, duration_sec, p_prev))

    return notes


def hz2midi(hz):
    # convert from Hz to midi note
    hz_nonneg = hz.copy()
    idx = hz_nonneg <= 0
    hz_nonneg[idx] = 1
    midi = 69 + 12*np.log2(hz_nonneg/440.)
    midi[idx] = 0

    # round
    midi = np.round(midi)

    return midi


def audio_to_midi_melodia(infile, outfile, smooth=0.25, minduration=0.1):
    # define analysis parameters
    fs = 44100
    hop = 128

    # load audio using librosa
    print('Loading audio...')
    signal, sr = librosa.load(infile)
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

    # segment sequence into individual midi notes
    notes = midi_to_notes(midi_pitch, fs, hop, smooth, minduration)

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
    args = parser.parse_args()

    audio_to_midi_melodia(args.infile, args.outfile, smooth=args.smooth, minduration=args.minduration)
