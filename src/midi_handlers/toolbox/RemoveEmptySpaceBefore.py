from midi_handlers.toolbox.MidiToolbox import MidiTool

class RemoveEmptySpaceBefore(MidiTool):

    def __init__(self):

        super().__init__(priority="first", do_prerun=True)

        self.first_note_delay = 999999


    def prerun_track_event(self, track):

        abs_time = 0

        for msg in track:
            abs_time += msg.time

            if msg.type == "note_on":

                if abs_time < self.first_note_delay:
                    self.first_note_delay = abs_time

                break


    def track_event(self, track):

        remaining_difference = self.first_note_delay

        for msg in track:

            if remaining_difference < 0:
                break

            msg_time = msg.time
            msg.time = msg.time - remaining_difference if msg.time > remaining_difference else 0
            remaining_difference -= msg_time



# def main():
#
#     from midi_handlers.toolbox.MidiToolbox import MidiToolbox
#     from midi_handlers.toolbox.NoteOnToNoteOff import NoteOnToNoteOff
#     import mido
#
#     track = mido.MidiTrack([
#                       mido.MetaMessage('key_signature', key='Ab', time=0),
#                       mido.MetaMessage('key_signature', key='Bb', time=0),
#                       mido.MetaMessage('key_signature', key='C#', time=0),
#                       mido.Message(type="note_on", channel=0, note=100, velocity=1, time=100),
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
#     track2 = mido.MidiTrack([
#         mido.MetaMessage('key_signature', key='Ab', time=0),
#         mido.MetaMessage('key_signature', key='Bb', time=50),
#         mido.MetaMessage('key_signature', key='C#', time=0),
#         mido.Message(type="note_on", channel=0, note=100, velocity=1, time=0),
#         mido.Message(type="note_on", channel=0, note=100, velocity=0, time=10),
#         mido.Message(type="note_on", channel=0, note=100, velocity=2, time=10),
#         mido.Message(type="note_on", channel=0, note=100, velocity=0, time=10),
#         mido.Message(type="note_on", channel=0, note=100, velocity=3, time=10),
#         mido.Message(type="note_on", channel=0, note=100, velocity=4, time=10),
#         mido.Message(type="note_on", channel=0, note=100, velocity=0, time=10),
#         mido.Message(type="note_on", channel=0, note=100, velocity=0, time=10),
#         mido.Message(type="note_on", channel=0, note=100, velocity=5, time=10),
#         mido.Message(type="note_on", channel=0, note=100, velocity=0, time=10),
#         mido.Message(type="note_on", channel=0, note=100, velocity=6, time=10),
#         mido.MetaMessage(type="end_of_track", time=10)
#     ])
#
#     mid = mido.MidiFile()
#     mid.tracks = [track, track2]
#
#     toolbox = MidiToolbox([RemoveEmptySpaceBefore, NoteOnToNoteOff])
#     new_mid = toolbox.process_midi_file(mid)
#
#     for msg in new_mid.tracks[0]:
#         print(msg)
#
# if __name__ == "__main__":
#     main()
