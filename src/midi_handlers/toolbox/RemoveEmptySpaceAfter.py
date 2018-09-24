from midi_handlers.toolbox.MidiToolbox import MidiTool

class RemoveEmptySpaceAfter(MidiTool):

    def __init__(self):

        super().__init__(priority="first", do_prerun=True)


    def prerun_file_event(self, mid):
        pass

    def prerun_track_event(self, track):
        pass

    def prerun_message_event(self, msg):
        pass

    def prerun_post_process(self):
        pass



def main():

    from midi_handlers.toolbox.MidiToolbox import MidiToolbox
    import mido

    track = mido.MidiTrack([
                      mido.MetaMessage('key_signature', key='Ab', time=0),
                      mido.MetaMessage('key_signature', key='Bb', time=0),
                      mido.MetaMessage('key_signature', key='C#', time=0),
                      mido.Message(type="note_on", channel=0, note=100, velocity=1, time=100),
                      mido.Message(type="note_on", channel=0, note=100, velocity=0, time=10),
                      mido.Message(type="note_on", channel=0, note=100, velocity=2, time=10),
                      mido.Message(type="note_on", channel=0, note=100, velocity=0, time=10),
                      mido.Message(type="note_on", channel=0, note=100, velocity=3, time=10),
                      mido.Message(type="note_on", channel=0, note=100, velocity=4, time=10),
                      mido.Message(type="note_on", channel=0, note=100, velocity=0, time=10),
                      mido.Message(type="note_on", channel=0, note=100, velocity=0, time=10),
                      mido.Message(type="note_on", channel=0, note=100, velocity=5, time=10),
                      mido.Message(type="note_on", channel=0, note=100, velocity=0, time=10),
                      mido.Message(type="note_on", channel=0, note=100, velocity=6, time=10),
                      mido.MetaMessage(type="end_of_track", time=10)
                  ])


    mid = mido.MidiFile()
    mid.tracks = [track]

    toolbox = MidiToolbox([RemoveEmptySpaceAfter])
    new_mid = toolbox.process_midi_file(mid)

    for msg in new_mid.tracks[0]:
        print(msg)

if __name__ == "__main__":
    main()
