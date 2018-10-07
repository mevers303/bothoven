# Mark Evers
# 9/21/18
# MidiLibrary.py
# Objects for managing a set of MIDI files.

import numpy as np
import mido

from files.file_functions import get_filenames
import wwts_globals



class MidiLibrary:

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




def main():

    lib = FlatMidiLibrary("midi/bach_cleaned")
    lib.load()

if __name__ == "__main__":
    main()
