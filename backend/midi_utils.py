import numpy as np
from midiutil.MidiFile import MIDIFile
from scipy.signal import medfilt

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

def midi_to_notes_with_confidence(midi, fs, minduration, confidence):
    notes = []
    p_prev = 0
    c_prev = 0
    duration = 0
    onset = 0
    for n, p, c in midi:
        if p == p_prev or c <= confidence:
            duration += 0.01
        else:
            # treat 0 as silence
            if p_prev > 0 and c_prev >= confidence:
                # only add notes that are long enough
                if duration >= minduration:
                    notes.append((onset, duration, p_prev))

            # start new note
            onset = n
            duration = 0.01
            p_prev = p
            c_prev = c

    # add last note
    if p_prev > 0:
        notes.append((onset, duration, p_prev))

    return notes

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