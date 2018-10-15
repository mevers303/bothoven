import mido
import os

from wwts_globals import progress_bar
from files.file_functions import get_filenames


in_dir = "/home/mark/Documents/raw_midi"
out_dir = "/media/mark/Data/Documents/python/bothoven/midi/monophonic"
good_programs = set(range(56, 80))


filenames = get_filenames(in_dir)
total = len(filenames)
done = 0

for filename in filenames:

    progress_bar(done, total, filename)
    done += 1

    mid = None
    try:
        mid = mido.MidiFile(filename)
    except KeyboardInterrupt as e:
        exit(1)
    except Exception as e:
        print("There was an error reading", filename)
        print(e)
        continue

    good_tracks = []

    for track in mid.tracks:
        last_program = -1

        for msg in track:
            if msg.type == "program_change" and msg.channel != 9:
                last_program = msg.program

        if last_program in good_programs:
            good_tracks.append(track)

    if len(good_tracks):
        new_mid = mido.MidiFile()
        new_mid.tracks = good_tracks
        try:
            new_mid.save(os.path.join(out_dir, os.path.basename(filename)))
        except KeyboardInterrupt as e:
            exit(1)
        except Exception as e:
            print("There was an error saving", os.path.join(out_dir, os.path.basename(filename)))
            print(e)
            continue

progress_bar(done, total, "Done!")
