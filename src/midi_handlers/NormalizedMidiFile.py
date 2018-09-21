import mido
import numpy as np
import wwts_globals


class NormalizedMidiFile(mido.MidiFile):


    def __init__(self, filename):

        super().__init__(filename)

        self.note_distribution = np.zeros((128,))
        self.keysig_distribution = np.zeros((12,))
        self.original_keysig = -1

        self.tick_transpose_coef = 1
        self.note_transpose_interval = 0

        self.normalize()


    def normalize(self):

        # read the file and calculate all the info we need first
        self.tick_transpose_coef = wwts_globals.TICKS_PER_BEAT / self.ticks_per_beat
        self.get_note_distributions()
        self.get_key_signature()
        self.get_note_transpose_interval()

        # build the new mido object
        new_tracks = [self.normalize_track(track) for track in self.tracks]

        self.ticks_per_beat = wwts_globals.TICKS_PER_BEAT
        self.tracks = new_tracks



    def get_note_transpose_interval(self):

        # first transpose to C based on key signature
        if self.original_keysig < 6:
            keysig_transpose_interval = -self.original_keysig
        else:
            keysig_transpose_interval = 12 - self.original_keysig

        # now transpose it to middle C (C4) based on the most common octave
        transposed_notes = np.roll(self.note_distribution, keysig_transpose_interval)
        C_octaves = {i: transposed_notes[i] for i in range(0, 128, 12)}
        octave_transpose_interval = 60 - max(C_octaves, key=lambda i: C_octaves[i])

        self.note_transpose_interval = keysig_transpose_interval + octave_transpose_interval


    def get_note_distributions(self):

        for msg in self:

            if msg.type == "note_on":

                if not msg.velocity:  # skip if it's a note off (velocity = 0)
                    continue

                if msg.channel != 10:  # skip channel 10 (drums)
                    self.note_distribution[msg.note] += 1
                    self.keysig_distribution[msg.note % 12] += 1


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


    def normalize_track(self, track):

        new_track = mido.MidiTrack()

        for msg in track:

            args = {}

            if hasattr(msg, "note"):
                args["note"] = msg.note + self.note_transpose_interval
            if hasattr(msg, "time"):
                args["time"] = int(msg.time * self.tick_transpose_coef)

            new_msg = msg.copy(**args)
            new_track.append(new_msg)

        return new_track


if __name__ == "__main__":
    mid = NormalizedMidiFile("/home/mark/Documents/Barcarolle in F sharp Major.mid")
    wwts_globals.dump_msgs(mid, 100)
