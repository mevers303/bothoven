import numpy as np
import music21

from bothoven_globals import NUM_STEPS
from functions.pickle_workaround import pickle_load



class Music21ArrayBuilder:

    def __init__(self, filename):

        self.filename = filename
        self.buf = []
        self.last_beat = 99999


    def mid_to_array(self):

        if self.filename.endswith(".pkl"):
            mid = music21.converter.thaw(self.filename)
        else:
            mid = music21.converter.parse(self.filename)

        for part in mid.parts:

            # need this to track start/end of track
            found_a_note = False

            for msg in part.flat.notesAndRests:

                # it will never get here if it never finds a note
                if not found_a_note:
                    found_a_note = True
                    self.buf.extend([[-1, -1, -1] for _ in range(NUM_STEPS - 1)])  # the empty buf at the beginning

                self.parse_msg(msg)

        return np.array(self.buf)


    def parse_msg(self, msg):

        if msg.beat < self.last_beat:
            self.buf.append([-2, -2, -2]) # a measure_start

        # find the one-hot note
        if msg.isNote:
            self.buf.append([msg.pitch.midi, msg.quarterLength, msg.beat])
        elif msg.isRest:
            self.buf.append([128, msg.quarterLength, msg.beat])
        elif msg.isChord:
            self.buf.append([-3, -3, -3])  # chord_start one-hot
            for note in msg._notes:
                self.buf.append([note.pitch.midi, note.quarterLength, msg.beat])
            self.buf.append([-4, -4, -4])  # chord_end one-hot
        else:
            raise TypeError("Unknown message in notesAndRests: " + msg.fullName)

        self.last_beat = msg.beat
