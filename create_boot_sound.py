#!/usr/bin/env python3

import numpy as np
from scipy.io import wavfile

def generate_boot_sound():
    # Sample rate
    sample_rate = 44100
    
    # Generate time array
    t = np.linspace(0, 1, sample_rate)
    
    # Create boot sound components
    startup_beep = 0.5 * np.sin(2 * np.pi * 880 * t[:int(sample_rate * 0.1)])  # 880 Hz for 0.1s
    power_up = 0.3 * np.sin(2 * np.pi * np.linspace(440, 880, int(sample_rate * 0.2)))  # Sweep from 440 to 880 Hz
    confirm_beep = 0.4 * np.sin(2 * np.pi * 1760 * t[:int(sample_rate * 0.05)])  # 1760 Hz for 0.05s
    
    # Add some silence between components
    silence = np.zeros(int(sample_rate * 0.05))
    
    # Combine all components
    sound = np.concatenate([
        startup_beep,
        silence,
        power_up,
        silence,
        confirm_beep
    ])
    
    # Apply fade in/out
    fade_samples = int(sample_rate * 0.01)
    fade_in = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)
    
    sound[:fade_samples] *= fade_in
    sound[-fade_samples:] *= fade_out
    
    # Normalize
    sound = np.int16(sound * 32767)
    
    # Save the sound
    wavfile.write('/etc/pokedexos/sounds/boot.wav', sample_rate, sound)

if __name__ == '__main__':
    # Create sounds directory if it doesn't exist
    import os
    os.makedirs('/etc/pokedexos/sounds', exist_ok=True)
    
    # Generate the boot sound
    generate_boot_sound() 