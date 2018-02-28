import pysam

def getRealReadPos(read, offset):

        if read.is_reverse:
            return getBackwardReadPos(read, offset)
        else:
            return getForwardReadPos(read, offset)+1


def getForwardReadPos(read, offset):
    sum = 0
    skip = 0
    indices = range(len(read.cigar))
    pos = read.pos
    for i in indices:
        t = read.cigar[i]

        nextStep = t[1]
        if t[0] == 3 :
            skip += nextStep
        else:
            if sum + nextStep > -offset:
                break
            sum += nextStep

    pos += (-offset + skip)
    return pos

def getBackwardReadPos(read, offset):
    sum = 0
    skip = 0
    indices = range(len(read.cigar)-1,-1,-1)

    pos = read.pos + read.alen

    for i in indices:

        t = read.cigar[i]
        nextStep = t[1]

        if t[0] == 3 :
            skip += nextStep
        else:
            if sum + nextStep > -offset:
                break
            sum += nextStep

    #if(offset!=0):
    #    print(read.cigar)
    pos -= (-offset + skip)

    #print "offset and skip: ", offset , skip
    return pos

def parseRead(read):



        if len(read.cigar) == 1:
            return read.alen, [(read.pos, read.pos+read.alen)], []

        length = 0
        gaps = []
        fills =[]
        currentPos = read.pos

        for t in read.cigar:
            prevPos = currentPos
            currentPos += t[1]
            if t[0] != 3:
                length += t[1]
                fills.append((prevPos, currentPos))
            else:
                gaps.append((prevPos, currentPos))
            currentPos += 1


        return length, fills, gaps

def isMultiMapper(read):

    tags = dict(read.tags)
    if not 'NH' in tags:
        return False
    return tags['NH'] > 1
##############################################################################################

def getPosOnExon(pos, transcript):


    if not (transcript['RNA_min'] <= pos <= transcript['RNA_max']):
        return -2

    for i in range(0, len(transcript['exon_positions'])):
        exon = transcript['exon_positions'][i]
        size = transcript['exon_sizes'][i]
        interval = (exon, exon + size)

        if interval[0] <= pos <= interval[1]:
            return i
    #print(pos, transcript['exon_positions'], transcript['exon_sizes'])
    return -1

def getOnExon(read, transcript, offset):

    realPos = getRealReadPos(read, offset)
    return getPosOnExon(realPos, transcript)

def checInterval(interval, pos):
    if interval[0] <= pos <= interval[1]:
        return 0
    elif pos < interval[0]:
        return -1
    elif interval[1] < pos:
        return 1

def dnatotranscript(dnapos, transcript):
    transcriptpos = 0
    exonIndex = -1
    for i in range(0, len(transcript['exon_positions'])):
        exon = transcript['exon_positions'][i]
        size = transcript['exon_sizes'][i]
        interval = (exon, exon + size)

        if interval[0] <= dnapos <= interval[1]:
            exonIndex = i
            transcriptpos += dnapos - exon
            break
        transcriptpos += size

    if exonIndex < 0:
        return -1
    return transcriptpos

def transcripttodna(transcriptpos, transcript):

    for i in range(0, len(transcript['exon_positions'])):
        exon = transcript['exon_positions'][i]
        size = transcript['exon_sizes'][i]


        next = transcriptpos - size
        if next <= 0:
            return exon + transcriptpos
            break
        transcriptpos -= size

    return -1

def moveOnTranscript(pos, transcript, steps) :

    transcriptpos = dnatotranscript(pos, transcript)
    transcriptpos += steps
    dnapos = transcripttodna(transcriptpos, transcript)

    #if abs(dnapos - pos) != 1:
    #    print pos, dnapos, transcript['transcript_id']
    return dnapos

def getDiffToCDS(read,transcript, offset,compareToMin  = True):
    if compareToMin:
        return getDiffToMinCDS(read, transcript, offset)
    else:
        return getDiffToMaxCDS(read, transcript, offset)
def getDiffToMinCDS(read, transcript, offset):
    realPos = getRealReadPos(read, offset)

    currentExon =getOnExon(read, transcript, offset)
    if currentExon < 0:
        return 4000

    differences = transcript['exon_distances'][currentExon]
    exonPos = transcript['exon_positions'][currentExon]


    diff = 0
    pos =transcript['CDS_min']
    if not transcript['forward']:
        pos =transcript['stop_codon'][1]

    if currentExon == transcript['start_exon']:
        diff = realPos - pos
    else:
        diff = differences[0] + realPos-exonPos

    if not transcript['forward']:
        diff = -diff


    return diff

def getDiffToMaxCDS(read, transcript, offset):
    realPos = getRealReadPos(read, offset)

    currentExon =getOnExon(read, transcript, offset)

    if currentExon < 0:
        return 4000

    differences = transcript['exon_distances'][currentExon]
    exonPos = transcript['exon_positions'][currentExon]
    exonSize = transcript['exon_sizes'][currentExon]

    diff = 0
    pos =transcript['CDS_max']

    if transcript['forward']:
        pos =transcript['stop_codon'][0]




    if currentExon == transcript['start_exon']:
        diff = pos - realPos

    else:
        diff = differences[1] + (exonSize - (realPos-exonPos))

    if  transcript['forward']:
             diff = -diff

    return diff



def getModulatedReadPos(read, gene, offset):

        modPos =  getDiffToCDS(read, gene, offset)

        return modPos % 3
