from collections import defaultdict
import numpy as np
import mido

from wwts_globals import NUM_FEATURES, NUM_STEPS


class MidiArrayBuilder:

    def __init__(self, filename):

        self.filename = filename
        self.tracks = []


    def mid_to_array(self):

        mid = mido.MidiFile(self.filename)

        for track in mid.tracks:

            # running total of the amount of time that has passed
            abs_time = 0
            track_dict = defaultdict(list)

            for msg in track:

                abs_time += msg.time

                if not (msg.type == 'note_on' or msg.type == 'note_off') or msg.channel == 9:  # skip drum tracks
                    continue

                # find the one-hot note
                note_code = msg.note
                if msg.type == "note_off" or not msg.velocity:
                    note_code += 128

                # add this note to our dictionary of absolute times
                track_dict[abs_time].append(note_code)

            if len(track_dict):
                self.tracks.append(track_dict)

        return self.flush_out_buf()


    def flush_out_buf(self):

        if not len(self.tracks):
            return []

        # empty buffer of NUM_STEPS for the beginning of the track
        buf = [np.zeros((NUM_STEPS - 1, NUM_FEATURES))]

        for track in self.tracks:

            track_buf = np.zeros((max(track) + 1 + 2, NUM_FEATURES))  # +1 because the abs_time is an index and +2 for track_start and track_end
            track_buf[0, -2] = 1  # track_start

            # index pair locations for numpy
            x = []
            y = []
            for abs_time, note_codes in track.items():
                x.extend([abs_time + 1] * len(note_codes))  # abs_time + 1 to skip over track_start
                y.extend(note_codes)

            track_buf[x, y] = 1  # set all those one-hots to 1
            track_buf[-1, -1] = 1  # track_end

            buf.append(track_buf)

        return np.concatenate(buf, axis=0)
