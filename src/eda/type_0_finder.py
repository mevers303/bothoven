import mido
import os


for root, dirs, files in os.walk("/home/mark/Documents/midi/130000_Pop_Rock_Classical_Videogame_EDM_MIDI_Archive[6_19_15]"):

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

        if mid.type == 0:

            channels = set([msg.channel for msg in mid if not msg.is_meta and msg.type != "sysex"])

            if len(channels) > 1:
                print(len(channels), "channels:", filename)
