import sys
import os

import pygame
import pygame.midi
from pygame.locals import *


pygame.init()
pygame.fastevent.init()
pygame.midi.init()

i = pygame.midi.Input(3)
going = True
while going:
  events = pygame.fastevent.get()
  for e in events:
    if e.type in [QUIT]:
      going = False
    if e.type in [KEYDOWN]:
      going = False
    if e.type in [pygame.midi.MIDIIN]:
      print (e)

  if i.poll():
    midi_events = i.read(10)
    # convert them into pygame events.
    midi_evs = pygame.midi.midis2events(midi_events, i.device_id)

    for m_e in midi_evs:
      pygame.fastevent.post( m_e )

del i
pygame.midi.quit()