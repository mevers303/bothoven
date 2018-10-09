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
MINIMUM_NOTE_LENGTH = TICKS_PER_BEAT / 2**4  # 64th notes
MINIMUM_NOTE_LENGTH_TRIPLETS = TICKS_PER_BEAT / 3 / 2**3  # 64th note triplets
MAXIMUM_NOTE_LENGTH = TICKS_PER_BEAT * 8   # two whole notes

# the number of steps in the model
NUM_STEPS = 64
# the number of features for the model
NUM_FEATURES = 256 + 1 + 2  # 256 note on/off + 1 time + 2 track start/end
# number of epochs to train for
N_EPOCHS = 20
# the batch size for training
BATCH_SIZE = 128
# T






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


# create a list of all the possible not durations to use to bin message durations into later on
this_bin = MAXIMUM_NOTE_LENGTH
DURATION_BINS = [this_bin]

while this_bin > MINIMUM_NOTE_LENGTH:
    # divide by half to get the next smallest note
    this_bin_duplet = int(this_bin / 2)
    this_bin_triplet = int(this_bin / 3)
    # add the dotted note duration first cause it's bigger
    DURATION_BINS.append(int(this_bin_duplet * 1.5))
    DURATION_BINS.append(int(this_bin_triplet * 1.5))
    DURATION_BINS.append(int(this_bin_duplet))
    DURATION_BINS.append(int(this_bin_triplet))

    this_bin = this_bin_duplet


####################### FUNCTIONS #######################
def bin_note_duration(duration):
    """
    Rounds the duration to the closest value in DURATION_BINS
    :param duration: This note's duration
    :return: A new duration in ticks
    """

    smallest_difference = MAXIMUM_NOTE_LENGTH
    best_match = MAXIMUM_NOTE_LENGTH

    for bin in DURATION_BINS:

        difference = abs(duration - bin)

        if not difference:
            # they're equal
            return bin
        elif difference < smallest_difference:
            # find the whichever bin it's closest to
            smallest_difference = difference
            best_match = bin
        elif difference > smallest_difference:
            # we passed our bin
            return best_match

    # this should never execute but just for sanity's sake
    return best_match


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
    octave = midi_note // 12 - 1

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
def progress_bar(done, total, text="", clear_when_done=False, resolution=0.333):
    """
    Prints a progress bar to stdout.
    :param done: Number of items complete
    :param total: Total number if items
    :param resolution: How often to update the progress bar (in seconds).
    :param text: Text to be displayed below the progress bar every update.
    :param clear_when_done: Clear the progress bar or leave it when completed?
    :return: None
    """

    global _progress_bar_last_time

    time_now = time()
    if time_now - _progress_bar_last_time < resolution and done < total:
        return

    # so we don't divide by 0
    if not total:
        i = 100
    else:
        # percentage done
        i = (done * 100) // total

    # go to beginning of our output
    if text and done > 0:
        stdout.write("\r")
        stdout.write("\033[F")
    else:
        stdout.write("\r")

    # print the progress bar
    stdout.write( "[" + (("-" * (i // 2)) +  (">" if i < 100 else "")).ljust(50) + "]" )
    # print the percentage
    stdout.write(str(i).rjust(4) + "%")
    # print the text progress
    stdout.write(" ({}/{})".format(done, total))
    # print the text below (if any)
    if text:
        stdout.write("\n" + (' ' * 256) + "\r")
        stdout.write(text)

    if i == 100:

        if clear_when_done:
            stdout.write('\r')
            stdout.write(' ' * 256)

            if text:
                stdout.write("\r")
                stdout.write("\033[F")
                stdout.write(' ' * 256)

            stdout.write('\r')

        else:
            stdout.write("\n")

    stdout.flush()

    _progress_bar_last_time = time_now
