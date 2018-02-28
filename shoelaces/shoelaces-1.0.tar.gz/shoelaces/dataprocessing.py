from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import numpy as np

from shoelaces.readProcessing import *
from shoelaces.changepoint_analysis import *


class sequenceProcessor(QObject):

    configLoaded = pyqtSignal(str)

    processStarted = pyqtSignal(int, str)
    processUpdated = pyqtSignal(int)
    processFinished = pyqtSignal(int)

    def __init__(self, transcripts = None, sequenceData = None, noise = None):
        QObject.__init__(self)
        self.transcripts = transcripts
        self.sequenceData = sequenceData
        self.lengthOffsets = {}
        self.noise = noise
        self.noiseIntervals = {}
    # result index
    #0: Chromoson    #1: RNA start coord    #2: RNA end coord    #3: name    #4: direction    #5: CDS start coord    #6: CDS end coord    #7: exon sizes    #8: exon starts

    def __bool__(self):
        if not self.transcripts:
            return False
        if not self.sequenceData:
            return False
        return True

    def setData(self, sequenceData):
        self.sequenceData = sequenceData

    def setTranscripts(self, transcripts):
        self.transcripts = transcripts

    def getReadBySpecs(self, pos, cigarstring, chromosome):
        reads = self.sequenceData.fetch(chromosome, pos, pos+1)
        for read in reads:
            if read.pos == pos and read.cigarstring == cigarstring:
                return read

    def checkOverlap(self, coord, read, checkToStart):
        threshold = 30
        pos = read.pos

        if read.is_reverse:
            if checkToStart:
                pos += read.alen - 1
                addRead = coord < pos < coord + threshold
            else:

                addRead = coord > pos > coord - threshold
        else:
            if checkToStart:
                addRead = coord > pos > coord - threshold
            else:
                pos += read.alen

                addRead = coord < pos < coord + threshold
        return addRead


    def plotDifferenceToCDS(self, cds_start = True, useOffsets = False, percentage = 1.0, ):
        if not self.sequenceData or not self.transcripts:
            return {}

        readBins = {}

        readsPertranscript = {}
        totalReads = 0

        usedCDScoords= []

        NoT = len(self.transcripts.transcripts)*percentage
        #print("Used transcripts:",NoT)
        progress = 0;

        self.processStarted.emit(NoT+1, "Processing Sequence Data")
        transcriptList =   self.transcripts.transcripts.items()

        if self.transcripts.genes:
            #print("Sorting transcripts")
            transcriptList = reversed(sorted(self.transcripts.transcripts.items(), key = lambda t: float(self.transcripts.genes[t[1]['gene_id']]['NoR'])/float(t[1]['CDS_length']) ))
        for (transcriptName, transcript) in transcriptList:

            #print(transcript[0])
            if progress >= NoT:
                break
            if not transcript['include']:
               # print('Not using', transcript[1]['transcript_id'])
                continue

            if not 'stop_codon' in transcript or not 'start_codon' in transcript:
                continue

            self.processUpdated.emit(progress)
            progress += 1

            forward = transcript['forward']

            interval = (-50, 200)

            if (cds_start and forward) or (not cds_start and not forward):
                coord = transcript['CDS_min']
            else:
                coord = transcript['CDS_max']
                interval = (-200, 50)

            #print(transcript[0], coord, interval)

            if self.sequenceData.isNoise(coord):
                continue

            if coord in usedCDScoords:
                continue

            chromosome = transcript['chromosome']
            fetchStartCoord = moveOnTranscript(coord, transcript, interval[0])
            fetchEndCoord = moveOnTranscript(coord, transcript, interval[1])
            reads = self.sequenceData.fetch(chromosome, fetchStartCoord, fetchEndCoord)

            usedCDScoords.append(coord)
            validReads = 0
            #minPos = 1000000000000
            #maxPos = 0
            for read in reads:
                if isMultiMapper(read):
                    continue

                validReads += 1

                #minPos = min(minPos, getRealReadPos(read,0))
                #maxPos = max(maxPos, getRealReadPos(read,0))

                length = read.infer_query_length()
                try:
                    readBins[length].append((read,  transcriptName))
                except:
                    readBins[length] = [(read,  transcriptName)]
            readsPertranscript[transcriptName] = validReads
            totalReads += validReads
            # print("transcript: ", transcriptName)
            # print("span: " , fetchEndCoord - fetchEndCoord)
            # print("read span: ", maxPos - minPos)

        nrOfPlots = len(readBins)
        plots = {}
        normalizedWeights = {}

        for key in readsPertranscript.keys():

            normalizedWeights[key] =  1.0 #/ readsPertranscript[key]

        self.processFinished.emit(0)
        QApplication.processEvents()

        self.processStarted.emit(nrOfPlots, "Generating Difference Plots")

        for key, i in zip(readBins, range(0,nrOfPlots)):
            self.processUpdated.emit(i)

            diffs = {}

            offset = 0
            # if useOffsets and key in self.lengthOffsets:
            #     offset = self.lengthOffsets[key]
            # elif useOffsets:
            #     continue

            for (read, transcriptId) in readBins[key]:
                cds_min = True
                if (read.is_reverse and cds_start) or (not cds_start and not read.is_reverse):
                    cds_min = False

                diff = getDiffToCDS(read, self.transcripts[transcriptId], offset, cds_min)

                diff += offset

                try:
                    diffs[diff] += normalizedWeights[transcriptId]
                except:
                    diffs[diff] = normalizedWeights[transcriptId]

            plots[key] = diffs
            sortedplot = sorted(diffs.items(), key=lambda x: x[0])
            # if key==28:
            #     for key in sortedplot:
            #         print(key)
        self.processFinished.emit(0)
        QApplication.processEvents()
        return plots

    def fourierTransform(self, plots):

        result = {}

        for length, plot in plots.items():

            self.populateHist(plot,range(1,150))

            sortedplot = sorted(plot.items(), key=lambda x: x[0])

            data = np.array([(val) for (key,val) in sortedplot if key >= 0 and key <= 150],np.float )
            try:
                ft = np.fft.fft(data, axis=0)
            except:
                continue
            amplitudes = abs(ft)
            frequencies = np.fft.fftfreq(len(data), 1)
            hist = {1/i:value for i, value in zip(frequencies, amplitudes) if i != 0}
            result[length] = hist
        return result

    def createModulusPlots(self, plots, offset = 1):
        results = {}
        for length, plot in plots.items():
            modplot = {}

            for pos, value in plot.items():
                m = offset + (pos % 3)
                try:
                    modplot[m] += plot[pos]
                except:
                    modplot[m] = plot[pos]
            results[length] = modplot
        return results

    def detectOffset(self, plots):
        result = {}
        self.processStarted.emit(len(plots.keys()), "Detecting Read Offsets")
        process = 0
        for length, plot in plots.items():
            self.processUpdated.emit(process)
            process+=1
            self.populateHist(plot, range(-30, 10))
            sortedplot = sorted(plot.items(), key=lambda x: x[0])


            #print(sortedplot)
            data = np.array([(val) for (key,val) in sortedplot],np.float )
            try:
                stats, pvals, nums = detect_mean_shift(data)
            except:
                continue

            changes = np.zeros(len(stats)-1)
            for s in range(len(stats)-1):
                changes[s] = stats[s+1] -  stats[s]


            ind = np.argmax(abs(changes))+1


            #print(ind)
            result[length] = sortedplot[ind][0]

        self.processFinished.emit(0)
        return result

    def findUsefulLengths(self, freqPlots, plots):

        usefulLengths = []
        for key,plot in freqPlots.items():

            largest = 0.0
            freq = 0.0
            func = self.getSubWig(plot,sorted(plot.keys()),1,15)

            plot = plots[key]
            sum= 0;
            for i, value in plot.items():
                sum += value;
            if sum <100:
                print("Not enough reads")
                continue;

            for currentFreq, value in func.items():

                if value > largest:

                    largest = value
                    freq = abs(currentFreq)

            if abs(freq - 3.0) < 0.1:# and largest/stdDev > 3:
                usefulLengths.append(key)

        return usefulLengths

    def populateHist(self, hist, range):
        for i in range:
            try:
                hist[i]
            except KeyError:
                hist[i] = 0

    def detectReadOffsets(self, data):

        for plot in data:

            if len(plot[0].keys()) < 15:
                continue
            length = plot[1]
            graph = sorted(plot[0])
            index = 0
            maxDiff = graph[0]
            for i in range(1, len(graph)):
                diff = (graph[i] - graph[i-1])
                if diff > maxDiff:
                    index = i
                    maxDiff = diff
            self.lengthOffsets[length] = -index

        #print self.lengthOffsets

    def setOffsets(self, readLength, offsets):

        self.lengthOffsets[readLength] = offsets

    #cigar
    #
    #M	BAM_CMATCH	    0
    #I	BAM_CINS	    1
    #D	BAM_CDEL	    2
    #N	BAM_CREF_SKIP	3
    #S	BAM_CSOFT_CLIP	4
    #H	BAM_CHARD_CLIP	5
    #P	BAM_CPAD	    6
    #=	BAM_CEQUAL	    7
    #X	BAM_CDIFF	    8

    def plotSumOntranscript(self, transcriptName, useOffsets=False):

        if not self.sequenceData:
            return {}
        if not(transcriptName in self.transcripts):
            #print "Not existing transcript:", transcriptName
            return {}

        transcript = self.transcripts[transcriptName]
        fetchStart = transcript['RNA_min']
        fetchEnd = transcript['RNA_max']
        chromosome = transcript['chromosome']

        reads = self.sequenceData.fetch(chromosome, fetchStart, fetchEnd)

        return self.plotsum(reads)

    def plotReadsOntranscript(self, transcriptName, useOffsets = False):

        if not self.sequenceData:
            return {}
        if not(transcriptName in self.transcripts.transcripts):
            #print "Not existing transcript:", transcriptName
            return {}

        transcript = self.transcripts[transcriptName]
        fetchStart = transcript['RNA_min']
        fetchEnd = transcript['RNA_max']

        chromosome = transcript['chromosome']
        try:
            reads = self.sequenceData.fetch(chromosome, fetchStart, fetchEnd)
        except ValueError:
            reads = []

        return self.plotReads(reads, useOffsets)

    def plotSum(self, reads):

        readPositions = {}
        count =0
        for read in reads:
            #length, fills, gaps = parseRead(read)



            for (start, finish) in read.get_blocks():
                for i in range(start+1, finish+1):
                    if(i == 24068169):
                        #print(read.qname)
                        #print(getRealReadPos(read,0))
                        count += 1;
                    try:
                        readPositions[i] += 1
                    except KeyError:
                        readPositions[i] = 1

        return readPositions

    def plotReads(self, reads, useOffsets = False):

        if not self.sequenceData:
            return {}

        readPositions = {}

        for read in reads:
            length, fill, gaps = parseRead(read)

            offset = 0
            if useOffsets and length in self.lengthOffsets:
                offset = self.lengthOffsets[length]
            elif useOffsets:
                continue

            #nucPos = getModulatedReadPos(read, transcript,offset)
            nucPos = getRealReadPos(read, offset)

            #if nucPos == -1:
                #print read.cigar, read.pos

            if nucPos in readPositions:
                readPositions[nucPos] += 1
            else:
                readPositions[nucPos] = 1

        return readPositions

    def gettranscriptStats(self, transcriptName, useOffsets=False, multimappers = 'ignore'):


        if not self.sequenceData:
            print ("No data")
            return {}

        if not (transcriptName in self.transcripts.transcripts):
            print ("Not existing transcript:", transcriptName)
            return {}

        transcript = self.transcripts[transcriptName]
        #print(transcript)

        fetchStart = transcript['RNA_min']
        fetchEnd = transcript['RNA_max']
        chromosome = transcript['chromosome']


        smallestCDS = transcript['CDS_min']
        largestCDS = transcript['CDS_max']

                #stop_codon not included in cds
        if('stop_codon' in transcript):
            if(transcript['forward']):
                largestCDS = transcript['stop_codon'][1]
            else:
                smallestCDS = transcript['stop_codon'][0]


        reads = self.sequenceData.fetch(chromosome, fetchStart, fetchEnd)
        #print ('Nr of reads:', len(reads))

        onUTRmin = 0
        onCDS = 0
        onUTRmax = 0
        isMM = 0
        onIntron = 0
        ignoreMM  = multimappers == 'ignore'



        for read in reads:

            mm = isMultiMapper(read)
            if mm and ignoreMM:
                isMM += 1
                continue

            length, fill, gaps = parseRead(read)

            offset = 0
            if useOffsets and length in self.lengthOffsets:
                offset = self.lengthOffsets[length]
            elif useOffsets:

                continue

            exonIndex = getOnExon(read, transcript, offset)

            if exonIndex == -2:

                continue
            elif exonIndex == -1:
                onIntron +=1
                continue

            pos = getRealReadPos(read, offset)
            if pos < smallestCDS:
                onUTRmin += 1
            elif pos > largestCDS:
                onUTRmax += 1
            elif smallestCDS <=  pos <= largestCDS:
                onCDS += 1



        if not transcript['forward']:
            temp = onUTRmax
            onUTRmax = onUTRmin
            onUTRmin = temp

        result = {}
        result['CDS'] = onCDS
        result['Leader'] = onUTRmin
        result['Trailer'] = onUTRmax
        result['Intron'] = onIntron
        result['Multimappers'] = isMM

        result['Sum'] =result['CDS']+result['Leader']+result['Trailer']+result['Intron']+result['Multimappers']
        return result

    def getgenestats(self, gene, useOffsets= False, multimappers = 'ignore'):
        if not self.sequenceData:
            return {}

        fetchStart = gene['RNA_min']
        fetchEnd = gene['RNA_max']
        chromosome = gene['chromosome']

        #smallestCDS = transcript['CDS_min']
        #largestCDS = transcript['CDS_max']
        if gene['reads']:
            reads = gene['reads']
        else:
            reads = self.sequenceData.fetch(chromosome, fetchStart, fetchEnd)
            gene['reads'] = reads

        onUTRmin = 0
        onCDS = 0
        onUTRmax = 0
        onIntron = 0
        onNoneCoding = 0
        isMM = 0
        ignoreMM = multimappers =='ignore'
        #print("Use offsets: ", useOffsets)
        for read in reads:

            mm =  isMultiMapper(read)

            if mm and ignoreMM:
                isMM += 1
                continue

            length, fill, gaps = parseRead(read)
            offset = 0
            if useOffsets and length in self.lengthOffsets:
                offset = self.lengthOffsets[length]
            elif useOffsets:
                continue

            inCDS = False
            inUTRmin = False
            inUTRmax = False
            inIntron = False
            for transcriptName, transcript in gene['transcripts'].items():

                smallestCDS = transcript['CDS_min']
                largestCDS = transcript['CDS_max']
                if('stop_codon' in transcript):
                    if(transcript['forward']):
                        largestCDS = transcript['stop_codon'][1]
                    else:
                        smallestCDS = transcript['stop_codon'][0]
                exonIndex = getOnExon(read, transcript, offset)

                if exonIndex == -2:
                    continue
                elif exonIndex == -1:
                    inIntron = True
                    continue

                pos = getRealReadPos(read, offset)
                if largestCDS >= pos >= smallestCDS :
                    inCDS = True
                    break
                if pos > largestCDS:
                    inUTRmax = True
                if pos < smallestCDS:
                    inUTRmin = True



            if inCDS:
                onCDS += 1
            elif inUTRmax:
                onUTRmax += 1
            elif inUTRmin:
                onUTRmin += 1
            elif inIntron:
                onIntron += 1
            else:
                for transcriptName, transcript in self.transcripts.noncodingtranscripts.items():
                    exonIndex = getOnExon(read, transcript, offset)
                    if exonIndex:
                        onNoneCoding += 1
                        break



        if not gene['forward']:
            temp = onUTRmax
            onUTRmax = onUTRmin
            onUTRmin = temp


        result = {}
        result['CDS'] = onCDS
        result['Leader'] = onUTRmin
        result['Trailer'] = onUTRmax
        result['Intron'] = onIntron
        result['Non-coding'] = onNoneCoding
        result['Multimappers'] = isMM
        result['Sum'] =result['CDS']+result['Leader']+result['Trailer']+result['Intron']+result['Non-coding']+result['Multimappers']
        return result

    def getglobalstats(self, useOffsets= False, multimappers = 'ignore'):

        return {}
        if not self.sequenceData:
            return {}

        onUTRmin = 0
        onCDS = 0
        onUTRmax = 0
        isMM = 0
        onIntron = 0
        onNoneCoding = 0
        ignoreMM = multimappers =='ignore'

        progress = 0;

        progressBar = QProgressDialog("Processing Sequence Data", "Abort", 0, len(self.transcripts.chromosomes))
        #progressBar.setWindowModality(Qt.WindowModal)
        progressBar.show()


        transcriptList = sorted(self.transcripts.transcripts.items(), key = lambda t: t[1]['RNA_min'])

        for chr in self.transcripts.chromosomes:
            #print("Fetching reads")
            reads = self.sequenceData.fetch(chr)

            i = 0
            for read in reads:

                i+=1
                mm =  isMultiMapper(read)

                if mm and ignoreMM:
                    isMM += 1
                    continue

                length, fill, gaps = parseRead(read)
                offset = 0
                if useOffsets and length in self.lengthOffsets:
                    offset = self.lengthOffsets[length]
                elif useOffsets:
                    continue

                inCDS = False
                inUTRmin = False
                inUTRmax = False
                inIntron = False

                pos = getRealReadPos(read, offset)

                for transcriptName, transcript in self.transcripts.transcripts.items():
                    smallestCDS = transcript['CDS_min']
                    largestCDS = transcript['CDS_max']
                    exonIndex = getOnExon(read, transcript, offset)

                    if exonIndex == -2:
                        continue
                    elif exonIndex == -1:
                        inIntron = True
                        continue

                    if largestCDS >= pos >= smallestCDS :
                        inCDS = True
                        break
                    if (pos > largestCDS and transcript['forward']) or (pos<smallestCDS and not transcript['forward']):
                        inUTRmax = True
                    else:
                        inUTRmin = True


                if inCDS:
                    onCDS += 1
                elif inUTRmax:
                    onUTRmax += 1
                elif inUTRmin:
                    onUTRmin += 1
                elif inIntron:
                    onIntron += 1


            progress +=1
            progressBar.setValue(progress)
            QApplication.processEvents()
        progressBar.close()
        result = {}
        result['CDS'] = onCDS
        result['Leader'] = onUTRmin
        result['Trailer'] = onUTRmax
        result['Intron'] = onIntron
        result['Multimappers'] = isMM


        return result

    def countStats(self, wig, forward ):

        onUTRmin = 0
        onCDS = 0
        onUTRmax = 0
        isMM = 0
        onIntron = 0
        onNoneCoding = 0
        sumReads = 0

        for chr, histogram in wig.items():

            positions = histogram
            if not chr in self.transcripts.chromosomes:
                continue

            transcriptList = self.transcripts.chromosomes[chr]
            for pos, count in positions.items():
                sumReads += count
                inCDS = False
                inUTRmin = False
                inUTRmax = False
                inIntron = False

                for transcript in transcriptList:
                    if transcript['forward'] != forward or not transcript['include']:
                        continue

                    smallestCDS = transcript['CDS_min']
                    largestCDS = transcript['CDS_max']
                    if('stop_codon' in transcript):
                        if(transcript['forward']):
                            largestCDS = transcript['stop_codon'][1]
                        else:
                            smallestCDS = transcript['stop_codon'][0]

                    exonIndex = getPosOnExon(pos, transcript)

                    if exonIndex == -2:
                        continue
                    elif exonIndex == -1:
                        inIntron = True
                        continue

                    if largestCDS >= pos >= smallestCDS :
                        inCDS = True
                        break
                    if (pos > largestCDS and transcript['forward']) or (pos<smallestCDS and not transcript['forward']):
                        inUTRmax = True
                    else:
                        inUTRmin = True


                if inCDS:
                    onCDS += count
                elif inUTRmax:
                    onUTRmax += count
                elif inUTRmin:
                    onUTRmin += count
                elif inIntron:
                    onIntron += count
                else:
                    for transcriptName, transcript in self.transcripts.noncodingtranscripts.items():
                        exonIndex = getPosOnExon(pos, transcript)
                        if exonIndex:
                            onNoneCoding += count
                            break
        return onUTRmin, onCDS, onUTRmax, onIntron, onNoneCoding, sumReads

    def getglobalstatsFromWig(self, useOffsets, lengths = []):

        if not self.sequenceData:
            return {}
        if not self.transcripts:
            return {}


        self.sequenceData.setUseOffsets(useOffsets)
        self.sequenceData.createWig()
        if not useOffsets and not lengths:
            lengths = self.sequenceData.splitWig['forward'].keys()

        elif(not lengths):
            lengths = self.sequenceData.splitWig['forward'].keys()
            lengthDist = {}

            for l in lengths :
                lengthDist[l] = 0


            result = {}
            result['Selected lengths'] = 'None'
            result['CDS'] = 0
            result['Leader'] = 0
            result['Trailer'] = 0
            result['Intron'] =  0
            result['Non-coding'] = 0
            result['Multimappers'] = 0
            return result, lengthDist



        onUTRminf, onCDSf, onUTRmaxf, onIntronf, onNoneCodingf = 0,0,0,0,0
        onUTRminb, onCDSb, onUTRmaxb, onIntronb, onNoneCodingb = 0,0,0,0,0
        lengthDist = {}

        self.processStarted.emit(len(lengths), "Processing Wig")
        counter = 0
        for length in lengths:
            self.processUpdated.emit(counter)
            counter += 1
            lengthDist[length] = 0
            try:
                a,b,c,e,f, sum =  self.countStats(self.sequenceData.splitWig['forward'][length], True)
                onUTRminf+=a
                onCDSf+=b
                onUTRmaxf+=c

                onIntronf+=e
                onNoneCodingf+=f
                lengthDist[length] += sum

            except KeyError:
                #print('Wrong forward length')
                pass

            try:

                g,h,i,k,l, sum =  self.countStats(self.sequenceData.splitWig['reverse'][length], False)
                onUTRminb += g
                onCDSb+=h
                onUTRmaxb+=i

                onIntronb+=k
                onNoneCodingb+=l
                lengthDist[length] += sum

            except KeyError:
                #print('Wrong reverse length')
                pass
        self.processFinished.emit(counter )

        result = {}



        result['CDS'] = onCDSf + onCDSb
        result['Leader'] = onUTRminf + onUTRminb
        result['Trailer'] = onUTRmaxf + onUTRmaxb
        result['Intron'] = onIntronf + onIntronb
        result['Non-coding'] = onNoneCodingf + onNoneCodingb
        result['Multimappers'] = self.sequenceData.multimappers
        result['Total amount of reads'] = result['CDS'] + result['Leader'] + result['Trailer'] + result['Intron'] + result['Non-coding'] + result['Multimappers']

        return result, lengthDist

    def plotAlltranscripts(self, function, transcripts = []):
        if not self.sequenceData:
            return {}
        if not transcripts:
            transcripts = self.transcripts.keys()
        result = {}
        for transcript in transcripts:
            #if (self.transcripts[transcript]['forward']):
            #    continue
            currentResult = function(transcript)
            for key in currentResult:
                if key in result:
                    result[key] += currentResult[key]
                else:
                    result[key] = currentResult[key]
        return result


    def writeWigToFile(self, filename, wig):
        print(filename)
        #print(wig)
        wigFile = open(filename, 'w')
        for chromosome, wig in wig.items():
            print(chromosome)
            wigFile.write("variableStep chrom=" + chromosome+"\n")
            for pos in sorted(wig):
                line = str(pos) + '\t' + str(wig[pos]) + '\n'
                wigFile.write(line)
        wigFile.close()


    def writeWigFile(self, filename, selectedlengths = [], split = False):


        if not self.sequenceData:
            return


        self.sequenceData.createWig()

        if split:
            if selectedlengths == []:
                forwardKeys = self.sequenceData.splitWig['forward'].keys()
                reverseKeys = self.sequenceData.splitWig['reverse'].keys()

                selectedlengths = list(set(forwardKeys).union(set(reverseKeys)))
            for length in selectedlengths:
                outputfile = filename + '-' + str(length)+'-forward.wig'
                try:
                    self.writeWigToFile(outputfile, self.sequenceData.splitWig['forward'][length])
                except KeyError:
                    continue
                outputfile = filename + '-' + str(length)+'-reverse.wig'
                try:
                    self.writeWigToFile(outputfile, self.sequenceData.splitWig['reverse'][length])
                except KeyError:
                    continue
        else:
            outputfile = filename +'-forward.wig'
            if self.sequenceData.forwardWig:
                self.writeWigToFile(outputfile, self.sequenceData.forwardWig)

            outputfile = filename +'-reverse.wig'
            if self.sequenceData.reverseWig:
                self.writeWigToFile(outputfile, self.sequenceData.reverseWig)



    def getSubWig(self, wig, positions, start, end):
        result = {}

        for pos in positions:
            #print(pos)
            if pos > end:
                break

            elif pos >= start:
                result[pos] = wig[pos]



        return result


    def writeRelateWigToFile(self, filename, wig):


        wigFile = open(filename, 'w')
        for chromosome, relateiveWig in wig.items():

            for transcriptName, wig in relateiveWig.items():
                #print(chromosome, transcriptName)
                wigFile.write("variableStep chrom=" + str(chromosome)+ " transcript_id="+transcriptName+"\n")
                for pos in sorted(wig):
                    line = str(pos) + '\t' + str(wig[pos]) + '\n'
                    wigFile.write(line)
        wigFile.close()

    def createRelativeWig(self, wig, forward):
        relativeWig = {}

        for chromosome, currentWig in wig.items():
            currentRelWig = {}

            positions = sorted(currentWig.keys())
            #print("Creating subwig chr:", chromosome)
            for transcriptName in self.transcripts.transcripts:
                transcript = self.transcripts[transcriptName]
                if transcript['chromosome'] != chromosome:
                    continue

                subWig = self.getSubWig(currentWig, positions, transcript['RNA_min'], transcript['RNA_max'])
                #print("Subwig", subWig)
                relSubWig = {}
                for pos, value in subWig.items():
                    transcriptpos = dnatotranscript(pos, transcript)
                    relSubWig[transcriptpos] = value
                currentRelWig[transcriptName] = relSubWig
            relativeWig[chromosome] = currentRelWig

        return relativeWig


    def writeRelativeWigFile(self, filename, selectedlengths, split = False, useOffset = False, multimappers = 'ignore'):

        if not self.sequenceData:
            return


        self.sequenceData.createWig()

        if split:

            if selectedlengths == []:
                forwardKeys = self.sequenceData.splitWig['forward'].keys()
                reverseKeys = self.sequenceData.splitWig['reverse'].keys()

                selectedlengths = list(set(forwardKeys).union(set(reverseKeys)))
            for length in selectedlengths:
                outputfile = filename + '-' + str(length)+'-forward.wig'
                try:
                    relWig = self.createRelativeWig(self.sequenceData.splitWig['forward'][length], True)
                    self.writeRelateWigToFile(outputfile, relWig)
                except KeyError:
                    continue
                outputfile = filename + '-' + str(length)+'-reverse.wig'
                try:
                    relWig = self.createRelativeWig(self.sequenceData.splitWig['reverse'][length], False)
                    self.writeRelateWigToFile(outputfile, relWig)
                except KeyError:
                    continue
        else:
            outputfile = filename +'-forward.wig'
            if self.sequenceData.forwardWig:
                relWig = self.createRelativeWig( self.sequenceData.forwardWig, True)
                self.writeRelateWigToFile(outputfile, relWig)

            outputfile = filename +'-reverse.wig'
            if self.sequenceData.reverseWig:
                relWig = self.createRelativeWig( self.sequenceData.reverseWig, False)
                self.writeRelateWigToFile(outputfile, relWig)






