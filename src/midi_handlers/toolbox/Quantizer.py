import wwts_globals
from midi_handlers.toolbox.MidiToolbox import MidiTool


class Quantizer(MidiTool):

    def __init__(self):

        super().__init__(priority="last", do_prerun=False)


    def post_track_event(self, track):

        original_abs_time = 0
        quantized_abs_time = 0

        for msg in track:
            original_abs_time += msg.time

            duplet_quantized_time = self.quantize_x(original_abs_time, wwts_globals.MINIMUM_NOTE_LENGTH)
            triplet_quantized_time = self.quantize_x(original_abs_time, wwts_globals.MINIMUM_NOTE_LENGTH_TRIPLETS)

            quantized_msg_abs_time = duplet_quantized_time if abs(original_abs_time - duplet_quantized_time) < abs(
                original_abs_time - triplet_quantized_time) else triplet_quantized_time
            quantized_msg_delta = quantized_msg_abs_time - quantized_abs_time

            msg.time = quantized_msg_delta
            quantized_abs_time = quantized_msg_abs_time


    @staticmethod
    def quantize_x(x, resolution):

        decimal_part = (x / resolution) % 1
        decimal_part = 1 - decimal_part if decimal_part > 0.5 else -decimal_part

        return int(round(x + (decimal_part * resolution)))



def main():

    from midi_handlers.toolbox.MidiToolbox import MidiToolbox
    import mido

    track = mido.MidiTrack([
        mido.MetaMessage('key_signature', key='Ab', time=0),
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

    toolbox = MidiToolbox([Quantizer])
    new_mid = toolbox.process_midi_file(mid)

    for msg in new_mid.tracks[0]:
        print(msg)

if __name__ == "__main__":
    main()
