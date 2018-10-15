# Mark Evers
# 9/21/18
# MidiLibrary.py
# Objects for managing a set of MIDI files.

import numpy as np
from midi_handlers.Music21ArrayBuilder import Music21ArrayBuilder

import wwts_globals
from wwts_globals import BATCH_SIZE, NUM_FEATURES, NUM_STEPS
from midi_handlers.MidiLibrary import MidiLibrary


class Music21LibraryFlat(MidiLibrary):

    def __init__(self, base_dir="", filenames=None, autoload=True):

        self.buf = None
        super().__init__(base_dir, filenames, autoload)
        self.beat_norm_max = 0


    def load(self):
        self.load_files()


    def load_files(self):

        temp_buf = []
        done = 0

        for filename in self.filenames:

            # update the progress bar to show it's working on the current file
            wwts_globals.progress_bar(done, self.filenames.size, "Buffering " + filename + "...", clear_when_done=True)
            # for progress tracking
            done += 1

            try:
                file_buf = Music21ArrayBuilder(filename).mid_to_array()
            except Exception as e:
                print("\nThere was an error buffering", filename)
                print(e)
                continue

            # slap this file's buffer onto the back of our running buffer
            temp_buf.extend(file_buf)

        # finish off the progress bar
        wwts_globals.progress_bar(done, self.filenames.size, "Buffering complete!", clear_when_done=True)

        self.buf = np.array(temp_buf)

        self.beat_norm_max = self.buf[:, -5].max()
        self.buf[:, -5] = self.buf[:, -5] / self.beat_norm_max


    def step_through(self):

        i = 0

        while i < self.buf.shape[0] - NUM_STEPS - 1:  # gotta leave room for the target at the end

            x = self.buf[i:i + NUM_STEPS]
            y = self.buf[i + NUM_STEPS]

            i += 1

            yield x, y


    def next_batch(self):

        i = 0
        batch_x = []
        batch_y = []

        while True:

            for x, y in self.step_through():

                if i >= BATCH_SIZE:
                    yield np.array(batch_x), np.array(batch_y)
                    batch_x.clear()
                    batch_y.clear()
                    i = 0

                batch_x.append(x)
                batch_y.append(y)
                i += 1

            yield np.array(batch_x), np.array(batch_y)
            batch_x.clear()
            batch_y.clear()
            i = 0


def main():

    import os
    import pickle

    lib_name = "bach"

    lib = Music21LibraryFlat(os.path.join("midi", lib_name))
    # lib.load()  # autoload is on by default

    print("Pickling...")
    with open(os.path.join(f"midi/pickles/{lib_name}_m21.pkl"), "wb") as f:
        pickle.dump(lib, f)
    print("Done!")



if __name__ == "__main__":
    main()
