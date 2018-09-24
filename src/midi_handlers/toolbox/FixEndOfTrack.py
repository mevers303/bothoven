from midi_handlers.toolbox.MidiToolbox import MidiTool
import mido


class FixEndOfTrack(MidiTool):

    def __init__(self):

        super().__init__(priority="first", do_prerun=True)

        self.current_pos = 0
        self.to_remove = None


    def prerun_track_event(self, track):

        self.current_pos = 0
        self.to_remove = []


    def prerun_message_event(self, msg):

        if msg.type == "end_of_track":
            self.to_remove.append(self.current_pos)

        self.current_pos += 1


    def prerun_post_track_event(self, track):

        for position in self.to_remove[::-1]:
            del track[position]

        track.append(mido.MetaMessage(type="end_of_track", time=0))





def main():

    from midi_handlers.toolbox.MidiToolbox import MidiToolbox

    track = mido.MidiTrack([
                      mido.MetaMessage('key_signature', key='Ab', time=0),
                      mido.MetaMessage('key_signature', key='Bb', time=0),
                      mido.MetaMessage('key_signature', key='C#', time=0),
                      mido.MetaMessage(type="end_of_track", time=0),
                      mido.Message(type="note_on", channel=0, note=100, velocity=1, time=100),
                      mido.Message(type="note_on", channel=0, note=100, velocity=0, time=10),
                      mido.Message(type="note_on", channel=0, note=100, velocity=2, time=10),
                      mido.Message(type="note_on", channel=0, note=100, velocity=0, time=10),
                      mido.Message(type="note_on", channel=0, note=100, velocity=3, time=10),
                      mido.MetaMessage(type="end_of_track", time=0),
                      mido.Message(type="note_on", channel=0, note=100, velocity=4, time=10),
                      mido.Message(type="note_on", channel=0, note=100, velocity=0, time=10),
                      mido.Message(type="note_on", channel=0, note=100, velocity=0, time=10),
                      mido.Message(type="note_on", channel=0, note=100, velocity=5, time=10),
                      mido.Message(type="note_on", channel=0, note=100, velocity=0, time=10),
                      mido.Message(type="note_on", channel=0, note=100, velocity=6, time=10),
                      mido.MetaMessage(type="end_of_track", time=0)
                  ])


    mid = mido.MidiFile()
    mid.tracks = [track]

    toolbox = MidiToolbox([FixEndOfTrack])
    new_mid = toolbox.process_midi_file(mid)

    for msg in new_mid.tracks[0]:
        print(msg)

if __name__ == "__main__":
    main()
