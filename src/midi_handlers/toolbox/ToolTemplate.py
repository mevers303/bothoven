from midi_handlers.toolbox.MidiToolbox import MidiTool

class ToolTemplate(MidiTool):

    def __init__(self):

        super().__init__(priority = "first", do_prerun = False)


    def prerun_file_event(self, mid):
        pass

    def prerun_track_event(self, track):
        pass

    def prerun_message_event(self, msg):
        pass

    def prerun_post_process(self):
        pass

    def file_event(self, mid):
        pass

    def track_event(self, track):
        pass

    def message_event(self, msg):
        pass

    def post_process(self):
        pass



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
