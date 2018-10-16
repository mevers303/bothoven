# Mark Evers
# 9/21/18
# MidiLibrary.py
# Objects for managing a set of MIDI functions.

import numpy as np
from midi_handlers.MidiArrayBuilder import MidiArrayBuilder
import scipy.sparse

from midi_handlers.MusicLibrary import MusicLibraryFlat
from bothoven_globals import BATCH_SIZE, NUM_FEATURES, NUM_STEPS


class MidiLibraryFlat(MusicLibraryFlat):

    def __init__(self, base_dir="", filenames=None, autoload=True):
        super().__init__(MidiArrayBuilder, base_dir, filenames, autoload)


    def load_files(self):

        super().load_files()

        self.buf = scipy.sparse.vstack(self.buf, format="csr", dtype=np.byte)


    def step_through(self):

        i = 0

        while i < self.buf.shape[0] - NUM_STEPS - 1:  # gotta leave room for the target at the end

            x = self.buf[i:i + NUM_STEPS].toarray()
            y = self.buf[i + NUM_STEPS].toarray()

            i += 1

            yield x, y


def main():

    import os
    import pickle

    lib_name = "metallica"

    lib = MidiLibraryFlat(os.path.join("midi", lib_name))
    # lib.load()  # autoload is on by default

    print("Pickling...")
    with open(os.path.join(f"midi/pickles/{lib_name}.pkl"), "wb") as f:
        pickle.dump(lib, f)
    print("Done!")

if __name__ == "__main__":
    main()
