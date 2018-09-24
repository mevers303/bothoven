# Mark Evers
# Created: 3/30/2018
# globals.py
# Global variables and functions

from sys import stdout
from numpy import argsort
from time import time



####################### OPTIONS #########################
######### FEATURES
# How many pieces must a composer have for us to consider them?
MINIMUM_WORKS = 100
# How many pieces will we use from each composer?
MAXIMUM_WORKS = 120

###### HYPER PARAMETERS
# How many ticks per beat should each track be converted to?
TICKS_PER_BEAT = 1024
# The resolution of music notes
MINIMUM_NOTE_LENGTH = TICKS_PER_BEAT / 32  # 128th notes
# The longest note allowed
MAXIMUM_NOTE_LENGTH = TICKS_PER_BEAT * 8   # two whole notes



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
    this_bin = int(this_bin / 2)
    # add the dotted note duration first cause it's bigger
    DURATION_BINS.append(int(this_bin * 1.5))
    DURATION_BINS.append(int(this_bin))




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


def get_key_signature(note_dist):
    """
    Uses the note distribution in the meta dataframe to determine a filename's key signature
    :param note_dist: Distribution of notes as per music_notes
    :return: The index of key_signatures that is the best match.
    """

    top_notes = set(argsort(note_dist)[::-1][:7])


    best_match = -1
    best_match_set_dif_len = 100

    for i in range(len(KEY_SIGNATURES)):

        # find number of uncommon notes
        set_dif_len = len(set(KEY_SIGNATURES[i]) - top_notes)

        # if this one is better than the last, save it
        if set_dif_len < best_match_set_dif_len:
            best_match = i
            best_match_set_dif_len = set_dif_len

            # if there are 0 uncommon notes, it is our match!
            if not best_match_set_dif_len:
                break


    return best_match


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
