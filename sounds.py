"""
Génération procédurale des sons (numpy) + initialisation pygame mixer.
"""

import pygame
import numpy as np
from constants import SAMPLE_RATE


def generer_tir():
    duration = 0.08
    n_samples = int(SAMPLE_RATE * duration)
    t = np.arange(n_samples) / SAMPLE_RATE
    freq = 880.0
    env = np.exp(-t * 40.0)
    signal = 0.3 * np.sin(2 * np.pi * freq * t) * env
    audio = (signal * 32767).astype(np.int16)
    stereo = np.column_stack((audio, audio))
    return stereo


def generer_explosion_grande():
    duration = 0.3
    n_samples = int(SAMPLE_RATE * duration)
    t = np.arange(n_samples) / SAMPLE_RATE
    white_noise = (np.random.rand(n_samples) * 2 - 1).astype(np.float64)
    freq_envelope = 200.0 - 180.0 * (t / duration)
    freq_envelope = np.maximum(freq_envelope, 30.0)
    phase = 2 * np.pi * freq_envelope * t
    lowpass = np.exp(-t * 8.0)
    signal = white_noise * 0.4 * lowpass * np.sin(phase)
    audio = (signal * 32767).astype(np.int16)
    stereo = np.column_stack((audio, audio))
    return stereo


def generer_explosion_petite():
    duration = 0.15
    n_samples = int(SAMPLE_RATE * duration)
    t = np.arange(n_samples) / SAMPLE_RATE
    white_noise = (np.random.rand(n_samples) * 2 - 1).astype(np.float64)
    freq_envelope = 300.0 - 250.0 * (t / duration)
    freq_envelope = np.maximum(freq_envelope, 50.0)
    phase = 2 * np.pi * freq_envelope * t
    lowpass = np.exp(-t * 15.0)
    signal = white_noise * 0.3 * lowpass * np.sin(phase)
    audio = (signal * 32767).astype(np.int16)
    stereo = np.column_stack((audio, audio))
    return stereo


def generer_perte_vie():
    duration = 0.4
    n_samples = int(SAMPLE_RATE * duration)
    t = np.arange(n_samples) / SAMPLE_RATE
    freq_start = 400.0
    freq_end = 80.0
    freq = freq_start + (freq_end - freq_start) * (t / duration)
    freq = np.maximum(freq, 20.0)
    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    env = np.exp(-t * 4.0) * (1 + 0.3 * np.sin(2 * np.pi * 3 * t))
    signal = 0.5 * np.sin(phase) * env
    audio = (signal * 32767).astype(np.int16)
    stereo = np.column_stack((audio, audio))
    return stereo


def initialiser_sons():
    pygame.mixer.pre_init(SAMPLE_RATE, -16, 2, 512)
    pygame.mixer.init()
    son_tir = pygame.sndarray.make_sound(generer_tir())
    son_explosion_grande = pygame.sndarray.make_sound(generer_explosion_grande())
    son_explosion_petite = pygame.sndarray.make_sound(generer_explosion_petite())
    son_perte_vie = pygame.sndarray.make_sound(generer_perte_vie())
    son_tir.set_volume(0.4)
    son_explosion_grande.set_volume(0.6)
    son_explosion_petite.set_volume(0.5)
    son_perte_vie.set_volume(0.5)
    return son_tir, son_explosion_grande, son_explosion_petite, son_perte_vie
