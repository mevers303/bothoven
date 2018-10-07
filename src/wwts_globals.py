# Mark Evers
# Created: 3/30/2018
# globals.py
# Global variables and functions

from sys import stdout
from time import time



####################### OPTIONS #########################
######### FEATURES
# How many pieces must a composer have for us to consider them?
MINIMUM_WORKS = 100
# How many pieces will we use from each composer?
MAXIMUM_WORKS = 120

###### HYPER PARAMETERS
# How many ticks per beat should each track be converted to?
TICKS_PER_BEAT = 1920
# The resolution of music notes
MINIMUM_NOTE_LENGTH = TICKS_PER_BEAT / 2**4  # 128th notes
MINIMUM_NOTE_LENGTH_TRIPLETS = TICKS_PER_BEAT / 3 / 2**3  # 128th note triplets

# the number of steps in the model
NUM_STEPS = 64
# the number of features for the model
NUM_FEATURES = 256 + 1 + 2  # 256 note on/off + 1 time + 2 track start/end
# number of epochs to train for
N_EPOCHS = 20
# the batch size for training
BATCH_SIZE = 64







####################### CONSTANTS #######################
#               0     1    2    3     4    5    6     7    8     9    10    11
MUSIC_NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

KEY_SIGNATURES = [[ 0,  2,  4,  5 , 7,  9, 11],  # C
                  [ 1,  3,  5,  6,  8, 10,  0],  # Db
                  [ 2,  4,  6,  7,  9, 11,  1],  # D
                  [ 3,  5,  7,  8, 10,  0,  2],  # Eb
                  [ 4,  6,  8,  9, 11,  1,  3],  # E
                  [ 5,  7,  9, 10,  0,  2,  4],  # F
                  [ 6,  8, 10, 11,  1,  3,  5],  # Gb
                  [ 7,  9, 11,  0,  2,  4,  6],  # G
                  [ 8, 10,  0,  1,  3,  5,  7],  # Ab
                  [ 9, 11,  1,  2,  4,  6,  8],  # A
                  [10,  0,  2,  3,  5,  7,  9],  # Bb
                  [11,  1,  3,  4,  6,  8, 10]]  # B



####################### FUNCTIONS #######################
def dump_tracks(midi_file):
    """
    Prints all the tracks in a mido MidiFile object.

    :param midi_file: A mido.MidiFile object.
    :return: None
    """
    for i, track in enumerate(midi_file.tracks):
        print(str(i).rjust(2), ": ", track, sep="")


def dump_msgs(mido_object, limit=25):
    """
    Prints all the messages contained in a track or midi file.  The delta time is in seconds when you give it a
    mido.MidiFile.

    :param track: A mido MidiTrack or MidiFile
    :return: None
    """
    print("Showing first", limit, "messages")
    for i, msg in enumerate(mido_object):
        if i >= limit:
            return
        print(str(i).rjust(4), ": ", msg, sep="")


def midi_to_music(midi_note):
    """
    Returns a tuple of (<note name>, octave).

    :param midi_note: The midi note value.
    :return: (<string> Note Name, <int> Octave)
    """

    music_note = MUSIC_NOTES[midi_note % 12]
    octave = int(midi_note / 12) - 1

    return music_note, octave


def midi_to_string(midi_note):
    """
    Converts a MIDI note to a string of it's name and octave (like C4 for middle C).

    :param midi_note: The midi note value
    :return: A string as described above.
    """
    note = midi_to_music(midi_note)
    return note[0] + str(note[1])


def to_reltime(messages):
    """
        Convert messages to relative time.
    """

    now = 0

    for msg in messages:
        delta = msg.time - now
        yield msg.copy(time=delta)
        now = msg.time


_progress_bar_last_time = 0
def progress_bar(done, total, resolution=0.125, text=""):
    """
    Prints a progress bar to stdout.
    :param done: Number of items complete
    :param total: Total number if items
    :param resolution: How often to update the progress bar (in seconds).
    :return: None
    """

    global _progress_bar_last_time

    time_now = time()
    if time_now - _progress_bar_last_time < resolution and done < total:
        return

    # percentage done
    i = int(done / total * 100)

    stdout.write('\r')
    # print the progress bar
    stdout.write("[{}]{}%".format(("-" * int(i / 2) + (">" if i < 100 else "")).ljust(50), str(i).rjust(4)))
    # print the text figures
    stdout.write(" ({}/{})".format(done, total))
    if text:
        stdout.write(" " + text)
    stdout.flush()

    if i == 100:
        # print("\n")
        stdout.write('\r')
        stdout.write(' ' * 120)
        stdout.write('\r')

    _progress_bar_last_time = time_now
