# Mark Evers
# 9/21/18
# MidiLibrary.py
# Objects for managing a set of MIDI functions.

from midi_handlers.MidiLibrary import MidiLibraryFlat
from functions.pickle_workaround import pickle_dump

import numpy as np



class SplitOutputMidiLibraryFlat(MidiLibraryFlat):


    def next_batch(self):

        batch_i = 0
        batch_x = []
        batch_y = []

        def give_yield():
            global batch_i, batch_x, batch_y
            yield_y = np.array(batch_y)
            yield np.array(batch_x), {"note_output": yield_y[:, :258], "delay_output": yield_y[:, 258:]}
            batch_x.clear()
            batch_y.clear()
            batch_i = 0


        while True:

            for x, y in self.step_through():

                if batch_i >= self.BATCH_SIZE:
                    give_yield()

                batch_x.append(x)
                batch_y.append(y)
                batch_i += 1

            give_yield()


def main():

    import os

    lib_name = "beatles"

    lib = SplitOutputMidiLibraryFlat(os.path.join("midi", lib_name))
    # lib.load()  # autoload is on by default

    print("Pickling...")
    pickle_dump(lib, f"midi/pickles/{lib_name}_midi_split_output.pkl")
    print("Done!")

if __name__ == "__main__":
    main()
