# Mark Evers
# 9/21/18
# MidiLibrary.py
# Objects for managing a set of MIDI functions.

from abc import ABC, abstractmethod
import numpy as np

from functions.file_functions import get_filenames
import bothoven_globals
from bothoven_globals import BATCH_SIZE, NUM_FEATURES, NUM_STEPS



class MusicLibrary(ABC):

    def __init__(self, array_builder_type, base_dir="", filenames=None, autoload=True):

        self.array_builder_type = array_builder_type
        self.base_dir = base_dir
        self.filenames = filenames
        self.midi = None

        # number of timesteps for lstm
        self.NUM_STEPS = 64
        # how many features does this model have?
        self.NUM_FEATURES = -1
        # the batch size for training
        self.BATCH_SIZE = 64

        if self.filenames is None:
            self.find_files()

        if autoload:
            self.load()


    def find_files(self):

        self.filenames = np.array(get_filenames(self.base_dir))
        print("Found", self.filenames.size, "functions in", self.base_dir + "...")


    @abstractmethod
    def load(self):
        pass



class MusicLibraryFlat(MusicLibrary, ABC):

    def __init__(self, array_builder_type, base_dir="", filenames=None, autoload=True):

        self.buf = None
        MusicLibrary.__init__(self, array_builder_type, base_dir, filenames, autoload)


    def load(self):
        self.load_files()


    def load_files(self):

        self.buf = []
        done = 0

        for filename in self.filenames:

            # update the progress bar to show it's working on the current file
            bothoven_globals.progress_bar(done, self.filenames.size, "Buffering " + filename + "...")
            # for progress tracking
            done += 1

            try:
                file_buf = self.array_builder_type(filename).mid_to_array()
            except Exception as e:
                print("\nThere was an error buffering", filename)
                print(e)
                continue

            # slap this file's buffer onto the back of our running buffer
            self.buf.append(file_buf)

        # finish off the progress bar
        bothoven_globals.progress_bar(done, self.filenames.size, "Buffering complete!")


    @abstractmethod
    def step_through(self):
        pass


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



class MusicLibrarySplit(MusicLibrary):

    def __init__(self, array_builder_type, flat_library_type, base_dir="", filenames=None, autoload=True):

        self.filenames_train = None
        self.filenames_test = None
        self.train_lib = None
        self.test_lib = None
        self.flat_library_type = flat_library_type

        super().__init__(array_builder_type, base_dir, filenames, autoload)


    def split_files(self):

        test_size = int(self.filenames.size / 4)
        test_indices = np.random.choice(self.filenames.size, size=test_size, replace=False)
        train_indices = np.delete(np.arange(self.filenames.size), test_indices)

        self.filenames_train = self.filenames[train_indices]
        self.filenames_test = self.filenames[test_indices]
        print("Buffering training set...")
        self.train_lib = self.flat_library_type(filenames=self.filenames_train)
        print("Buffering test set...")
        self.test_lib = self.flat_library_type(filenames=self.filenames_test)


    def load(self):
        self.split_files()

    def step_through(self):
        pass




def main():

    import os
    import pickle

    lib_name = "metallica_m21"

    lib = MusicLibraryFlat(os.path.join("midi", lib_name))
    # lib.load()  # autoload is on by default

    print("Pickling...")
    with open(os.path.join(f"midi/pickles/{lib_name}.pkl"), "wb") as f:
        pickle.dump(lib, f)
    print("Done!")



if __name__ == "__main__":
    main()
