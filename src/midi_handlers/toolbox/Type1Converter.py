from collections import defaultdict
from midi_handlers.toolbox.MidiToolbox import MidiTool
import mido



class Type1Converter(MidiTool):

    def __init__(self):

        super().__init__(priority="last")

        self.original_mid = None

        self.conversion_necessary = False
        self.new_mid = mido.MidiFile(type=1)  # new mido to hold new file
        self.new_tracks = defaultdict(mido.MidiTrack)  # dict to hold a track for each channel

        self.meta_channel = 0  # the current chanel to display meta messages
        self.absolute_time = 0  # a running total of ticks gone by


    def file_event(self, mid):

        # Some sanity checks
        if mid.type == 0:
            self.conversion_necessary = True
        elif mid.type == 2:
            raise NotImplementedError("Type 2 MIDI files are not supported!")
        elif mid.type != 1:
            raise NotImplementedError("Unknown MIDI file type!")
        elif not len(mid.tracks):
            raise TypeError("This MIDI file does not have a track.")
        elif len(mid.tracks) > 1:
            raise TypeError("This MIDI file is type 0 but it has more than one track???")

        self.original_mid = mid


    def track_event(self, track):

        self.absolute_time = 0


    def message_event(self, msg):

        self.absolute_time += msg.time

        if msg.type == "channel_prefix":
            self.meta_channel = msg.channel
        elif msg.is_meta:
            self.new_tracks[self.meta_channel].append(msg.copy(time=self.absolute_time))
        else:
            self.new_tracks[msg.channel].append(msg.copy(time=self.absolute_time))


    def post_process(self):

        self.original_mid.tracks.clear()

        for channel, track in sorted(self.new_tracks.items(), key=lambda x: x[0]):
            self.original_mid.tracks.append(  mido.MidiTrack( mido.midifiles.tracks.fix_end_of_track(mido.midifiles.tracks._to_reltime(track)) )  )

        self.original_mid.type = 1
