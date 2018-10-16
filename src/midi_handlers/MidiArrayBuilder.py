from collections import defaultdict
import numpy as np
import mido
import scipy.sparse

from bothoven_globals import NUM_FEATURES, NUM_STEPS


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
        buf = [scipy.sparse.csr_matrix((NUM_STEPS - 1, NUM_FEATURES), dtype=np.byte)]

        for track in self.tracks:

            # index pair locations for sparse matrix
            x = [0, max(track) + 2]
            y = [NUM_FEATURES - 2, NUM_FEATURES - 1]
            data = [1, 1]
            for abs_time, note_codes in track.items():
                x.extend([abs_time + 1] * len(note_codes))  # abs_time + 1 to skip over track_start
                y.extend(note_codes)
                data.extend([1] * len(note_codes))

            track_buf = scipy.sparse.csr_matrix((data, (x, y)), shape=(max(track) + 1 + 2, NUM_FEATURES),
                                          dtype=np.byte)  # +1 because the abs_time is an index and +2 for track_start and track_end

            buf.append(track_buf)

        return scipy.sparse.vstack(buf, format="csr", dtype=np.byte)
