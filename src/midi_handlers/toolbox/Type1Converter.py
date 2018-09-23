from collections import defaultdict, deque
import mido




def convert_to_type_1(mid):

    # Some sanity checks
    if mid.type == 1:
        return mid
    elif mid.type == 2:
        raise NotImplementedError("Type 2 MIDI files are not supported!")
    elif mid.type != 0:
        raise NotImplementedError("Unknown MIDI file type!")
    elif len(mid.tracks) != 1:
        raise TypeError("This type 0 MIDI file has more than one track???")

    new_mid = mido.MidiFile()  # new mido to hold new file
    channels = defaultdict(mido.MidiTrack)  # dict to hold a track for each channel

    # loop through the original and split into tracks
    for msg in mid.tracks[0]:
