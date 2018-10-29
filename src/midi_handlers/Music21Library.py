# Mark Evers
# 9/21/18
# MidiLibrary.py
# Objects for managing a set of MIDI functions.

import numpy as np
import scipy.sparse as sps
from midi_handlers.Music21ArrayBuilder import Music21ArrayBuilder

from midi_handlers.MusicLibrary import MusicLibraryFlat, MusicLibrarySplit


class Music21LibraryFlat(MusicLibraryFlat):

    def __init__(self, base_dir="", filenames=None, autoload=True):

        super().__init__(Music21ArrayBuilder, base_dir, filenames, autoload)

        self.note_to_one_hot = None
        self.one_hot_to_note = None
        self.duration_to_one_hot = None
        self.one_hot_to_duration = None
        self.offset_to_one_hot = None
        self.one_hot_to_offset = None


    def load_files(self):

        super().load_files()
        self.explode_buf()


    def explode_buf(self):

        temp_buf = np.vstack(self.buf)
        notes = temp_buf[:, 0]
        durations = temp_buf[:, 1]
        offsets = temp_buf[:, 2]

        self.note_to_one_hot, self.one_hot_to_note = self.convert_to_one_hot(notes)
        self.duration_to_one_hot, self.one_hot_to_duration = self.convert_to_one_hot(durations)
        self.offset_to_one_hot, self.one_hot_to_offset = self.convert_to_one_hot(offsets)
        self.NUM_FEATURES =  + len(self.note_to_one_hot) + len(self.duration_to_one_hot) + len(self.offset_to_one_hot)

        x = [i for i in range(temp_buf.shape[0])] * 3
        y = [self.note_to_one_hot[x] for x in notes] + \
            [self.duration_to_one_hot[x] + len(self.note_to_one_hot) for x in durations] + \
            [self.offset_to_one_hot[x] + len(self.note_to_one_hot) + len(self.duration_to_one_hot) for x in offsets]
        data = [1 for _ in range(temp_buf.shape[0] * 3)]

        self.buf = sps.csr_matrix((data, (x, y)), shape=(temp_buf.shape[0], self.NUM_FEATURES), dtype=np.byte)


    @staticmethod
    def convert_to_one_hot(x):
        unique_x = np.unique(x)
        x_to_one_hot = {item: i for i, item in enumerate(unique_x)}
        one_hot_to_x = {i: item for i, item in enumerate(unique_x)}

        return x_to_one_hot, one_hot_to_x


class Music21LibrarySplit(MusicLibrarySplit):

    def __init__(self, base_dir="", filenames=None, autoload=True):
        super().__init__(Music21ArrayBuilder, Music21LibraryFlat, base_dir, filenames, autoload)


def main():

    import os
    import pickle
    from music21.corpus import getComposer

    lib_name = "bach"
    filenames = [x.as_posix() for x in getComposer("bach")]

    lib = Music21LibrarySplit(filenames=filenames)
    # lib = Music21LibraryFlat(filenames=np.array([str(x) for x in music21.corpus.getComposer("bach")]))
    # lib.load()  # autoload is on by default

    print("Pickling...")
    with open(os.path.join(f"midi/pickles/{lib_name}_m21.pkl"), "wb") as f:
        pickle.dump(lib, f)
    print("Done!")



if __name__ == "__main__":
    main()
