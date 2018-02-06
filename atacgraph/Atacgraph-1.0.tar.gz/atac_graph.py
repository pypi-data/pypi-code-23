import pandas as pd
import numpy as np
import sys
import math
import os
import subprocess, sys
import glob
import time
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

tstart = time.time()#time start

#input_gene = sys.argv[1]
#input_bam = sys.argv[2]
#output = sys.argv[3]
input_bam = "Ctrl_1.bam"
input_gene = "genes.gtf"

print "ATAC-seq_Pipeline_START"

subprocess.call('''samtools index %s'''%(input_bam),shell=True)

if glob.glob(input_gene+'.gtf'):
	print ""
else:
	subprocess.call('''gffread %s -T -o %s'''%(input_gene,input_gene+'.gtf'),shell=True)

print "*----------------------*"
print "|Bam_read_length_filter|"
print "*----------------------*"
subprocess.call('samtools view -H %s > %s'%(input_bam,input_bam+'_header.sam'), shell=True)
subprocess.call('''samtools view %s -f 0x02| awk '{ if ( $9>200||$9<-200 ) print$0} '>%s'''%(input_bam,input_bam+'_long.sam'),shell=True)
subprocess.call('''samtools view %s -f 0x02| awk '{ if ( $9<=200 && $9>= -200) print$0} '>%s'''%(input_bam,input_bam+'_short.sam'),shell=True)
subprocess.call('''cat %s %s|samtools view -bS - > %s'''%(input_bam+'_header.sam',input_bam+'_long.sam',input_bam+'_long.bam'),shell=True)
subprocess.call('''cat %s %s|samtools view -bS - > %s'''%(input_bam+'_header.sam',input_bam+'_short.sam',input_bam+'_short.bam'),shell=True)


print "*--------------*"
print "|Index_Bam_File|"
print "*--------------*"
subprocess.call('''samtools index %s'''%(input_bam+'_long.bam'),shell=True)
subprocess.call('''samtools index %s'''%(input_bam+'_short.bam'),shell=True)


print "*----------------*"
print "|Making peak file|"
print "*----------------*"
subprocess.call('''macs2 callpeak -t %s --nomodel --broad --shift -10 --extsize 20 -n %s'''%(input_bam,input_bam+'_integ_peak'), shell=True)
subprocess.call('''macs2 callpeak -t %s --format BAMPE --broad -n %s'''%(input_bam+'_long.bam',input_bam+'_long_peak'), shell=True)
subprocess.call('''macs2 callpeak -t %s --format BAMPE --broad -n %s'''%(input_bam+'_short.bam',input_bam+'_short_peak'), shell=True)	



#annotation name
gene = "gene_body"
exon = "exons"
intron = "introns"
utr3 = "3utr"
utr5 = "5utr"
cds = "cds"
promoter = "gene_promoter"
igr = "gene_igr"
annotation_name=[promoter,gene,exon,intron,utr5,cds,utr3,igr]

integ_peak=input_bam+'_integ_peak_peaks.broadPeak'
long_peak=input_bam+'_long_peak_peaks.broadPeak'
short_peak=input_bam+'_short_peak_peaks.broadPeak'
peak_name = [integ_peak,long_peak,short_peak]

bam_coverage=input_bam+'_coverage.bw'
long_bam_coverage=input_bam+'_long_coverage.bw'
short_bam_coverage=input_bam+'_short_coverage.bw'
bam_coverage_name=[bam_coverage,long_bam_coverage,short_bam_coverage]


#Making bam coverage

subprocess.call('''bamCoverage -b %s -bs 10 --normalizeUsingRPKM --Offset 1 20 -o %s'''%(input_bam, input_bam+'_coverage.bw'),shell=True)
subprocess.call('''bamCoverage -b %s -bs 10 --normalizeUsingRPKM -e -o %s'''%(input_bam+'_long.bam', input_bam+'_long_coverage.bw'),shell=True)
subprocess.call('''bamCoverage -b %s -bs 10 --normalizeUsingRPKM -e -o %s'''%(input_bam+'_short.bam', input_bam+'_short_coverage.bw'),shell=True)



print "*--------------------------------*"
print "|Extract UTR, exon, cds from gene|"
print "*--------------------------------*"

subprocess.call('''python extract_transcript_regions.py -i %s -o %s --gtf'''%(input_gene+'.gtf',input_gene+'.gtf'), shell=True)
print "*-------------------------------------*"
print "|Convert this blockbed (bed12) to bed6|"
print "*-------------------------------------*"
for i in annotation_name:
	subprocess.call('''cat %s | bed12ToBed6 -i stdin -n > %s'''%(input_gene+'.gtf'+'_'+i+'.bed',input_gene+'.gtf'+'_'+i+'_bed6.bed'),shell=True)



#find gene_body.bed
genes = pd.read_csv(input_gene+'.gtf', header=None, sep="\t")
genes.columns=['chr','unknow', 'exon', 'g_str', 'g_end', 'g_score', 'g_dir','.', 'gene_name']
genes=genes[genes.exon=='exon']
gene_col=genes['gene_name'].str.split(';', expand=True)
gene_col.columns=gene_col.ix[1,:]
gene_id = gene_col.filter(regex='gene_id')
gene_id = gene_id.ix[:,0].str.split(' ', expand=True)
gene_id[2] = gene_id[2].map(lambda x: x.lstrip('"').rstrip('"'))
gene_id.columns=['num','g_name','gene_id']
gene_bed = genes.ix[:,['chr', 'g_str', 'g_end', 'g_score','g_dir']].join(gene_id['gene_id'])
gene_bed = gene_bed.ix[:,['chr', 'g_str', 'g_end', 'gene_id','g_score','g_dir']]
gene_bed=gene_bed.drop_duplicates(subset=['g_str','g_end'],keep='first')
gene_bed=gene_bed.sort_values(['chr','g_str'],ascending=[True,True])
gene_bed=gene_bed.drop_duplicates(subset=['g_str'],keep='last')
gene_group=gene_bed.groupby(['chr','gene_id','g_score','g_dir']).agg({'g_str':'min', 'g_end':'max'}).reset_index()
gene_group = gene_group.drop_duplicates(subset=['g_str','g_end'],keep='first')
gene_body=gene_group.sort_values(['chr','g_str'],ascending=[True,True])
gene_body=gene_body.drop_duplicates(subset=['g_str'],keep='last')
gene_body = gene_body.ix[:,['chr', 'g_str', 'g_end', 'gene_id','g_score','g_dir']]
gene_body=gene_body[~gene_body.gene_id.str.contains('MI')]
gene_body.to_csv(input_gene+'.gtf'+'_gene_body_bed6.bed', sep='\t',index=False, header=None)

genome_bp=gene_body.groupby(['chr']).agg({'g_end':'max'}).reset_index()
genome_bp = genome_bp['g_end'].sum()

#find promoter.bed
gene_body['pro_str'] = np.where(gene_body.g_dir == '+', gene_body.g_str - 2000, gene_body.g_end - 0)
gene_body['pro_end'] = np.where(gene_body.g_dir == '+', gene_body.g_str + 0, gene_body.g_end + 2000)
num = gene_body._get_numeric_data()
num[num<0]=0
gene_promoter = gene_body.ix[:, ['chr','pro_str','pro_end','gene_id','g_score','g_dir']]
gene_promoter.columns=['chr','g_str','g_end','gene_id','g_score','g_dir']

gene_promoter.to_csv(input_gene+'.gtf'+"_gene_promoter_bed6.bed", sep='\t',index=False, header=None)



#find igr.bed
gene_body['igr_str'] = gene_body['g_end'].shift(1).fillna(0).astype(int)+1
gene_body['igr_end'] = gene_body['g_str']-1
gene_body['igr_chr'] = gene_body['chr'].shift(1).fillna('chr1')
igrcol = gene_body.ix[:,('igr_chr','g_str','igr_str','igr_end')]
igrcol.columns = ['chr', 'g_str', 'igr_str', 'igr_end']
genecol=gene_body.ix[:,['chr','g_str','g_end','gene_id','g_score','g_dir']]
geneigr = pd.merge(genecol, igrcol, how='left', on=['chr', 'g_str'])
geneigr.igr_str=geneigr.igr_str.fillna(0).astype(int)
geneigr.igr_end=geneigr.igr_end.fillna(geneigr.g_str-1).astype(int)
geneigr = geneigr.ix[:,('chr', 'igr_str','igr_end', 'gene_id','g_score', 'g_dir')]
geneigr = geneigr[geneigr['igr_str']<geneigr['igr_end']]
geneigr=geneigr.drop_duplicates(subset=['igr_str','igr_end'],keep='first')
geneigr.to_csv(input_gene+'.gtf'+"_gene_igr_bed6.bed", sep="\t", index=False, header=None)


for i in annotation_name:
#	gene_anootation_file = pd.read_csv(input_gene+'.gtf'+'_'+i+'_bed6.bed', header=None, sep="\t")
#	gene_anootation_file.columns=['chr','g_str','g_end','gene_id','g_id','g_dir']
#	gene_anootation_file=gene_anootation_file.drop_duplicates(subset=['g_str', 'g_end'], keep='first')
#	gene_anootation_file.to_csv(input_gene+'.gtf'+'_'+i+'_bed6.bed', sep='\t',index=False, header=None)
	subprocess.call('''bedtools sort -i %s|bedtools merge -c 4,5,6 -o collapse,collapse,collapse >%s '''%(input_gene+'.gtf'+'_'+i+'_bed6.bed',input_gene+'.gtf'+'_'+i+'_merge.bed'),shell=True)


#peak bp count

def peak_bp(peak):
	peak = pd.read_csv(peak, header=None, sep="\t").ix[:,0:5]
	peak.columns = ['chr', 'peak_str', 'peak_end', 'peak_id', 'peak_value', 'peak_dir']
	peak=peak.drop_duplicates(subset=['peak_str', 'peak_end'], keep='first')
	peak['bp'] = (peak.peak_end - peak.peak_str)
	peak_bp = peak.bp.sum()
	return peak_bp



#annotation bp count
def ano_bp(anno):
	ano = pd.read_csv(input_gene+'.gtf'+'_'+anno+'_merge.bed', header=None, sep="\t")
	ano.columns=['chr','g_str','g_end','gene_id','g_id','g_dir']
	ano=ano.drop_duplicates(subset=['g_str', 'g_end'], keep='first')
	ano['bp'] = (ano.g_end - ano.g_str)
	ano_bp = ano.bp.sum()
	return ano_bp



print "---------------------------------------"
print "|Making annotation_peak_associate file|"
print "---------------------------------------"

for i in annotation_name:
	for j in peak_name:
		subprocess.call('''bedtools intersect -nonamecheck -a %s -b %s -wo > %s'''%(input_gene+'.gtf'+'_'+i+'_merge.bed',j,j+'_'+i+'.txt'),shell=True)

print "-------------------------------------"
print "|Annotation_peak_associate file Done|"
print "-------------------------------------"

#annotation_peak bp count
def annopeakbp(peak,anno):
	anno_peak_asso = pd.read_csv(peak+'_'+anno+'.txt', header=None, sep="\t")
	anno_peak_asso_bp = anno_peak_asso[len(anno_peak_asso.columns)-1].sum()
	anno_peak_asso_bp = float(anno_peak_asso_bp)
	return anno_peak_asso_bp


#making Enrichment Graph

def enrichment_num(peak,anno):
	enrichment=math.log((annopeakbp(peak,anno)/peak_bp(peak))/(ano_bp(anno)/genome_bp),2)
	return enrichment


#making associate table
def associate(inpeak):
	peak = pd.read_csv(inpeak, header=None, sep="\t").ix[:,0:5]
	gene_body = pd.read_csv(input_gene+'.gtf'+'_gene_body_merge.bed', header=None, sep="\t")
	peak.columns = ['chr', 'peak_str', 'peak_end', 'peak_name','peak_value','peak_dir']
	gene_body.columns = ['chr', 'gbed_str', 'gbed_end', 'gene_id', 'gene_value', "gene_dir"]
	gene_body['pro_str'] = np.where(gene_body.gene_dir == '+', gene_body.gbed_str -2000, gene_body.gbed_end -0)
	gene_body['pro_end'] = np.where(gene_body.gene_dir == '+', gene_body.gbed_str +0, gene_body.gbed_end +2000)
	combined = pd.merge(gene_body, peak, on='chr')
	combined['Genebody'] = np.where((combined.gbed_str < combined.peak_end) & (combined.gbed_end > combined.peak_str), 1, 0)
	combined['Promoter'] = np.where((combined.pro_str < combined.peak_end) & (combined.pro_end > combined.peak_str), 1, 0)
	summary = combined[(combined.Promoter > 0) | (combined.Genebody > 0)]
	s1 = summary.drop(summary.columns[6:13], axis = 1).drop(summary.columns[4], axis = 1)
	s1_group=s1.groupby(['gene_id', 'chr', 'gbed_str', 'gbed_end', 'gene_dir']).agg({'Genebody':'sum', 'Promoter':'sum'}).reset_index().sort_values(["chr","gbed_str"])
	s1_group.to_csv(inpeak+"_gene"+"_summary_table", sep='\t',index=False)

#peak bed to bedgraph to bigWig and heatmap
#def peak_bedgraph(peak):
	#inpeak = pd.read_csv(peak, header=None, sep="\t")
	#inpeak=inpeak.ix[:,0:2]
	#inpeak[4]=1
	#inpeak.to_csv(peak+'.bedGraph',index=None, header=None, sep="\t")
	#subprocess.call('''bedGraphToBigWig %s https://genome.ucsc.edu/goldenpath/help/hg19.chrom.sizes  %s'''%(peak+'.bedGraph',peak+'.bw'),shell=True)
	#subprocess.call('''computeMatrix scale-regions -S %s -R %s --missingDataAsZero -bs 10 -a 1000 -b 1000 -out %s --outFileNameMatrix %s'''%(peak+'.bw',input_gene+'.gtf'+'_gene_body_merge.bed',peak+'gene_body'+'.matrix.gz',peak+'gene_body'+'.matrix.txt'),shell=True)
	#subprocess.call('''plotHeatmap -m %s -out %s --legendLocation none'''%(peak+'gene_body'+'.matrix.gz',peak+'gene_body_heatmap.png'),shell=True)
	

def coverage_heatmap(coverage):
	subprocess.call('''computeMatrix scale-regions -S %s -R %s --missingDataAsZero -bs 10 -a 1000 -b 1000 -out %s --outFileNameMatrix %s'''%(coverage,input_gene+'.gtf'+'_gene_body_merge.bed',coverage+'gene_body'+'.matrix.gz',coverage+'gene_body'+'.matrix.txt'),shell=True)
	subprocess.call('''plotHeatmap -m %s -out %s --legendLocation none'''%(coverage+'gene_body'+'.matrix.gz',coverage+'gene_body_heatmap.png'),shell=True)

#making table and peak_bed to bedgraph
print "-----------------------------------------------"
print "|Making Summary Table and Peak Density Heatmap|"
print "-----------------------------------------------"
for i in peak_name:
	summary_table = associate(i)
	#peaktobedgraph=peak_bedgraph(i)

for i in bam_coverage_name:
	bamcoveragegraph=coverage_heatmap(i)

print "*--------------------------------------------*"
print "| Summary Table and Peak Density Heatmap Done|"
print "*--------------------------------------------*"



print "\n""Making plot""\n"
plt.style.use('ggplot')
annotationname = ['Promoter','Genebody','Exon','Intron','5UTR','CDS','3UTR','IGR']
annotationname_index = range(len(annotationname))
for i in peak_name:
	enrichment_data = []
	for j in annotation_name:
		enrichment_data.append(enrichment_num(i,j))
	fold_enrich = enrichment_data
	fig = plt.figure()
	ax1 = fig.add_subplot(1,1,1)
	ax1.bar(annotationname_index, fold_enrich, align='center',color='darkblue')
	ax1.xaxis.set_ticks_position('bottom')
	ax1.yaxis.set_ticks_position('left')
	plt.xticks(annotationname_index, annotationname, fontsize='small')
	plt.ylabel("Fold Enrichment (log2)")
	plt.title(i+'_Fold_Enrichment')
	plt.savefig(i+'_Fold_Enrichment'+'.png',dpi=400,bbox_inches='tight')
	plt.close(fig)


#Making tophat junction for IGV
subprocess.call('''samtools view %s|awk '{if ($7 == "=" && $9>0){print $1"\t"$3"\t"$4"\t"$7"\t"$8"\t"$9}} ' >%s'''%(input_bam,input_bam+'paired'), shell="True")

with open(input_bam+'_junction.bed', 'w') as c:
	track_name = '''track name=junctions description="TopHat junctions"'''
	blank=""
	c.write("%s\n%s"%(track_name,blank))

c1_pe = pd.read_csv(input_bam+'paired', header=None, sep="\t")
c1_pe[7] = c1_pe[2]+c1_pe[4]
c1_pe = c1_pe.ix[:,(1,2,4,0)]
c1_pe.columns=['chr','str','end','name']
bin_size = int(10)
c1_pe.str=c1_pe.str//bin_size*bin_size
c1_pe.end=c1_pe.end//bin_size*bin_size
c1_score=c1_pe.groupby(['chr','str','end']).count().reset_index()
c1_score['chrname']=c1_score.chr+c1_score.str.map(str)
c1_score['dir']='+'
c1_score['thickstart']=c1_score.str
c1_score['thickend']=c1_score.end
c1_score['block_count']=2
c1_score['block_size']="1,1"
c1_score['location']=c1_score.end-c1_score.str-1

#rgb_200_up_below
c1_score['rgb']=np.where(c1_score['location']>200,'255,0,0','0,0,255')
c1_score['zero']=0
c1_score['block_location']=c1_score['zero'].map(str)+","+c1_score['location'].map(str)
c1_junction_pd = c1_score.ix[:,('chr','str','end','chrname','name','dir','thickstart','thickend','rgb','block_count','block_size','block_location')]
c1_junction_pd.to_csv(input_bam+'_junction.bed',mode='a', header=None, index=None, sep="\t")

tend = time.time()#time stop

print "---------- %s seconds ----------" %(tend-tstart)









