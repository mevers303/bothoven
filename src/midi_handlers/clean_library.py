import mido
import os

from midi_handlers.toolbox.FixEndOfTrack import FixEndOfTrack
from midi_handlers.toolbox.MiddleCTransposer import MiddleCTransposer
from midi_handlers.toolbox.MidiToolbox import MidiToolbox
from midi_handlers.toolbox.NoteOnToNoteOff import NoteOnToNoteOff
from midi_handlers.toolbox.OpenNoteFixer import OpenNoteFixer
from midi_handlers.toolbox.RemoveEmptySpaceBefore import RemoveEmptySpaceBefore
from midi_handlers.toolbox.TickTransposer import TickTransposer
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

    tool_list = [TickTransposer, RemoveEmptySpaceBefore, OpenNoteFixer, FixEndOfTrack, MiddleCTransposer, NoteOnToNoteOff, Type1Converter]
    toolbox = MidiToolbox(tool_list)
    print("Toolbox loaded")

    done = 0
    for filename in filenames:
        mid = toolbox.process_midi_file(mido.MidiFile(filename))
        mid.save(filename.replace("midi/classical/Bach/", "midi/bach_cleaned/"))
        done += 1
        progress_bar(done, filenames_count)

if __name__ == "__main__":
    main()
