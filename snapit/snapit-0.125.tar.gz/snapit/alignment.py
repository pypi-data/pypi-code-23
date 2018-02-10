"""
alignment.py
Alignment algorithms
"""

from collections import defaultdict
from os import path, makedirs, remove
import difflib
import io
from Bio.Blast import NCBIXML
import subprocess
from .alignment import makeFasta, translate_dna

def BLASTp(query, index, file_folder):
    """
    Protein BLAST a list of sequences against RefSeq human protein database

    :param query: List of AA sequences (list)
    :param index: ID number of splicing event (int)
    :return: List of lists of BLAST hit, expected score, query sequence for every sequence in query (list[list[string, float, string], ...])
    """
    # Make temp folder
    if not path.exists(file_folder + "/Temp/"):
        makedirs(file_folder + "/Temp/")
    tempFolder = file_folder + "/Temp/"
    if query:
        isoforms = []
        # Write temporary fasta file
        seqFile = tempFolder + "seq_" + str(index) + ".fasta"
        with open(seqFile, "w") as seq1:
            seq1.write(makeFasta(query))
        # BLAST against RefSeq human protein database
        # Set BLASTDB environmental variable
        # Convert byte to string
        output = subprocess.check_output(file_folder + "/Install/ncbi-blast-2.7.1+/bin/blastp -query " + seqFile + " -db human.all.protein.faa -outfmt 5 -num_threads 4", env={'BLASTDB': file_folder + '/Install/ncbi-blast-2.7.1+/blastdb'}, shell=True).decode("utf-8")
        remove(seqFile)
        # Parse output as XML
        blast_result_record_list = NCBIXML.parse(io.StringIO(output))
        # Print BLAST hit title and expected score
        for blast_result_record in blast_result_record_list:
            for alignment in blast_result_record.alignments:
                for hsp in alignment.hsps:
                    isoforms.append([alignment.title, hsp.expect, hsp.query])
        return isoforms
    else:
        return []


def UTR_test_and_find_best_match(exon0Seq, exon2Seq, CDS, matching_aa_seq):
    """
    Map exons to CDS and UTR

    :param exon0Seq: DNA sequence of upstream exon (string)
    :param exon2Seq: DNA sequence of downstream exon (string)
    :param CDS: CDS sequence of protein (string)
    :param matching_aa_seq: AA sequence of protein (string)
    :return: List of aligment score, start index, end index, UTR5, UTR3, CDS for splicing event (list[float, int, int, bool, bool, string])
    """
    output_match_list = []
    # Translate CDS
    translatedCDS = translate_dna(CDS)
    # Upstream and downstream exons
    for exon_seq in [exon0Seq, exon2Seq]:
        match_score = 0
        CDS_match_start_index = 0
        CDS_match_end_index = 0
        UTR5 = False
        UTR3 = False
        match_list = [match_score, CDS_match_start_index, CDS_match_end_index, UTR5, UTR3, CDS]
        # Perfect match, exon sequence is in CDS
        if str(exon_seq) in str(CDS):
            # 1 is highest score: 100% match
            match_score = 1
            # Start index of CDS where exon is matched > AA start position of downstream exon > upper bound of cassette exon
            CDS_match_start_index = CDS.find(exon_seq)
            # End index of CDS where exon is matched > AA end position of upstream exon > lower bound of cassette exon
            CDS_match_end_index = CDS_match_start_index + len(exon_seq)
            # Translated CDS maps to canonical AA sequence
            if translatedCDS in matching_aa_seq:
                match_list = [match_score, CDS_match_start_index, CDS_match_end_index, UTR5, UTR3, CDS]
                output_match_list.append(match_list)
        # Not perfect match
        else:
            # CDS is protein coding sequence,excluding 5' UTR and 3' UTR
            # 5' UTR defined as first 15 nucleotides of CDS
            UTR5_seq = CDS[:15]
            # 3' UTR defined as last 15 nucleotides of CDS
            UTR3_seq = CDS[-15:]
            # 5' UTR sequence found in upstream or downstream exon > CDS begins downstream of UTR > cassette exon is in UTR if 5' UTR is in downstream exon
            if UTR5_seq in exon_seq:
                if exon_seq == exon2Seq:
                    UTR5 = True
                # Find exon region without UTR
                match_start_index_of_ex = exon_seq.find(UTR5_seq)
                match_end_index_of_ex = len(exon_seq)
                exon_wo_UTR = exon_seq[match_start_index_of_ex:match_end_index_of_ex]
                match_score = len(exon_wo_UTR) / len(exon_seq)
                # Map exon sequence without UTR to CDS
                CDS_match_start_index = CDS.find(exon_wo_UTR)
                CDS_match_end_index = CDS_match_start_index + len(exon_wo_UTR)
                # Should match beginning but CDS_match_start_index = -1 if exon_wo_UTR not within CDS so we define as not matched
                if CDS_match_start_index != 0:
                    UTR5 = False
                    match_score = 0
            # 3' UTR sequence found in upstream or downstream exon > CDS begins upstream of UTR > cassette exon is in UTR if 3' UTR is in upstream exon
            if UTR3_seq in exon_seq:
                if exon_seq == exon0Seq:
                    UTR3 = True
                # Find exon region without UTR
                match_end_index_of_ex = exon_seq.find(UTR3_seq) + len(UTR3_seq)
                match_start_index_of_ex = 0
                exon_wo_UTR = exon_seq[match_start_index_of_ex:match_end_index_of_ex]
                match_score = len(exon_wo_UTR) / len(exon_seq)
                # Map exon sequence wihtout UTR to CDS
                CDS_match_start_index = CDS.find(exon_wo_UTR)
                CDS_match_end_index = CDS_match_start_index + len(exon_wo_UTR)
                # Should match end but algorithm will occasionally mess up so we define as not matched
                if CDS_match_end_index != len(CDS):
                    UTR3 = False
                    match_score = 0
            # Only if translated CDS matches AA sequence
            if translatedCDS == matching_aa_seq:
                match_list = [match_score, CDS_match_start_index, CDS_match_end_index, UTR5, UTR3, CDS]
                output_match_list.append(match_list)
            # Not perfect match or in UTR, attempt to match exon sequence to CDS
            else:
                match_score = 0.0
                # Find max similarity
                for index_start in range(0, (len(CDS) - len(exon_seq))):
                    candidate = CDS[index_start:index_start + len(exon_seq)]
                    compare = difflib.SequenceMatcher(None, exon_seq, candidate)
                    # similarity = 2 * shared element / total elements in two strings, 1.0 is the highest score
                    similarity = compare.ratio()
                    if similarity > match_score:
                        match_score = similarity
                        CDS_match_start_index = index_start
                        CDS_match_end_index = index_start + len(exon_seq)
                # Only if translated CDS matches AA sequence
                if translatedCDS == matching_aa_seq:
                    match_list = [match_score, CDS_match_start_index, CDS_match_end_index, UTR5, UTR3, CDS]
                    output_match_list.append(match_list)
    return output_match_list


def localizeCassetteExon(upExonEnd, downExonStart, extraDomains, notAligned):
    """
    Localizes cassette exon to extracellular domain of protein

    :param upExonEnd: End index of upstream exon in protein AA sequence (float)
    :param downExonStart: Start index of downstream exon in protein AA sequence (float)
    :param extraDomains: List of lists lower bound and upper bound of extracellular/membrane domains (list[list[int, int], ...])
    :param notAligned: Exons that did not align to CDS (string)
    :return: Exons that localize to the extracellular/membrane domain (string)
    """
    exonsMatched = "N/A"
    # If protein has annotated extracellular domain
    if extraDomains:
        # Get boundary positions of extracellular domain
        for x in extraDomains:
            lowerBound = x[0]
            upperBound = x[1]
            # If exons aligned to CDS
            if notAligned == "Aligned":
                # Both exons start and end positions fall within extracellular domain
                if lowerBound < int(upExonEnd) < int(downExonStart) < upperBound:
                    exonsMatched = "Both"
            elif notAligned == "Downstream":
                # Upstream exon end positions falls within extracellular domain
                if lowerBound < int(upExonEnd) < upperBound:
                    exonsMatched = "Upstream"
            elif notAligned == "Upstream":
                # Downstream exon start position falls within extracellular domain
                if lowerBound < int(downExonStart) < upperBound:
                    exonsMatched = "Downstream"
    return exonsMatched


def findIsoform(seq0, seq1, seq2, strand, index, threshold, junction, extracellular):
    """
    Find possible parent isoforms that display splicing pattern

    :param seq0: DNA sequence of upstream exon (string)
    :param seq1: DNA sequence of cassette exon (string)
    :param seq2: DNA sequence of downstream exon (string)
    :param strand: '+' or '-' strand (string)
    :param index: ID number of splicing event (int)
    :param threshold: BLAST expected score cutoff (float)
    :param junction: Number of bases upstream and downstream of splice junction to be included (int)
    :param extracellular: Cassette exon is extracellular (bool)
    :return: List of lists of possible BLAST hits when cassette exon is spliced in or skipped (list[list[string, ...], list[string, ...]])
    """
    # Sequences must be able to encode at least 1 codon
    if len(seq0) >= 3 and len(seq1) >= 3 and len(seq2) >= 3 and extracellular:
        try:
            if strand == '+':
                # 3 possible reading frames, cassette included
                readingFrame1 = translate_dna(seq0[len(seq0) - junction:] + seq1 + seq2[:junction])
                readingFrame2 = translate_dna(seq0[len(seq0) - junction + 1:] + seq1 + seq2[:junction])
                readingFrame3 = translate_dna(seq0[len(seq0) - junction + 2:] + seq1 + seq2[:junction])
                # 3 possible reading frames, cassette skipped
                readingFrame4 = translate_dna(seq0[len(seq0) - junction:] + seq2[:junction])
                readingFrame5 = translate_dna(seq0[len(seq0) - junction + 1:] + seq2[:junction])
                readingFrame6 = translate_dna(seq0[len(seq0) - junction + 2:] + seq2[:junction])
            if strand == '-':
                readingFrame1 = translate_dna(seq2[len(seq2) - junction:] + seq1 + seq0[:junction])
                readingFrame2 = translate_dna(seq2[len(seq2) - junction + 1:] + seq1 + seq0[:junction])
                readingFrame3 = translate_dna(seq2[len(seq2) - junction + 2:] + seq1 + seq0[:junction])
                readingFrame4 = translate_dna(seq2[len(seq2) - junction:] + seq0[:junction])
                readingFrame5 = translate_dna(seq2[len(seq2) - junction + 1:] + seq0[:junction])
                readingFrame6 = translate_dna(seq2[len(seq2) - junction + 2:] + seq0[:junction])
            possibleAASeqsInc = [readingFrame1, readingFrame2, readingFrame3]
            possibleAASeqsSkip = [readingFrame4, readingFrame5, readingFrame6]
            # BLAST exon combinations (cassette included) against RefSeq human protein database, keep lowest expected score
            isoform1_list = []
            blast = BLASTp(possibleAASeqsInc, index)
            try:
                eScore = defaultdict(list)
                for x in blast:
                    eScore[x[0], x[2]].append(x[1])
                for k, v in eScore.items():
                    minEScore = min(v)
                    if minEScore < threshold:
                        isoform1_list.append([k, minEScore])
            except:
                pass
            # BLAST exon combinations (cassette excluded) against RefSeq human protein database, keep lowest expected score
            isoform2_list = []
            blast = BLASTp(possibleAASeqsSkip, index)
            try:
                eScore = defaultdict(list)
                for x in blast:
                    eScore[x[0], x[2]].append(x[1])
                for k, v in eScore.items():
                    minEScore = min(v)
                    if minEScore < threshold:
                        isoform2_list.append([k, minEScore])
            except:
                pass
            if isoform1_list or isoform2_list:
                return [isoform1_list, isoform2_list]
            else:
                return []
        except:
            return []
    else:
        return []
