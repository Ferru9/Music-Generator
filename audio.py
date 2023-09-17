import mido
import pygame
import time
import random
import numpy as np

# Constants for note names and scales
NOTE_NAMES = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
MAJOR_SCALE = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4']

# Define genetic algorithm parameters
POPULATION_SIZE = 10
NUM_GENERATIONS = 50

# Function to create a random melody
def create_random_melody():
    melody = []
    for _ in range(32):  # 32 notes in the melody
        melody_note = random.choice(MAJOR_SCALE)
        melody.append(melody_note)
    return melody

# Function to evaluate the fitness of a melody (complex fitness function)
def evaluate_fitness(melody):
    fitness_score = 0

    # 1. Melody Length: Encourage melodies of a specific length (e.g., 32 notes)
    if len(melody) == 32:
        fitness_score += 1

    # 2. Unique Notes: Encourage melodies with more unique notes
    unique_notes = len(set(melody))
    fitness_score += unique_notes

    # 3. Melody Contour: Encourage melodies with a rising or falling contour
    contour = [1 if melody[i] < melody[i + 1] else -1 for i in range(len(melody) - 1)]
    contour_score = sum(contour)
    fitness_score += contour_score

    # 4. Harmony: Encourage melodies that fit well with a chord progression
    # You can define chord progressions and assign higher fitness to melodies that match them

    # 5. Rhythmic Patterns: Encourage melodies with interesting rhythmic patterns
    rhythmic_score = 0
    for i in range(1, len(melody)):
        if random.random() < 0.2:  # Rhythmic variation rate
            rhythmic_score += 1
    fitness_score += rhythmic_score

    return fitness_score

# Function to select melodies for the next generation based on their fitness
def select_melodies(population):
    # Select melodies based on their fitness (higher fitness has a better chance)
    fitness_scores = [evaluate_fitness(melody) for melody in population]
    selected_indices = np.random.choice(range(len(population)), size=POPULATION_SIZE, p=fitness_scores/np.sum(fitness_scores))
    selected_melodies = [population[i] for i in selected_indices]
    return selected_melodies

# Function to create a new generation of melodies through crossover and mutation
def create_next_generation(selected_melodies):
    next_generation = []

    # Perform crossover to create new melodies
    for _ in range(POPULATION_SIZE):
        parent1, parent2 = random.choices(selected_melodies, k=2)
        crossover_point = random.randint(1, len(parent1) - 1)
        child = parent1[:crossover_point] + parent2[crossover_point:]
        next_generation.append(child)

    # Perform mutation by randomly changing some notes
    for i in range(POPULATION_SIZE):
        if random.random() < 0.2:  # Mutation rate
            mutation_point = random.randint(0, len(next_generation[i]) - 1)
            next_generation[i][mutation_point] = random.choice(MAJOR_SCALE)

    return next_generation

# Function to convert note names to MIDI note numbers
def note_to_midi_note_number(note):
    octave = int(note[-1])
    note_name = note[:-1]
    return NOTE_NAMES.index(note_name) + 12 * octave

# Output MIDI file name for the best melody
best_melody_file = 'best_melody.mid'

# Genetic algorithm for melody generation
population = [create_random_melody() for _ in range(POPULATION_SIZE)]

for generation in range(NUM_GENERATIONS):
    print(f"Generation {generation + 1}/{NUM_GENERATIONS}")
    selected_melodies = select_melodies(population)
    best_melody = max(selected_melodies, key=evaluate_fitness)
    best_melody_track = mido.MidiTrack()
    for note in best_melody:
        note_number = note_to_midi_note_number(note)
        best_melody_track.append(mido.Message('note_on', note=note_number, velocity=64, time=0))
        best_melody_track.append(mido.Message('note_off', note=note_number, velocity=64, time=500))
    mid = mido.MidiFile()
    mid.tracks.append(best_melody_track)
    mid.save(best_melody_file)
    print(f"Best melody fitness: {evaluate_fitness(best_melody)}")
    population = create_next_generation(selected_melodies)

# Play the best generated melody
pygame.init()
pygame.mixer.music.load(best_melody_file)
pygame.mixer.music.play()
print("Playing the best generated melody...")
while pygame.mixer.music.get_busy():
    time.sleep(1)
