from midiutil import MIDIFile
import logging
LOG = logging.getLogger("audioToMidi")

def save(path, tempo, notes):
    new_midi = MIDIFile(1)
    new_midi.addTempo(0, 0, tempo)
    for note in notes:
        assert len(note) == 5
        pitch = note[0]
        start_time = note[1]
        duration = note[2]
        velocity = note[3]
        new_midi.addNote(0, 0, pitch, start_time, duration, velocity)
    with open(path+".mid", "wb+") as f:
        new_midi.writeFile(f)

