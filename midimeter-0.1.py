#!/usr/bin/env python

"""
MIDImeter v0.1 by Art Chaidarun

2011-01-29

"""
from __future__ import division

import os
import sys
import time

import pygame as pg
from pygame import midi


def textblit(text, bgsurf, x, y, align="l"):
  """Display text using character sprites"""
  window.blit(bgsurf, (x, y))
  w = 0
  xi = x
  for c in text:
    w += csprite[c][1]
  if w > bgsurf.get_width():
    w = bgsurf.get_width()
  if align == "r":
    x += bgsurf.get_width() - w
  if align == "c":
    x += (bgsurf.get_width() - w) // 2
  # NOTE TO SELF: The loop below detects text overflow... try using the
  # optional "area" parameter of surface.blit instead
  for c in text:
    if bgsurf.get_width() < x - xi + csprite[c][1]:
      break
    window.blit(csprite[c][0], (x, y))
    x += csprite[c][1]

def rainbow(c):
  """Convert green-to-red spectrum percentage into RGB tuple"""
  c = round(c * 255)
  if c in range(0, 64):
    return (c * 4, 128 + c * 2, 32 - c // 2)
  else:
    return (255, 255 - (c - 64) * 4 // 3, 0)

def update_dev(increment=0):
  """Update the current MIDI input device"""
  global devno, idevs, devbg, numbg
  devno += increment
  if devno >= len(idevs):
    devno = 0
  if devno < 0:
    devno = len(idevs) - 1
  textblit(idevs[devno][1], devbg, 1, 152, "c")
  textblit(str(devno + 1), numbg, 81, 179, "r")
  textblit(str(len(idevs)), numbg, 126, 179, "l")

def update_time():
  """Update the playing time"""

def update_info():
  """Update the performance stats"""

def update_boards():
  """Update the keyboard displays"""
  global id, dur, note, k1, k2, k3, whiteids, blackids
  


#**************************************************************** PROGRAM SETUP
pg.init()
midi.init()

# Load surfaces
background = pg.image.load("background.png")
wglow = pg.image.load("wglow.png")
bglow = pg.image.load("bglow.png")
blackshadow = pg.image.load("blackshadow.png")
blacks = pg.image.load("blacks.png")
whites = background.subsurface((9, 261, 782, 90))
devbg = background.subsurface((1, 152, 238, 11))
numbg = background.subsurface((126, 197, 34, 11))
infobg = background.subsurface((689, 180, 85, 11))
ifont = pg.image.load("alph.png")

# Create variables
alphanum = "0123456789abcdefghijklmnopqrstuvwxyz "
widths = [12,  6, 12, 12, 11, 12, 12, 11, 12, 12, 12, 11, 12,
          12, 11, 12, 12, 11,  5, 12, 11, 12, 12, 11, 12, 12,
          12, 11, 12, 12, 11, 12, 11, 12, 12, 12, 11]
whiteids = [21, 23, 24, 26, 28, 29, 31, 33, 35, 36, 38, 40, 41,
            43, 45, 47, 48, 50, 52, 53, 55, 57, 59, 60, 62, 64,
            65, 67, 69, 71, 72, 74, 76, 77, 79, 81, 83, 84, 86,
            88, 89, 91, 93, 95, 96, 98, 100, 101, 103, 105, 107, 108]
blackids = [22, 25, 27, 30, 32, 34, 37, 39, 42, 44, 46, 49,
            51, 54, 56, 58, 61, 63, 66, 68, 70, 73, 75, 78,
            80, 82, 85, 87, 90, 92, 94, 97, 99, 102, 104, 106]  
blackxs = [21, 51, 66, 96, 111, 126, 156, 171, 201, 216, 231, 261,
           276, 306, 321, 336, 366, 381, 411, 426, 441, 471, 486, 516,
           531, 546, 576, 591, 621, 636, 651, 681, 696, 726, 741, 756]
csprite = {}
x = 0
i = 0
for c in alphanum:
  csprite[c] = (ifont.subsurface((x, 0, widths[i], 11)), widths[i])
  x += widths[i]
  i += 1
running = True
recording = True
idevs = []
piano = -1
# Detect all MIDI devices, filter out outputs, create sanitized list of inputs
if 0 < midi.get_count():
  for i in range(midi.get_count()):
    if midi.get_device_info(i)[2]: # if device is an input device
      nm = ''
      for c in bytes.decode(midi.get_device_info(i)[1]).lower():
        if 0 <= alphanum.find(c):
          nm += c
      while 0 <= nm.find("  "):
        nm = nm.replace("  ", " ")
      idevs.append((i, nm))
      if (0 <= nm.find("piano") or 0 <= nm.find("key")) and 0 > piano:
        piano = i
# Select initial input device
if 0 < piano or 0 < len(idevs):
  if 0 < piano:
    devid = piano
  else:
    devid = idevs[0][0]
  idev = midi.Input(devid)
  for n in range(len(idevs)):
    if idevs[n][0] == devid:
      devno = n
      break
else:
  devid = -1

# Create program window
os.environ['SDL_VIDEO_CENTERED'] = '1'
pg.display.set_icon(pg.image.load("icon.png"))
pg.display.set_caption("MIDImeter v0.1")
window = pg.display.set_mode((800, 600))

# Display program background
window.blit(background, (0, 0))
window.blit(blacks, (9, 261))
window.blit(blacks, (9, 381))
window.blit(blacks, (9, 501))
update_dev(0)
pg.display.flip()

#******************************************************************** MAIN LOOP
while running:
  events = pg.event.get()
  for e in events:
    if e.type in [pg.QUIT]:
      del idev
      midi.quit()
      sys.exit()
    if e.type in [pg.KEYDOWN]:
      recording = True
  k1 = 0 # keyboard 1 current max value
  k2 = 0 # keyboard 2 current max value
  k3 = 0 # keyboard 3 current max value
  note = [0] * 128 # [note id]
  for i in range(128):
    # Volume, timestamp, hit count, duration, duration * volume
    note[i] = {'vol': 0, 'stamp': 0, 'hits': 0, 'dur': 0, 'dvol': 0}
  if recording:
    pg.event.clear()
  while recording:
    events = pg.event.get()
    for e in events:
      if e.type in [pg.QUIT]:
        del idev
        midi.quit()
        sys.exit()
      if e.type in [pg.KEYDOWN]:
        key = pg.key.name(e.key)
        if key == "left":
          update_dev(-1)
          pg.display.flip()
        elif key == "right":
          update_dev(1)
          pg.display.flip()
        else:
          recording = False
          break
      if e.type in [midi.MIDIIN]:
        id = e.data1
        if e.status in range(128, 160):
          window.blit(whites, (9, 261))
          window.blit(whites, (9, 381))
          window.blit(whites, (9, 501))
          if e.data2 and e.status > 143:
            # If note was turned on
            note[id]['vol'] = e.data2
            note[id]['stamp'] = e.timestamp
          if e.status < 144 or (e.status > 143 and e.data2 == 0):
            # If note was turned off
            note[id]['hits'] += 1
            dur = e.timestamp - note[id]['stamp']
            h = note[id]['hits']
            note[id]['dur'] += dur
            note[id]['dvol'] += dur * note[id]['vol']
            if h > k1:
              k1 = h
            if h * note[id]['dur'] > k2: 
              k2 = h * note[id]['dur']
            if note[id]['dvol'] > k3:
              k3 = note[id]['dvol']
          for i in range(52): # process white keys
            j = whiteids[i]
            h = note[j]['hits']
            if h:
              x = 11 + 15 * i
              window.fill(rainbow(h / k1), (x, 263, 13, 86))
              window.fill(rainbow(h * note[j]['dur'] / k2), (x, 383, 13, 86))
              window.fill(rainbow(note[j]['dvol'] / k3), (x, 503, 13, 86))
          window.blit(blacks, (9, 261))
          window.blit(blacks, (9, 381))
          window.blit(blacks, (9, 501))
          for i in range(36): # process black keys
            j = blackids[i]
            h = note[j]['hits']
            if h:
              x = blackxs[i]
              window.fill(rainbow(h / k1), (x, 263, 7, 53))
              window.fill(rainbow(h * note[j]['dur'] / k2), (x, 383, 7, 53))
              window.fill(rainbow(note[j]['dvol'] / k3), (x, 503, 7, 53))
          window.blit(blackshadow, (9, 261))
          window.blit(blackshadow, (9, 381))
          window.blit(blackshadow, (9, 501))
          if e.status < 144 or (e.status > 143 and e.data2 == 0):
            note[id]['vol'] = 0
          for id in range (21, 109):
            if note[id]['vol']:
              if id in whiteids:
                x = 15 * whiteids.index(id) + 11
                window.blit(wglow, (x, 320))
                window.blit(wglow, (x, 440))
                window.blit(wglow, (x, 560))
              else:
                x = blackxs[blackids.index(id)]
                window.blit(bglow, (x, 287))
                window.blit(bglow, (x, 407))
                window.blit(bglow, (x, 527))
          pg.display.flip()
    if idev.poll():
      midi_events = idev.read(10)
      # convert them into pg events.
      midi_evs = midi.midis2events(midi_events, idev.device_id)
      for m_e in midi_evs:
        pg.event.post(m_e)
del idev
midi.quit()