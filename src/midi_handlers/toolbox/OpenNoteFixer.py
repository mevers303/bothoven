from collections import defaultdict
from midi_handlers.toolbox.MidiToolbox import MidiTool
import mido

class OpenNoteFixer(MidiTool):

    def __init__(self):

        super().__init__(priority = "first", do_prerun = False)

        self.open_notes = None
        self.current_track = None
        self.current_pos = 0
        self.cum_time = 0

        self.to_remove = None


    def track_event(self, track):

        self.open_notes = defaultdict(list)
        self.current_track = track
        self.current_pos = 0
        self.cum_time = 0
        self.to_remove = []


    def message_event(self, msg):

        if self.cum_time:
            msg.time += self.cum_time
            self.cum_time = 0

        if msg.type == "note_on" and msg.velocity:

            if self.note_is_open(msg.note, msg.channel):
                new_msg = mido.Message(type="note_off", channel=msg.channel, note=msg.note, velocity=0, time=msg.time)
                self.current_track.insert(self.current_pos, new_msg)
                msg.time = 0
                self.remove_from_open_notes(msg.note, msg.channel)

            else:
                self.add_to_open_notes(msg.note, msg.channel)

        elif msg.type == "note_off" or (msg.type == "note_on" and not msg.velocity):

            if self.note_is_open(msg.note, msg.channel):
                self.remove_from_open_notes(msg.note, msg.channel)
            else:
                self.cum_time += msg.time
                self.to_remove.append(self.current_pos)

        elif msg.type == "end_of_track":

            if len(self.open_notes):
                this_time = msg.time
                last_open_note = 0
                last_channel = -1

                for open_note, channels in self.open_notes.items():
                    for channel in channels:
                        self.current_track.insert(self.current_pos, mido.Message(type="note_off", channel=channel, note=open_note, velocity=0, time=this_time))
                        last_open_note = open_note
                        last_channel = channel
                        if this_time:
                            this_time = 0

                # remove the last open_note in the set because it will be skipped when the messages loop continues
                self.remove_from_open_notes(last_open_note, last_channel)
                msg.time = 0

        self.current_pos += 1


    def post_track_event(self, track):
        for position in self.to_remove[::-1]:
            del track[position]


    def note_is_open(self, note, channel):
        return note in self.open_notes and channel in self.open_notes[note]


    def add_to_open_notes(self, note, channel):
        self.open_notes[note].append(channel)


    def remove_from_open_notes(self, note, channel):
        self.open_notes[note].remove(channel)
        if not len(self.open_notes[note]):
            del self.open_notes[note]




# def main():
#
#     from midi_handlers.toolbox.MidiToolbox import MidiToolbox
#     import os
#
#     for root, dirs, files in os.walk(
#             "/home/mark/Documents/midi/130000_Pop_Rock_Classical_Videogame_EDM_MIDI_Archive[6_19_15]"):
#
#         for file in files:
#
#             l_file = file.lower()
#             if not (l_file.endswith(".mid") or l_file.endswith(".midi") or l_file.endswith(".smf")):
#                 continue
#             filename = os.path.join(root, file)
#
#             try:
#                 mid = mido.MidiFile(filename)
#             except KeyboardInterrupt:
#                 raise KeyboardInterrupt
#             except:
#                 continue
#
#             toolbox = MidiToolbox([OpenNoteFixer])
#             new_mid = toolbox.process_midi_file(mid)
#
#             print(filename)
#
#             # print(filename, sum([len(track) for track in mid.tracks]), "->", sum([len(track) for track in new_mid.tracks]))
#             #
#             # for old_track, new_track in zip(mid.tracks, new_mid.tracks):
#             #
#             #     i = 0
#             #
#             #     while True:
#             #
#             #         if i >= len(old_track) or i >= len(new_track):
#             #             break
#             #
#             #         if old_track[i].type != new_track[i].type:
#             #             print("=" * 80)
#             #             print("=" * 80)
#             #             for j in range(i - 3, i + 15):
#             #                 print(j, old_track[j], "->", new_track[j])
#             #
#             #         i += 1
#             #
#             # print("\n\n")
#
#
#
# def main2():
#
#     from midi_handlers.toolbox.MidiToolbox import MidiToolbox
#     from midi_handlers.toolbox.NoteOnToNoteOff import NoteOnToNoteOff
#
#     track = mido.MidiTrack([
#                       mido.Message(type="note_on", channel=0, note=100, velocity=1, time=0),
#                       mido.Message(type="note_on", channel=0, note=100, velocity=0, time=10),
#                       mido.Message(type="note_on", channel=0, note=100, velocity=2, time=10),
#                       mido.Message(type="note_on", channel=0, note=100, velocity=0, time=10),
#                       mido.Message(type="note_on", channel=0, note=100, velocity=3, time=10),
#                       mido.Message(type="note_on", channel=0, note=100, velocity=4, time=10),
#                       mido.Message(type="note_on", channel=0, note=100, velocity=0, time=10),
#                       mido.Message(type="note_on", channel=0, note=100, velocity=0, time=10),
#                       mido.Message(type="note_on", channel=0, note=100, velocity=5, time=10),
#                       mido.Message(type="note_on", channel=0, note=100, velocity=0, time=10),
#                       mido.Message(type="note_on", channel=0, note=100, velocity=6, time=10),
#                       mido.MetaMessage(type="end_of_track", time=10)
#                   ])
#
#     mid = mido.MidiFile()
#     mid.tracks = [track]
#
#     toolbox = MidiToolbox([OpenNoteFixer, NoteOnToNoteOff])
#     new_mid = toolbox.process_midi_file(mid)
#
#     for msg in new_mid.tracks[0]:
#         print(msg)
#
#
#
# if __name__ == "__main__":
#     main2()
