# Mark Evers
# 9/21/18
# MidiLibrary.py
# Objects for managing a set of MIDI functions.

import numpy as np
from midi_handlers.Music21ArrayBuilder import Music21ArrayBuilder

import bothoven_globals
from midi_handlers.MusicLibrary import MusicLibraryFlat


class Music21LibraryFlat(MusicLibraryFlat):

    def __init__(self, base_dir="", filenames=None, autoload=True):

        super().__init__(Music21ArrayBuilder, base_dir, filenames, autoload)

        self.beat_norm_max = 0
        self.NUM_FEATURES = 128 + 1 + len(bothoven_globals.DURATION_BINS) + 1 + 2 + 2  # midi notes + rest note + time bins + 1 beat offset + 2 chord on/off + 2 track start/end


    def load_files(self):

        super().load_files()

        self.buf = np.vstack(self.buf)

        self.beat_norm_max = self.buf[:, -5].max()
        self.buf[:, -5] = self.buf[:, -5] / self.beat_norm_max


    def step_through(self):

        i = 0

        while i < self.buf.shape[0] - self.NUM_STEPS - 1:  # gotta leave room for the target at the end

            x = self.buf[i:i + self.NUM_STEPS]
            y = self.buf[i + self.NUM_STEPS]

            i += 1

            yield x, y


def main():

    import os
    import pickle

    lib_name = "metallica"

    lib = Music21LibraryFlat(os.path.join("midi", lib_name))
    # lib = Music21LibraryFlat(filenames=np.array([str(x) for x in music21.corpus.getComposer("bach")]))
    # lib.load()  # autoload is on by default

    print("Pickling...")
    with open(os.path.join(f"midi/pickles/{lib_name}_m21.pkl"), "wb") as f:
        pickle.dump(lib, f)
    print("Done!")



if __name__ == "__main__":
    main()
