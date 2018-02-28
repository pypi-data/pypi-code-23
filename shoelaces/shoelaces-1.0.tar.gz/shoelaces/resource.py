from shoelaces.dataprocessing import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

#import statsmodule
from xml.dom import minidom

class Resource(QObject):

    dataLoaded = pyqtSignal(str)
    transcriptLoaded = pyqtSignal(str)
    configLoaded = pyqtSignal(str)

    processStarted = pyqtSignal(int, str)
    processUpdated = pyqtSignal(int)
    processFinished = pyqtSignal(int)

    def __init__(self, name, type, ext):
        #QObject.__init__(self)
        super(Resource, self).__init__()
        self.name = name
        self.type = type
        self.ext = ext

    def GetName(self):
        return self.name

    def GetType(self):
        return self.type

    def GetFileEXT(self):

        return self.ext

    def load(self):
        pass


class SequenceResource(Resource):
    def __init__(self, filename):
        super(SequenceResource, self).__init__(filename, "SequenceResource", "bam")

        self.samfile = None
        self.datafile = filename
        self.openDatafile(filename)
        self.splitWig = {}
        self.forwardWig = {}
        self.reverseWig = {}
        self.offsets = {}
        self.updateWig = True
        self.noise = None
        self.noiseIntervals = {}
        self.useOffsets = False
        self.multimappers = 0


    def __del__(self):
        if self.samfile:
            self.samfile.close()

    def openDatafile(self, filename):
        try:
            #print("Opening file ", filename)
            self.samfile = pysam.Samfile(filename)

        except IOError:
            print( 'File not found')
            self.__del__()

        self.dataLoaded.emit(filename)

    def fetch(self, chromosome=None, start=None, end=None):

        try:
            sequences = list(self.samfile.fetch(chromosome, start, end))
        except ValueError:
            print("Error fetching reads!", chromosome, start, end)
            sequences = []
        return sequences

    def count(self, chromosome=None, start=None, end=None):

        try:
            return self.samfile.count(chromosome, start, end)
        except :
            print("Error counting reads!", chromosome, start, end)
            return -1

    def sumWig(self, inputWig, lengths = []):
        result = {}
        for length, wig in inputWig.items():
            if lengths and not length in lengths:
                continue

            for chromosome, hist in wig.items():
                try:
                    result[chromosome]
                except KeyError:
                    result[chromosome] = hist.copy()

                    continue

                for pos, count, in hist.items():
                    try:
                        result[chromosome][pos] += count
                    except KeyError:
                        result[chromosome][pos] = count

        return result

    def createSplitWig(self, offsets):

        sum = 0;

        forward = {}
        reverse = {}

        multimappers = 0;
        refs = self.samfile.references
        refCount = self.samfile.nreferences
        self.processStarted.emit(refCount, "Creating wig")
        progress = 0;
        for ref in refs:
            #print(ref);
            self.processUpdated.emit(progress)
            progress+=1
            try:
                for ba in self.samfile.fetch(ref):
                    mm = isMultiMapper(ba)
                    if mm :

                        multimappers += 1
                        sum +=1
                        continue;


                    if (ba.is_reverse):

                        pyAll = reverse;

                    else:

                        pyAll = forward;



                    length = ba.infer_query_length();
                    try:
                        pCurrentLengthWig =pyAll[length]
                    except:
                        pyAll[length] = {}
                        pCurrentLengthWig =pyAll[length]

                    try:
                        hist  = pCurrentLengthWig[ ref]
                    except:
                        pCurrentLengthWig[ref] = {}
                        hist = pCurrentLengthWig[ref]


                    try:
                        offset = offsets[length];
                    except:
                        offset = 0;
                    position = getRealReadPos(ba, offset);

                    try:
                        hist[position] += 1
                    except:
                        hist[position] = 1

                    sum +=1
            except:
                print("Error reading bam-file")


        self.processFinished.emit(progress)



        Result = {};
        Result['forward'] = forward
        Result['reverse'] = reverse
        Result['multimappers'] = multimappers

        return Result;

    def createWig(self):



        if (self.updateWig):

            self.reset()
            lengths = []
            offsets = {}
            if self.useOffsets:
                lengths = self.offsets.keys()
                offsets = self.offsets
            #print("Updating wig... Offsets: ", offsets, " Lengths: ", lengths)
            self.splitWig = self.createSplitWig(offsets)
            self.forwardWig = self.sumWig(self.splitWig['forward'], lengths)
            self.reverseWig = self.sumWig(self.splitWig['reverse'], lengths)
            self.multimappers = self.splitWig['multimappers']
            self.updateWig = False

    def GetWig(self, strain, length=0):
        if not length:
            if strain == 'forward':
                return self.forwardWig
            else:
                return self.reverseWig
        else:
            try:
                return self.splitWig[strain][length]
            except KeyError:
                return {}

    def setWig(self, wig, strain, length=0):
        if not length:
            if strain == 'forward':
                self.forwardWig = wig
            else:
                self.reverseWig = wig
        else:
            try:
                self.splitWig[strain][length] = wig
            except KeyError:
                pass

    def setOffsets(self, offsets):
        if offsets != self.offsets:
            self.offsets = offsets.copy()
            self.updateWig = True

    def setUseOffsets(self, useOffsets):
        if useOffsets != self.useOffsets:
            self.updateWig = True
        self.useOffsets = useOffsets

    def reset(self):
        self.forwardWig = {}
        self.reverseWig = {}
        self.splitWig = {}
        self.updateWig = True
        #self.name.replace('-filtered', '')

    def setNoise(self, res):
        self.updateWig = True
        if not res:
            self.noise = None
            self.noiseIntervals = {}
            return

        if res.GetType() == 'TranscriptResource':
            self.noise = res
            self.processNoise()

    def processNoise(self):
        if not self.noise:
            return
        self.noiseIntervals = {}
        for name, transcript in self.noise.transcripts.items():
            chr = transcript['chromosome']
            try:
                self.noiseIntervals[chr]
            except KeyError:
                self.noiseIntervals[chr] = []
            for start, size in zip(transcript['exon_positions'], transcript['exon_sizes']):
                self.noiseIntervals[chr].append((start, start+size))

        for chr in self.noiseIntervals:
            #print(chr)
            self.noiseIntervals[chr].sort(key=lambda i: i[0])


    def isNoise(self, pos):
        for chr, intervals in self.noiseIntervals.items():
            for (start, end) in intervals:
                if start <= pos <= end:
                    return True
        return False

    def filterWig(self, wig):
        #print(self.noiseIntervals)
        #print(self.noise.transcripts['ENSDART00000079692']['exon_positions'])
        #print(self.noise.transcripts['ENSDART00000079692']['exon_sizes'])


        for chr, intervals in self.noiseIntervals.items():
            for (start, end) in intervals:
                for pos in range(start, end+1):
                    try:
                        del wig[chr][pos]
                    except KeyError:
                        pass

    def filter(self):
        #print( 'filtering')
        self.createWig()

        self.processStarted.emit(len(self.splitWig['forward'].items() ) + len(self.splitWig['reverse'].items() ),"Loading Transcript File")
        progress = 0
        for length, wig in self.splitWig['forward'].items():
            self.processUpdated.emit(progress)
            progress += 1
            self.filterWig(wig)

        self.forwardWig = self.sumWig(self.splitWig['forward'])

        for length, wig in self.splitWig['reverse'].items():
            self.processUpdated.emit(progress)
            progress += 1
            self.filterWig(wig)
        self.reverseWig = self.sumWig(self.splitWig['reverse'])

        #self.name = self.name + '-filtered'

        self.processFinished.emit(progress)


class TranscriptResource(Resource):
    def __init__(self, filename, ext):
        super(TranscriptResource, self).__init__(filename, "TranscriptResource", "gtf")
        self.transcripts = {}
        self.genes = {}
        self.chromosomes = {}
        self.lengthOffsets = {}
        self.noncodingtranscripts = {}
        self.ext = ext

    def load(self):
        self.openTranscriptFile(self.name,self.ext)

    def openTranscriptFile(self, filename, ext):
        if ext == 'bed':
            self.parseBedFile(filename)

        elif ext == 'gtf':
            self.parseGTFFile(filename)
        self.transcriptfile = filename

        self.transcriptLoaded.emit(filename)

    def addReadsToGene(self, sequenceData):
        if not sequenceData:
            for geneName, gene in self.genes.items():
                gene['NoR'] = 0
                gene['reads'] = []
            return



        progress = 0
        #print("adding reads to genes", len(self.genes.keys()))
        self.processStarted.emit(len(self.genes.keys()),"Adding Reads to Genes")
        for geneName, gene in self.genes.items():


            self.processUpdated.emit(progress)
            progress += 1

            fetchStart = gene['RNA_min']
            fetchEnd = gene['RNA_max']
            chromosome = gene['chromosome']

            try:
                nor = sequenceData.count(chromosome, fetchStart, fetchEnd)
            except ValueError:
                reads = []
            gene['NoR'] = nor
            gene['reads'] = []
        self.processFinished.emit(0)
        #print("Finished")

    def parseBedLine(self, bedLine):
        elements = bedLine.split()
        if (len(elements) != 12):
            return '',{}
        result = {'chromosome': elements[0]}
        transcript = elements[3]
        forward = elements[5] == '+'
        result['forward'] = forward
        result['CDS_min'] = eval(elements[6])
        result['CDS_max'] = eval(elements[7])
        result['RNA_min'] = eval(elements[1])
        result['RNA_max'] = eval(elements[2])

        nrOfExons = eval(elements[9])
        exonSizes = [eval(x) for x, i in zip(elements[10].split(','), range(0, nrOfExons))]
        exonRelPos = [eval(x) for x, i in zip(elements[11].split(','), range(0, nrOfExons))]

        exonPos = []
        differences = []

        currentSum = 0
        transcriptLength = sum(exonSizes)
        for ePos, eSize in zip(exonRelPos, exonSizes):
            exonPos.append(result['RNA_min'] + ePos)
            differences.append((currentSum, transcriptLength-(currentSum +eSize)))
            currentSum += eSize

        #detect valid transcripts
        maxIndex = 0
        minIndex = 0
        gapToCDSmin = 0
        gapToCDSMax = 0
        transcriptLength = 0
        for i in range(0, nrOfExons):

            if exonPos[i] + exonSizes[i] > result['CDS_min'] >= exonPos[i]:
                minIndex = i
            if exonPos[i] + exonSizes[i] > result['CDS_max'] >= exonPos[i]:
                maxIndex = i
            transcriptLength += exonSizes[i]

        result['transcript_length'] = transcriptLength

        for i in range(minIndex):
            gapToCDSmin += exonSizes[i]
        gapToCDSmin += result['CDS_min'] - exonPos[minIndex]
        for i in range(len(exonSizes)-1, maxIndex, -1):
            gapToCDSMax += exonSizes[i]
        gapToCDSMax += exonPos[maxIndex] + exonSizes[maxIndex] - result['CDS_max']

        differences = [(differences[i][0] - gapToCDSmin, differences[i][1] - gapToCDSMax) for i in range(nrOfExons)]

        if forward:
            distances = [(e[0], e[1] - 2) for e in differences ]
            result['start_exon'] = minIndex
            result['end_exon'] = maxIndex
        else:
            distances = [(e[0] - 2, e[1]) for e in differences ]
            result['start_exon'] = maxIndex
            result['end_exon'] = minIndex

        result['exon_sizes'] = exonSizes
        result['exon_positions'] = exonPos
        result['exon_distances'] = distances
        result['gene_id'] = ''
        result['transcript_id'] = transcript
        result['include'] = True

        return transcript, result

    def parseBedFile(self, bedFilename):
        bedFile = open(bedFilename, 'r')
        self.transcripts = {}
        self.genes = {}
        self.chromosomes = []

        self.processStarted.emit(len(bedFile.readlines()),"Loading Transcript File")


        bedFile = open(bedFilename, 'r')

        for i, line in enumerate(bedFile.readlines()):
            self.processUpdated.emit(i)
            transcript, result = self.parseBedLine(line)

            if result:
                self.transcripts[transcript] = result

                if not(result['chromosome'] in self.chromosomes):
                    self.chromosomes[result['chromosome']] = [result]
                else:
                    self.chromosomes[result['chromosome']].append(result)
        self.processFinished.emit(0)

    def parseGTFLine(self, line):
        if len(line) == 0:
            return {}
        elif not line.find('#') == -1:
            return {}
        result = {}
        input = line.split('\t')

        result['chromosome'] = input[0]
        result['input_type'] = input[1]
        result['type'] = input[2]
        result['start'] = int(input[3])
        result['end'] = int(input[4])
        result['direction'] = input[6] == '+'
        # if result['direction']:
        #     result['start'] -= 1;
        #     result['end'] -= 1;
        # else:
        #     result['start'] -= 1;
            #result['end'] -= 1;
        attributes = input[8].split(';')
        for attribute in attributes:
            s = attribute.split()
            if len(s) > 1:
                result[s[0]] = s[1].strip("\"")

        if 'exon_number' not in result:
            result['exon_number'] = -1


        return result

    def detectValidTranscript(self, transcript):


        nrOfExons = len(transcript['exon_sizes'])
        transcript['exon_sizes'] = [x for (y,x) in sorted(zip(transcript['exon_positions'], transcript['exon_sizes']), key=lambda pair: pair[0])]
        transcript['exon_positions'] = sorted(transcript['exon_positions'])
        #print transcript['exon_positions']
        if transcript['CDS_max'] < transcript['CDS_min']:

            return False


        iMin = getPosOnExon(transcript['CDS_min'], transcript)
        iMax = getPosOnExon(transcript['CDS_max'], transcript)



        if iMin < 0 or iMax < 0:
            return False



        transcript['end_exon'] = iMax
        transcript['start_exon'] = iMin

        minIndex = transcript['start_exon']
        maxIndex = transcript['end_exon']



        if transcript['forward']:
            if 'stop_codon' in transcript:
                e = moveOnTranscript(transcript['stop_codon'][0],transcript, -1)
                transcript['CDS_max'] = e
        else:
             if 'stop_codon' in transcript:
                e = moveOnTranscript(transcript['stop_codon'][1],transcript, +1)
                transcript['CDS_min'] = e

        totalLength = sum(transcript['exon_sizes'])
        fromStart = 0
        fromEnd = totalLength
        distances = []


        transcriptLength = 0
        for s in transcript['exon_sizes']:
            distances.append((fromStart, fromEnd-s))
            fromStart += s
            fromEnd -= s
            transcriptLength += s
        transcript['transcript_length'] = transcriptLength

        CDSLength = sum(transcript['exon_sizes'][iMin:iMax])
        CDSLength -= transcript['CDS_min'] - transcript['exon_positions'][iMin]
        CDSLength += transcript['CDS_max'] - transcript['exon_positions'][iMax]
        transcript['CDS_length'] = CDSLength
        transcript['start_exon'] = minIndex
        minExonPos = transcript['exon_positions'][minIndex]

        minDiffPos = transcript['CDS_min']

        maxDiffPos = transcript['CDS_max']
        if (transcript['forward'] and 'stop_codon' in transcript):
            maxDiffPos = transcript['stop_codon'][0]

        elif 'stop_codon' in transcript:
            minDiffPos = transcript['stop_codon'][1]
            transcript['start_exon'] = iMax
            transcript['end_exon'] =  iMin
        gapToCDSmin = distances[minIndex][0] + minDiffPos - minExonPos


        maxExonPos = transcript['exon_positions'][maxIndex] + transcript['exon_sizes'][maxIndex]

        gapToCDSmax = distances[maxIndex][1] + maxExonPos - maxDiffPos


        moddeddistances = [(e[0] - gapToCDSmin, e[1] - gapToCDSmax) for e in distances ]
        if transcript['forward']:
            distances = [(e[0]+1,  e[1]) for e in moddeddistances ]
        else:
            distances = [(e[0] , e[1]+1) for e in moddeddistances ]

        transcript['exon_distances'] = distances

        return True

    def parseGTFFile(self, gtfFileName):


        self.transcripts = {}
        self.genes = {}
        self.chromosomes = {}
        currentGene = {}

        currentTranscript = {}
        #hasStart = False
        #hasFinish = False




        gtfFile = open(gtfFileName, 'r')

        self.processStarted.emit(len(gtfFile.readlines()),"Loading Transcript File")
        gtfFile = open(gtfFileName, 'r')

        acceptedTypes = ['ensembl_havana', 'ensembl', 'havana','protein_coding','mm9_ensGene']



        for i, line in enumerate(gtfFile.readlines()):

            entry = self.parseGTFLine(line)

            self.processUpdated.emit(i)

            #if not entry or not entry['input_type'] in acceptedTypes:
            if not entry:
                continue
            current = {}

            geneID = entry['gene_id']
            transcriptID = None
            if not entry['type'] == 'gene':
                transcriptID = entry['transcript_id']




            current['gene_id'] = geneID
            current['chromosome'] = entry['chromosome']
            current['forward'] = entry['direction']
            current['RNA_min'] = int(entry['start'])
            current['RNA_max'] = int(entry['end'])

            if not geneID in self.genes:
                currentGene = {}
                currentGene['transcripts'] = {}
                currentGene['non_coding'] = {}
                currentGene['chromosome'] = current['chromosome']
                currentGene['NoR'] = 0
                currentGene['NoT'] = 0
                currentGene['reads'] = []
                currentGene['include'] = True
                currentGene['forward'] = entry['direction']
                currentGene['RNA_min'] = int(entry['start'])
                currentGene['RNA_max'] = int(entry['end'])
                currentGene['gene_id'] = geneID

                self.genes[geneID] = currentGene
            else:
                currentGene = self.genes[geneID]

            if transcriptID and not transcriptID in self.transcripts:
                currentTranscript = {}
                currentTranscript['chromosome'] = current['chromosome']
                currentTranscript['include'] = True
                currentTranscript['forward'] = entry['direction']
                currentTranscript['RNA_min'] = current['RNA_min']
                currentTranscript['RNA_max'] = current['RNA_max']
                currentTranscript['CDS_min'] = current['RNA_max']
                currentTranscript['CDS_max'] = current['RNA_min']
                currentTranscript['start_exon'] = 10000
                currentTranscript['end_exon'] = -1
                currentTranscript['exon_sizes'] = []
                currentTranscript['exon_positions'] = []
                currentTranscript['exon_distances'] = []
                currentTranscript['include'] = True
                currentTranscript['gene_id'] = geneID
                currentTranscript['transcript_id'] = transcriptID
                self.transcripts[transcriptID] = currentTranscript
            elif transcriptID:
                currentTranscript = self.transcripts[transcriptID]


            if entry['type'] == 'exon':
                currentTranscript['exon_sizes'].append(current['RNA_max'] - current['RNA_min'] )
                currentTranscript['exon_positions'].append(current['RNA_min'])
                currentTranscript['RNA_min'] = min(current['RNA_min'], currentTranscript['RNA_min'])
                currentTranscript['RNA_max'] = max(current['RNA_max'], currentTranscript['RNA_max'])

            elif entry['type'] == 'start_codon':
                if not 'start_codon' in currentTranscript:
                    currentTranscript['start_codon'] = [current['RNA_min'], current['RNA_max']]
                else:
                    currentTranscript['start_codon'][0] = min(currentTranscript['start_codon'][0], current['RNA_min'])
                    currentTranscript['start_codon'][1] = max(currentTranscript['start_codon'][1], current['RNA_max'])
            elif entry['type'] == 'stop_codon':
                if not 'stop_codon' in currentTranscript:
                    currentTranscript['stop_codon'] = [current['RNA_min'], current['RNA_max']]
                else:
                    currentTranscript['stop_codon'][0] = min(currentTranscript['stop_codon'][0], current['RNA_min'])
                    currentTranscript['stop_codon'][1] = max(currentTranscript['stop_codon'][1], current['RNA_max'])


            elif entry['type'] == 'CDS':
                currentTranscript['start_exon'] = min(int(entry['exon_number'])-1, currentTranscript['start_exon'])
                currentTranscript['end_exon'] = max(int(entry['exon_number'])-1, currentTranscript['end_exon'])
                currentTranscript['CDS_min'] = min(current['RNA_min'], currentTranscript['CDS_min'])
                currentTranscript['CDS_max'] = max(current['RNA_max'], currentTranscript['CDS_max'])

            elif entry['type'] == 'gene':
                currentGene['RNA_min'] = int(entry['start'])
                currentGene['RNA_max'] = int(entry['end'])


            elif entry['type'] == 'transcript':
                currentTranscript['RNA_min'] = current['RNA_min']
                currentTranscript['RNA_max'] = current['RNA_max']

        removal = []
        for transcriptID, transcript in self.transcripts.items():
            #print(transcriptID)
            if self.detectValidTranscript(transcript):
                if not 'stop_codon' in transcript or not 'start_codon' in transcript:
                    removal.append(transcriptID)
                    print("not stop or start codon on ", transcriptID)


                g = transcript['gene_id']
                transcript['non_coding'] = False

                if not transcript['chromosome'] in self.chromosomes:
                    self.chromosomes[transcript['chromosome']] = [transcript]
                else:
                    self.chromosomes[transcript['chromosome']].append(transcript)

                try:
                    self.genes[g]['transcripts'][transcriptID] = transcript
                    self.genes[g]['NoT'] += 1
                except KeyError:
                    pass
            else:
                transcript['non_coding'] = True
                self.noncodingtranscripts[transcriptID] = transcript
                removal.append(transcriptID)

        print("Non-coding transcripts: ", len(self.noncodingtranscripts.items()))
        for transcriptID in removal:
            try:
                if 'gene_id' in self.transcripts[transcriptID]:
                    gene = self.genes[self.transcripts[transcriptID]['gene_id']]
                    gene['non_coding'][transcriptID] = self.transcripts[transcriptID]
                    del gene['transcripts'][transcriptID]


            except KeyError:
                pass

            self.transcripts.__delitem__(transcriptID)


        gtfFile.close()

        self.processFinished.emit(0)

    def gettranscript(self,name):
        return self.transcripts[name]

    def __getitem__(self, name):
        return self.transcripts[name]


class ConfigResource(Resource):
    def __init__(self, filename='temp.xml'):
        super(ConfigResource, self).__init__(filename, "ConfigResource", "xml")
        self.filename = filename
        self.resources = {}
        self.activeTranscript = None
        self.activeSequence = None
        self.activeNoise = None
        self.lengthOffsets = {}
        self.disabled = []
        self.currentRatio = 0.1

    def write(self):

        #print(self.lengthOffsets)
        f = open(self.filename, 'w')
        f.write("<config>\n")
        f.write("<offsets>\n")
        for len in self.lengthOffsets:
            f.write('\t<offset length=\"'+str(len)+ '\" value=\"' + str(self.lengthOffsets[len])+'\"></offset>\n')
        f.write("</offsets>\n")

        f.write("<ratios>\n")
        f.write('\t<ratio value=\"' + str(self.currentRatio) +'\"></ratio>\n')
        f.write("</ratios>\n")
        f.write("<files>\n")
        for name, res in self.resources.items():
            f.write('\t<file filetype=\"'+ res.GetType()+ '\"' +  ' name=\"' + name+'\"></file>\n')

        if self.activeTranscript:
            f.write('\t<file filetype=\"ActiveTranscript\"' +  ' name=\"' + self.activeTranscript.GetName()+'\"></file>\n')
        if self.activeSequence:
            f.write('\t<file filetype=\"ActiveSequence\"' +  ' name=\"' + self.activeSequence.GetName()+'\"></file>\n')
        if self.activeNoise:
            f.write('\t<file filetype=\"ActiveNoise\"' +  ' name=\"' + self.activeNoise.GetName()+'\"></file>\n')
        f.write("</files>\n")
        f.write("<disabled>\n")
        for resName, res in self.resources.items():
            if res.GetType() == 'TranscriptResource':
                for name, transcript in res.transcripts.items():

                    if not transcript['include']:
                        f.write('\t<transcript name=\"' + name+'\" resource=\"' + resName +  '\"></transcript>\n')



        f.write("</disabled>\n")
        f.write("</config>\n")
        f.close()

    def load(self):
        try:
            xmldoc = minidom.parse(self.filename)
        except IOError:
            print ('File not found')

            return

        for offset in xmldoc.getElementsByTagName('offset'):
            self.setOffset(int(offset.attributes['length'].value), int(offset.attributes['value'].value))
        for file in xmldoc.getElementsByTagName('file'):
            #print file
            filetype = file.attributes['filetype'].value

            filename = file.attributes['name'].value
            elements = filename.split('.')
            ext = elements[len(elements) - 1].lower()
            if filetype == 'TranscriptResource':
                res = TranscriptResource(filename, ext)
                self.resources[filename] = res
            elif filetype == 'SequenceResource':
                res = SequenceResource(filename)
                self.resources[filename] = res

            elif filetype == 'ActiveTranscript':
                self.activeTranscript = self.resources[filename]
            elif filetype == 'ActiveSequence':
                self.activeSequence = self.resources[filename]
            elif filetype == 'ActiveNoise':
                self.activeNoise = self.resources[filename]
        if self.activeTranscript:
            for transcript in xmldoc.getElementsByTagName('transcript'):
                name = transcript.attributes['name'].value
                try:
                    self.activeTranscript.transcripts[name]['include'] = False

                except KeyError:
                    print('can not find transcript', name)


        for e in xmldoc.getElementsByTagName('ratio'):
            self.currentRatio = float(e.attributes['value'].value)

        for disabled in xmldoc.getElementsByTagName('disabled'):
            for transcript  in disabled.getElementsByTagName('transcript'):

                self.disabled.append((transcript.attributes['name'].value, transcript.attributes['resource'].value))





    def setOffset(self,length, offset):
        self.lengthOffsets[length] = offset


class resourceItemDelegate(QStyledItemDelegate):
    def __init__(self, resources, Parent = None):
        super(resourceItemDelegate, self).__init__(Parent)
        self.resources = resources

    def paint(self, painter, option, index):

        painter.save()

        name = str(index.data(Qt.DisplayRole))
        res = self.resources[name]
        splitName = name.split('/')

        recItem = option.rect.adjusted(1,1,-2,-2)
        recHighlight = QRect(recItem.x(),recItem.y(),recItem.width(),recItem.height()/2).adjusted(1,1,-2,-2)
        recButton = recItem.adjusted(1,1,-1,-1)
        recText = recButton.adjusted(8,2,-8-24-4,-2)

        fRoundness = 3.0
        fOpacity = 1.0

        colColor = QColor(Qt.gray)

        painter.setRenderHint(QPainter.Antialiasing)

        if (option.state & QStyle.State_Selected):

            colColor = QColor(Qt.blue).lighter()
            painter.setPen(QPen(QBrush(Qt.white), 4.0))
            outline = QPainterPath()
            outline.addRoundedRect(QRectF(recButton), fRoundness, fRoundness,Qt.AbsoluteSize)
            painter.setOpacity(fOpacity*0.75)
            painter.drawPath(outline)
        elif(index.data(Qt.WhatsThisRole)):
            colColor = QColor(Qt.red).lighter()
            painter.setPen(QPen(QBrush(Qt.white), 4.0))
            outline = QPainterPath()
            outline.addRoundedRect(QRectF(recButton), fRoundness, fRoundness,Qt.AbsoluteSize)
            painter.setOpacity(fOpacity*0.75)
            painter.drawPath(outline)


        colHighlight = QColor(colColor.lighter())
        colShadow = QColor(colColor.darker())

        painter.setPen(QPen(QBrush(Qt.black), 2.0))

        outline = QPainterPath()
        outline.addRoundedRect(QRectF(recButton), fRoundness, fRoundness,Qt.AbsoluteSize)
        painter.setOpacity(fOpacity)
        painter.drawPath(outline)

        gradient = QLinearGradient(0, 0, 0, 1)
        gradient.setCoordinateMode(QGradient.ObjectBoundingMode)
        gradient.setSpread(QGradient.ReflectSpread)
        gradient.setColorAt(0.0, colColor)
        gradient.setColorAt(0.4, colColor)
        gradient.setColorAt(0.6, colColor)
        gradient.setColorAt(1.0, colColor)

        brush = QBrush(gradient)
        painter.setBrush(brush)
        painter.setPen(QPen(QBrush(colColor), 2.0))

        path = QPainterPath()
        path.addRoundedRect(QRectF(recButton), fRoundness, fRoundness,Qt.AbsoluteSize)
        painter.setClipPath(path)

        painter.setOpacity(fOpacity)
        painter.drawRoundedRect(QRectF(recButton), fRoundness, fRoundness,Qt.AbsoluteSize)

        painter.setBrush(QBrush(Qt.white))
        painter.setPen(QPen(QBrush(Qt.white), 0.01))
        painter.setOpacity(0.30)
        painter.drawRect(recHighlight)

        fonName = option.font
        fonInfo = fonName
        fonInfo.setPointSize(fonName.pointSize())

        iNameTextFlags = Qt.AlignLeft
        iInfoTextFlags = Qt.AlignLeft

        recNameText =QRect()
        recInfoText = QRect()

        strNameText = splitName[len(splitName)-1]


        strInfoText = res.GetType()#name.replace(splitName[len(splitName)-1],'')

        fmName = QFontMetrics (fonName)
        recNameText = fmName.boundingRect(recText,iNameTextFlags,strNameText)

        fmInfo = QFontMetrics (fonInfo)
        recInfoText = fmInfo.boundingRect(recText.adjusted(0,fmName.lineSpacing(),0,0),iInfoTextFlags,strInfoText)

        recTotalText = recNameText.united(recInfoText)
        fOffset = max(0.0,recText.height()-recTotalText.height())*0.5
        recNameText.translate(0.0,fOffset)
        recInfoText.translate(0.0,fOffset)


        strNameText = fmName.elidedText(strNameText,Qt.ElideRight,recText.width())
        strInfoText = fmName.elidedText(strInfoText,Qt.ElideRight,recText.width())

        painter.setFont(fonName)
        painter.setPen(Qt.white)
        painter.setOpacity(1.0)
        painter.drawText(recNameText, iNameTextFlags, strNameText)

        painter.setFont(fonInfo)
        painter.setPen(Qt.white)
        painter.setOpacity(1.0)
        painter.drawText(recInfoText, iInfoTextFlags, strInfoText)

        painter.restore()



    def sizeHint (self, option, index ):
        return QStyledItemDelegate.sizeHint(self, option, index).expandedTo(QSize(48,48))


class resourceDock(QDockWidget):

    selected = pyqtSignal(Resource)
    useTranscriptResource = pyqtSignal(Resource)
    useSequenceResource = pyqtSignal(Resource)
    useNoiseResource = pyqtSignal(Resource)


    def __init__(self, parent = None):
        super(resourceDock, self).__init__(parent)
        self.resources = {}
        self.activeTranscriptResource = None
        self.activeSequenceResource = None
        self.activeConfigResource = None
        self.noiseResource = None
        self.mainWidget = QWidget(self)
        self.mainLayout = QVBoxLayout(self.mainWidget)

        self.resourceView = QListView(self.mainWidget)
        self.resourceView.setAutoFillBackground(True)
        self.resourceView.setWordWrap(True)


        model = QStandardItemModel(self.resourceView)
        self.resourceView.setModel(model)
        self.resourceView.setItemDelegate(resourceItemDelegate(self.resources, self.resourceView))


        self.resourceView.setSelectionMode(QAbstractItemView.MultiSelection)
        self.resourceView.clicked.connect(self.resourceSelected)
        self.resourceView.pressed.connect(self.setCurrentIndex)
        self.resourceView.setContextMenuPolicy(Qt.CustomContextMenu);
        self.resourceView.customContextMenuRequested.connect(self.showContextMenu)

        self.mainLayout.addWidget(self.resourceView)
        self.mainWidget.setLayout(self.mainLayout)


        self.setWidget(self.mainWidget)
        self.setWindowTitle("Resources")

        self.currentResource = None


    def setCurrentIndex(self,index):

        key = str(index.data(Qt.DisplayRole))
        try:
            self.currentResource = self.resources[key]
        except KeyError:
            pass

    def clearSelection(self):
        self.resourceView.selectionModel().clearSelection()
        self.activeTranscriptResource = None
        self.activeSequenceResource = None


    def resourceSelected(self, index):

        #item = self.resourceView.model().data(index, Qt.DisplayRole)
        key = str(index.data(Qt.DisplayRole))
        res = self.resources[key]



        if not self.resourceView.selectionModel().isSelected(index):


            if res.GetType() == "SequenceResource":
                self.activeSequenceResource = None
                self.useSequenceResource.emit(None)
            elif res.GetType() == "TranscriptResource":
                self.activeTranscriptResource = None
                self.useTranscriptResource.emit(None)
            return

        if res.GetType() == "SequenceResource" and self.activeSequenceResource:
            items = self.resourceView.model().findItems(self.activeSequenceResource.GetName(), Qt.MatchFixedString)
            for i in items:
                index = self.resourceView.model().indexFromItem(i)
                self.resourceView.selectionModel().select(index, QItemSelectionModel.Deselect)
        elif res.GetType() == "TranscriptResource" and self.activeTranscriptResource:
            items = self.resourceView.model().findItems(self.activeTranscriptResource.GetName(), Qt.MatchFixedString)
            for i in items:
                index = self.resourceView.model().indexFromItem(i)
                self.resourceView.selectionModel().select(index, QItemSelectionModel.Deselect)

        if res.GetType()=='SequenceResource':
            self.activeSequenceResource = res
            self.useSequenceResource.emit(res)

        elif res.GetType()=='TranscriptResource':
            self.activeTranscriptResource = res
            self.useTranscriptResource.emit(res)
        self.resourceView.update()


    def updateResourceView(self):


        oldSelection = (self.activeTranscriptResource, self.activeSequenceResource)
        self.activeTranscriptResource = None
        self.activeSequenceResource = None


        self.resourceView.model().clear()

        for name, resource in self.resources.items():
            resourceItem = QStandardItem(resource.GetName())
            if resource == self.noiseResource:
                resourceItem.setData(QVariant(True), Qt.WhatsThisRole)

            self.resourceView.model().appendRow(resourceItem)


        self.setSelectedResource(oldSelection[0])
        self.setSelectedResource(oldSelection[1])

    def append(self, resource):
        self.resources[resource.GetName()] = resource

        resourceItem = QStandardItem(resource.GetName())
        self.resourceView.model().appendRow(resourceItem)
        #self.updateResourceView()

    def setSelectedResource(self, res):
        if not res:
            return
        items = self.resourceView.model().findItems(res.GetName(), Qt.MatchFixedString)
        for i in items:
            index = self.resourceView.model().indexFromItem(i)
            self.resourceView.selectionModel().select(index, QItemSelectionModel.Select)
            self.resourceSelected(index)

    def setNoiceResource(self, res):
        if not res:
            return
        self.noiseResource = res
        self.updateResourceView()
        self.useNoiseResource.emit(self.noiseResource)

    def hasResource(self, name):
        return name in self.resources

    def removeResource(self):
        if self.currentResource == self.activeTranscriptResource:
            self.activeTranscriptResource = None
            self.useTranscriptResource.emit(None)
        if self.currentResource == self.activeSequenceResource:
            self.activeSequenceResource = None
            self.useSequenceResource.emit(None)
        if self.currentResource == self.noiseResource:
            self.noiseResource = None
            self.useNoiseResource.emit(None)

        items = self.resourceView.model().findItems(self.currentResource.GetName(), Qt.MatchFixedString)
        for i in items:
            index = self.resourceView.model().indexFromItem(i)
            self.resourceView.model().removeRow(index.row())
        del self.resources[self.currentResource.GetName()]

        del self.currentResource
        self.currentResource = None

    def getResource(self, name):
        if name in self.resources:
            return self.resources[name]
        else:
            return None
    def getResources(self):
        resList = []
        for name, res in self.resources.items():
            resList.append(res)

        return resList

    def getResourcesDict(self):

        return self.resources

    def toggleNoiceResource(self):
        if self.noiseResource == self.currentResource:
            self.noiseResource = None
            self.useNoiseResource.emit(None)

        elif self.currentResource.GetType() == 'TranscriptResource':

            self.noiseResource = self.currentResource
            self.useNoiseResource.emit(self.currentResource)

        self.updateResourceView()

    def selectCurrentResource(self):
        self.setSelectedResource(self.currentResource)

    def showContextMenu(self,position):

        select = QAction('Select',self)
        select.triggered.connect(self.selectCurrentResource)

        setAsNoise = QAction('Set as noise', self)
        setAsNoise.triggered.connect(self.toggleNoiceResource)

        remove = QAction('Remove', self)
        remove.triggered.connect(self.removeResource)

        lisActions = []
        lisActions.append(select)
        lisActions.append(setAsNoise)
        lisActions.append(remove)
        QMenu.exec(lisActions, self.mapToGlobal(position));


class transcriptItemDelegate(QStyledItemDelegate):
    def __init__(self, items, Parent = None):
        super(transcriptItemDelegate, self).__init__(Parent)
        self.items = items

    def paint(self, painter, option, index):
        currentRow = index.sibling(index.row(), 0)
        itemname = str(currentRow.data(Qt.DisplayRole))
        name = str(index.data(Qt.DisplayRole))
        background = option.rect.adjusted(1,1,-2,-2)
        colColor = QColor(Qt.gray)

        try:
            item = self.items[itemname]
            if item['include']:
                background = option.rect.adjusted(1,1,-2,-2)
                colColor = QColor(Qt.blue).lighter()
            if item['non_coding'] == True:

                background = option.rect.adjusted(1,1,-2,-2)
                colColor = QColor(Qt.red).lighter()
        except KeyError:
            pass
        painter.setPen(QPen(QBrush(colColor), 2.0))
        painter.drawText(background, Qt.AlignLeft,name)


class transcriptView(QDockWidget):
    selectionChanged = pyqtSignal(list)
    usageToggled = pyqtSignal()
    processStarted = pyqtSignal(int, str)
    processUpdated = pyqtSignal(int)
    processFinished = pyqtSignal(int)

    def __init__(self, title, labels,  Parent=None):
        super(transcriptView, self).__init__(Parent)
        self.setObjectName(title)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)
        self.setWindowTitle(title)
        self.view = QTreeWidget(self)
        self.view.setColumnCount(len(labels))
        self.view.setSortingEnabled(True)
        self.view.setHeaderLabels(labels)
        self.view.itemDoubleClicked.connect(self.emitSelected)
        self.actionToggleUsage = QAction("Toggle Usage", self.view)
        self.actionToggleUsage.triggered.connect(self.toggleUsage)
        self.actionSelect = QAction("Load transcript/Gene...", self.view)
        self.actionSelect.triggered.connect(self.emitSelected)
        self.view.setContextMenuPolicy(Qt.ActionsContextMenu);
        self.view.addAction(self.actionToggleUsage);
        self.view.addAction(self.actionSelect);
        self.setWidget(self.view)

    def updateView(self, items, attribs):

        self.viewItems = items
        self.view.setItemDelegate(transcriptItemDelegate(items, self))
        self.view.clear()
        itemList = []
        self.processStarted.emit(len(items.keys()), "Updating "+str(self.windowTitle()))
        process = 0
        for name, value in items.items():
            self.processUpdated.emit(process)
            process+=1
            item = QTreeWidgetItem()
            for counter, key in enumerate(attribs):
                #item.setData(counter,Qt.DisplayRole, len(gene['transcripts']))
                item.setData(counter, Qt.DisplayRole, value[key])
            itemList.append(item)
        self.view.insertTopLevelItems(0, itemList)
        self.view.resizeColumnToContents(0)
        self.view.show()
        self.processFinished.emit(0)

    def clear(self):
        self.view.clear()

    def getSelection(self):
        selection = self.view.selectedItems()
        realSelection = []
        for item in selection:
            key = str(item.data(0,Qt.DisplayRole))
            realItem = self.viewItems[key]
            realSelection.append(realItem)
        return realSelection

    def emitSelected(self):
        self.selectionChanged.emit(self.getSelection())

    def toggleUsage(self):

        selection = self.getSelection()

        self.toggleUsageOfElement(selection)
        self.usageToggled.emit()

    def toggleUsageOfElement(self, element):

        selection = self.getSelection()
        if not selection:
            return
        for item in selection:
            item['include'] = not item['include']
            if 'transcripts' in item:
                for name, transcript in item['transcripts'].items():
                    transcript['include'] =  item['include']
    def update(self):
        print("updating ", self.objectName() )
        self.view.resizeColumnToContents(0)
