#! /usr/bin/env python

from fusionfusion.config import *
from fusionfusion import region_utils
from fusionfusion import regions

def get_chimera_info(input_file, output_file):

    min_read_pair_num = param_conf.min_read_pair_num
    min_valid_read_pair_ratio = param_conf.min_valid_read_pair_ratio
    min_cover_size = param_conf.min_cover_size
    min_chimeric_size = param_conf.min_chimeric_size
    anchor_size_thres = param_conf.anchor_size_thres


    hin = open(input_file, 'r')
    hout = open(output_file, 'w')

    print >> hout, '\t'.join(["Chr_1", "Pos_1", "Dir_1", "Chr_2", "Pos_2", "Dir_2", 
                              "Inserted_Seq", "Read_Pair_Num", "Max_Over_Hang_1", "Max_Over_Hang_2"])

    for line in hin:
        F = line.rstrip('\n').split('\t')

        if F[0] == F[3] and abs(int(F[1]) - int(F[4])) < min_chimeric_size: continue

        coveredRegion_primary = F[9].split(';')
        coveredRegion_pair = F[12].split(';')
        coveredRegion_SA = F[15].split(';')

        # check the number of unique read pairs
        coveredRegion_meta = [coveredRegion_primary[i] + ';' + coveredRegion_pair[i] + ';' + coveredRegion_SA[i] for i in range(0, len(coveredRegion_primary))]
        uniqueCoverdRegion_meta = list(set(coveredRegion_meta))
        if len(uniqueCoverdRegion_meta) < min_read_pair_num: continue

        # check the maximum anchor size
        coverRegionSize_primary = map(region_utils.getCoverSize, coveredRegion_primary)
        coverRegionSize_SA = map(region_utils.getCoverSize, coveredRegion_SA)
        anchor_size = [min(coverRegionSize_primary[i], coverRegionSize_SA[i]) for i in range(len(coverRegionSize_primary))]
        if max(anchor_size) < anchor_size_thres: continue

        # check for the covered region
        pairPos = F[17].split(';')
        primaryPos = F[18].split(';')

        region1 =  regions.Regions()
        region2 =  regions.Regions()

        for i in range(0, len(coveredRegion_primary)):
            if primaryPos[i] == "1" and pairPos != "0":
                for reg in coveredRegion_primary[i].split(','):
                    region1.addMerge(reg)
            elif primaryPos[i] == "2" and pairPos != "0":
                for reg in coveredRegion_primary[i].split(','):
                    region2.addMerge(reg)

        for i in range(0, len(coveredRegion_SA)):
            if primaryPos[i] == "1" and pairPos != "0":
                for reg in coveredRegion_SA[i].split(','):
                    region2.addMerge(reg)
            elif primaryPos[i] == "2" and pairPos != "0":
                for reg in coveredRegion_SA[i].split(','):
                    region1.addMerge(reg)

        for i in range(0, len(coveredRegion_pair)):
            if (primaryPos[i] == "1" and pairPos[i] == "1") or (primaryPos[i] == "2" and pairPos[i] == "2"):
                for reg in coveredRegion_pair[i].split(','):
                    region1.addMerge(reg)
            elif (primaryPos[i] == "1" and pairPos[i] == "2") or (primaryPos[i] == "2" and pairPos[i] == "1"):
                for reg in coveredRegion_pair[i].split(','):
                    region2.addMerge(reg)

        region1.reduceMerge()
        region2.reduceMerge()

        if region1.regionSize() < min_cover_size or region2.regionSize() < min_cover_size: continue


        print >> hout, '\t'.join(F[0:7]) + '\t' + str(len(uniqueCoverdRegion_meta)) + '\t' + str(region1.regionSize()) + '\t' + str(region2.regionSize())

    hin.close()
    hout.close()

