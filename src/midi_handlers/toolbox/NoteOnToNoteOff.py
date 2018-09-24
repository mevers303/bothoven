from midi_handlers.toolbox.MidiToolbox import MidiTool
import mido

class NoteOnToNoteOff(MidiTool):

    def __init__(self):

        super().__init__(priority="first", do_prerun=False)

        self.current_track = None
        self.current_pos = 0


    def track_event(self, track):
        self.current_track = track
        self.current_pos = 0


    def message_event(self, msg):

        if msg.type == "note_on" and not msg.velocity:
            new_msg = mido.Message(type="note_off", channel=msg.channel, note=msg.note, velocity=msg.velocity, time=msg.time)
            self.current_track[self.current_pos] = new_msg

        self.current_pos += 1
