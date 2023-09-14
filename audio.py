import mido
from mido import MidiFile, MidiTrack, Message
import pygame
import time
import random

# Function to create a MIDI file with a melody
def create_melody_midi(output_file):
    mid = MidiFile()

    track = MidiTrack()
    mid.tracks.append(track)

    # Define the musical rules for generating the melody
    scale_notes = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4']
    melody_length = 20

    for _ in range(melody_length):
        #chosing a random scale note
        note = random.choice(scale_notes)
        note_number = note_to_midi_note_number(note)
        #the intesity of how the note is, or its "loudness"
        velocity = random.randint(40, 80)
        #how much a note will be playing for
        time_increment = random.randint(100, 400)

        track.append(Message('note_on', note=note_number, velocity=velocity, time=0))
        track.append(Message('note_off', note=note_number, velocity=velocity, time=time_increment))

    mid.save(output_file)

# Function to convert note names to MIDI note numbers
def note_to_midi_note_number(note):
    note_names = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    octave = int(note[-1])
    note_name = note[:-1]
    return note_names.index(note_name) + 12 * octave

# Output MIDI file name for the generated melody
output_file = 'procedural_melody.mid'

# Create the procedural melody
create_melody_midi(output_file)

# Play the generated melody
pygame.init()
pygame.mixer.music.load(output_file)
pygame.mixer.music.play()
while pygame.mixer.music.get_busy():
    time.sleep(1)
