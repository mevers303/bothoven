# Mark Evers
# 9/21/18
# MidiLibrary.py
# Objects for managing a set of MIDI functions.

import scipy.sparse
from midi_handlers.MusicLibrary import MusicLibraryFlat
from midi_handlers.MidiArrayBuilder import MidiArrayBuilder
from functions.pickle_workaround import pickle_dump

import numpy as np



class MidiLibraryFlat(MusicLibraryFlat):

    def __init__(self, base_dir="", filenames=None, autoload=True):

        self.max_delay = 0
        self.delay_to_one_hot = None
        self.one_hot_to_delay = None

        super().__init__(MidiArrayBuilder, base_dir, filenames, autoload)

        # number of timesteps for lstm
        self.NUM_STEPS = 64
        # how many features does this model have?
        # the batch size for training
        self.BATCH_SIZE = 64


    def load_files(self):

        super().load_files()

        # build the time one-hot from the second item in the tuple
        delay_buf = np.hstack(x[1] for x in self.buf)
        unique_delays = np.unique(delay_buf)
        self.delay_to_one_hot = {delay: i for i, delay in enumerate(unique_delays)}
        self.one_hot_to_delay = {i: delay for i, delay in enumerate(unique_delays)}

        data = [1 for _ in range(delay_buf.size)]
        x = np.arange(delay_buf.size)
        y = [self.delay_to_one_hot[delay] for delay in delay_buf]
        delay_buf_onehot = scipy.sparse.csr_matrix((data, (x, y)), shape=(delay_buf.size, unique_delays.size))

        # build the sparse matrix from the first iem in the tuple
        self.buf = scipy.sparse.vstack((x[0] for x in self.buf), format="csr")

        # combine them
        self.buf = scipy.sparse.hstack((self.buf, delay_buf_onehot), format="csr")



def main():

    import os

    lib_name = "beatles"

    lib = MidiLibraryFlat(os.path.join("midi", lib_name))
    # lib.load()  # autoload is on by default

    print("Pickling...")
    pickle_dump(lib, f"midi/pickles/{lib_name}_midi.pkl")
    print("Done!")

if __name__ == "__main__":
    main()
