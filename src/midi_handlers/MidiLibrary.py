# Mark Evers
# 9/21/18
# MidiLibrary.py
# Objects for managing a set of MIDI files.

import numpy as np
import mido
import os
import random
from sklearn.model_selection import train_test_split

from files.file_functions import get_filenames
import wwts_globals



class FlatMidiLibrary:

    def __init__(self, base_dir):

        self.base_dir = base_dir
        self.filenames = None
        self.filenames_count = 0
        self.mids = None

        self.get_filenames()


    def get_filenames(self):

        self.filenames = get_filenames(self.base_dir)
        self.filenames_count = len(self.filenames)
        print("Found", self.filenames_count, "in", self.base_dir)


    def load(self):

        self.mids = []
        done = 0

        for filename in self.filenames:
            try:
                self.mids.append(mido.MidiFile(filename))
            except Exception as e:
                print("\nThere was an error reading", filename)
                print(e)
            finally:
                done += 1
                wwts_globals.progress_bar(done, self.filenames_count)


    def step_through(self):

        for mid in self.mids:

            for track in mid.tracks:

                # time series matrix
                buf = np.zeros((wwts_globals.NUM_STEPS, wwts_globals.NUM_FEATURES))
                # set special one-hot for track_start
                buf[-1, -2] = 1
                # cumulative delta time from skipped notes
                cum_time = 0

                for msg in track:

                    if msg.type != "note_on" or msg.type != "note_off":
                        # store the delta time of any skipped messages
                        cum_time += msg.time
                        continue

                    # move the time series up one
                    buf = np.roll(buf, -1, axis=0)
                    # set the time
                    buf[-1, 0] = msg.time + cum_time
                    # reset skipped time delta
                    cum_time = 0
                    # find the one-hot note code
                    note_code = msg.note + 1 if msg.type == "note_on" else msg.note + 128 + 1
                    buf[note_code] = 1

                    # spit out this buffer
                    yield buf

                # if there were actual usable messages in the track, end the track
                if buf[-1, -2] != 1:
                    buf = np.roll(buf, -1, axis=0)
                    # special one-hot for track end
                    buf[-1, -1] = 1
                    yield buf





class MidiLibrary:

    def __init__(self, base_dir):

        self.base_dir = base_dir

        self.filenames = None
        self.filenames_count = 0
        self.labels = None
        self.composers = None

        self.get_filenames()


    def get_filenames(self):

        """
            Returns a list of files in <self.base_dir> and their associated label in y.  Files must be in
            <dir>/<composer>/*.mid"

            :return: None
        """

        self.filenames = []
        self.labels = []
        self.composers = set()

        for composer in os.listdir(self.base_dir):

            composer_files = []
            for root, dirs, files in os.walk(os.path.join(self.base_dir, composer)):

                for file in files:

                    full_path = os.path.join(root, file)
                    filename = file.lower()
                    if not (filename.endswith(".mid") or filename.endswith(".midi") or filename.endswith(".smf")):
                        print("Unknown file:", full_path)
                        continue

                    composer_files.append(full_path)

            composer_works = len(composer_files)
            if composer_works < wwts_globals.MINIMUM_WORKS:
                print("Not enough works for {}, ({})".format(composer, composer_works))
                continue
            if composer_works > wwts_globals.MAXIMUM_WORKS:
                composer_files = random.sample(composer_files, wwts_globals.MAXIMUM_WORKS)
                composer_works = wwts_globals.MAXIMUM_WORKS

            self.filenames.extend(composer_files)
            self.labels.extend([composer] * composer_works)
            self.composers.add(composer)
            print("Added {} ({})".format(composer, composer_works))

        self.filenames_count = len(self.filenames)
        print("Found", self.filenames_count, "files from", len(self.composers), "artists!")



class MidiLibrarySplit(MidiLibrary):

    def __init__(self, base_dir):

        super().__init__(base_dir)

        self.filenames_train = None
        self.labels_train = None
        self.filenames_test = None
        self.labels_test = None

        self.split_files()


    def split_files(self):

        self.filenames_train, self.filenames_test, self.labels_train, self.labels_test = train_test_split(self.filenames, self.labels, stratify=self.labels)





def main():

    lib = FlatMidiLibrary("midi/bach_cleaned")
    lib.load()

if __name__ == "__main__":
    main()
