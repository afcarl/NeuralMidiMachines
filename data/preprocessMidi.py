from music21 import *
import numpy as np
import glob
from collections import OrderedDict
import torchfile


def parseMidiFile(fn, keep_rythm=False, transpose_to=None):

    '''Loads a midi file, using music21,
    flattens out the different tracks 
    and saves the results in OrderedDict,
    using the offset (time) as key and the
    values : set(pitch_of_note_1, ...)
     '''

    #load and convert to music21 format
    midi_data = converter.parse(fn)
    
    #if we do not use rythm, we set spacing between each
    #note / chord to 1.
    if not keep_rythm:
        unique_offsets = np.unique([n.offset for n in midi_data.flat.notes])
        offset2discr = {offset:i for i, offset in enumerate(unique_offsets)}

    if transpose_to:
        k = midi_data.analyze('key')
        i = interval.Interval(k.tonic, pitch.Pitch(transpose_to))
        midi_data = midi_data.transpose(i)

    seq = OrderedDict()
    for n in midi_data.flat.notes:
        
        if keep_rythm:
            offset = n.offset
            
        else:
            offset = offset2discr[n.offset]

        seq.setdefault(offset, set())
        if isinstance(n, note.Note):
            seq[offset].add(n.pitch.midi)
        
        #if n is a chord, get each note of n
        elif isinstance(n, chord.Chord):
            for chord_note in n:
                seq[offset].add(chord_note.pitch.midi)

    return seq.items()


def writeMidiFile(fn, seq):
    recons = stream.Part()
    recons.insert(0, instrument.ElectricGuitar())
    i = 0
    for offset, pitches in seq:
        i += 1
        if len(pitches) > 1:
            recons.insert(offset, chord.Chord(pitches))
        else:
            recons.insert(offset, note.Note(list(pitches)[0]))
    
    recons.write('midi', fn)


def writeMidiFileFromTensor(tensor_fn, out_fn):
    
    tensor = torchfile.load(tensor_fn)
    recons = stream.Part()
    recons.insert(0, instrument.ElectricGuitar())

    for offset, notes in enumerate(tensor[0]):
        
        for pitch, volume in enumerate(notes):
            n = note.Note(pitch)
            n.volume = volume
            recons.insert(offset, n)

    recons.write('midi', out_fn)


def parseSeqFile(fn):
    seq = []
    with open(fn, 'r') as f:
        for line in f:
            offset, notes = line.split(':')
            notes = notes.replace('\n', '').split(',')
            notes = [int(n) for n in notes]
            seq.append((int(offset), notes))
    return seq


def writeSeqFile(file, seq):
    for offset, notes in seq:
        line = str(offset)+':'+str(list(notes))[1:-1]+'\n'
        file.write(line)


def main():

    midi_fns = glob.glob('midi/*')
    path = 'seqs_transposed'
    transpose_to = 'C'

    print 'Converting midi files to seq files....'

    error_count = 0
    for i, midi_fn in enumerate(midi_fns):
        
        try:
            print 'Preprocessing file '+str(i)+' of '+str(len(midi_fns))\
                +' '+midi_fn+'...'

            seq = parseMidiFile(midi_fn, keep_rythm=False, transpose_to=transpose_to)

            seq_fn = path + '/' + midi_fn[5:-4] + '.seq'
            
            file = open(seq_fn, 'w')
            writeSeqFile(file, seq)
            file.close()

        except:
            error_count += 1
            print 'Error reading '+midi_fn+' !'

    print 'Preprocessed '+str(i)+' files with '+str(error_count)+' errors!'


    #seqs = []
    #seq_fns = glob.glob('seqs/*')
    #for seq_fn in seq_fns:
    #    seqs.append(parseSeqFile(seq_fn))
    #overlap = 25
    #seq_length = 50
    #
    #batch_file = open('batches.seqs', 'w')
    #
    #batches = []
    #for seq, seq_fn in zip(seqs, seq_fns):
    #    for i in range(0, len(seq) - seq_length + 1, overlap):
    #        batch = seq[i:i + seq_length]
    #        batch_file.write(str(len(batch))+','+seq_fn+'\n')
    #        batches.append(batch)
    #        writeSeqFile(batch_file, batch)
    #
    #print 'Created '+str(len(batches))+' batches.'
    #
    #batch_file.close()
    #print 'Done !'



if __name__ == "__main__":
    main()