# Mark Evers
# 9/21/18
# MidiLibrary.py
# Objects for managing a set of MIDI functions.

import numpy as np
from midi_handlers.MidiArrayBuilder import MidiArrayBuilder
import scipy.sparse

from midi_handlers.MusicLibrary import MusicLibraryFlat


class MidiLibraryFlat(MusicLibraryFlat):

    def __init__(self, base_dir="", filenames=None, autoload=True):
        super().__init__(MidiArrayBuilder, base_dir, filenames, autoload)


    def load_files(self):

        super().load_files()

        self.buf = scipy.sparse.vstack(self.buf, format="csr", dtype=np.byte)
        self.NUM_FEATURES = 128 + 128 + 2  # note_on + note_off + 2 track start/end


    def step_through(self):

        i = 0

        while i < self.buf.shape[0] - self.NUM_STEPS - 1:  # gotta leave room for the target at the end

            x = self.buf[i:i + self.NUM_STEPS].toarray()
            y = self.buf[i + self.NUM_STEPS].toarray()[0]

            i += 1

            yield x, y


def main():

    import os
    import pickle

    lib_name = "bach"

    lib = MidiLibraryFlat(os.path.join("midi", lib_name))
    # lib.load()  # autoload is on by default

    print("Pickling...")
    os.makedirs("midi/pickles")
    with open(os.path.join(f"midi/pickles/{lib_name}_midi.pkl"), "wb") as f:
        pickle.dump(lib, f)
    print("Done!")

if __name__ == "__main__":
    main()
