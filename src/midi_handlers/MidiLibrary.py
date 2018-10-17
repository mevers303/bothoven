# Mark Evers
# 9/21/18
# MidiLibrary.py
# Objects for managing a set of MIDI functions.

import scipy.sparse
from midi_handlers.MusicLibrary import MusicLibraryFlat
from midi_handlers.MidiArrayBuilder import MidiArrayBuilder
from functions.pickle_workaround import pickle_dump



class MidiLibraryFlat(MusicLibraryFlat):

    def __init__(self, base_dir="", filenames=None, autoload=True):

        self.max_delay = 0

        super().__init__(MidiArrayBuilder, base_dir, filenames, autoload)

        # number of timesteps for lstm
        self.NUM_STEPS = 64
        # how many features does this model have?
        self.NUM_FEATURES = 128 + 128 + 1 + 2  # note_on + note_off + 2 track start/end
        # the batch size for training
        self.BATCH_SIZE = 64


    def load_files(self):

        super().load_files()

        self.buf = scipy.sparse.vstack(self.buf)
        self.max_delay = self.buf[:, -3].max()
        self.buf[:, -3] = self.buf[:, -3] / self.max_delay


    def step_through(self):

        i = 0

        while i < self.buf.shape[0] - self.NUM_STEPS - 1:  # gotta leave room for the target at the end

            x = self.buf[i:i + self.NUM_STEPS].toarray()
            y = self.buf[i + self.NUM_STEPS].toarray()[0]

            i += 1

            yield x, y


def main():

    import os

    lib_name = "metallica"

    lib = MidiLibraryFlat(os.path.join("midi", lib_name))
    # lib.load()  # autoload is on by default

    print("Pickling...")
    pickle_dump(lib, f"midi/pickles/{lib_name}_midi.pkl")
    print("Done!")

if __name__ == "__main__":
    main()
