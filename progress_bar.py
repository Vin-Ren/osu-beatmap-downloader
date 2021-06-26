# https://gist.github.com/rougier/c0d31f5cbdaac27b876c
# -----------------------------------------------------------------------------
# Copyright (c) 2016, Nicolas P. Rougier
# Distributed under the (new) BSD License.
# -----------------------------------------------------------------------------
import sys, math


def make_simple_progress(progress, max, length, prefix="", suffix=""):
	value = progress/max
	filled = math.floor(value*(length-2))
	empty = length-2-filled
	progressbar = f"\r{prefix}[{'█'*filled}{' '*empty}]{value*100:.1f}%{suffix}"
	return progressbar


def make_progress(value, length=40, title = " ", vmin=0.0, vmax=1.0, prefix="", suffix=""):
	"""
	Text progress bar
	Parameters
	----------
	value : float
		Current value to be displayed as progress
	vmin : float
		Minimum value
	vmax : float
		Maximum value
	length: int
		Bar length (in character)
	title: string
		Text to be prepend to the bar
	"""
	# Block progression is 1/8
	blocks = ["", "▏","▎","▍","▌","▋","▊","▉","█"]
	vmin = vmin or 0.0
	vmax = vmax or 1.0
	lsep, rsep = "▏", "▕"

	# Normalize value
	value = min(max(value, vmin), vmax)
	value = (value-vmin)/float(vmax-vmin)

	v = value*length
	x = math.floor(v) # integer part
	y = v - x         # fractional part
	base = 0.125      # 0.125 = 1/8
	prec = 3
	i = int(round(base*math.floor(float(y)/base),prec)/base)
	bar = "█"*x + blocks[i]
	n = length-len(bar)
	bar = lsep + bar + " "*n + rsep
	return f"\r{title}{prefix}{bar}{value*100:.1f}%{suffix}"


def progress(value,  length=40, title = " ", vmin=0.0, vmax=1.0):
	"""
	Text progress bar
	Parameters
	----------
	value : float
		Current value to be displayed as progress
	vmin : float
		Minimum value
	vmax : float
		Maximum value
	length: int
		Bar length (in character)
	title: string
		Text to be prepend to the bar
	"""
	# Block progression is 1/8
	blocks = ["", "▏","▎","▍","▌","▋","▊","▉","█"]
	vmin = vmin or 0.0
	vmax = vmax or 1.0
	lsep, rsep = "▏", "▕"

	# Normalize value
	value = min(max(value, vmin), vmax)
	value = (value-vmin)/float(vmax-vmin)

	v = value*length
	x = math.floor(v) # integer part
	y = v - x         # fractional part
	base = 0.125      # 0.125 = 1/8
	prec = 3
	i = int(round(base*math.floor(float(y)/base),prec)/base)
	bar = "█"*x + blocks[i]
	n = length-len(bar)
	bar = lsep + bar + " "*n + rsep

	sys.stdout.write("\r" + title + bar + " %.1f%%" % (value*100))
	sys.stdout.flush()


# -----------------------------------------------------------------------------
if __name__ == '__main__':
	import time

	for i in range(1000):
		print(make_progress(i, vmin=0, vmax=999), end='')
		#progress(i, vmin=0, vmax=999)
		time.sleep(0.005)
	sys.stdout.write("\n")