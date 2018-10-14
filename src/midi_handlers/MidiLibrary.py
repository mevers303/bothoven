# Mark Evers
# 9/21/18
# MidiLibrary.py
# Objects for managing a set of MIDI files.

from abc import ABC, abstractmethod
import numpy as np
from midi_handlers.Music21ArrayBuilder import Music21ArrayBuilder

from files.file_functions import get_filenames
import wwts_globals
from wwts_globals import BATCH_SIZE, NUM_FEATURES, NUM_STEPS



class MidiLibrary(ABC):

    def __init__(self, base_dir="", filenames=None, autoload=True):

        self.base_dir = base_dir
        self.filenames = filenames
        self.midi = None

        if self.filenames is None:
            self.find_files()

        if autoload:
            self.load()


    def find_files(self):

        self.filenames = np.array(get_filenames(self.base_dir))
        print("Found", self.filenames.size, "files in", self.base_dir)


    @abstractmethod
    def load(self):
        pass



class MidiLibraryFlat(MidiLibrary):

    def __init__(self, base_dir="", filenames=None, autoload=True):

        self.buf = None
        super().__init__(base_dir, filenames, autoload)


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

        self.buf = np.concatenate(temp_buf, axis=0)


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




class MidiLibrarySplit(MidiLibrary):

    def __init__(self, base_dir):

        self.filenames_train = None
        self.filenames_test = None
        self.train_lib = None
        self.test_lib = None

        super().__init__(base_dir)


    def split_files(self):

        test_size = int(self.filenames.size / 4)
        test_indices = np.random.choice(self.filenames.size, size=test_size, replace=False)
        train_indices = np.delete(np.arange(self.filenames.size), test_indices)

        self.filenames_train = self.filenames[train_indices]
        self.filenames_test = self.filenames[test_indices]
        print("Buffering training set...")
        self.train_lib = MidiLibraryFlat(filenames=self.filenames_train)
        print("Buffering test set...")
        self.test_lib = MidiLibraryFlat(filenames=self.filenames_test)


    def load(self):

        self.split_files()

    def step_through(self):
        pass




def main():

    import os
    import pickle

    lib_name = "metallica_m21"

    lib = MidiLibraryFlat(os.path.join("midi", lib_name))
    # lib.load()  # autoload is on by default

    print("Pickling...")
    with open(os.path.join(f"midi/pickles/{lib_name}.pkl"), "wb") as f:
        pickle.dump(lib, f)
    print("Done!")



if __name__ == "__main__":
    main()
