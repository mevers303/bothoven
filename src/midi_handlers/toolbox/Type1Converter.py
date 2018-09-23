from collections import defaultdict
from midi_handlers.toolbox.MidiToolbox import MidiTool, MidiToolbox
import mido



class Type1Converter(MidiTool):

    def __init__(self):

        super().__init__(priority="last", do_prerun=False)

        self.mid = None

        self.conversion_necessary = False
        self.new_mid = mido.MidiFile(type=1)  # new mido to hold new file
        self.new_tracks = defaultdict(mido.MidiTrack)  # dict to hold a track for each channel

        self.meta_channel = 0  # the current chanel to display meta messages
        self.absolute_time = 0  # a running total of ticks gone by


    def file_event(self, mid):

        # Some sanity checks
        if mid.type == 0:

            if not len(mid.tracks):
                raise TypeError("This MIDI file does not have a track.")
            if len(mid.tracks) > 1:
                raise TypeError("This MIDI file is type 0 but it has more than one track???")

            self.conversion_necessary = True
            self.mid = mid

        elif mid.type == 2:
            raise NotImplementedError("Type 2 MIDI files are not supported!")
        elif mid.type != 1:
            raise TypeError("Unknown MIDI file type!")


    def track_event(self, track):

        if not self.conversion_necessary:
            return

        self.absolute_time = 0


    def message_event(self, msg):

        if not self.conversion_necessary:
            return

        self.absolute_time += msg.time

        if msg.type == "channel_prefix":
            self.meta_channel = msg.channel
        elif msg.is_meta:
            self.new_tracks[self.meta_channel].append(msg.copy(time=self.absolute_time))
        elif msg.type == "sysex":
            self.new_tracks[0].append(msg.copy(time=self.absolute_time))
        else:
            self.new_tracks[msg.channel].append(msg.copy(time=self.absolute_time))


    def post_process(self):

        if not self.conversion_necessary:
            return

        self.mid.tracks.clear()

        for channel, track in sorted(self.new_tracks.items(), key=lambda x: x[0]):
            self.mid.tracks.append(mido.MidiTrack(mido.midifiles.tracks.fix_end_of_track(mido.midifiles.tracks._to_reltime(track))))

        self.mid.type = 1




def main():

    toolbox = MidiToolbox([Type1Converter])


    mid = mido.MidiFile("/home/mark/Documents/midi/130000_Pop_Rock_Classical_Videogame_EDM_MIDI_Archive[6_19_15]/1/1-2-3_ngoi_sao.mid")
    new_mid = toolbox.process_midi_file(mid)

    # new_mid.print_tracks()

    for original, new in zip(mid, new_mid):
        if original.time != new.time:
            print("Oh damn.")

    print("Done... ?")

if __name__ == "__main__":
    main()
