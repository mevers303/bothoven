from midi_handlers.toolbox.MidiToolbox import MidiTool

class NoteOnToNoteOff(MidiTool):

    def __init__(self):

        super().__init__(priority = "first", do_prerun = False)


    def message_event(self, msg):

        if msg.type == "note_on" and not msg.velocity:
            msg.type = "note_off"
