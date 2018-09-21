## Normalizing a MIDI file
MIDI files must be normalized in two ways to be meaningfully analyzed:
1.  The ticks must be in the same scale.
2.  The note values must be normalized, which consists of two steps:
    1.  The notes all be transposed to the same key signature.  We will
        use C major/A minor.
    2.  The notes must be centered around Middle C (C5).
```
    def normalize(self):

        midi_file = mido.MidiFile(self.filename)

        self.tick_transposer_coef = TICKS_PER_BEAT / midi_file.ticks_per_beat
        self.note_transpose_interval = MidiFileNormalizer.get_note_transpose_interval(midi_file)
```

### Normalizing the tick resolution
This is rather simple.  A variable `TICKS_PER_BEAT` is defined in
*wwts_globals.py* that determines the number of ticks per beat that we
will convert each MIDI file into.  We then simply find the coefficient
that will change each track to the proper resolution:
```
self.tick_transposer_coef = TICKS_PER_BEAT / midi_file.ticks_per_beat
```

### Normalizing the note values
