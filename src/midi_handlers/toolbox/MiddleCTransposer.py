from midi_handlers.toolbox.MidiToolbox import MidiTool
import numpy as np
import wwts_globals

class MiddleCTransposer(MidiTool):

    def __init__(self):

        super().__init__(priority = "first", do_prerun = True)

        self.note_distribution = np.zeros((128,))
        self.keysig_distribution = np.zeros((12,))
        self.original_keysig = -1
        self.note_transpose_interval = 0


    def prerun_message_event(self, msg):

        if msg.type == "note_on":

            if not msg.velocity:  # skip if it's a note off (velocity = 0)
                return

            if msg.channel != 10:  # skip channel 10 (drums)
                self.note_distribution[msg.note] += 1
                self.keysig_distribution[msg.note % 12] += 1


    def prerun_post_process(self, mid):

        self.get_key_signature()
        self.get_note_transpose_interval()


    def message_event(self, msg):

        if msg.type == "note_on" or msg.type == "note_off":

            note = msg.note
            note += self.note_transpose_interval

            while note > 127:
                note -= 12
            while note < 0:
                note += 12

            msg.note = note


    def get_key_signature(self):

        # find the 7 most common notes
        top_7_notes = set(np.argsort(self.keysig_distribution)[::-1][:7])

        best_match = -1
        best_match_set_difference = 100

        # loop through each key signature and find the one that matches best
        for i in range(len(wwts_globals.KEY_SIGNATURES)):

            # find number of uncommon notes
            set_difference = len(set(wwts_globals.KEY_SIGNATURES[i]) - top_7_notes)

            # if this one has less mismatched notes, set it as the best match so far
            if set_difference < best_match_set_difference:
                best_match = i
                best_match_set_difference = set_difference

                # if there are 0 uncommon notes, it is our match!
                if not best_match_set_difference:
                    break

        self.original_keysig = best_match


    def get_note_transpose_interval(self):

        # first transpose to C based on key signature
        if self.original_keysig < 6:
            keysig_transpose_interval = -self.original_keysig
        else:
            keysig_transpose_interval = 12 - self.original_keysig

        # now transpose it to middle C (C4) based on the most common octave
        transposed_notes = np.roll(self.note_distribution, keysig_transpose_interval)
        c_octaves = {i: transposed_notes[i] for i in range(0, 128, 12)}
        octave_transpose_interval = 60 - max(c_octaves, key=lambda i: c_octaves[i])

        self.note_transpose_interval = keysig_transpose_interval + octave_transpose_interval





# def main():
#
#     from midi_handlers.toolbox.MidiToolbox import MidiTool, MidiToolbox
#     import mido
#
#     toolbox = MidiToolbox([MiddleCTransposer])
#     mid = mido.MidiFile("/home/mark/Documents/Barcarolle in F sharp Major.mid")
#     new_mid = toolbox.process_midi_file(mid)
#
#     # new_mid.print_tracks()
#
#     # for original, new in zip(mid, new_mid):
#     #     if original.type == "note_on" or original.type == "note_off":
#     #         if original.note != new.note:
#     #             print(original, "->", new)
#
#     print("Done... ?")
#
# if __name__ == "__main__":
#     main()
