import numpy as np
import mido

from midi_handlers.MidiLibrary import MidiLibraryFlat

class MidiArrayBuilder:

    def __init__(self, filename):

        self.filename = filename
        self.buf = []


    def mid_to_array(self):

        mid = mido.MidiFile(self.filename)

        for track in mid.tracks:

            # need this to track start/end of track
            found_a_note = False

            for msg in track:

                if not (msg.type == 'note_on' or msg.type == 'note_off') or msg.channel == 9:  # skip drum tracks
                    continue

                # it will never get here if it never finds a note
                if not found_a_note:
                    found_a_note = True
                    self.special_step(-2)  # start_track one-hot

                # find the one-hot note
                note_code = msg.note
                if msg.type == "note_off" or not msg.velocity:
                    note_code += 128

                self.note_step(note_code, msg.time)

            if found_a_note:
                # slide a start_end in there
                self.special_step(-1)

        if len(self.buf):
            self.buf = [np.zeros(MidiLibraryFlat.NUM_FEATURES) for _ in range(MidiLibraryFlat.NUM_STEPS - 1)] + self.buf  # the empty buf at the beginning

        return self.buf


    def special_step(self, i):

        this_step = np.zeros(MidiLibraryFlat.NUM_FEATURES)
        this_step[i] = 1
        self.buf.append(this_step)


    def note_step(self, note_i, delay):

        this_step = np.zeros(MidiLibraryFlat.NUM_FEATURES)

        this_step[note_i] = 1  # the midi note one-hot
        this_step[256] = delay  # the duration one-hot

        self.buf.append(this_step)
