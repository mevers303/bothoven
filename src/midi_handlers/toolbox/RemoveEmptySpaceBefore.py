from midi_handlers.toolbox.MidiToolbox import MidiTool

class ToolTemplate(MidiTool):

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

            if not remaining_difference:
                break

            msg_time = msg.time
            msg.time = msg.time - remaining_difference if msg.time > remaining_difference else 0
            remaining_difference -= msg_time



def main():

    from midi_handlers.toolbox.MidiToolbox import MidiToolbox
    import mido

    toolbox = MidiToolbox([ToolTemplate])
    mid = mido.MidiFile("/home/mark/Documents/Barcarolle in F sharp Major.mid")
    new_mid = toolbox.process_midi_file(mid)

    for original, new in zip(mid, new_mid):
        if original.time != new.time:
            print(original.time - new.time)

    print("Done... ?")

if __name__ == "__main__":
    main()
