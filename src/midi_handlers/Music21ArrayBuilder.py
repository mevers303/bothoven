import copy
import numpy as np
import music21

from bothoven_globals import NUM_FEATURES, NUM_STEPS, get_note_duration_bin, MAXIMUM_NOTE_LENGTH



class Music21ArrayBuilder:

    def __init__(self, filename):

        self.filename = filename
        self.buf = []


    def mid_to_array(self):

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

        # find the one-hot note
        if msg.isNote:
            self.buf.append([msg.pitch.midi, msg.quarterLength, msg.beat])
        elif msg.isRest:
            self.buf.append([128, msg.quarterLength, msg.beat])
        elif msg.isChord:
            self.buf.append([-2, -2, -2])  # chord_start one-hot
            for note in msg._notes:
                self.buf.append([note.pitch.midi, note.quarterLength, note.beat])
            self.buf.append([-3, -3, -3])  # chord_end one-hot
        else:
            raise TypeError("Unknown message in notesAndRests: " + msg.fullName)
