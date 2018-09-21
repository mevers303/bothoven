import mido
import numpy as np
from wwts_globals import TICKS_PER_BEAT, KEY_SIGNATURES


class MidiFileNormalizer:


    def __init__(self, filename, do_normalize=True):

        self.filename = filename

        self.tick_transposer_coef = 1
        self.note_transpose_interval = 0

        if do_normalize:
            self.normalize()


    def normalize(self):

        midi_file = mido.MidiFile(self.filename)

        self.tick_transposer_coef = TICKS_PER_BEAT / midi_file.ticks_per_beat
        self.note_transpose_interval = MidiFileNormalizer.get_note_transpose_interval(midi_file)


    @staticmethod
    def get_note_transpose_interval(midi_file):
        """
        Gets the transpose interval for a filename from the meta dataframe.

        :return: The interval to use to transpose this file to the correct key signature.
        """

        # get the key signature
        note_dist = MidiFileNormalizer.get_note_distribution(midi_file)
        key_sig = MidiFileNormalizer.get_key_signature(note_dist)

        # first transpose based on key signature
        if key_sig < 6:
            transpose_interval = -key_sig
        else:
            transpose_interval = 12 - key_sig


        return transpose_interval


    @staticmethod
    def get_note_distribution(midi_file):

        note_distribution = np.zeros((12,))

        for msg in midi_file:

            if msg.type == "note_on":
                if not msg.velocity:  # skip if it's a note off (velocity = 0)
                    continue
                if msg.channel != 10:  # skip channel 10 (drums)
                    note_distribution[msg.note % 12] += 1

        return note_distribution


    @staticmethod
    def get_key_signature(note_dist):
        """
        Uses the note distribution in the meta dataframe to determine a filename's key signature
        :param note_dist: Distribution of notes as per music_notes
        :return: The index of key_signatures that is the best match.
        """

        top_7_notes = set(np.argsort(note_dist)[::-1][:7])

        best_match = -1
        best_match_set_difference = 100

        for i in range(len(KEY_SIGNATURES)):

            # find number of uncommon notes
            set_difference = len(set(KEY_SIGNATURES[i]) - top_7_notes)

            # if this one is better than the last, save it
            if set_difference < best_match_set_difference:
                best_match = i
                best_match_set_difference = set_difference

                # if there are 0 uncommon notes, it is our match!
                if not best_match_set_difference:
                    break

        return best_match
