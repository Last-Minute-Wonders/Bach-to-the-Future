from pretty_midi import PrettyMIDI
import pretty_midi, csv, itertools, time, os
from sys import platform as SYS_PLATFORM
import sys, subprocess

sys.path.append(".\\FluidSynth_Windows")

from os import path

DEFAULT_SOUND_FONT = 'soundfont.sf3'
DEFAULT_SAMPLE_RATE = 44100

class FluidSynth():
	def __init__(self, sound_font=DEFAULT_SOUND_FONT, sample_rate=DEFAULT_SAMPLE_RATE):
		self.sample_rate = sample_rate
		self.sound_font = os.path.expanduser(sound_font)

	def midi_to_audio(self, midi_file, audio_file):
		if SYS_PLATFORM == "win32":
			subprocess.call(['FluidSynth_Windows\\fluidsynth.exe', '-ni', self.sound_font, midi_file, '-F', audio_file, '-r', str(self.sample_rate)])
		else:
			subprocess.call(['fluidsynth', '-ni', self.sound_font, midi_file, '-F', audio_file, '-r', str(self.sample_rate)])

	def play_midi(self, midi_file):
		subprocess.call(['fluidsynth', '-i', self.sound_font, midi_file, '-r', str(self.sample_rate)])

fs = FluidSynth('soundfont.sf3')

def midiInfo(midi_path):
	mid = PrettyMIDI(midi_path)
	instruments = []
	unsaturated_volume = []
	for number, instrument in enumerate(mid.instruments):
		instruments.append(str(number+1) + ') ' + pretty_midi.program_to_instrument_name(instrument.program) + ', ' + instrument.name.strip())
		volume_messages = [msg.value for msg in instrument.control_changes if msg.number == 7]
		if volume_messages and min(volume_messages) > 0:
			unsaturated_volume.append(min(volume_messages))

	if unsaturated_volume:
		unsaturated_volume = min(unsaturated_volume)
		return (instruments, unsaturated_volume)
	return (instruments, 'NO VOL')
	


def midiFunnel(midi_path, quantize, onekey, changeTempo, changeVolume, chosen_instruments):
	directory, name = path.split(midi_path)
	name = name.rsplit('.', 1)[0]
	new_midi_path = path.join('tracks', name + '.mid')

	mid = PrettyMIDI(midi_path)
	mid.remove_invalid_notes()
	average_tempo = mid.estimate_tempo()
	crotchet = 60 / average_tempo
	unit_time = 'NOT QUANTIZED'

	totalInstruments = len(mid.instruments)
	initial_instruments = mid.instruments[0].name
	for i in range(1, totalInstruments):
		if i == totalInstruments - 1:
			initial_instruments += ' and ' + mid.instruments[i].name
		else:
			initial_instruments += ', ' + mid.instruments[i].name
	########################################################################
	if quantize:
		average_tempo = int(round(mid.estimate_tempo(), 3))
		crotchet = 60 / average_tempo
		unit_time = 60 / (average_tempo * quantize)
		for instrument in mid.instruments:
			for note in instrument.notes:
				note.start = note.start // unit_time * unit_time
				duration = note.get_duration() // unit_time * unit_time
				note.end = note.start + duration
	#########################################################################
	if changeVolume or changeTempo != 1:
		for instrument in mid.instruments:
			for msg in instrument.control_changes:
				msg.time *= changeTempo
				if changeVolume and msg.number == 7 and msg.value > 0:
					msg.value = max(min(127, msg.value + changeVolume), 0)
	#########################################################################
	if changeTempo != 1:
		for key_signature in mid.key_signature_changes:
			key_signature.time *= changeTempo
		for time_signature in mid.time_signature_changes:
			time_signature.time *= changeTempo
		for instrument in mid.instruments:
			for pitch_bend in instrument.pitch_bends:
				pitch_bend.time *= changeTempo
			for note in instrument.notes:
				note.start *= changeTempo
				note.end *= changeTempo
		for lyric in mid.lyrics:
			lyric.time *= changeTempo
	#########################################################################
	mid.write(new_midi_path)
	mid = PrettyMIDI(new_midi_path)

	end_time = max(instrument.notes[-1].end for instrument in mid.instruments)
	songLength = time.strftime("%M:%S", time.gmtime(end_time))

	if chosen_instruments:
		for number, instrument in enumerate(mid.instruments.copy()):
			if number not in chosen_instruments:
				mid.instruments.remove(instrument)
	remainingInstruments = len(mid.instruments)
	selected_instruments = pretty_midi.program_to_instrument_name(mid.instruments[0].program)
	for i in range(1, remainingInstruments):
		if i == remainingInstruments - 1:
			selected_instruments += ' and ' + pretty_midi.program_to_instrument_name(mid.instruments[0].program)
		else:
			selected_instruments += ', ' + pretty_midi.program_to_instrument_name(mid.instruments[0].program)

	notes = [x.notes for x in mid.instruments]
	flatten = list(itertools.chain(*notes))

	melody = {}
	for note in flatten:
		if note.start not in melody:
			melody[note.start] = note
		elif note.pitch > melody[note.start].pitch:
			melody[note.start] = note
	melody = list(melody.values())
	print(f'\nNo chords: {len(melody)}\nWith chords: {len(flatten)}')

	if onekey:
		cut_off = 0  # end time of previous note
		for note in melody.copy():
			if note.start < cut_off:
				melody.remove(note)
			else:
				cut_off = note.end
		print(f'Onekey: {len(melody)}')

	csv_rows = [[x.end, x.start, x.get_duration(), x.pitch, x.get_duration() > crotchet] for x in melody]
	totalNotes = len(csv_rows)
	sustainedNotes = 0
	totalSustainDuration = 0
	for row in csv_rows:
		if row[4]:
			sustainedNotes += 1
			totalSustainDuration += row[2]

	info_header = ['totalNotes', 'sustainedNotes', 'totalSustainDuration', \
	               'songLength', 'selected_instruments', 'initial_instruments', 'average_tempo', 'unit_time',
	               'crotchet','songLength_in_seconds']
	info = [totalNotes, sustainedNotes, totalSustainDuration, \
	        songLength, selected_instruments, initial_instruments, average_tempo, unit_time, crotchet, end_time]

	csv_path = path.join('beatmaps', name + '.csv')
	with open(csv_path, 'w', newline='') as file:
		writer = csv.writer(file)
		writer.writerow(info_header)
		writer.writerow(info)
		writer.writerow(['End Time', 'Start Time', 'Duration', 'Pitch', 'Sustained'])
		writer.writerows(csv_rows)
	print('CSV COMPLETE!')

	audio_path = path.join('wav_files', name + '.flac')
	print('STARTING FLAC GENERATION, PLEASE WAIT...')
	if SYS_PLATFORM == "win32":
		from os import environ
		environ["PATH"] += ".\\FluidSynth_Windows"
	fs.midi_to_audio(new_midi_path, audio_path)
	print('FINISHED FLAC GENERATION!')
	
	os.remove(new_midi_path)
