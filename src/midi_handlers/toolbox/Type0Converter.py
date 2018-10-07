from midi_handlers.toolbox.MidiToolbox import MidiTool
import mido

class Type0Converter(MidiTool):

    def __init__(self):

        super().__init__(priority="last", do_prerun=False)


    def post_process(self, mid):

        if mid.type == 0:
            return

        new_track = mido.midifiles.tracks.merge_tracks(mid.tracks)
        mid.tracks.clear()
        mid.tracks.append(new_track)
        mid.type = 0


#
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
#         mido.Message(type="note_on", channel=1, note=100, velocity=1, time=1),
#         mido.Message(type="note_on", channel=1, note=100, velocity=0, time=10),
#         mido.Message(type="note_on", channel=1, note=100, velocity=2, time=10),
#         mido.Message(type="note_on", channel=1, note=100, velocity=0, time=10),
#         mido.Message(type="note_on", channel=1, note=100, velocity=3, time=10),
#         mido.Message(type="note_on", channel=1, note=100, velocity=4, time=11),
#         mido.Message(type="note_on", channel=1, note=100, velocity=0, time=10),
#         mido.Message(type="note_on", channel=1, note=100, velocity=0, time=10),
#         mido.Message(type="note_on", channel=1, note=100, velocity=5, time=11),
#         mido.Message(type="note_on", channel=1, note=100, velocity=0, time=10),
#         mido.Message(type="note_on", channel=1, note=100, velocity=6, time=10),
#         mido.MetaMessage(type="end_of_track", time=10)
#     ])
#
#     mid = mido.MidiFile()
#     mid.tracks = [track, track2]
#
#     toolbox = MidiToolbox([Type0Converter, NoteOnToNoteOff])
#     new_mid = toolbox.process_midi_file(mid)
#
#     for msg in new_mid.tracks[0]:
#         print(msg)
#
# if __name__ == "__main__":
#     main()
