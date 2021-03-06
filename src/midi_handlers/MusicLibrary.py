# Mark Evers
# 9/21/18
# MidiLibrary.py
# Objects for managing a set of MIDI functions.

from abc import ABC, abstractmethod
import numpy as np

from functions.file_functions import get_filenames
import bothoven_globals
from bothoven_globals import NUM_STEPS



class MusicLibrary(ABC):

    def __init__(self, array_builder_type, base_dir="", filenames=None, autoload=True):

        self.array_builder_type = array_builder_type
        self.base_dir = base_dir
        self.filenames = filenames
        self.midi = None

        # how many features does this model have?
        self.num_features = -1
        # batch size to use when training the model
        self.batch_size = -1

        if self.filenames is None:
            self.find_files()
        elif type(self.filenames) is list:
            self.filenames = np.array(self.filenames)

        if autoload:
            self.load_files()


    def find_files(self):

        self.filenames = np.array(get_filenames(self.base_dir, [".mid", ".midi", ".smf"]))
        print("Found", self.filenames.size, "files in", self.base_dir + "...")


    @abstractmethod
    def load_files(self):
        pass



class MusicLibraryFlat(MusicLibrary):

    def __init__(self, array_builder_type, base_dir="", filenames=None, autoload=True):

        self.buf = None
        MusicLibrary.__init__(self, array_builder_type, base_dir, filenames, autoload)


    def load_files(self):

        self.buf = []
        done = 0

        bad_files = []

        for filename in self.filenames:

            # update the progress bar to show it's working on the current file
            bothoven_globals.progress_bar(done, self.filenames.size, "Buffering " + filename + "...")
            # for progress tracking
            done += 1

            try:
                file_buf = self.array_builder_type(filename).mid_to_array()
            except Exception as e:
                bad_files.append(done - 1)  # done - 1 is the index
                print("\nError!", e)
                print()
                continue

            # slap this file's buffer onto the back of our running buffer
            self.buf.append(file_buf)

        # finish off the progress bar
        bothoven_globals.progress_bar(done, self.filenames.size, "Buffering complete!")

        self.filenames = np.delete(self.filenames, bad_files)



    def step_through(self):

        i = 0

        while i < self.buf.shape[0] - NUM_STEPS - 1:  # gotta leave room for the target at the end

            x = self.buf[i:i + NUM_STEPS].toarray()
            y = self.buf[i + NUM_STEPS].toarray()[0]

            i += 1

            yield x, y


    def next_batch(self):

        i = 0
        batch_x = []
        batch_y = []

        while True:

            for x, y in self.step_through():

                if i >= self.batch_size:
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



class MusicLibrarySplit(MusicLibrary, ABC):

    def __init__(self, array_builder_type, flat_library_type, base_dir="", filenames=None, autoload=True):

        self.filenames_train = None
        self.filenames_test = None
        self.train_lib = None
        self.test_lib = None
        self.flat_library_type = flat_library_type

        super().__init__(array_builder_type, base_dir, filenames, autoload)


    def split_files(self):

        test_size = self.filenames.size // 10
        test_indices = np.random.choice(self.filenames.size, size=test_size, replace=False)
        train_indices = np.delete(np.arange(self.filenames.size), test_indices)

        self.filenames_train = self.filenames[train_indices]
        self.filenames_test = self.filenames[test_indices]
        print("Buffering training set...")
        self.train_lib = self.flat_library_type(filenames=self.filenames_train)
        print("Buffering test set...")
        self.test_lib = self.flat_library_type(filenames=self.filenames_test)


    def load_files(self):
        self.split_files()

    def step_through(self):
        pass
