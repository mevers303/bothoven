# Mark Evers
# 9/21/18
# MidiLibrary.py
# Objects for managing a set of MIDI functions.

import numpy as np
import scipy.sparse as sps
from midi_handlers.Music21ArrayBuilder import Music21ArrayBuilder
from functions.pickle_workaround import pickle_dump

from midi_handlers.MusicLibrary import MusicLibrary, MusicLibraryFlat, MusicLibrarySplit
import functions.s3 as s3


class Music21Library(MusicLibraryFlat):

    def __init__(self, base_dir="", filenames=None, autoload=True):

        self.note_to_one_hot = None
        self.one_hot_to_note = None
        self.duration_to_one_hot = None
        self.one_hot_to_duration = None

        super().__init__(Music21ArrayBuilder, base_dir, filenames, autoload)


    def load_files(self):
        super().load_files()
        if not self.note_to_one_hot:
            self.get_one_hots()


    def get_one_hots(self):
        print("Parsing notes...")

        temp_buf = np.vstack(self.buf)
        notes = temp_buf[:, 0]
        durations = temp_buf[:, 1]

        self.note_to_one_hot, self.one_hot_to_note = self.convert_to_one_hot(notes)
        self.duration_to_one_hot, self.one_hot_to_duration = self.convert_to_one_hot(durations)
        self.num_features = len(self.note_to_one_hot) + len(self.duration_to_one_hot) + 1

        print(f"Found {temp_buf.shape[0]} rows with {self.num_features} features!")


    @staticmethod
    def convert_to_one_hot(x):
        unique_x = np.unique(x)
        x_to_one_hot = {item: i for i, item in enumerate(unique_x)}
        one_hot_to_x = {i: item for i, item in enumerate(unique_x)}

        return x_to_one_hot, one_hot_to_x



class Music21LibraryFlat(Music21Library):

    def __init__(self, base_dir="", filenames=None, autoload=True, note_to_one_hot=None, one_hot_to_note=None,
                 duration_to_one_hot=None, one_hot_to_duration=None, num_features=None):

        super().__init__(base_dir, filenames, False)

        self.note_to_one_hot = note_to_one_hot
        self.one_hot_to_note = one_hot_to_note
        self.duration_to_one_hot = duration_to_one_hot
        self.one_hot_to_duration = one_hot_to_duration
        self.num_features = num_features
        self.avg_offset = 0
        self.max_offset = 0

        if autoload:
            self.load_files()


    def load_files(self):
        super().load_files()
        self.explode_buf()


    def explode_buf(self):
        temp_buf = np.vstack(self.buf)
        notes = temp_buf[:, 0]
        durations = temp_buf[:, 1]
        offsets = temp_buf[:, 2]
        # normalize the offsets
        self.avg_offset = offsets.mean()
        self.max_offset = np.max([np.abs(n) for n in offsets])
        offsets = offsets - self.avg_offset
        offsets = offsets / self.max_offset

        x = [i for i in range(temp_buf.shape[0])] * 3
        y = [self.note_to_one_hot[note] for note in notes] + \
            [self.duration_to_one_hot[duration] + len(self.note_to_one_hot) for duration in durations] + \
            [len(self.note_to_one_hot) + len(self.duration_to_one_hot) for _ in range(offsets.shape[0])]
        data = [1 for _ in range(temp_buf.shape[0] * 2)] + list(offsets)

        self.buf = sps.csr_matrix((data, (x, y)), shape=(temp_buf.shape[0], self.num_features), dtype=np.byte)


    def next_batch(self):

        batch_i = 0
        batch_x = []
        batch_y = []

        while True:

            for x, y in self.step_through():

                if batch_i >= self.batch_size:
                    yield_y = np.array(batch_y)
                    yield np.array(batch_x), {
                                              "n": yield_y[:, :len(self.note_to_one_hot)],
                                              "d": yield_y[:, len(self.note_to_one_hot):len(self.note_to_one_hot) + len(self.duration_to_one_hot)],
                                              "o": yield_y[:, len(self.note_to_one_hot) + len(self.duration_to_one_hot)]
                                             }
                    batch_x.clear()
                    batch_y.clear()
                    batch_i = 0

                batch_x.append(x)
                batch_y.append(y)
                batch_i += 1

            yield_y = np.array(batch_y)
            yield np.array(batch_x), {
                                      "n": yield_y[:, :len(self.note_to_one_hot)],
                                      "d": yield_y[:, len(self.note_to_one_hot):len(self.note_to_one_hot) + len(self.duration_to_one_hot)],
                                      "o": yield_y[:, len(self.note_to_one_hot) + len(self.duration_to_one_hot)]
                                     }
            batch_x.clear()
            batch_y.clear()
            batch_i = 0


class Music21LibrarySplit(Music21Library):

    def __init__(self, base_dir="", filenames=None, autoload=True, split_ratio=0.25):

        self.train_indices = None
        self.test_indices = None
        self.train_lib = None
        self.test_lib = None
        self.split_ratio = split_ratio

        super().__init__(base_dir, filenames, autoload)


    def load_files(self):
        super().load_files()
        self.split_files()


    def split_files(self):

        test_size = round(self.filenames.size * self.split_ratio)
        self.test_indices = np.random.choice(self.filenames.size, size=test_size, replace=False)
        self.train_indices = np.delete(np.arange(self.filenames.size), self.test_indices)

        self.train_lib = Music21LibraryFlat(filenames=self.filenames[self.train_indices],
                                            autoload=False,
                                            note_to_one_hot=self.note_to_one_hot,
                                            one_hot_to_note=self.one_hot_to_note,
                                            duration_to_one_hot=self.duration_to_one_hot,
                                            one_hot_to_duration=self.one_hot_to_duration,
                                            num_features=self.num_features)
        self.train_lib.buf = [self.buf[x] for x in self.train_indices]
        self.train_lib.explode_buf()

        self.test_lib = Music21LibraryFlat(filenames=self.filenames[self.test_indices],
                                           autoload=False,
                                           note_to_one_hot=self.note_to_one_hot,
                                           one_hot_to_note=self.one_hot_to_note,
                                           duration_to_one_hot=self.duration_to_one_hot,
                                           one_hot_to_duration=self.one_hot_to_duration,
                                           num_features=self.num_features)
        self.test_lib.buf = [self.buf[x] for x in self.test_indices]
        self.test_lib.explode_buf()

        del self.buf


def main():

    import os

    lib_name = "chopin_2hand"
    lib = Music21LibrarySplit(os.path.join("midi", lib_name))

    print("Pickling...")
    path = f"midi/pickles/{lib_name}_m21.pkl"
    pickle_dump(lib, path)
    s3.upload_file(path)
    print("Done!")



if __name__ == "__main__":
    main()
