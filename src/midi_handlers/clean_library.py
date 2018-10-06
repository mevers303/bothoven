import mido
import os

from midi_handlers.toolbox.FixEndOfTrack import FixEndOfTrack
from midi_handlers.toolbox.MiddleCTransposer import MiddleCTransposer
from midi_handlers.toolbox.MidiToolbox import MidiToolbox
from midi_handlers.toolbox.NoteOnToNoteOff import NoteOnToNoteOff
from midi_handlers.toolbox.OpenNoteFixer import OpenNoteFixer
from midi_handlers.toolbox.Quantizer import Quantizer
from midi_handlers.toolbox.RemoveEmptySpaceBefore import RemoveEmptySpaceBefore
from midi_handlers.toolbox.TickTransposer import TickTransposer
from midi_handlers.toolbox.Type0Converter import Type0Converter
from midi_handlers.toolbox.Type1Converter import Type1Converter
from wwts_globals import progress_bar


def get_filenames(base_dir):

    filenames = []

    for root, dirs, files in os.walk(base_dir):

        for file in files:

            full_path = os.path.join(root, file)
            filename = file.lower()
            if not (filename.endswith(".mid") or filename.endswith(".midi") or filename.endswith(".smf")):
                print("Unknown file:", full_path)
                continue

            filenames.append(full_path)

    return filenames



def main():

    base_dir = "midi/classical/Bach"

    filenames = get_filenames("midi/classical/Bach")
    filenames_count = len(filenames)
    print("Found", filenames_count, "in", base_dir)

    tool_list = [Quantizer, NoteOnToNoteOff, TickTransposer, RemoveEmptySpaceBefore, OpenNoteFixer, FixEndOfTrack, MiddleCTransposer, Type1Converter]
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
            continue

        try:
            mid.save("midi/bach_cleaned/" + os.path.basename(filename))
        except KeyboardInterrupt:
            raise KeyboardInterrupt
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
    tool_list = [Type1Converter, Type0Converter, Quantizer, NoteOnToNoteOff, TickTransposer, RemoveEmptySpaceBefore, OpenNoteFixer, FixEndOfTrack, MiddleCTransposer]
    toolbox = MidiToolbox(tool_list)

    mid = mido.MidiFile(filename)
    new_mid = toolbox.process_midi_file(mid)
    new_mid.save("midi/output.mid")



if __name__ == "__main__":
    main()
