import numpy as np
import music21.converter

from wwts_globals import NUM_FEATURES, NUM_STEPS, get_note_duration_bin



class MidiToArrayBuilder:

    def __init__(self, filename):

        self.filename = filename
        self.buf = []


    def mid_to_array(self):

        # TODO: Code for handling too large durations

        mid = music21.converter.parse(self.filename, quantizePost=False)

        for track in mid.parts:

            # need this to track start/end of track
            found_a_note = False

            for msg in track.notesAndRests:

                # it will never get here if it never finds a note
                if not found_a_note:
                    found_a_note = True
                    self.buf.extend([np.zeros(NUM_FEATURES) for _ in range(NUM_STEPS - 1)])  # the empty buf at the beginning
                    self.special_step(-2)  # start_track one-hot

                self.parse_msg(msg)

            if found_a_note:
                # slide a start_end in there
                self.special_step(-1)

        return self.buf


    def parse_msg(self, msg):

        # find the one-hot note
        if msg.isNote:
            self.note_step(msg.pitch.midi, msg.quarterLength)
        elif msg.isRest:
            self.note_step(128, msg.quarterLength)
        elif msg.isChord:
            self.special_step(-4)  # chord_start one-hot
            for pitch in msg.pitches:
                self.note_step(pitch.midi, msg.quarterLength)
            self.special_step(-3)  # chord_end one-hot
        else:
            raise TypeError("Unknown message in notesAndRests: " + msg.fullName)



    def special_step(self, i):

        this_step = np.zeros(NUM_FEATURES)
        this_step[i] = 14
        self.buf.append(this_step)


    def note_step(self, note_i, duration):

        this_step = np.zeros(NUM_FEATURES)

        this_step[note_i] = 1  # the midi note one-hot
        this_step[129 + get_note_duration_bin(duration)] = 1  # the duration one-hot

        self.buf.append(this_step)
