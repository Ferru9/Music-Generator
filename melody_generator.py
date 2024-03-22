import mido
import time
import random

#Mapping notes to its midi value depending, for simplicity it will stay in one octave
NOTE_TO_MIDI = {
    'REST': None,  
    'C': 60,
    'C#': 61,
    'D': 62,
    'D#': 63,
    'E': 64,
    'F': 65,
    'F#': 66,
    'G': 67,
    'G#': 68,
    'A': 69,
    'A#': 70,
    'B': 71
}

# Modes to modify my scale depending on my starting note
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

#Getting the notes 
def get_notes(scale, mode):
    notes = [scale]
    steps = scales[mode]
    for step in steps:
        scale += step
        notes.append(scale)
    return notes

# Genetic Algorithm Components

#initialize my population with the following parameters, the size, the bars(determining the length of the song) and my notes
def initialize_population(size, bars, notes):
    #adding rest notes so more rest notes will get a chance to generate
    available_notes = notes + ['REST', 'REST', 'REST']  # Increased chances for REST note.
    #randomize the available notes and setting the bar length
    return [random.choices(available_notes, k=bars * 4) for _ in range(size)]


# This function performs a simple crossover operation between two parent
# It combines the genetic information from two parents to create a child

def crossover(parent1, parent2):
    # Find the midpoint of the parent DNA sequences
    cut = len(parent1) // 2
    # Create a child DNA sequence by taking the first half from parent1 and the second half from parent2
    child = parent1[:cut] + parent2[cut:]
    return child



def mutate(individual, notes, mutation_rate=0.01):
    # Create a list of available notes, including 'REST' as a possible note choice.
    available_notes = notes + ['REST', 'REST', 'REST']  # Increased chances for REST note.

    # Loop through each note 
    for i in range(len(individual)):
        # Check if a random number falls below the mutation_rate, which controls mutation probability.
        if random.random() < mutation_rate:
            # If the condition is met (probability check), perform the mutation:
            
            # Choose a new note randomly from the available notes and replace the current note.
            individual[i] = random.choice(available_notes)

    # Return the mutated individual with potentially changed notes.
    return individual

def fitness(individual, notes):

    score = 0
    length = len(individual)  # Define the length variable

    # Helper function to get note index, gracefully handling 'REST'
    def get_note_index(note):
        if note == 'REST':
            return -1
        return notes.index(note)

    #Reward the resolution from the 7th scale degree to the tonic
    for i in range(1, len(individual)):
        if individual[i - 1] == notes[-2] and individual[i] == notes[0]:
            score += 10

    #Penalize large jumps in the melody
    for i in range(1, len(individual)):
        interval = abs(get_note_index(individual[i]) - get_note_index(individual[i - 1]))
        if interval > 4 and interval != 1:
            score -= 15

    #Reward stepwise motion
    for i in range(1, len(individual)):
        interval = abs(get_note_index(individual[i]) - get_note_index(individual[i - 1]))
        if interval == 1:
            score += 10

    #Ensure the melody begins and ends on the tonic (root note of the scale)
    if individual[0] == notes[0]:
        score += 20
    if individual[-1] == notes[0]:
        score += 20

    #Dynamic Movement
    range_used = len(set(individual))
    score += range_used * 5 

    #Climactic Moment
    climax_position = individual.index(max(individual, key=get_note_index))
    if length * 0.4 <= climax_position <= length * 0.6:  # Check if climax is around the middle
        score += 10

    #Anticipation
    for i in range(1, len(individual) - 1):
        if individual[i - 1] == notes[4] and individual[i] == notes[-2] and individual[i + 1] == notes[0]:  # 5th to 7th to tonic
            score += 10

    #Encourage moderate use of rest notes
    num_rests = individual.count('REST')
    proportion_rests = num_rests / len(individual)
    
    # Define the preferred range for rest proportion
    MIN_PREFERRED_PROPORTION = 0.1  # Example: 10%
    MAX_PREFERRED_PROPORTION = 0.25  # Example: 25%

    if MIN_PREFERRED_PROPORTION <= proportion_rests <= MAX_PREFERRED_PROPORTION:
        score += 20  # Reward for being within the preferred range
    else:
        score -= 10  # Penalty for being outside the preferred range

    #Balance
    first_half_avg = sum([get_note_index(note) for note in individual[:length//2]]) / (length // 2)
    second_half_avg = sum([get_note_index(note) for note in individual[length//2:]]) / (length // 2)
    if first_half_avg < second_half_avg:
        score -= 10
    else:
        score += 10
        
    #Musical Phrasing
    phrase_start = 0
    phrase_end = 0
    total_phrases = 0
    current_phrase_length = 0
    max_phrase_length = len(individual) // 4  # Adjust based on typical phrase lengths

    for i in range(len(individual)):
        if individual[i] != 'REST':
            current_phrase_length += 1
        if i > 0 and individual[i] == 'REST' and individual[i - 1] != 'REST':
            phrase_end = i - 1
            if current_phrase_length > 1:
                total_phrases += 1
                # Evaluate dynamics within the phrase (example: louder endings)
                if individual[phrase_start] == individual[phrase_end]:
                    score += 5  # Slight reward for ending on the same note
                else:
                    score += 10  # Reward for dynamic contrast within the phrase
                # Penalize phrases that are too long or too short
                if current_phrase_length > max_phrase_length:
                    score -= 10
                elif current_phrase_length < max_phrase_length // 2:
                    score -= 10
            current_phrase_length = 0
            phrase_start = i + 1

    # Reward melodies with well-structured 
    score += total_phrases * 20
    
    #Melodic Direction
    upward_movements = 0
    downward_movements = 0
    
    for i in range(1, length):
        prev_note_index, curr_note_index = get_note_index(individual[i - 1]), get_note_index(individual[i])
        if curr_note_index > prev_note_index:
            upward_movements += 1
        elif curr_note_index < prev_note_index:
            downward_movements += 1
            
    # Ensure both upward and downward movements are present
    if upward_movements > 0 and downward_movements > 0:
        score += 20
    else:
        score -= 20  # Penalize if only one type of movement is dominant

    max_score = sum([x for x in [((length - 1) * 10 + 15 + length * 10 + 20 + (length - 1) * 10), (range_used * 5), 10, 10, 10]])
    
    #normalized_score = max(0, score) / max_score
    normalized_score = max(0, score) / max_score
    return normalized_score

# Calculate the number of differences between two individuals.
def distance(ind1, ind2):
    return sum(1 for x, y in zip(ind1, ind2) if x != y)

# Calculate fitness with a penalty for similarity to others in the population.
def shared_fitness(individual, population, notes, sigma_share=5):
    raw_fitness = fitness(individual, notes)  # Assumes another function defines fitness.
    # Count similar individuals within sigma_share distance.
    niche_count = sum(1 for other in population if distance(individual, other) < sigma_share)
    return raw_fitness / niche_count

# Select the top N individuals based on shared fitness.
def select_best_with_sharing(population, notes, top_n=10):
    # Calculate shared fitness for each individual.
    scored = [(shared_fitness(ind, population, notes), ind) for ind in population]
    scored.sort(key=lambda x: x[0], reverse=True)  # Sort by shared fitness.
    # Return the top N individuals with the highest shared fitness.
    return [x[1] for x in scored[:top_n]]

# Select the best individual from a random subset based on raw fitness.
def tournament_selection(population, notes, tournament_size=5):
    # Randomly select a group of individuals for a tournament.
    participants = random.choices(population, k=tournament_size)
    # Choose the individual with the highest raw fitness as the winner.
    return max(participants, key=lambda ind: fitness(ind, notes))  # Assumes another function defines fitness.


def main():
    # User prompts
    scale_name = input("Enter scale root note (e.g., C, E, G#): ").upper()
    while scale_name not in NOTE_TO_MIDI:
        print("Invalid note name. Please use a valid note (e.g., C, D#, F).")
        scale_name = input("Enter scale root note (e.g., C, E, G#): ").upper()

    scale = NOTE_TO_MIDI[scale_name]
    mode = input("Enter mode (major/minor/dorian/phrygian/lydian/mixolydian/locrian/aeolian): ")
    while mode not in scales:
        print("Invalid mode. Please select from the given options.")
        mode = input("Enter mode (major/minor/dorian/phrygian/lydian/mixolydian/locrian/aeolian): ")

    bpm = int(input("Enter BPM: "))
    bars = int(input("Enter number of bars: "))

    notes = get_notes(scale, mode)

    # Genetic algorithm parameters
    population_size = 250
    generations = 100
    elitism_count = 25  # Number of top melodies to directly pass to the next generation

    # Initialize population
    population = initialize_population(population_size, bars, notes)


    
    # Create an empty list to store the scores of each generation
    generation_scores = []

    for gen in range(generations):
        next_gen = []

        # Elitism: Directly pass the best melodies to the next generation
        best = select_best_with_sharing(population, notes, top_n=elitism_count)
        next_gen.extend(best)

        # Produce the remaining offspring via crossover and mutation
        while len(next_gen) < population_size:
            parent1 = tournament_selection(population, notes)
            parent2 = tournament_selection(population, notes)
            child = crossover(parent1, parent2)

            # Adjust mutation rate
            mutation_rate = 0.07
            child = mutate(child, notes, mutation_rate)

            next_gen.append(child)

        population = next_gen

        # Print generation info
        best_score = fitness(best[0], notes)
        print(f"Generation {gen + 1} completed. Best Score: {best_score:.4f}")

        # Append the score of the best melody of this generation to the list
        generation_scores.append(best_score)

    # Save the scores to a text file
    with open('generation_scores.txt', 'w') as file:
        for i, score in enumerate(generation_scores):
            file.write(f"{score:.4f}\n")

    print("Saved the scores to 'generation_scores.txt'")


    # Save the best melody to MIDI
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)

    # Standard resolution for MIDI files
    ticks_per_beat = 480  # Adjust this value if needed
    mid.ticks_per_beat = ticks_per_beat

    # Convert BPM to microseconds per beat and set the tempo
    microseconds_per_beat = mido.bpm2tempo(bpm)
    track.append(mido.MetaMessage('set_tempo', tempo=microseconds_per_beat, time=0))

    # Calculate ticks for a quarter note (assuming each note is a quarter note)
    ticks_per_note = ticks_per_beat

    last_note = 'REST'  # Initialize with a rest
    for note in best[0]:
        if note == 'REST':
            if last_note != 'REST':
                # Add a delay for the rest
                track.append(mido.Message('note_off', velocity=0, time=ticks_per_note))
        else:
            midi_value = note
            track.append(mido.Message('note_on', note=midi_value, velocity=64, time=0))
            track.append(mido.Message('note_off', note=midi_value, velocity=64, time=ticks_per_note))

        last_note = note

    mid.save('best_melody.mid')
    print("Saved the best melody to 'best_melody.mid'")

if __name__ == "__main__":
    main()
