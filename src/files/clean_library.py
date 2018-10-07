import mido
import os

from files.file_functions import get_filenames
from midi_handlers.toolbox.FixEndOfTrack import FixEndOfTrack
from midi_handlers.toolbox.MiddleCTransposer import MiddleCTransposer
from midi_handlers.toolbox.MidiToolbox import MidiToolbox
from midi_handlers.toolbox.NoteOnToNoteOff import NoteOnToNoteOff
from midi_handlers.toolbox.NoteSorter import NoteSorter
from midi_handlers.toolbox.OpenNoteFixer import OpenNoteFixer
from midi_handlers.toolbox.Quantizer import Quantizer
from midi_handlers.toolbox.RemoveEmptySpaceBefore import RemoveEmptySpaceBefore
from midi_handlers.toolbox.TickTransposer import TickTransposer
from midi_handlers.toolbox.Type0Converter import Type0Converter
from midi_handlers.toolbox.Type1Converter import Type1Converter
from wwts_globals import progress_bar



def main():

    base_dir = "midi/classical/Bach"
    out_dir = "midi/bach_cleaned"

    filenames = get_filenames("midi/classical/Bach")
    filenames_count = len(filenames)
    print("Found", filenames_count, "in", base_dir)

    tool_list = [Type1Converter, Type0Converter, Quantizer, NoteSorter, NoteOnToNoteOff, TickTransposer, RemoveEmptySpaceBefore, OpenNoteFixer, FixEndOfTrack, MiddleCTransposer]
    toolbox = MidiToolbox(tool_list)
    print("Toolbox loaded")

    done = 0
    for filename in filenames:

        try:
            mid = toolbox.process_midi_file(mido.MidiFile(filename))
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except Exception as e:
            print("\nThere was an error reading", filename)
            print(e)
            done += 1
            progress_bar(done, filenames_count)
            continue

        try:
            mid.save(os.path.join(out_dir, os.path.basename(filename)))
        except KeyboardInterrupt:
            exit(1)
        except Exception as e:
            print("\nThere was an error saving", mid.save(os.path.basename(filename)))
            print(e)
            continue
        finally:
            done += 1
            progress_bar(done, filenames_count)



def main2():

    filename = "midi/test.mid"

    # tool_list = [TickTransposer, RemoveEmptySpaceBefore, OpenNoteFixer, FixEndOfTrack, MiddleCTransposer, NoteOnToNoteOff, Type1Converter]
    tool_list = [TickTransposer, Type1Converter, Type0Converter, Quantizer, NoteSorter, NoteOnToNoteOff, RemoveEmptySpaceBefore, OpenNoteFixer, FixEndOfTrack, MiddleCTransposer]
    toolbox = MidiToolbox(tool_list)

    mid = mido.MidiFile(filename)
    new_mid = toolbox.process_midi_file(mid)
    new_mid.save("midi/output.mid")



if __name__ == "__main__":
    main()
