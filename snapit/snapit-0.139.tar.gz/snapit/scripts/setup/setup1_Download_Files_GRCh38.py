"""
setup1_Download_Files_GRCh38.py
This downloads all initial files necessary for the rest of setup
1. Ensembl human CDS annotation
2. Human ID mapping file
3. Human genome
4. Gene description file
5. RefSeq Human protein database
6. NCBI BLAST+ API
7. TMHMM Version 2.0 API
"""

from os import path, makedirs, remove
import gzip
from urllib.request import urlretrieve
from biomart import BiomartServer
import subprocess

def does_file_exist(file_location, make = True):
    try:
        open(file_location, "r")
        return True
    except FileNotFoundError:
        if make == True:
            open(file_location, "w")
        return False

file_folder = path.dirname(path.abspath(__file__)).replace("/scripts/setup", "")
folder_list_to_make = ["/reference_data", "/reference_data/data_to_run_main", "/reference_data/initial_download", "/reference_data/setup", "/Install", "/Temp"]

for folder in folder_list_to_make:
    if not path.exists(file_folder + folder):
        makedirs(file_folder + folder)

print("\nDownloading...\n"
      "1\tHomo_sapiens.GRCh38.cds.all.fa\n"
      "\tThis is found from Ensembl under CDS\n"
      "\thttp://uswest.ensembl.org/info/data/ftp/index.html\n"
      "2\tHUMAN_9606_idmapping_selected.txt\n"
      "\tThis is found from UniProt\n"
      "\tftp://ftp.uniprot.org/pub/databases/uniprot/current_release/\n"
      "\tknowledgebase/idmapping/by_organism/"
      "HUMAN_9606_idmapping_selected.tab.gz\n"
      "3\thg38.fa.gz\n"
      "\tThis is found from UCSC\n"
      "\thttp://hgdownload.soe.ucsc.edu/goldenPath/hg38/bigZips/\n"
      "4\tGene_Description.txt\n"
      "\tThis is found from Ensembl Biomart\n\n"
      "We will place all four files into /reference_data/initial_download/\n"
      "This will take ~4G of space.")

# Download human genome
hg38_file = file_folder + "/reference_data/data_to_run_main/hg38.fa"
if not does_file_exist(hg38_file, make=False):
    print("\nDownloading the human genome...")
    hg38_gz = file_folder + "/reference_data/data_to_run_main/hg38.fa.gz"
    hg38_link = "http://hgdownload.soe.ucsc.edu/goldenPath/hg38/bigZips/hg38.fa.gz"
    urlretrieve(hg38_link, hg38_gz)
    # Unzip
    with gzip.open(hg38_gz, 'rb') as f, \
        open(hg38_file, "w") as output:
            for line in f:
                line = line.decode("utf-8")
                output.write(line)
    # Delete zipped file
    remove(hg38_gz)

# Download Ensembl human CDS annotation
Ensembl_ENSG_CDS_file = file_folder + "/reference_data/initial_download/Homo_sapiens.GRCh38.cds.all.fa"
if not does_file_exist(Ensembl_ENSG_CDS_file, make=False):
    print("Downloading all CDS from Ensembl...")
    Ensembl_ENSG_CDS_gz = file_folder + "/reference_data/initial_download/Homo_sapiens.GRCh38.cds.all.fa.gz"
    Ensembl_ENSG_CDS_link = "ftp://ftp.ensembl.org/pub/release-87/fasta/homo_sapiens/cds/Homo_sapiens.GRCh38.cds.all.fa.gz"
    urlretrieve(Ensembl_ENSG_CDS_link, Ensembl_ENSG_CDS_gz)
    with gzip.open(Ensembl_ENSG_CDS_gz, 'rb') as f, \
        open(Ensembl_ENSG_CDS_file, "w") as output:
        file_content = f.read().decode('utf-8')
        output.write(file_content)
    # Delete zipped file
    remove(Ensembl_ENSG_CDS_gz)

# Download human mapping file
ID_mapping_file = file_folder + "/reference_data/initial_download/HUMAN_9606_idmapping_selected.txt"
if not does_file_exist(ID_mapping_file, make = False):
    print("Downloading ID mapping tool from UniProt...")
    ID_mapping_gz = file_folder + "/reference_data/initial_download/HUMAN_9606_idmapping_selected.txt.gz"
    ID_mapping_link = "ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/by_organism/HUMAN_9606_idmapping_selected.tab.gz"
    urlretrieve(ID_mapping_link, ID_mapping_gz)
    with gzip.open(ID_mapping_gz, 'rb') as f, \
        open(ID_mapping_file, "w") as output:
        file_content = f.read().decode("utf-8")
        output.write(file_content)
    # Delete zipped file
    remove(ID_mapping_gz)

# Download gene description mapping file
description_file = file_folder + "/reference_data/data_to_run_main/Gene_Description.txt"
if not does_file_exist(description_file, make = False):
    print("Downloading gene description mapping file from Ensembl...")
    attr = ['ensembl_gene_id', 'external_gene_name', 'description']
    server = BiomartServer("http://www.ensembl.org/biomart")
    hge = server.datasets['hsapiens_gene_ensembl']
    response = hge.search({'attributes': attr}, header=1)
    with open(description_file, "w") as output:
        for line in response.iter_lines():
            line = line.decode('utf-8') + "\n"
            output.write(line)

# Install BLAST and TMHMM
print("\nInstalling...\n"
      "1\tNBCI BLAST+ 2.7.1 API\n"
      "\tThis is found from NCBI\n"
      "\tftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/\n"
      "2\tTMHMM v. 2.0 API\n"
      "\tThis is found from TMHMM\n"
      "\thttp://www.cbs.dtu.dk/cgi-bin/nph-sw_request?tmhmm\n")

# Make directory for installed APIs
install_folder = file_folder + "/Install"
if not path.exists(install_folder):
	makedirs(install_folder)

# Download NCBI BLAST+ API
if not does_file_exist(install_folder + "/ncbi-blast-2.7.1+/bin/blastp", make = False):
    blast_gz = install_folder + "/ncbi-blast-2.7.1+-x64-linux.tar.gz"
    blast_link = "ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/2.7.1/ncbi-blast-2.7.1+-x64-linux.tar.gz"
    urlretrieve(blast_link, blast_gz)
    subprocess.call("cd " + install_folder + "\ntar -zxvf ncbi-blast-2.7.1+-x64-linux.tar.gz", shell = True)
    # Make directory for databases
    if not path.exists(file_folder + "/Install/ncbi-blast-2.7.1+/blastdb"):
        makedirs(file_folder + "/Install/ncbi-blast-2.7.1+/blastdb")

# Download RefSeq Human protein database (NP, XP)
refseq_file = file_folder + "/Install/ncbi-blast-2.7.1+/blastdb/human.all.protein.faa"
if not does_file_exist(refseq_file, make = False):
    print("\nDownloading RefSeq Human protein database (NP, XP)...")
    with open(refseq_file, "a+") as output:
        for x in range(1,39):
            refseq_gz = file_folder + "/reference_data/initial_download/human." + str(x) + ".protein.faa.gz"
            refseq_link = "ftp://ftp.ncbi.nlm.nih.gov/refseq/H_sapiens/mRNA_Prot/human." + str(x) + ".protein.faa.gz"
            urlretrieve(refseq_link, refseq_gz)
            with gzip.open(refseq_gz, 'rb') as f:
                file_content = f.read().decode("utf-8")
                output.write(file_content)
            # Delete zipped file
            remove(refseq_gz)
    subprocess.call(file_folder + "/Install/ncbi-blast-2.7.1+/bin/makeblastdb -in " + refseq_file + " -title human.all.protein.faa -parse_seqids -dbtype prot", shell = True)

# Download TMHMM v. 2.0 API
if not does_file_exist(install_folder + "/tmhmm-2.0c/bin/tmhmm", make = False):
    input("\nTMHMM requires academic permission for usage.\n"
          "To get access to the TMHMM v. 2.0 API, please visit the academic download page:\n"
          "http://www.cbs.dtu.dk/cgi-bin/nph-sw_request?tmhmm\n"
          "and enter your credentials for download access.\n\n"
          "Follow instructions to download\n"
          "'tmhmm-2.0c.Linux.tar.gz'"
          "and move/copy the file to\n'" +
          install_folder + "/'\n\n"
          "Hit enter when complete to continue with setup.\n")
    subprocess.call("cd " + install_folder + "\ntar -zxvf tmhmm-2.0c.Linux.tar.gz", shell = True)

    # Edit executable files
    with open(install_folder + "/tmhmm-2.0c/bin/tmhmm", "r+") as tmhmm,\
        open(install_folder + "/tmhmm-2.0c/bin/tmhmmformat.pl", "r+") as tmhmmformat:

        # Edit /tmhmm
        tmhmm_content = tmhmm.readlines()
        tmhmm_content[0] = '#!/usr/bin/perl\n'
        tmhmm_content[62] = '$wd = "Temp/TMHMM_$$";\n'

        # Edit /tmhmm
        tmhmm_content = tmhmm.readlines()
        tmhmm_content[0] = '#!/usr/bin/perl\n'
        tmhmm_content[23] = '$opt_short = 1;\t\t# Short output format\n'
        tmhmm_content[24] = '$opt_plot = 0;\t\t# Produce graphics\n'
        tmhmm_content[62] = '$wd = "Temp/TMHMM_$$";\n'

        # Edit /tmhmmformat.pl
        tmhmmformat_content = tmhmmformat.readlines()
        tmhmmformat_content[0] = '#!/usr/bin/perl\n'
        tmhmmformat_content[19] = '$opt_short = 1;\t\t# Short output format\n'
        tmhmmformat_content[20] = '$opt_plot = 0;\t\t# Produce graphics\n'

    # Overwrite previous files
    with open(install_folder + "/tmhmm-2.0c/bin/tmhmm", "w") as tmhmm, \
        open(install_folder + "/tmhmm-2.0c/bin/tmhmmformat.pl", "w") as tmhmmformat:
        tmhmm.writelines(tmhmm_content)
        tmhmmformat.writelines(tmhmmformat_content)
