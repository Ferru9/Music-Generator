import mido
import pygame
import time
import random
import numpy as np

# Constants for note names and scales
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Chord Progressions (example)
CHORD_PROGRESSIONS = [
    ['C', 'C#', 'G'],
    ['D', 'F#', 'A'],
    ['E', 'G', 'B'],
    ['A', 'C', 'E'],
]

# Function to get a random chord progression
def get_random_chord_progression():
    return random.choice(CHORD_PROGRESSIONS)

# Function to get user input for BPM
def get_user_bpm():
    while True:
        try:
            bpm = int(input("Enter the desired BPM (Beats Per Minute): "))
            if 30 <= bpm <= 240:  # Adjust the range as needed
                return bpm
            else:
                print("BPM should be in the range of 30 to 240.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

# Function to create a random melody based on the selected scale and chord progression
def create_random_melody_with_chords(scale, chord_progression, num_phrases=4, notes_per_phrase=8):
    melody = []
    for _ in range(num_phrases):
        for chord_name in chord_progression:
            chord = [note + str(4) for note in chord_name.split()]
            phrase = [random.choice(chord) for _ in range(notes_per_phrase // len(chord))]
            melody.extend(phrase)
    return melody

# Function to generate harmony for a given melody
def generate_harmony(melody, harmony_intervals):
    harmony = []
    for note in melody:
        if ' ' in note:
            # Handle chord names by splitting them into individual notes
            chord_notes = note.split()
            for chord_note in chord_notes:
                if chord_note in NOTE_NAMES:
                    note_index = NOTE_NAMES.index(chord_note)
                    harmony_note_index = (note_index + harmony_intervals[note_index]) % len(NOTE_NAMES)
                    harmony_note = NOTE_NAMES[harmony_note_index] + chord_note[-1]
                    harmony.append(harmony_note)
        else:
            # Handle single notes
            note_index = NOTE_NAMES.index(note[:-1])
            harmony_note_index = (note_index + harmony_intervals[note_index]) % len(NOTE_NAMES)
            harmony_note = NOTE_NAMES[harmony_note_index] + note[-1]
            harmony.append(harmony_note)
    return harmony

def evaluate_fitness(melody, harmony, chord_progression):
    fitness_score = 0

    # 1. Melody Length: Encourage melodies of a specific length (e.g., 32 notes)
    if len(melody) == 32:
        fitness_score += 1

    # 2. Unique Notes: Encourage melodies with more unique notes
    unique_notes = len(set(melody))
    fitness_score += unique_notes * 0.5  # Adjust the weight as needed

    # 3. Chord Tones: Assign higher fitness for melody notes that are chord tones
    chord_tones = set()
    for chord in chord_progression:
        chord_tones.update(chord.split())
    chord_tone_count = sum(1 for note in melody if note.split()[-1] in chord_tones)
    fitness_score += chord_tone_count * 2  # Adjust the weight as needed

    # 4. Voice Leading: Encourage smooth voice leading between chords
    voice_leading_score = 0
    for i in range(len(melody) - 1):
        note1 = melody[i].split()[-1]
        note2 = melody[i + 1].split()[-1]
        if note1 in chord_tones and note2 in chord_tones:
            index1 = chord_tones.index(note1)
            index2 = chord_tones.index(note2)
            voice_leading_score += abs(index2 - index1)
    fitness_score += voice_leading_score * 0.1  # Adjust the weight as needed

    # 5. Rhythmic Patterns: Encourage melodies with interesting rhythmic patterns
    rhythmic_score = 0
    for i in range(1, len(melody)):
        if random.random() < 0.2:  # Rhythmic variation rate
            rhythmic_score += 1
    fitness_score += rhythmic_score * 0.2  # Adjust the weight as needed

    # 6. Melodic Contour: Encourage melodies with a balanced contour
    contour = [1 if melody[i] < melody[i + 1] else -1 for i in range(len(melody) - 1)]
    contour_score = sum(contour)
    fitness_score += contour_score * 0.2  # Adjust the weight as needed

    return fitness_score



# Function to select melodies for the next generation based on their fitness
def select_melodies(population, chord_progression):
    # Select melodies based on their fitness (higher fitness has a better chance)
    fitness_scores = [evaluate_fitness(melody, harmony, chord_progression) for melody, harmony in population]
    selected_indices = np.random.choice(range(len(population)), size=POPULATION_SIZE, p=fitness_scores/np.sum(fitness_scores))
    selected_melodies = [population[i] for i in selected_indices]
    return selected_melodies

# Function to create a new generation of melodies through crossover and mutation
def create_next_generation(selected_melodies, harmony_intervals):
    next_generation = []

    # Perform crossover to create new melodies
    for _ in range(POPULATION_SIZE):
        parent1, parent2 = random.choices(selected_melodies, k=2)
        crossover_point = random.randint(1, len(parent1[0]) - 1)
        child_melody = parent1[0][:crossover_point] + parent2[0][crossover_point:]
        child_harmony = parent1[1][:crossover_point] + parent2[1][crossover_point:]
        next_generation.append((child_melody, child_harmony))

    # Perform mutation by randomly changing some notes
    for i in range(POPULATION_SIZE):
        if random.random() < 0.2:  # Mutation rate
            mutation_point = random.randint(0, len(next_generation[i][0]) - 1)
            next_generation[i][0][mutation_point] = random.choice(selected_scale)
            next_generation[i][1][mutation_point] = random.choice(harmony_intervals[:len(next_generation[i][1])])  # Ensure harmony_intervals length matches melody

    return next_generation

# Function to convert note names to MIDI note numbers
def note_to_midi_note_number(note):
    if isinstance(note, str):
        note_name = note[:-1]  # Remove the octave part
        octave = int(note[-1])
        return NOTE_NAMES.index(note_name) + 12 * octave
    return 0  # Return 0 if note is None or empty

# Get user input for scale and mode
scale_choice = input("Choose a scale (e.g., C, D, E, F, G, A, B): ").upper()

# Define scales
scales = {
    'C': ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4'],
    'D': ['D4', 'E4', 'F#4', 'G4', 'A4', 'B4', 'C#5'],
    'E': ['E4', 'F#4', 'G#4', 'A4', 'B4', 'C#5', 'D#5'],
    'F': ['F4', 'G4', 'A4', 'A#4', 'C5', 'D5', 'E5'],
    'G': ['G4', 'A4', 'B4', 'C5', 'D5', 'E5', 'F#5'],
    'A': ['A4', 'B4', 'C#5', 'D5', 'E5', 'F#5', 'G#5'],
    'B': ['B4', 'C#5', 'D#5', 'E5', 'F#5', 'G#5', 'A#5'],
    # Add more scales as needed
}

# Check if the user's scale choice is valid
if scale_choice not in scales:
    print("Invalid scale choice. Exiting.")
    exit(1)

# Get user input for mode
mode_choice = input("Choose a mode (e.g., Major, Dorian, Phrygian, etc.): ").capitalize()

# Define modes
modes = {
    'Major': [2, 2, 1, 2, 2, 2, 1],         # Major scale intervals
    'Dorian': [2, 1, 2, 2, 2, 1, 2],       # Dorian mode intervals
    'Phrygian': [1, 2, 2, 2, 1, 2, 2],     # Phrygian mode intervals
    'Lydian': [2, 2, 2, 1, 2, 2, 1],       # Lydian mode intervals
    'Mixolydian': [2, 2, 1, 2, 2, 1, 2],   # Mixolydian mode intervals
    'Aeolian': [2, 1, 2, 2, 1, 2, 2],      # Aeolian (Natural Minor) mode intervals
    'Locrian': [1, 2, 2, 1, 2, 2, 2],      # Locrian mode intervals
    'Minor': [2, 1, 2, 2, 1, 2, 2],        # Minor (Diatonic) mode intervals
    # Add more modes as needed
}

# Calculate the selected scale based on the chosen mode
selected_scale = scales[scale_choice]

# Apply the selected mode to the scale
if mode_choice in modes:
    mode_intervals = modes[mode_choice]
    modified_scale = []
    for i in range(len(selected_scale)):
        # Apply the mode intervals to the selected scale
        modified_note_index = (i + sum(mode_intervals[:i])) % len(NOTE_NAMES)
        modified_note = NOTE_NAMES[modified_note_index] + str(i // len(NOTE_NAMES) + 4)
        modified_scale.append(modified_note)

    print(f"Original Scale: {selected_scale}")
    print(f"Mode Applied: {mode_choice}")
    print(f"Modified Scale: {modified_scale}")
    selected_scale = modified_scale
else:
    print("Invalid mode choice. Using the natural scale without applying a mode.")

# Define harmony intervals (adjust as needed)
harmony_intervals = [4, 3, 5, 4, 3, 4, 3, 4, 3, 5, 4, 3]

# Output MIDI file name for the best melody
best_melody_file = 'best_melody.mid'

# Genetic algorithm for melody generation
POPULATION_SIZE = 10
NUM_GENERATIONS = 20

# Get user input for BPM
desired_bpm = get_user_bpm()

# Calculate the time duration for each note and rest based on the desired BPM
milliseconds_per_beat = 60000 / desired_bpm  # Convert BPM to milliseconds per beat

# Get user input for chord progression selection
print("Available Chord Progressions:")
for i, progression in enumerate(CHORD_PROGRESSIONS, start=1):
    print(f"{i}. {' -> '.join(progression)}")

while True:
    try:
        chord_choice = int(input("Select a chord progression (1 to 3): "))
        if 1 <= chord_choice <= len(CHORD_PROGRESSIONS):
            chord_progression = CHORD_PROGRESSIONS[chord_choice - 1]
            break
        else:
            print("Invalid choice. Please select a valid chord progression.")
    except ValueError:
        print("Invalid input. Please enter a valid number.")

# Initialize population with both melody and harmony
population = [(create_random_melody_with_chords(selected_scale, chord_progression, num_phrases=4, notes_per_phrase=8),
               generate_harmony(create_random_melody_with_chords(selected_scale, chord_progression, num_phrases=4, notes_per_phrase=8), harmony_intervals))
              for _ in range(POPULATION_SIZE)]

for generation in range(NUM_GENERATIONS):
    print(f"Generation {generation + 1}/{NUM_GENERATIONS}")
    selected_melodies = select_melodies(population, chord_progression)
    best_melody, best_harmony = max(selected_melodies, key=lambda x: evaluate_fitness(x[0], x[1], chord_progression))

    best_melody_track = mido.MidiTrack()
    best_harmony_track = mido.MidiTrack()

    for melody_note, harmony_note in zip(best_melody, best_harmony):
        melody_note_number = (note_to_midi_note_number(melody_note) if melody_note else 0)
        harmony_note_number = (note_to_midi_note_number(harmony_note) if harmony_note else 0)

        if melody_note_number:
            best_melody_track.append(mido.Message('note_on', note=melody_note_number, velocity=64, time=0))
            best_melody_track.append(mido.Message('note_off', note=melody_note_number, velocity=64, time=int(milliseconds_per_beat)))

        if harmony_note_number:
            best_harmony_track.append(mido.Message('note_on', note=harmony_note_number, velocity=64, time=0))
            best_harmony_track.append(mido.Message('note_off', note=harmony_note_number, velocity=64, time=int(milliseconds_per_beat)))

    mid = mido.MidiFile()
    mid.tracks.append(best_melody_track)
    mid.tracks.append(best_harmony_track)
    mid.save(best_melody_file)

    print(f"Best melody fitness: {evaluate_fitness(best_melody, best_harmony, chord_progression)}")

    population = create_next_generation(selected_melodies, harmony_intervals)

# Play the best generated melody
pygame.init()
pygame.mixer.music.load(best_melody_file)
pygame.mixer.music.play()

print("Playing the best generated melody...")
while pygame.mixer.music.get_busy():
    time.sleep(1)
