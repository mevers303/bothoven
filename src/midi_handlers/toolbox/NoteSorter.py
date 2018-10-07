from collections import defaultdict
from midi_handlers.toolbox.MidiToolbox import MidiTool
import mido


class NoteSorter(MidiTool):

    def __init__(self):

        super().__init__(priority="last", do_prerun=False)

        self.abs_time = 0
        self.notes = defaultdict(list)


    def track_event(self, track):

        self.abs_time = 0
        self.notes.clear()


    def message_event(self, msg):

        self.abs_time += msg.time
        self.notes[self.abs_time].append(msg)


    def post_track_event(self, track):

        new_track = mido.MidiTrack()
        last_msg_time = 0

        for msg_abs_time, messages in sorted(self.notes.items(), key=lambda x: x[0]):

            # velocity_code = 1 if not hasattr(x, "velocity") else (2 if x.velocity else 0)
            # note_code = msg.note if hasattr(x, "note") else 0
            sorted_messages = sorted(messages, key=lambda x: (1 if not hasattr(x, "velocity") else (2 if x.velocity else 0),
                                                              x.note if hasattr(x, "note") else 0))

            delta_time = msg_abs_time - last_msg_time
            new_track.append(sorted_messages[0].copy(time=delta_time))
            last_msg_time = msg_abs_time

            for msg in sorted_messages[1:]:
                new_track.append(msg.copy(time=0))

        track.clear()
        track.extend(new_track)




# def main():
#
#     from midi_handlers.toolbox.MidiToolbox import MidiToolbox
#     import mido
#
#     track = mido.MidiTrack([
#         mido.MetaMessage('key_signature', key='Ab', time=0),
#         mido.Message(type="note_on", channel=0, note=1, velocity=1, time=62),
#         mido.Message(type="note_on", channel=0, note=1, velocity=0, time=62),
#         mido.Message(type="note_on", channel=0, note=2, velocity=2, time=62),
#         mido.Message(type="note_on", channel=0, note=99, velocity=3, time=62),
#         mido.Message(type="note_on", channel=0, note=4, velocity=4, time=0),
#         mido.MetaMessage('key_signature', key='Ab', time=0),
#         mido.Message(type="note_on", channel=0, note=2, velocity=0, time=0),
#         mido.Message(type="note_on", channel=0, note=100, velocity=100, time=0),
#         mido.Message(type="note_on", channel=0, note=100, velocity=0, time=35),
#         mido.Message(type="note_on", channel=0, note=99, velocity=0, time=0),
#         mido.Message(type="note_on", channel=0, note=4, velocity=0, time=0),
#         mido.Message(type="note_on", channel=0, note=100, velocity=6, time=167),
#         mido.MetaMessage(type="end_of_track", time=10)
#     ])
#
#     mid = mido.MidiFile()
#     mid.tracks = [track]
#
#     toolbox = MidiToolbox([NoteSorter])
#     new_mid = toolbox.process_midi_file(mid)
#
#     for msg in new_mid.tracks[0]:
#         print(msg)
#
# if __name__ == "__main__":
#     main()
