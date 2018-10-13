# Mark Evers
# 9/21/18
# MidiLibrary.py
# Objects for managing a set of MIDI files.

from abc import ABC, abstractmethod
import numpy as np
import music21

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

            wwts_globals.progress_bar(done, filenames.size, "Buffering " + filename + "...", clear_when_done=True)
            done += 1

            try:
                mid = music21.converter.parse(filename)
            except Exception as e:
                print("\nThere was an error reading", filename)
                print(e)
                continue

            buf.extend(MidiLibrary.mid_to_array(mid))

        wwts_globals.progress_bar(done, filenames.size, "Buffering complete!", clear_when_done=True)

        return np.array(buf)


    @staticmethod
    def mid_to_array(mid):

        # empty space before each file
        buf = [np.zeros(NUM_FEATURES) for _ in range(NUM_STEPS - 1)]

        for track in mid.parts:

            # need this to track start/end of track
            found_a_note = False

            for msg in track.notesAndRests:

                # it will never get here if it never finds a note
                if not found_a_note:
                    found_a_note = True
                    # slide a start_track in there
                    this_step = np.zeros(NUM_FEATURES)
                    this_step[-2] = 1
                    buf.append(this_step)

                # find the one-hot note
                if msg.isNote:
                    buf.append(MidiLibrary.build_step(msg.pitch.midi, msg.quarterLength))
                elif msg.isRest:
                    buf.append(MidiLibrary.build_step(128, msg.quarterLength))
                elif msg.isChord:
                    for note in msg._notes:
                        buf.append(MidiLibrary.build_step(note.pitch.midi, note.quarterLength, chord=True))
                    pass
                else:
                    raise TypeError("Unknown message in notesAndRests: " + msg.fullName)

            if found_a_note:
                # slide a start_end in there
                this_step = np.zeros(NUM_FEATURES)
                this_step[-1] = 1
                buf.append(this_step)

        if len(buf) == 63:
            # raise Exception("No notes found in the MIDI file!")
            return []

        return buf


    @staticmethod
    def build_step(note_i, duration, chord=False):

        # find the one-hot note duration
        duration_i = wwts_globals.get_note_duration_bin(duration)

        # buffer for the current step we are on
        this_step = np.zeros(NUM_FEATURES)
        this_step[note_i] = 1
        this_step[129 + duration_i] = 1
        if chord:
            this_step[129 + len(wwts_globals.DURATION_BINS)] = 1

        return this_step



class MidiLibraryFlat(MidiLibrary):

    def __init__(self, base_dir="", filenames=None, autoload=True):

        self.buf = None
        super().__init__(base_dir, filenames, autoload)


    def load(self):
        self.buf = self.load_files(self.filenames)


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

    lib_name = "metallica"

    lib = MidiLibraryFlat(os.path.join("midi", lib_name))
    # lib.load()  # autoload is on by default

    print("Pickling...")
    with open(os.path.join(f"midi/pickles/{lib_name}.pkl"), "wb") as f:
        pickle.dump(lib, f)
    print("Done!")


def test():

    import os
    import pickle

    lib_name = "metallica"

    print("Loading pickle...")
    with open(os.path.join(f"midi/pickles/{lib_name}.pkl"), "rb") as f:
        lib = pickle.load(f)
    print("Done!")

    for x, y in lib.step_through():
        print("x:")
        print(x)
        print("y:")
        print(y)
        print("\n")


if __name__ == "__main__":
    main()
