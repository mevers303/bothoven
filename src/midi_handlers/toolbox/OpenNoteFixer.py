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

        self.open_notes = set()
        self.current_track = track
        self.current_pos = 0
        self.cum_time = 0
        self.to_remove = []


    def message_event(self, msg):

        if self.cum_time:
            msg.time += self.cum_time
            self.cum_time = 0

        if msg.type == "note_on" and msg.velocity:

            if msg.note in self.open_notes:
                self.current_track.insert(self.current_pos, msg.copy(type="note_off", velocity=0))
                msg.time = 0
                self.open_notes.remove(msg.note)

            else:
                self.open_notes.add(msg.note)

        elif msg.type == "note_off" or (msg.type == "note_on" and not msg.velocity):

            if msg.note in self.open_notes:
                self.open_notes.remove(msg.note)
            else:
                self.cum_time += msg.time
                self.to_remove.append(msg)

        elif msg.type == "end_of_track":

            if len(self.open_notes):
                this_time = msg.time
                last_open_note = 0

                for open_note in self.open_notes:
                    self.current_track.insert(self.current_pos, mido.Message(type="note_off", note=open_note, velocity=0, time=this_time))
                    last_open_note = open_note
                    if this_time:
                        this_time = 0

                # remove the last open_note in the set because it will be skipped when the messages loop continues
                self.open_notes.remove(last_open_note)

        self.current_pos += 1


    def post_track_event(self, track):

        for msg in self.to_remove:
            track.remove(msg)



def main():

    from midi_handlers.toolbox.MidiToolbox import MidiToolbox
    import os

    for root, dirs, files in os.walk(
            "/home/mark/Documents/midi/130000_Pop_Rock_Classical_Videogame_EDM_MIDI_Archive[6_19_15]"):

        for file in files:

            l_file = file.lower()
            if not (l_file.endswith(".mid") or l_file.endswith(".midi") or l_file.endswith(".smf")):
                continue
            filename = os.path.join(root, file)

            try:
                mid = mido.MidiFile(filename)
            except KeyboardInterrupt as e:
                raise e
            except:
                continue

            toolbox = MidiToolbox([OpenNoteFixer])
            new_mid = toolbox.process_midi_file(mid)


if __name__ == "__main__":
    main()
