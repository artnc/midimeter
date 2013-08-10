#!/usr/bin/env python

"""
MIDImeter v0.2 by Art Chaidarun

2012-08-03

"""
from __future__ import division

import os
import time

import pygame as pg
import pygame.midi

def textblit(text, x, y, boxwidth, align="l"):
  """Display text in the custom font"""
  textwidth = typeface.size(text)[0]
  if textwidth > boxwidth:
    textwidth = boxwidth
  if align == "c":
    x += (boxwidth - textwidth) // 2
  elif align == "r":
    x += boxwidth - textwidth
  window.blit(typeface.render(text, 1, (0, 0, 0)), (x, y))

def rainbow(numerator, denominator):
  """Convert green-to-red spectrum percentage into RGB tuple"""
  try:
    c = round(numerator / denominator * 255)
    if c in range(64):
      return (c * 4, 128 + c * 2, 32 - c // 2)
    else:
      return (255, 255 - (c - 64) * 4 // 3, 0)
  except ZeroDivisionError as e:
    # If no data, return the mid-spectrum color (i.e. orange)
    return (255, 170, 0)

def reset_stats():
  """Reset all information"""
  global hitcount, pitchcount, minhits, maxhits, minstamp, maxstamp, minvolume, maxvolume, note
  hitcount = 0
  pitchcount = 0
  minhits = 88
  maxhits = 0
  minstamp = 600000
  maxstamp = 0
  minvolume = 128
  maxvolume = 0
  note = [0] * 128 # [note pitch]
  for i in range(128):
    # Total hit count, last hit timestamp, current hit volume, max hit volume
    note[i] = {'hits': 0, 'stamp': 0, 'active': 0, 'maxvol': 0}
  pg.event.clear()

def clear_whites():
  """Blank out the white keys"""
  # Benchmark results: For painting 156 keys vs. blitting 3 keyboards, draw.rect
  # is 2.5x faster than window.blit while window.fill is 8.5x faster than blit.
  for i in [263, 383, 503]:
    for j in range(52):
      window.fill((255, 255, 255), (11 + 15 * j, i, 13, 86))

def clear_blacks():
  """Blank out the black keys"""
  for i in [263, 383, 503]:
    window.blit(whiteshadow, (11, i))
    for j in blackxs:
      window.fill((0, 0, 0), (j - 2, i, 11, 55))
      window.fill((45, 45, 45), (j, i, 7, 53))

def show_shadows():
  """Overlay black keys' shadows onto keyboards"""
  window.blit(blackshadow, (9, 261))
  window.blit(blackshadow, (9, 381))
  window.blit(blackshadow, (9, 501))

def update_dev(increment=0):
  """Update the current MIDI input device"""
  global devno
  devno += increment
  if devno >= len(idevs):
    devno = 0
  if devno < 0:
    devno = len(idevs) - 1
  window.blit(devbg, (1, 152))
  window.blit(numbg, (81, 179))
  window.blit(numbg, (126, 179))
  textblit(idevs[devno][1], 1, 152, 238, "c")
  textblit(str(devno + 1), 81, 179, 34, "r")
  textblit(str(len(idevs)), 126, 179, 34, "l")

def update_time():
  """Update the playing time"""

def update_info():
  """Update the performance stats"""

pg.init()
pg.fastevent.init()
pg.midi.init()

# Load startup resources
background = pg.image.load("background.png")
devbg = background.subsurface((1, 152, 238, 15))
numbg = background.subsurface((126, 197, 34, 15))
typeface = pg.font.Font("VarelaRound-Regular.ttf", 15)

# Detect all MIDI devices, filter out outputs, create sanitized list of inputs
idevs = []
piano = -1
if pg.midi.get_count() > 0:
  for i in range(pg.midi.get_count()):
    if pg.midi.get_device_info(i)[2]: # if device is an input device
      name = pg.midi.get_device_info(i)[1]
      while "  " in name:
        name = name.replace("  ", " ")
      idevs.append((i, name))
      lname = name.lower()
      if piano < 0 and any(x in lname for x in ("piano", "key", "usb")):
        piano = i

# Select initial input device
if 0 < piano or 0 < len(idevs):
  if 0 < piano:
    devid = piano
  else:
    devid = idevs[0][0]
  idev = pg.midi.Input(devid)
  for n in range(len(idevs)):
    if idevs[n][0] == devid:
      devno = n
      break
else:
  devid = -1

# Create program window
os.environ['SDL_VIDEO_CENTERED'] = '1'
pg.display.set_icon(pg.image.load("icon.png"))
pg.display.set_caption("MIDImeter v0.2")
window = pg.display.set_mode((800, 600))

# Display program window
window.blit(background, (0, 0))
update_dev(0)
# TODO: Convert all flips into updates
pg.display.flip()

# Lazy-initialize stuff that isn't required for initial window display
import sys
wglow = pg.image.load("wglow.png")
bglow = pg.image.load("bglow.png")
blackshadow = pg.image.load("blackshadow.png")
whiteshadow = pg.image.load("whiteshadow.png")
infobg = background.subsurface((689, 180, 85, 11))
whitepitches = [21, 23, 24, 26, 28, 29, 31, 33, 35, 36, 38, 40, 41,
                43, 45, 47, 48, 50, 52, 53, 55, 57, 59, 60, 62, 64,
                65, 67, 69, 71, 72, 74, 76, 77, 79, 81, 83, 84, 86,
                88, 89, 91, 93, 95, 96, 98, 100, 101, 103, 105, 107, 108]
blackpitches = [22, 25, 27, 30, 32, 34, 37, 39, 42, 44, 46, 49,
                51, 54, 56, 58, 61, 63, 66, 68, 70, 73, 75, 78,
                80, 82, 85, 87, 90, 92, 94, 97, 99, 102, 104, 106]
blackxs      = [21, 51, 66, 96, 111, 126, 156, 171, 201, 216, 231, 261,
                276, 306, 321, 336, 366, 381, 411, 426, 441, 471, 486, 516,
                531, 546, 576, 591, 621, 636, 651, 681, 696, 726, 741, 756]
recording = False
reset_stats()

while 1:
  events = pg.fastevent.get()
  for e in events:
    if e.type in [pg.midi.MIDIIN]:
      pitch = e.data1
      if e.status in range(128, 160):
        clear_whites()
        # MIDI reference: http://www.onicos.com/staff/iz/formats/midi-event.html
        if e.status < 144:
          # Note was turned off
          note[pitch]['active'] = 0
        elif e.status < 160:
          # Note was turned on
          if not recording:
            recording = True
            # Set the starting time as the current MIDI timestamp - 2. Two ms
            # must be subtracted to prevent the elapsed variable from being
            # 0, which causes a ZeroDivisionError in rainbow().
            starttime = pg.midi.time() - 2
          note[pitch]['active'] = 1
          hitcount += 1
          note[pitch]['hits'] += 1
          # Update statistics' ranges
          if note[pitch]['hits'] < minhits:
            minhits = note[pitch]['hits']
          if note[pitch]['hits'] > maxhits:
            maxhits = note[pitch]['hits']
          elapsed = int(e.timestamp) - starttime
          note[pitch]['stamp'] = elapsed
          if e.data2 > note[pitch]['maxvol']:
            note[pitch]['maxvol'] = e.data2
          if e.data2 < minvolume:
            minvolume = e.data2
            deltavolume = maxvolume - minvolume + 1
          if e.data2 > maxvolume:
            maxvolume = e.data2
            deltavolume = maxvolume - minvolume + 1
        else:
          continue
        # Update white key displays
        for i in range(52):
          j = whitepitches[i]
          h = note[j]['hits']
          if h:
            x = 11 + 15 * i
            window.fill(rainbow(note[j]['stamp'], elapsed), (x, 263, 13, 86))
            window.fill(rainbow(h, maxhits), (x, 383, 13, 86))
            window.fill(rainbow(note[j]['maxvol'] - minvolume, deltavolume), (x, 503, 13, 86))
        # Update black key displays
        clear_blacks()
        for i in range(36):
          j = blackpitches[i]
          h = note[j]['hits']
          if h:
            x = blackxs[i]
            window.fill(rainbow(note[j]['stamp'], elapsed), (x, 263, 7, 53))
            window.fill(rainbow(h, maxhits), (x, 383, 7, 53))
            window.fill(rainbow(note[j]['maxvol'] - minvolume, deltavolume), (x, 503, 7, 53))
        show_shadows()
        # Overlay blue glows onto active keys
        for pitch in range (21, 109):
          if note[pitch]['active']:
            if pitch in whitepitches:
              x = 15 * whitepitches.index(pitch) + 11
              window.blit(wglow, (x, 320))
              window.blit(wglow, (x, 440))
              window.blit(wglow, (x, 560))
            else:
              x = blackxs[blackpitches.index(pitch)]
              window.blit(bglow, (x, 287))
              window.blit(bglow, (x, 407))
              window.blit(bglow, (x, 527))
        for i in [263, 383, 503]:
          pg.display.update((11, i, 780, 86))
    elif e.type in [pg.KEYDOWN]:
      keyname = pg.key.name(e.key)
      if keyname == "space":
        # Stop recording
        recording = False
        clear_whites()
        clear_blacks()
        show_shadows()
        reset_stats()
        pg.display.flip()
      elif keyname == "left":
        # Scroll USB device selection leftward
        update_dev(-1)
        pg.display.flip()
      elif keyname == "right":
        # Scroll USB device selection rightward
        update_dev(1)
        pg.display.flip()
    elif e.type in [pg.QUIT]:
      del idev
      pg.midi.quit()
      sys.exit(0)
  if idev.poll():
    midi_events = idev.read(10)
    # convert them into pg events.
    midi_evs = pg.midi.midis2events(midi_events, idev.device_id)
    for m_e in midi_evs:
      pg.fastevent.post(m_e)
