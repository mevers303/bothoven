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
                buf = np.zeros((wwts_globals.NUM_STEPS, wwts_globals.NUM_FEATURES), dtype=np.uint32)
                # set special one-hot for track_start
                buf[-1, -2] = 1
                # cumulative delta time from skipped notes
                cum_time = 0

                for msg in track:

                    if not (msg.type == "note_on" or msg.type == "note_off"):
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
                    yield buf, target

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
                    yield buf, target
                else:
                    pass

            print(len(mid.tracks), mid.filename)




def main():

    import pickle

    # lib = MidiLibrary("midi/bach_cleaned")
    # lib.load()
    #
    # with open("midi/pickles/bach.pkl", "wb") as f:
    #     pickle.dump(lib, f)

    with open("midi/pickles/bach.pkl", "rb") as f:
        lib = pickle.load(f)

    x = 0

    for buf, target in lib.step_through():
        pass
        # print("time:", str(time).rjust(5), "note: ", note)

if __name__ == "__main__":
    main()
