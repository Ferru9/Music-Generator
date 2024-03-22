import mido
from mido import Message, MidiFile, MidiTrack
import random

# Mapping notes to their MIDI value. Only using one octave for simplicity.
NOTE_TO_MIDI = {
    'C': 60, 'C#': 61, 'D': 62, 'D#': 63, 'E': 64,
    'F': 65, 'F#': 66, 'G': 67, 'G#': 68, 'A': 69,
    'A#': 70, 'B': 71
}

# Define the structure of scales as a sequence of intervals.
scales = {
    'major': [2, 2, 1, 2, 2, 2, 1],
    'minor': [2, 1, 2, 2, 1, 2, 2],
    'dorian': [2, 1, 2, 2, 2, 1, 2],
    'phrygian': [1, 2, 2, 2, 1, 2, 2],
    'lydian': [2, 2, 2, 1, 2, 2, 1],
    'mixolydian': [2, 2, 1, 2, 2, 1, 2],
    'locrian': [1, 2, 2, 1, 2, 2, 2],
    'aeolian': [2, 1, 2, 2, 1, 2, 2]
}

# Define the structure of chords based on scale degrees.
chord_structures = {
    'major': [0, 4, 7],  # Major triad: root, major third, perfect fifth
    'minor': [0, 3, 7],  # Minor triad: root, minor third, perfect fifth
    'major_seventh': [0, 4, 7, 11],  # Major seventh
    'minor_seventh': [0, 3, 7, 10],  # Minor seventh
    'dominant_seventh': [0, 4, 7, 10],  # Dominant seventh
    'diminished': [0, 3, 6],  # Diminished triad
    'diminished_seventh': [0, 3, 6, 9],  # Diminished seventh
    'augmented': [0, 4, 8],  # Augmented triad
    'suspended_second': [0, 2, 7],  # Suspended second
    'suspended_fourth': [0, 5, 7],  # Suspended fourth
    'augmented_seventh': [0, 4, 8, 10]  # Augmented seventh
}

# Define typical chord types for each scale degree in different modes
mode_chord_types = {
    'major': ['major', 'minor', 'minor', 'major', 'dominant_seventh', 'minor', 'diminished'],
    'minor': ['minor', 'diminished', 'augmented', 'minor', 'minor', 'major', 'major_seventh'],
    'dorian': ['minor', 'minor', 'major', 'major', 'minor', 'diminished', 'major'],
    'phrygian': ['minor', 'major', 'diminished', 'minor', 'dominant_seventh', 'major', 'minor'],
    'lydian': ['major', 'major', 'diminished', 'dominant_seventh', 'minor', 'minor', 'augmented'],
    'mixolydian': ['major', 'minor', 'diminished', 'major', 'minor', 'minor', 'major_seventh'],
    'locrian': ['diminished', 'major', 'minor', 'diminished', 'minor', 'major', 'minor_seventh'],
    'aeolian': ['minor', 'diminished', 'major', 'minor', 'minor', 'major', 'dominant_seventh']
}

def create_scale(root, mode):
    if root not in NOTE_TO_MIDI:
        raise ValueError("Root note is not valid")
    
    root_midi = NOTE_TO_MIDI[root]
    scale_intervals = scales[mode]
    scale_notes = [root_midi]  # Start with the root note.

    # Build the scale up to the next octave.
    current_note = root_midi
    for interval in scale_intervals:
        current_note += interval
        scale_notes.append(current_note % 128)  # Ensure MIDI note number is within valid range
    
    return scale_notes

def generate_chord_progression(root, mode, progression):
    scale_notes = create_scale(root, mode)
    chords = []

    for degree in progression:
        degree_index = degree - 1

        # Selecting chord type based on degree and mode
        chord_type = mode_chord_types[mode][degree_index]

        chord_notes = [scale_notes[(degree_index + interval) % len(scale_notes)] for interval in chord_structures[chord_type]]
        chords.append(chord_notes)
    
    return chords

def generate_random_progression(mode, length=4):
    # Generate a random chord progression
    progression = []
    for _ in range(length):
        degree = random.randint(1, 7)  # Choose a random degree from 1 to 7
        progression.append(degree)
    return progression

def play_chords(chord_progression, tempo, bars):
    ticks_per_beat = 480  # Standard resolution for MIDI files
    microseconds_per_beat = mido.bpm2tempo(tempo)  # Convert BPM to microseconds per beat

    mid = MidiFile(ticks_per_beat=ticks_per_beat)  # Create a new MIDI file
    track = MidiTrack()
    mid.tracks.append(track)

    # Set the tempo of the MIDI file
    track.append(mido.MetaMessage('set_tempo', tempo=microseconds_per_beat, time=0))
    
    track.append(Message('program_change', program=12, time=0))

    # Calculate the duration of a bar in ticks (assuming 4/4 time)
    bar_duration = 4 * ticks_per_beat
    
    for bar in range(bars):
        for chord in chord_progression:
            time_passed = 0
            for note in chord:
                track.append(Message('note_on', note=note, velocity=64, time=time_passed))
                time_passed = 0  # Subsequent notes in the chord have no delay
            
            # Wait for the duration of the bar before turning off the chord
            track.append(Message('note_off', note=chord[0], velocity=64, time=bar_duration))
            for note in chord[1:]:
                track.append(Message('note_off', note=note, velocity=64, time=0))

    mid.save('chord_progression.mid')


# User inputs
tempo = int(input("Enter the tempo in BPM: "))
bars = int(input("Enter the number of bars: "))
mode = input("Enter mode (major/minor/dorian/phrygian/lydian/mixolydian/locrian/aeolian): ")
root_note = input("Enter the root note (e.g., 'C', 'D#', 'F'): ")

# Generate random chord progression
progression_degrees = generate_random_progression(mode, length=4)  # You can adjust the length as needed

# Generate and play the chord progression.
chord_progression = generate_chord_progression(root_note, mode, progression_degrees)
play_chords(chord_progression, tempo, bars)

print("Chord progression MIDI file created and saved as 'chord_progression.mid'.")
