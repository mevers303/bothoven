# Mark Evers
# 9/21/18
# MidiLibrary.py
# Objects for managing a set of MIDI files.

import numpy as np
import mido
import random
from sklearn.model_selection import train_test_split

from files.file_functions import get_filenames
import wwts_globals



class MidiLibrary:

    def __init__(self, base_dir, autoload=True):

        self.base_dir = base_dir
        self.filenames = None
        self.mids = None

        self.get_filenames()
        if autoload:
            self.load()


    def get_filenames(self):

        self.filenames = np.array(get_filenames(self.base_dir))
        print("Found", self.filenames.size, "in", self.base_dir)


    def load(self):

        midi_files = []
        done = 0

        for filename in self.filenames:
            try:
                midi_files.append(mido.MidiFile(filename))
            except Exception as e:
                print("\nThere was an error reading", filename)
                print(e)
            finally:
                done += 1
                wwts_globals.progress_bar(done, self.filenames.size)

        self.mids = np.array(midi_files)


    def step_through(self):

        for mid in self.mids:

            for track in mid.tracks:

                # time series matrix
                buf = np.zeros((wwts_globals.NUM_STEPS, wwts_globals.NUM_FEATURES), dtype=np.uint32)
                # set special one-hot for track_start
                buf[-1, -2] = 1
                # cumulative delta time from skipped notes
                cum_time = 0

                for msg in track:

                    if not (msg.type == "note_on" or msg.type == "note_off") or msg.channel == 9:  # skip drum tracks
                        # store the delta time of any skipped messages
                        cum_time += msg.time
                        continue

                    # the next note beyond the buffer
                    target = np.zeros((wwts_globals.NUM_FEATURES), dtype=np.uint32)
                    # set the time
                    target[0] = msg.time + cum_time
                    # reset skipped time delta
                    cum_time = 0
                    # find the one-hot note code
                    note_code = msg.note + 1 if msg.type == "note_on" else msg.note + 128 + 1
                    target[note_code] = 1
                    # spit out this buffer
                    yield buf.copy(), target

                    # move the time series up one
                    buf = np.roll(buf, -1, axis=0)
                    # store this message as the last in the time series
                    buf[-1] = target

                # now this is the end of the track
                # if there were actual usable messages in the track, end the track
                if buf[-1, -2] != 1:
                    # special one-hot for track end
                    target = np.zeros((wwts_globals.NUM_FEATURES), dtype=np.uint32)
                    target[-1] = 1
                    # yield the end of track
                    yield buf.copy(), target
                else:
                    pass

            print(len(mid.tracks), mid.filename)



class MidiLibrarySplit(MidiLibrary):

    def __init__(self, base_dir):

        super().__init__(base_dir)

        self.filenames_train = None
        self.filenames_test = None
        self.mids_train = None
        self.mids_test = None


    def split_files(self):

        test_size = int(self.filenames.size / 4)
        test_indices = np.random.choice(self.filenames.size, size=test_size, replace=False)
        train_indices = np.delete(np.arange(self.filenames.size), test_indices)

        self.filenames_train = self.filenames[train_indices]
        self.filenames_test = self.filenames[test_indices]
        self.mids_train = self.mids[train_indices]
        self.mids_test = self.mids[test_indices]


    def load(self):

        super().load()
        self.split_files()



def main():

    import pickle

    lib = MidiLibrary("midi/bach_cleaned")
    lib.load()

    with open("midi/pickles/bach.pkl", "wb") as f:
        pickle.dump(lib, f)

    # with open("midi/pickles/bach.pkl", "rb") as f:
    #     lib = pickle.load(f)

        # x = 0
        #
        # for buf, target in lib.step_through():
        #     pass
        #     # print("time:", str(time).rjust(5), "note: ", note)

if __name__ == "__main__":
    main()
