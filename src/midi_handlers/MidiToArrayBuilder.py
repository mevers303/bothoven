import copy
import numpy as np
import music21

from wwts_globals import NUM_FEATURES, NUM_STEPS, get_note_duration_bin, MAXIMUM_NOTE_LENGTH



class MidiToArrayBuilder:

    def __init__(self, filename):

        self.filename = filename
        self.buf = []


    def mid_to_array(self):

        mid = music21.converter.parse(self.filename, quantizePost=False)

        for part in mid.parts:

            # need this to track start/end of track
            found_a_note = False

            for msg in part.notesAndRests:

                # it will never get here if it never finds a note
                if not found_a_note:
                    found_a_note = True
                    self.buf.extend([np.zeros(NUM_FEATURES) for _ in range(NUM_STEPS - 1)])  # the empty buf at the beginning
                    self.special_step(-2)  # start_track one-hot

                # truncate long messages and pad the end with one or more rests
                while msg.quarterLength > MAXIMUM_NOTE_LENGTH:
                        msg = self.parse_too_long_msg(msg)

                self.parse_msg(msg)

            if found_a_note:
                # slide a start_end in there
                self.special_step(-1)

        return self.buf


    def parse_msg(self, msg):

        # find the one-hot note
        if msg.isNote:
            self.note_step(msg.pitch.midi, msg.quarterLength, msg.beat)
        elif msg.isRest:
            self.note_step(128, msg.quarterLength, msg.beat)
        elif msg.isChord:
            self.special_step(-4)  # chord_start one-hot
            for note in msg._notes:
                self.note_step(note.pitch.midi, note.quarterLength, msg.beat)
            self.special_step(-3)  # chord_end one-hot
        else:
            raise TypeError("Unknown message in notesAndRests: " + msg.fullName)


    def parse_too_long_msg(self, msg):

        # sanity check
        if msg.quarterLength <= MAXIMUM_NOTE_LENGTH:
            return msg

        # create a copy of the note and change the duration, then parse that instead
        new_msg = copy.deepcopy(msg)
        new_msg.quarterLength = MAXIMUM_NOTE_LENGTH
        self.parse_msg(new_msg)

        # turn the message into a rest and return it
        return music21.note.Rest(quarterLength=msg.quarterLength - MAXIMUM_NOTE_LENGTH)


    def special_step(self, i):

        this_step = np.zeros(NUM_FEATURES)
        this_step[i] = 14
        self.buf.append(this_step)


    def note_step(self, note_i, duration, beat):

        this_step = np.zeros(NUM_FEATURES)

        this_step[note_i] = 1  # the midi note one-hot
        this_step[129 + get_note_duration_bin(duration)] = 1  # the duration one-hot
        this_step[-5] = beat  #

        self.buf.append(this_step)
