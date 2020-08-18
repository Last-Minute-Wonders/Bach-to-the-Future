import mido
import time, concurrent.futures
from vlc import MediaPlayer

filename = '.\\tracks\\bach_minuet.midi'

mid = mido.MidiFile(filename)

'''
Goal:
TO CONVERT (ANY) MIDI FILES INTO THE FOLLOWING FORM
1. PRESERVE ACCURATE ABSOLUTE TIME FOR EVERY MIDI MESSAGE
2. ONLY FILTER OUT TOP NOTES (FOR NOW)
3. EVERY NOTE MUST HAVE BEGINNING AND END.
4. COMPILE IT INTO A LIST
'''


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


def notesFilter(mid):
    filter1 = list(filter(lambda x: x.time > 0 or x.type == 'note_on' or x.type == 'note_off', mid))

    abs_time = 0
    for msg in filter1:
        abs_time += msg.time
        msg.time = abs_time  # write over
    filter2 = list(filter(lambda x: not x.is_meta, filter1))  # remove meta_messages

    note_on = list(filter(lambda x: x.type == 'note_on' and x.velocity > 0, filter2))
    note_off = list(filter(lambda x: x.type == 'note_off' or x.velocity == 0, filter2))
    zipped = []
    for i in note_on:
        for j in note_off:
            if j.time >= i.time and i.note == j.note:
                zipped.append((i, j))
                break  # break out of inner loop as pairing is unique.

    # Repackaging for OOP
    result = []
    for _ in zipped:
        start_time = _[0].time
        end_time = _[1].time
        note = _[0].note
        result.append(Note(start_time, end_time, note))

    # Filter out the MELODY (TOP NOTE)
    melody = {}
    for note in result:
        if note.start_time not in melody:
            melody[note.start_time] = note
        elif note.note > melody[note.start_time].note:
            melody[note.start_time] = note
    return list(melody.items())

time_map = notesFilter(mid)

def relativeTime(lst):
    result = [0]
    for i in range(1, len(lst)):
        rel_time = lst[i][0] - lst[i-1][0]
        result.append(rel_time)
    return result

beat_map = relativeTime(time_map)

def play(lst):
    beat = 0
    for i in lst:
        beat += 1
        time.sleep(i)
        print(beat)



def player(filename):
    MediaPlayer(filename).play()


if __name__ == '__main__':
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.submit(player, filename)
        executor.submit(play, beat_map)

# for i in notesFilter(mid).items():
#     print(i)
#     # print(i[0].note == i[1].note, i)
#
# print(mid.length)



