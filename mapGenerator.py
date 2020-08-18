import mido, csv
import pygame, time


class Note:  # Specific for mido
	def __init__(self, start_time, end_time, note):
		"""
		:param start_time: absolute time
		:param end_time: absolute time
		:param note: 0-127
        """
		self.start_time = start_time
		self.end_time = end_time
		self.note = note
		self.duration = self.end_time - self.start_time


def trackAnalysis(filename):
	mid = mido.MidiFile(filename)
	no_of_tracks = len(mid.tracks)
	print(f'Track Length: {no_of_tracks}')
	for track in mid.tracks:
		print(track.name)


def beatmapGenerator(filename: str, selected_tracks=(), onekey: bool = False):
	"""
	
	:return list of (relative_time, Note)
	:param filename: path to the MIDI file
	:param selected_tracks: tuple of selected tracks names
	:param onekey: to allow the game to be playable with one finger only, i.e. no time overlap between notes
	"""
	mid = mido.MidiFile(filename)
	
	if selected_tracks:
		for track in mid.tracks.copy():
			if track.name not in selected_tracks:
				mid.tracks.remove(track)
	
	print(mid.tracks)
	
	mid = list(mid)
	
	# 1. Convert the time in ALL messages to absolute time
	abs_time = 0
	for msg in mid:
		abs_time += msg.time
		msg.time = abs_time  # writing over mido
	
	# 2. Filter out note types
	filter1 = list(filter(lambda x: x.type == 'note_on' or x.type == 'note_off', mid))
	
	# 3. Split the list into on and off, before pairing the notes
	note_on = list(filter(lambda x: x.velocity > 0 and x.type == 'note_on', filter1))
	note_off = list(filter(lambda x: x.velocity == 0 or x.type == 'note_off', filter1))
	note_pairs = []
	for i in note_on:
		for j in note_off:
			if j.time > i.time and i.note == j.note:
				note_pairs.append((i, j))
				break

	# Check if any notes were left out
	flatten_note_pairs = [note for pair in note_pairs for note in pair]
	check = (len(flatten_note_pairs) == len(filter1), (len(flatten_note_pairs), len(filter1)))
	print(f'note_pairs length check: {check[1]}')
	assert check[0], 'Some notes were left out during pairing'
	
	# Repackaging as Note instances
	allNotes = []
	for on, off in note_pairs:
		allNotes.append(Note(on.time, off.time, on.note))
	
	'''
    4. Filtering notes out for unique start_time's. If two or more notes have the same start_time,
    the highest note is selected.
    * This is a lazy way to extract out a sensible melody line from most pieces as the top notes 
    often stand out the most and represent the melody
    '''
	melody = {}
	for note in allNotes:
		if note.start_time not in melody:
			melody[note.start_time] = note
		elif note.note > melody[note.start_time].note:
			melody[note.start_time] = note
	melodyNotes = list(melody.values())
	
	# 5. Compiling notes with their relative time.
	def relativeTime(lst):
		result = [(lst[0].start_time, lst[0])]
		for i in range(1, len(lst)):
			rel_time = lst[i].start_time - lst[i - 1].start_time
			result.append((rel_time, lst[i]))
		return result
	
	if onekey:
		ONEKEY = []
		cut_off = 0  # end_time of the last note
		for note in melodyNotes:
			if note.start_time >= cut_off:
				ONEKEY.append(note)
				cut_off = note.end_time
		print(len(ONEKEY))
		return relativeTime(ONEKEY)
	
	return relativeTime(melodyNotes)


filename = '/Users/chence08/PycharmProjects/Bach-to-the-future/Prototype 2/tracks/Mary Had A Little Lamb.midi'
mid = mido.MidiFile(filename)
trackAnalysis(filename)
beatmap = beatmapGenerator(filename, (), True)


with open('beatmaps/Mary Had A Little Lamb.csv', 'w', newline='') as file:
	writer = csv.writer(file)
	writer.writerow(['Relative Time', 'Note', 'Duration', 'Start Time', 'End Time'])
	for a, b in beatmap:
		zero = a
		one = b.note
		two = b.duration
		three = b.start_time
		four = b.end_time
		writer.writerow([zero, one, two, three, four])


NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
NOTES_IN_OCTAVE = len(NOTES)


def number_to_note(number: int) -> tuple:
	assert number >= 0 and number <= 127, "number should be between 0 and 127"
	octave = number // NOTES_IN_OCTAVE - 1
	note = NOTES[number % NOTES_IN_OCTAVE]
	
	return note, octave


def playBeatmap(lst):  # sleep is inaccurate, tends to accumulate delay.
	# count = 0
	for i in lst:
		# count += 1
		time.sleep(i[0])
		print(number_to_note(i[1].note))
		# print(count)
	time.sleep(5)

# if __name__ == '__main__':
#
# 	pygame.mixer.init()
# 	pygame.mixer.music.load('/Users/chence08/PycharmProjects/Bach-to-the-future/Prototype 2/wav_files/Blue Danube Waltz.wav')
# 	pygame.mixer.music.play()
#
#
# 	playBeatmap(beatmap)
