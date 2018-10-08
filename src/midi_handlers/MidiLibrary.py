# Mark Evers
# 9/21/18
# MidiLibrary.py
# Objects for managing a set of MIDI files.

from abc import ABC, abstractmethod
import numpy as np
import mido
import random
from sklearn.model_selection import train_test_split

from files.file_functions import get_filenames
import wwts_globals
from wwts_globals import NUM_STEPS, NUM_FEATURES



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
        print("Found", self.filenames.size, "in", self.base_dir)


    @abstractmethod
    def load(self):
        pass


    @abstractmethod
    def step_through(self):
        pass


    @staticmethod
    def load_files(filenames):

        buf = []
        done = 0

        for filename in filenames:

            wwts_globals.progress_bar(done, filenames.size, "Buffering " + filename + "...")
            done += 1

            try:
                mid = mido.MidiFile(filename)
            except Exception as e:
                print("\nThere was an error reading", filename)
                print(e)
                continue

            buf.extend(MidiLibrary.mid_to_array(mid))

        wwts_globals.progress_bar(done, filenames.size, "Buffering complete!")

        return np.array(buf, dtype=np.uint32)


    @staticmethod
    def mid_to_array(mid):

        # empty space before each file
        buf = [np.zeros(NUM_FEATURES, dtype=np.uint32) for _ in range(NUM_STEPS - 1)]

        for track in mid.tracks:

            # cumulative delta time from skipped notes
            cum_time = 0
            # need this to track start/end of track
            found_a_note = False

            for msg in track:

                if not (msg.type == "note_on" or msg.type == "note_off") or msg.channel == 9:  # skip drum tracks
                    # store the delta time of any skipped messages
                    cum_time += msg.time
                    continue

                # it will never get here if it never finds a note
                if not found_a_note:
                    found_a_note = True
                    # slide a start_track in there
                    this_step = np.zeros(NUM_FEATURES, dtype=np.uint32)
                    this_step[-2] = 1
                    buf.append(this_step)

                # the current step we are on
                this_step = np.zeros(NUM_FEATURES, dtype=np.uint32)
                this_step[-3] = msg.time + cum_time
                cum_time = 0
                # find the one-hot note code
                note_code = msg.note if msg.type == "note_on" else msg.note + 128
                this_step[note_code] = 1

                buf.append(this_step)

            if found_a_note:
                # slide a start_end in there
                this_step = np.zeros(NUM_FEATURES, dtype=np.uint32)
                this_step[-1] = 1
                buf.append(this_step)

        return buf



class MidiLibraryFlat(MidiLibrary):

    def __init__(self, base_dir="", filenames=None, autoload=True):

        self.buf = None
        super().__init__(base_dir, filenames, autoload)


    def load(self):
        self.buf = self.load_files(self.filenames)


    def step_through(self):

        i = 0

        while True:

            # reset it when it gets to the end
            if i > self.buf.shape[0] - NUM_STEPS - 1:  # gotta leave room for the target at the end
                i = 0

            x = self.buf[i:i + NUM_STEPS]
            y = self.buf[i + NUM_STEPS]

            i += 1

            yield x, y



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

    import pickle

    lib = MidiLibrarySplit("midi/bach_cleaned")
    # lib.load()  # autoload is on by default

    with open("midi/pickles/bach.pkl", "wb") as f:
        pickle.dump(lib, f)

    # with open("midi/pickles/bach.pkl", "rb") as f:
    #     lib = pickle.load(f)

    # for buf, target in lib.step_through():
    #     pass
    #     # print("time:", str(time).rjust(5), "note: ", note)

if __name__ == "__main__":
    main()
