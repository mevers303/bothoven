# Mark Evers
# 9/21/18
# MidiLibrary.py
# Objects for managing a set of MIDI functions.

import numpy as np
import scipy.sparse as sps
from midi_handlers.Music21ArrayBuilder import Music21ArrayBuilder

from midi_handlers.MusicLibrary import MusicLibrary, MusicLibraryFlat, MusicLibrarySplit


class Music21Library(MusicLibraryFlat):

    def __init__(self, base_dir="", filenames=None, autoload=True):

        self.note_to_one_hot = None
        self.one_hot_to_note = None
        self.duration_to_one_hot = None
        self.one_hot_to_duration = None
        self.offset_to_one_hot = None
        self.one_hot_to_offset = None

        super().__init__(Music21ArrayBuilder, base_dir, filenames, autoload)


    def load(self):
        super().load()
        if not self.note_to_one_hot:
            self.get_one_hots()


    def get_one_hots(self):
        print("Parsing notes...")

        temp_buf = np.vstack(self.buf)
        notes = temp_buf[:, 0]
        durations = temp_buf[:, 1]
        offsets = temp_buf[:, 2]

        self.note_to_one_hot, self.one_hot_to_note = self.convert_to_one_hot(notes)
        self.duration_to_one_hot, self.one_hot_to_duration = self.convert_to_one_hot(durations)
        self.offset_to_one_hot, self.one_hot_to_offset = self.convert_to_one_hot(offsets)
        self.NUM_FEATURES = + len(self.note_to_one_hot) + len(self.duration_to_one_hot) + len(self.offset_to_one_hot)


    @staticmethod
    def convert_to_one_hot(x):
        unique_x = np.unique(x)
        x_to_one_hot = {item: i for i, item in enumerate(unique_x)}
        one_hot_to_x = {i: item for i, item in enumerate(unique_x)}

        return x_to_one_hot, one_hot_to_x



class Music21LibraryFlat(Music21Library):

    def __init__(self, base_dir="", filenames=None, autoload=True, note_to_one_hot=None, one_hot_to_note=None,
                 duration_to_one_hot=None, one_hot_to_duration=None, offset_to_one_hot=None, one_hot_to_offset=None,
                 num_features=None):

        super().__init__(base_dir, filenames, False)

        self.note_to_one_hot = note_to_one_hot
        self.one_hot_to_note = one_hot_to_note
        self.duration_to_one_hot = duration_to_one_hot
        self.one_hot_to_duration = one_hot_to_duration
        self.offset_to_one_hot = offset_to_one_hot
        self.one_hot_to_offset = one_hot_to_offset
        self.NUM_FEATURES = num_features

        if autoload:
            self.load_files()


    def load(self):
        super().load()
        self.explode_buf()


    def explode_buf(self):
        temp_buf = np.vstack(self.buf)
        notes = temp_buf[:, 0]
        durations = temp_buf[:, 1]
        offsets = temp_buf[:, 2]

        x = [i for i in range(temp_buf.shape[0])] * 3
        y = [self.note_to_one_hot[x] for x in notes] + \
            [self.duration_to_one_hot[x] + len(self.note_to_one_hot) for x in durations] + \
            [self.offset_to_one_hot[x] + len(self.note_to_one_hot) + len(self.duration_to_one_hot) for x in offsets]
        data = [1 for _ in range(temp_buf.shape[0] * 3)]

        self.buf = sps.csr_matrix((data, (x, y)), shape=(temp_buf.shape[0], self.NUM_FEATURES), dtype=np.byte)


class Music21LibrarySplit(Music21Library):

    def __init__(self, base_dir="", filenames=None, autoload=True):

        self.train_indices = None
        self.test_indices = None
        self.train_lib = None
        self.test_lib = None

        super().__init__(base_dir, filenames, autoload)


    def load(self):
        super().load()
        self.split_files()


    def split_files(self):

        test_size = self.filenames.size // 10
        self.test_indices = np.random.choice(self.filenames.size, size=test_size, replace=False)
        self.train_indices = np.delete(np.arange(self.filenames.size), self.test_indices)

        self.train_lib = Music21LibraryFlat(filenames=self.filenames[self.train_indices],
                                            autoload=False,
                                            note_to_one_hot=self.note_to_one_hot,
                                            one_hot_to_note=self.one_hot_to_note,
                                            duration_to_one_hot=self.duration_to_one_hot,
                                            one_hot_to_duration=self.one_hot_to_duration,
                                            offset_to_one_hot=self.offset_to_one_hot,
                                            one_hot_to_offset=self.one_hot_to_offset,
                                            num_features=self.NUM_FEATURES)
        self.train_lib.buf = [self.buf[x] for x in self.train_indices]
        self.train_lib.explode_buf()

        self.test_lib = Music21LibraryFlat(filenames=self.filenames[self.test_indices],
                                           autoload=False,
                                           note_to_one_hot=self.note_to_one_hot,
                                           one_hot_to_note=self.one_hot_to_note,
                                           duration_to_one_hot=self.duration_to_one_hot,
                                           one_hot_to_duration=self.one_hot_to_duration,
                                           offset_to_one_hot=self.offset_to_one_hot,
                                           one_hot_to_offset=self.one_hot_to_offset,
                                           num_features=self.NUM_FEATURES)
        self.test_lib.buf = [self.buf[x] for x in self.test_indices]
        self.test_lib.explode_buf()

        del self.buf

def main():

    import os
    import pickle

    lib_name = "bach_short"

    lib = Music21LibrarySplit(os.path.join("midi", lib_name))
    # from music21.corpus import getComposer
    # filenames = [x.as_posix() for x in getComposer("bach")]
    # lib = Music21LibrarySplit(filenames=filenames)

    print("Pickling...")
    with open(os.path.join(f"midi/pickles/{lib_name}_m21.pkl"), "wb") as f:
        pickle.dump(lib, f)
    print("Done!")



if __name__ == "__main__":
    main()
