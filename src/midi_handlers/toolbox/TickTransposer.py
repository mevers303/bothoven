from midi_handlers.toolbox.MidiToolbox import MidiTool
import wwts_globals
import numpy as np



class TickTransposer(MidiTool):

    def __init__(self):

        super().__init__(priority = "first", do_prerun = False)

        self.tick_transpose_coef = 1


    def file_event(self, mid):

        # force it to be numpy for better precision
        self.tick_transpose_coef = np.float64(wwts_globals.TICKS_PER_BEAT) / mid.ticks_per_beat
        mid.ticks_per_beat = wwts_globals.TICKS_PER_BEAT


    def message_event(self, msg):

        if hasattr(msg, "time"):
            msg.time = np.round(msg.time * self.tick_transpose_coef)




# def main():
#
#     from midi_handlers.toolbox.MidiToolbox import MidiToolbox
#     import mido
#
#     toolbox = MidiToolbox([TickTransposer])
#     mid = mido.MidiFile("/home/mark/Documents/Barcarolle in F sharp Major.mid")
#     new_mid = toolbox.process_midi_file(mid)
#
#     for original, new in zip(mid, new_mid):
#         if original.time != new.time:
#             print(original.time - new.time)
#
#     print("Done... ?")
#
# if __name__ == "__main__":
#     main()
