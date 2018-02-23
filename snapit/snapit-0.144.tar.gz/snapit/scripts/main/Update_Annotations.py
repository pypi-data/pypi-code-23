"""
Update_Annotations.py
"""


from requests import get
from time import strftime
from os import path, makedirs
from csv import reader
from collections import defaultdict
import glob


def does_file_exist(file_location, make = True):
    try:
        open(file_location, "r")
    except FileNotFoundError:
        if make:
            open(file_location, "w")
        return False
    return True


# Assign update date
today = strftime("%Y%m%d")

# Set directories
folder = path.dirname(path.abspath(__file__))
folder_main = folder.replace("/scripts/main", "")
final_use_folder = folder_main + "/reference_data/data_to_run_main"
annotations_folder = folder_main + "/UniProt_Annotations/"

# Make folder for annotation if does not exist
if not path.exists(annotations_folder):
    makedirs(annotations_folder)


# Ask user to select exisiting annotation or to update annotation
update = int(input("\nWhich UniProtKb annotation would you like to use? (1/2):\n"
                   "1\tUse an existing UniProt annotation\n"
                   "2\tGet the most updated annotation?\n"))

# Make a list of the annotation folders for user to pick from
list_of_anno = glob.glob(annotations_folder + "/*/")
print("\nPlease wait while we update annotations...")
# If folder is empty, get updated annotation
if len(list_of_anno) == 0:
    update = 2

# Use existing UniProtKb annotation
if update == 1:
    print("\nSelect the desired annotation date:")
    # List dates of all existing annotation
    for index, anno_date in enumerate(list_of_anno):
        anno_date = anno_date.replace(annotations_folder, "").replace("/", "")
        year_month_date = anno_date[0:4] + "-" + anno_date[4:6] + "-" + anno_date[6:8]
        print(str(index + 1) + "\t" + year_month_date)
    # Ask user to select annotation
    selected_anno = int(input()) - 1
    # Set annotation folder to selection
    annotation_folder = list_of_anno[selected_anno]
    date = annotation_folder.replace(annotations_folder, "").replace("/", "")

# Get most updated annotation
if update == 2:
    today_annotations_folder = folder_main + "/UniProt_Annotations/" + today + "/"
    if not path.exists(today_annotations_folder):
        makedirs(today_annotations_folder)
    annotation_folder = today_annotations_folder
    date = today


# Annotation files to write from keywords for 'cell surface' proteins
update_list = ["UniProt_Topological_Domain_Annotation",
               "UniProt_Single_Pass_Type_I_Annotation",
               "UniProt_Single_Pass_Type_II_Annotation",
               "UniProt_Single_Pass_Type_III_Annotation",
               "UniProt_Single_Pass_Type_IV_Annotation",
               "UniProt_Multi_Pass_Annotation",
               "UniProt_Cell_Envelope_Annotation",
               "UniProt_Cell_Junction_Annotation",
               "UniProt_Cell_Membrane_Annotation",
               "UniProt_Cell_Surface_Annotation",
               "UniProt_Extracellular_Side_Annotation",
               "UniProt_Extracellular_Space_Annotation",
               "UniProt_GPI_Anchor_Annotation",
               "UniProt_Lipid_Anchor_Annotation",
               "UniProt_Secreted_Annotation"]

file_list = []
# Append date to filename
for file_simp in update_list:
    file_name = annotation_folder + file_simp + "_" + date + ".txt"
    file_list.append(file_name)

Genes_with_UniProt_Topological_Domain_Annotation = file_list[0]
Genes_with_UniProt_Single_Pass_Type_I_Annotation = file_list[1]
Genes_with_UniProt_Single_Pass_Type_II_Annotation = file_list[2]
Genes_with_UniProt_Single_Pass_Type_III_Annotation = file_list[3]
Genes_with_UniProt_Single_Pass_Type_IV_Annotation = file_list[4]
Genes_with_UniProt_Multi_Pass_Annotation = file_list[5]
Genes_with_UniProt_Cell_Envelope_Annotation = file_list[6]
Genes_with_UniProt_Cell_Junction_Annotation = file_list[7]
Genes_with_UniProt_Cell_Membrane_Annotation = file_list[8]
Genes_with_UniProt_Cell_Surface_Annotation = file_list[9]
Genes_with_UniProt_Extracellular_Side_Annotation = file_list[10]
Genes_with_UniProt_Extracellular_Space_Annotation = file_list[11]
Genes_with_UniProt_GPI_Anchor_Annotation = file_list[12]
Genes_with_UniProt_Lipid_Anchor_Annotation = file_list[13]
Genes_with_UniProt_Secreted_Annotation = file_list[14]


# Extract annotations from proteins classified under each 'cell surface' category
annotations_to_update = []
for file in file_list:
    if not does_file_exist(file, make = False):
        annotations_to_update.append(file)

# Annotation is found by searching subcellular localization key term and human organism on UniProtKb and downloading all results
if annotations_to_update != []:
    print("Updating annotations from UniProt...")
    for file in annotations_to_update:
        if file == file_list[0]:
            # Genes with "topological domain" annotated
            topological_annotation_link = "http://www.uniprot.org/uniprot/?sort=score&desc=&compress=no&query=%22topological%20domain%22&fil=organism:%22Homo%20sapiens%20(Human)%20[9606]%22&format=tab&force=yes&columns=id,entry%20name,reviewed,protein%20names,genes,organism,length,feature(TOPOLOGICAL%20DOMAIN),feature(TRANSMEMBRANE),feature(INTRAMEMBRANE),comment(SUBCELLULAR%20LOCATION)"
            topological_domain = get(topological_annotation_link).text
            with open(file, "w") as f:
                f.write(topological_domain)
        elif file == file_list[1]:
            # Genes with single-pass membrane type I
            #single_pass_type_I_search = "http://www.uniprot.org/uniprot/?query=locations%3A%28location%3A%22Single-pass+type+I+membrane+protein+%5BSL-9905%5D%22%29+AND+organism%3A%22Homo+sapiens+%28Human%29+%5B9606%5D%22&sort=score"
            single_pass_type_I_link = "http://www.uniprot.org/uniprot/?sort=score&desc=&compress=no&query=locations:(location:%22Single-pass%20type%20I%20membrane%20protein%20[SL-9905]%22)%20AND%20organism:%22Homo%20sapiens%20(Human)%20[9606]%22&fil=&format=tab&force=yes&columns=id,entry%20name,reviewed,protein%20names,genes,organism,length,feature(TOPOLOGICAL%20DOMAIN),feature(TRANSMEMBRANE),feature(INTRAMEMBRANE),comment(SUBCELLULAR%20LOCATION)"
            single_pass_type_I = get(single_pass_type_I_link).text
            with open(file, "w") as f:
                f.write(single_pass_type_I)
        elif file == file_list[2]:
            # Genes with single-pass membrane type II
            #single_pass_type_II_search = "http://www.uniprot.org/uniprot/?query=locations%3A%28location%3A%22Single-pass+type+II+membrane+protein+%5BSL-9906%5D%22%29+AND+organism%3A%22Homo+sapiens+%28Human%29+%5B9606%5D%22&sort=score"
            single_pass_type_II_link = "http://www.uniprot.org/uniprot/?sort=score&desc=&compress=no&query=locations:(location:%22Single-pass%20type%20II%20membrane%20protein%20[SL-9906]%22)%20AND%20organism:%22Homo%20sapiens%20(Human)%20[9606]%22&fil=&format=tab&force=yes&columns=id,entry%20name,reviewed,protein%20names,genes,organism,length,feature(TOPOLOGICAL%20DOMAIN),feature(TRANSMEMBRANE),feature(INTRAMEMBRANE),comment(SUBCELLULAR%20LOCATION)"
            single_pass_type_II = get(single_pass_type_II_link).text
            with open(file, "w") as f:
                f.write(single_pass_type_II)
        elif file == file_list[3]:
            # Genes with single-pass membrane type III
            #single_pass_type_III_search = "http://www.uniprot.org/uniprot/?query=locations%3A%28location%3A%22Single-pass+type+III+membrane+protein+%5BSL-9907%5D%22%29+AND+organism%3A%22Homo+sapiens+%28Human%29+%5B9606%5D%22&sort=score"
            single_pass_type_III_link = "http://www.uniprot.org/uniprot/?sort=score&desc=&compress=no&query=locations:(location:%22Single-pass%20type%20III%20membrane%20protein%20[SL-9907]%22)%20AND%20organism:%22Homo%20sapiens%20(Human)%20[9606]%22&fil=&format=tab&force=yes&columns=id,entry%20name,reviewed,protein%20names,genes,organism,length,feature(TOPOLOGICAL%20DOMAIN),feature(TRANSMEMBRANE),feature(INTRAMEMBRANE),comment(SUBCELLULAR%20LOCATION)"
            single_pass_type_III = get(single_pass_type_III_link).text
            with open(file, "w") as f:
                f.write(single_pass_type_III)
        elif file == file_list[4]:
            # Genes with single-pass membrane type IV
            #single_pass_type_IV_search = "http://www.uniprot.org/uniprot/?query=locations:(location:%22Single-pass%20type%20IV%20membrane%20protein%20[SL-9908]%22)&fil=organism%3A%22Homo+sapiens+%28Human%29+%5B9606%5D%22&sort=score"
            single_pass_type_IV_link = "http://www.uniprot.org/uniprot/?sort=score&desc=&compress=no&query=locations:(location:%22Single-pass%20type%20IV%20membrane%20protein%20[SL-9908]%22)&fil=organism:%22Homo%20sapiens%20(Human)%20[9606]%22&format=tab&force=yes&columns=id,entry%20name,reviewed,protein%20names,genes,organism,length,feature(TOPOLOGICAL%20DOMAIN),feature(TRANSMEMBRANE),feature(INTRAMEMBRANE),comment(SUBCELLULAR%20LOCATION)"
            single_pass_type_IV = get(single_pass_type_IV_link).text
            with open(file, "w") as f:
                f.write(single_pass_type_IV)
        elif file == file_list[5]:
            # Genes with multi-pass membrane
            #multi_pass_search = "http://www.uniprot.org/uniprot/?query=locations%3A%28location%3A%22Multi-pass+membrane+protein+%5BSL-9909%5D%22%29+AND+organism%3A%22Homo+sapiens+%28Human%29+%5B9606%5D%22&sort=score"
            multi_pass_link = "http://www.uniprot.org/uniprot/?sort=score&desc=&compress=no&query=locations:(location:%22Multi-pass%20membrane%20protein%20[SL-9909]%22)%20AND%20organism:%22Homo%20sapiens%20(Human)%20[9606]%22&fil=&format=tab&force=yes&columns=id,entry%20name,reviewed,protein%20names,genes,organism,length,feature(TOPOLOGICAL%20DOMAIN),feature(TRANSMEMBRANE),feature(INTRAMEMBRANE),comment(SUBCELLULAR%20LOCATION)"
            multi_pass = get(multi_pass_link).text
            with open(file, "w") as f:
                f.write(multi_pass)
        elif file == file_list[6]:
            # Genes with cell envelope
            #cell_envelope_search = "http://www.uniprot.org/uniprot/?query=locations:(location:%22Cell%20envelope%20[SL-0036]%22)&fil=organism%3A%22Homo+sapiens+%28Human%29+%5B9606%5D%22"
            cell_envelope_link = "http://www.uniprot.org/uniprot/?sort=score&desc=&compress=no&query=locations:(location:%22Cell%20envelope%20[SL-0036]%22)&fil=organism:%22Homo%20sapiens%20(Human)%20[9606]%22&format=tab&force=yes&columns=id,entry%20name,reviewed,protein%20names,genes,organism,length,feature(TOPOLOGICAL%20DOMAIN),feature(TRANSMEMBRANE),feature(INTRAMEMBRANE),comment(SUBCELLULAR%20LOCATION)"
            cell_envelope = get(cell_envelope_link).text
            with open(file, "w") as f:
                f.write(cell_envelope)
        elif file == file_list[7]:
            # Genes with cell junction
            #cell_junction_search = "http://www.uniprot.org/uniprot/?query=locations:(location:%22Cell%20junction%20[SL-0038]%22)&fil=organism%3A%22Homo+sapiens+%28Human%29+%5B9606%5D%22&sort=score"
            cell_junction_link = "http://www.uniprot.org/uniprot/?sort=score&desc=&compress=no&query=locations:(location:%22Cell%20junction%20[SL-0038]%22)&fil=organism:%22Homo%20sapiens%20(Human)%20[9606]%22&format=tab&force=yes&columns=id,entry%20name,reviewed,protein%20names,genes,organism,length,feature(TOPOLOGICAL%20DOMAIN),feature(TRANSMEMBRANE),feature(INTRAMEMBRANE),comment(SUBCELLULAR%20LOCATION)"
            cell_junction = get(cell_junction_link).text
            with open(file, "w") as f:
                f.write(cell_junction)
        elif file == file_list[8]:
            # Genes with cell membrane
            #cell_membrane_search = "http://www.uniprot.org/uniprot/?query=locations:(location:%22Cell%20membrane%20[SL-0039]%22)&fil=organism%3A%22Homo+sapiens+%28Human%29+%5B9606%5D%22&sort=score"
            cell_membrane_link = "http://www.uniprot.org/uniprot/?sort=score&desc=&compress=no&query=locations:(location:%22Cell%20membrane%20[SL-0039]%22)&fil=organism:%22Homo%20sapiens%20(Human)%20[9606]%22&format=tab&force=yes&columns=id,entry%20name,reviewed,protein%20names,genes,organism,length,feature(TOPOLOGICAL%20DOMAIN),feature(TRANSMEMBRANE),feature(INTRAMEMBRANE),comment(SUBCELLULAR%20LOCATION)"
            cell_membrane = get(cell_membrane_link).text
            with open(file, "w") as f:
                f.write(cell_membrane)
        elif file == file_list[9]:
            # Genes with cell surface
            #cell_surface_search = "http://www.uniprot.org/uniprot/?query=locations:(location:%22Cell%20surface%20[SL-0310]%22)&fil=organism%3A%22Homo+sapiens+%28Human%29+%5B9606%5D%22&sort=score"
            cell_surface_link = "http://www.uniprot.org/uniprot/?sort=score&desc=&compress=no&query=locations:(location:%22Cell%20surface%20[SL-0310]%22)&fil=organism:%22Homo%20sapiens%20(Human)%20[9606]%22&format=tab&force=yes&columns=id,entry%20name,reviewed,protein%20names,genes,organism,length,feature(TOPOLOGICAL%20DOMAIN),feature(TRANSMEMBRANE),feature(INTRAMEMBRANE),comment(SUBCELLULAR%20LOCATION)"
            cell_surface = get(cell_surface_link).text
            with open(file, "w") as f:
                f.write(cell_surface)
        elif file == file_list[10]:
            # Genes with extracellular side
            #extracellular_side_search = "http://www.uniprot.org/uniprot/?query=locations:(location:%22Extracellular%20side%20[SL-9911]%22)&fil=organism%3A%22Homo+sapiens+%28Human%29+%5B9606%5D%22&sort=score"
            extracellular_side_link = "http://www.uniprot.org/uniprot/?sort=score&desc=&compress=no&query=locations:(location:%22Extracellular%20side%20[SL-9911]%22)&fil=organism:%22Homo%20sapiens%20(Human)%20[9606]%22&format=tab&force=yes&columns=id,entry%20name,reviewed,protein%20names,genes,organism,length,feature(TOPOLOGICAL%20DOMAIN),feature(TRANSMEMBRANE),feature(INTRAMEMBRANE),comment(SUBCELLULAR%20LOCATION)"
            extracellular_side = get(extracellular_side_link).text
            with open(file, "w") as f:
                f.write(extracellular_side)
        elif file == file_list[11]:
            # Genes with extracellular space
            #extracellular_space_search = "http://www.uniprot.org/uniprot/?query=locations:(location:%22Extracellular%20space%20[SL-0112]%22)&fil=organism%3A%22Homo+sapiens+%28Human%29+%5B9606%5D%22&sort=score"
            extracellular_space_link = "http://www.uniprot.org/uniprot/?sort=score&desc=&compress=no&query=locations:(location:%22Extracellular%20space%20[SL-0112]%22)&fil=organism:%22Homo%20sapiens%20(Human)%20[9606]%22&format=tab&force=yes&columns=id,entry%20name,reviewed,protein%20names,genes,organism,length,feature(TOPOLOGICAL%20DOMAIN),feature(TRANSMEMBRANE),feature(INTRAMEMBRANE),comment(SUBCELLULAR%20LOCATION)"
            extracellular_space = get(extracellular_space_link).text
            with open(file, "w") as f:
                f.write(extracellular_space)
        elif file == file_list[12]:
            # Genes with GPI anchor
            #GPI_anchor_search = "http://www.uniprot.org/uniprot/?query=locations:(location:%22GPI-anchor%20[SL-9902]%22)&fil=organism%3A%22Homo+sapiens+%28Human%29+%5B9606%5D%22&sort=score"
            GPI_anchor_link = "http://www.uniprot.org/uniprot/?sort=score&desc=&compress=no&query=locations:(location:%22GPI-anchor%20[SL-9902]%22)&fil=organism:%22Homo%20sapiens%20(Human)%20[9606]%22&format=tab&force=yes&columns=id,entry%20name,reviewed,protein%20names,genes,organism,length,feature(TOPOLOGICAL%20DOMAIN),feature(TRANSMEMBRANE),feature(INTRAMEMBRANE),comment(SUBCELLULAR%20LOCATION)"
            GPI_anchor = get(GPI_anchor_link).text
            with open(file, "w") as f:
                f.write(GPI_anchor)
        elif file == file_list[13]:
            # Genes with lipid anchor
            #lipid_anchor_search = "http://www.uniprot.org/uniprot/?query=locations:(location:%22Lipid-anchor%20[SL-9901]%22)&fil=organism%3A%22Homo+sapiens+%28Human%29+%5B9606%5D%22&sort=score"
            lipid_anchor_link = "http://www.uniprot.org/uniprot/?sort=score&desc=&compress=no&query=locations:(location:%22Lipid-anchor%20[SL-9901]%22)&fil=organism:%22Homo%20sapiens%20(Human)%20[9606]%22&format=tab&force=yes&columns=id,entry%20name,reviewed,protein%20names,genes,organism,length,feature(TOPOLOGICAL%20DOMAIN),feature(TRANSMEMBRANE),feature(INTRAMEMBRANE),comment(SUBCELLULAR%20LOCATION)"
            lipid_anchor = get(lipid_anchor_link).text
            with open(file, "w") as f:
                f.write(lipid_anchor)
        elif file == file_list[14]:
            # Genes with secreted
            #secreted_search = "http://www.uniprot.org/uniprot/?query=locations:(location:%22Secreted%20[SL-0243]%22)&fil=organism%3A%22Homo+sapiens+%28Human%29+%5B9606%5D%22&sort=score"
            secreted_link = "http://www.uniprot.org/uniprot/?sort=score&desc=&compress=no&query=locations:(location:%22Secreted%20[SL-0243]%22)&fil=organism:%22Homo%20sapiens%20(Human)%20[9606]%22&format=tab&force=yes&columns=id,entry%20name,reviewed,protein%20names,genes,organism,length,feature(TOPOLOGICAL%20DOMAIN),feature(TRANSMEMBRANE),feature(INTRAMEMBRANE),comment(SUBCELLULAR%20LOCATION)"
            secreted = get(secreted_link).text
            with open(file, "w") as f:
                f.write(secreted)
        else:
            continue


# Subset topological annotation
UniProtKb_topological_domain_file = folder_main + "/UniProt_Annotations/UniProtKb_Only_Domains.txt"
with open(UniProtKb_topological_domain_file, "w") as output:
    output.write("UniProtKb\tCytoplasmic_Domains\tTransmembrane_Domains\tExtracellular_Domains\tIntramembrane_Domains\n")

# UniProtKb to topology dictionary
UniProtKb_to_Topological_Domains_dict = defaultdict(list)
# List used to keep track of unique entries
genes_with_topo_domain_list = []


# Analyze the rest of the genes with topological domain annotation
with open(Genes_with_UniProt_Topological_Domain_Annotation, "r") as topo,\
    open(UniProtKb_topological_domain_file, "a") as output:
    topo_csv = reader(topo, delimiter = "\t")
    next(topo)
    for line in topo_csv:
        UniProtKb = str(line[0])
        # Skips entries already in the dictionary for a unique list
        if UniProtKb in genes_with_topo_domain_list:
            continue
        # Lists to store topological domains
        cytoplasmic_domains_list = []
        extracellular_domains_list = []
        transmembrane_domains_list = []
        intramembrane_domains_list = []
        # Get topological domains: 'Cytoplasmic' and 'Extracellular'
        topological_domains = line[7].replace("TOPO_DOM ","").split(".; ")
        for item in topological_domains:
            # Topological domains key terms
            cytoplasmic = " Cytoplasmic"
            extracellular = " Extracellular"
            # If protein has cytoplasmic domain, store in list
            if cytoplasmic in item:
                domain = item.partition(cytoplasmic)[0].replace(" ", "-")
                cytoplasmic_domains_list.append(domain)
            # If protein has extracellular domain, store in list
            # Confident these have true extracellular domains because we search for 'Extracellular'
            if extracellular in item:
                domain = item.partition(extracellular)[0].replace(" ", "-")
                extracellular_domains_list.append(domain)
        # Get transmembrane domains
        transmembrane_domains = line[8].replace("TRANSMEM ", "").split(".; ")
        for item in transmembrane_domains:
            if item == "":
                continue
            domain = str(item.split(' ')[0]) + "-" + str(item.split(' ')[1])
            transmembrane_domains_list.append(domain)
        # Get intramembrane domains
        intramembrane_domains = line[9].replace("INTRAMEM ", "").split(".; ")
        for item in intramembrane_domains:
            if item == "":
                continue
            # If protein has intramembrane domain, store in list
            domain = str(item.split(' ')[0]) + "-" + str(item.split(' ')[1])
            intramembrane_domains_list.append(domain)
        # Proteins known to have topological annotation, add all to topological domains dictionary
        if extracellular_domains_list != [] or cytoplasmic_domains_list != [] or intramembrane_domains_list != [] or transmembrane_domains_list != []:
            genes_with_topo_domain_list.append(UniProtKb)
            UniProtKb_to_Topological_Domains_dict[UniProtKb].extend((cytoplasmic_domains_list, transmembrane_domains_list, extracellular_domains_list, intramembrane_domains_list))
            output.write(UniProtKb + "\t" + str(cytoplasmic_domains_list) + "\t" + str(transmembrane_domains_list)+ "\t" +str(extracellular_domains_list) + "\t" + str(intramembrane_domains_list) + "\n")


# Annotate extracellular/cytoplasmic domain of single pass proteins based on the transmembrane domain annotations
single_pass_file_list = file_list[1:5]
for file in single_pass_file_list:
    # N terminus of Type II and Type IV membrane proteins is cytoplasmic
    if file == Genes_with_UniProt_Single_Pass_Type_II_Annotation or file == Genes_with_UniProt_Single_Pass_Type_IV_Annotation:
        N = "Cytoplasmic"
    # N terminus of Type I and Type III membrane proteins is extramembrane, termed and considered 'extracellular' until better annotation is available
    if file == Genes_with_UniProt_Single_Pass_Type_I_Annotation or file == Genes_with_UniProt_Single_Pass_Type_III_Annotation:
        N = "Extracellular"
    # Open each of the separate single pass membrane protein files
    with open(file, "r") as single_pass_file, \
        open(UniProtKb_topological_domain_file, "a") as output:
        single_pass_file_csv = reader(single_pass_file, delimiter = "\t")
        next(single_pass_file)
        for line in single_pass_file_csv:
            UniProtKb = str(line[0])
            if UniProtKb in genes_with_topo_domain_list:
                continue
            length = int(line[6])
            # Lists to store topological domains
            cytoplasmic_domains_list = []
            extracellular_domains_list = []
            transmembrane_domains_list = []
            intramembrane_domains_list = []
            # Get topological domains: 'Cytoplasmic' and 'Extracellular'
            topological_domains = line[7].replace("TOPO_DOM ", "").split(".; ")
            for item in topological_domains:
                # Topological domains key terms
                cytoplasmic = " Cytoplasmic"
                extracellular = " Extracellular"
                # If protein has cytoplasmic domain, store in list
                if cytoplasmic in item:
                    domain = item.partition(cytoplasmic)[0].replace(" ", "-")
                    cytoplasmic_domains_list.append(domain)
                # If protein has extracellular domain, store in list
                # Confident these have true extracellular domains because we search for 'Extracellular'
                if extracellular in item:
                    domain = item.partition(extracellular)[0].replace(" ", "-")
                    extracellular_domains_list.append(domain)
            # Get transmembrane domains
            transmembrane_domains = line[8].replace("TRANSMEM ", "").split(".; ")
            for item in transmembrane_domains:
                if item == "":
                    continue
                # If protein has transmembrane domain, store in list
                domain = str(item.split(' ')[0]) + "-" + str(item.split(' ')[1])
                transmembrane_domains_list.append(domain)

            # Use transmembrane annotation to infer topological domain
            # If transmembrane domains list only has one entry (expected for single pass membrane proteins)
            if transmembrane_domains_list != [] and len(transmembrane_domains_list) == 1:
                transmembrane_start = int(transmembrane_domains_list[0].partition("-")[0])
                transmembrane_end = int(transmembrane_domains_list[0].partition("-")[2])
                # Use membrane protein type and transmembrane domain annotation to infer cytoplasmic domain
                if cytoplasmic_domains_list == []:
                    if N == "Extracellular":
                        cytoplasmic_domain_inferred_start = transmembrane_end + 1
                        cytoplasmic_domain_inferred_end = length
                        cytoplasmic_domains_list.append(str(cytoplasmic_domain_inferred_start) + "-" + str(cytoplasmic_domain_inferred_end))
                    if N == "Intracellular":
                        cytoplasmic_domain_inferred_start = 1
                        cytoplasmic_domain_inferred_end = transmembrane_start - 1
                        cytoplasmic_domains_list.append(str(cytoplasmic_domain_inferred_start) + "-" + str(cytoplasmic_domain_inferred_end))
                # Use membrane protein type and transmembrane domain annotation to infer extramembrane domain
                # These are not necessarily true extracellular domains
                if extracellular_domains_list == []:
                    if N == "Intracellular":
                        extracellular_domain_inferred_start = transmembrane_end + 1
                        extracellular_domain_inferred_end = length
                        extracellular_domains_list.append(
                            str(extracellular_domain_inferred_start) + "-" + str(extracellular_domain_inferred_end))
                    if N == "Extracellular":
                        extracellular_domain_inferred_start = 1
                        extracellular_domain_inferred_end = transmembrane_start - 1
                        extracellular_domains_list.append(
                            str(extracellular_domain_inferred_start) + "-" + str(extracellular_domain_inferred_end))

            # Get intramembrane domains
            intramembrane_domains = line[9].replace("INTRAMEM ", "").split(".; ")
            for item in intramembrane_domains:
                if item == "":
                    continue
                # If protein has intramembrane domain, store in list
                domain = str(item.split(' ')[0]) + "-" + str(item.split(' ')[1])
                intramembrane_domains_list.append(domain)
            # Topological domains required for protein to be stored in topological domains dictionary
            if extracellular_domains_list != [] or cytoplasmic_domains_list != [] or intramembrane_domains_list != [] or transmembrane_domains_list != []:
                genes_with_topo_domain_list.append(UniProtKb)
                UniProtKb_to_Topological_Domains_dict[UniProtKb].extend((cytoplasmic_domains_list, transmembrane_domains_list, extracellular_domains_list, intramembrane_domains_list))
                output.write(UniProtKb + "\t" + str(cytoplasmic_domains_list) + "\t" + str(transmembrane_domains_list) + "\t" +
                             str(extracellular_domains_list) + "\t" + str(intramembrane_domains_list) + "\n")


for file in file_list[5:15]:
    with open(file, "r") as membrane, \
        open(UniProtKb_topological_domain_file, "a") as output:
        membrane_csv = reader(membrane, delimiter = "\t")
        next(membrane)
        for line in membrane_csv:
            UniProtKb = str(line[0])
            # Skips entries already in the dictionary for a unique list
            if UniProtKb in genes_with_topo_domain_list:
                continue
            # Lists to store topological domains
            cytoplasmic_domains_list = []
            extracellular_domains_list = []
            transmembrane_domains_list = []
            intramembrane_domains_list = []
            # Get topological domains: 'Cytoplasmic' and 'Extracellular'
            topological_domains = line[7].replace("TOPO_DOM ", "").split(".; ")
            for item in topological_domains:
                # Topological domains key terms
                cytoplasmic = " Cytoplasmic"
                extracellular = " Extracellular"
                # If protein has cytoplasmic domain, store in list
                if cytoplasmic in item:
                    domain = item.partition(cytoplasmic)[0].replace(" ", "-")
                    cytoplasmic_domains_list.append(domain)
                # If protein has extracellular domain, store in list
                # Confident these have true extracellular domains because we search for 'Extracellular'
                if extracellular in item:
                    domain = item.partition(extracellular)[0].replace(" ", "-")
                    extracellular_domains_list.append(domain)
            # Get transmembrane domains
            transmembrane_domains = line[8].replace("TRANSMEM ", "").split(".; ")
            for item in transmembrane_domains:
                if item == "":
                    continue
                # If protein has transmembrane domain, store in list
                domain = str(item.split(' ')[0]) + "-" + str(item.split(' ')[1])
                transmembrane_domains_list.append(domain)
            # Get intramembrane domains
            intramembrane_domains = line[9].replace("INTRAMEM ", "").split(".; ")
            for item in intramembrane_domains:
                if item == "":
                    continue
                # If protein has intramembrane domain, store in list
                domain = str(item.split(' ')[0]) + "-" + str(item.split(' ')[1])
                intramembrane_domains_list.append(domain)
            # Topological domains required for protein to be stored in topological domains dictionary
            if extracellular_domains_list != [] or cytoplasmic_domains_list != [] or intramembrane_domains_list != [] or transmembrane_domains_list != []:
                genes_with_topo_domain_list.append(UniProtKb)
                UniProtKb_to_Topological_Domains_dict[UniProtKb].extend((cytoplasmic_domains_list, transmembrane_domains_list, extracellular_domains_list, intramembrane_domains_list))
                output.write(UniProtKb + "\t" + str(cytoplasmic_domains_list) + "\t" + str(transmembrane_domains_list) + "\t" +
                             str(extracellular_domains_list) + "\t" + str(intramembrane_domains_list) + "\n")


# Output information about the annotations of genes
notes = annotation_folder + "Notes_about_these_files.txt"
# List of 'cell surface' proteins
cell_surface_annotation_list = []
missing_topo_domain_gene_list = []
with open(notes, "w") as output:
    # All annotation files
    for file_location in file_list:
        file_name = file_location.replace(str(folder_main + "/UniProt_Annotations/"), "")
        file_protein_subcategory = file_name.partition("_")[2].partition("_Annotation")[0].replace("_", " ")
        with open(file_location, "r") as file:
            file_csv = reader(file, delimiter = "\t")
            next(file)
            # Total proteins classified as 'cell surface' (non-unique)
            total_count = 0
            # Proteins that have some topological annotation
            topo_dom_count = 0
            # Proteins without any topological annotation
            no_topo_dom_count = 0
            trans_dom_count = 0
            intra_dom_count = 0
            trans_and_intra_dom_count = 0
            for line in file_csv:
                UniProtKb = str(line[0])
                total_count += 1
                # Add all unique 'cell surface' proteins to cell surface list
                if UniProtKb not in cell_surface_annotation_list:
                    cell_surface_annotation_list.append(UniProtKb)
                # Check if 'cell surface' proteins are in topology list
                if UniProtKb in genes_with_topo_domain_list:
                    topo_dom_count += 1
                    # Count transmembrane and intramembrane domains
                    if line[8] != "":
                        trans_dom_count += 1
                    if line[9] != "":
                        intra_dom_count += 1
                    if line[8] != "" and line[9] != "":
                        trans_and_intra_dom_count += 1
                # Add 'cell surface' proteins without topological annotation to missing topology list
                elif UniProtKb not in missing_topo_domain_gene_list:
                    missing_topo_domain_gene_list.append(UniProtKb)
                    no_topo_dom_count += 1
            output.write(file_name+"\n"+ "\tThere are " + str(total_count) + " " + file_protein_subcategory + " proteins\n"
                         + "\t\t" + str(topo_dom_count) + " have topological domain annotations\n"
                         + "\t\t" + str(no_topo_dom_count) + " don't have topological domain annotations\n"
                         + "\t\t\t" + str(trans_dom_count) + " of those have transmembrane domain annotations\n"
                         + "\t\t\t" + str(intra_dom_count) + " of these have intramembrane domain annotations\n"
                         + "\t\t\t" + str(trans_and_intra_dom_count) + " of these have both transmembrane and intramembrane domain annotations\n\n")

# Get all subcellular localization annotation from UniProtKb
subcellular_location_output_folder = annotation_folder + "/Subcellular_Location/"
if not path.exists(subcellular_location_output_folder):
    makedirs(subcellular_location_output_folder)

subcellular_location_link = "http://www.uniprot.org/locations/?sort=&desc=&compress=no&query=&fil=&format=tab&force=yes&columns=id"
subcellular_location_list = get(subcellular_location_link).text.split("\n")
del subcellular_location_list[-1]
del subcellular_location_list[0]


# UniProtKb to subcellular localization dictionary
UniProtKb_to_Subcell_Loc_dict = defaultdict(list)

non_human_subcell_loc_file = annotations_folder + "/Non_Human_subcell_loc.txt"
non_human_subcell_loc_list = []
# Read existing file containing non-human subcellular localization terms
if does_file_exist(non_human_subcell_loc_file, make = True):
    with open(non_human_subcell_loc_file, "r") as non_human_subcell_loc:
        non_human_subcell_loc_csv = reader(non_human_subcell_loc, delimiter = "\t")
        for line in non_human_subcell_loc_csv:
            if line[0] == []:
                continue
            # Stores all existing annotation into list
            non_human_subcell_loc_list.append(line[0])

# Append list of non-human subcellular locations
with open(non_human_subcell_loc_file, "a+") as non_human_subcell_loc:
    # All subcellular locations from UniProtKb
    for line in subcellular_location_list:
        line = line.split("\t")
        subcellular_location = line[3]
        subcell_loc_code = line[0]
        # Check for subcellular localization file with list of proteins
        file = subcellular_location_output_folder + subcellular_location.replace(" ", "_") + "_" + today + ".txt"
        if does_file_exist(file, make = False):
            with open(file, "r") as f:
                f_csv = reader(f, delimiter = "\t")
                # For existing subcellular localization files, add proteins to subcellular localization dictionary
                for l in f_csv:
                    UniProtKb_to_Subcell_Loc_dict[l[0]].append(subcellular_location)
            continue
        # Skip if term is a non-human term
        elif subcellular_location in non_human_subcell_loc_list:
            continue
        # Annotation not updated
        else:
            link = "http://www.uniprot.org/uniprot/?sort=score&desc=&compress=no&query=locations:(location:%22" + subcellular_location.replace(" ", "%20") + "%20" + "[" + subcell_loc_code + "]" + "%22)&fil=organism:%22Homo%20sapiens%20(Human)%20[9606]%22&format=tab&force=yes&columns=id,entry%20name,reviewed,protein%20names,genes,organism,length,feature(TOPOLOGICAL%20DOMAIN),feature(TRANSMEMBRANE),feature(INTRAMEMBRANE),comment(SUBCELLULAR%20LOCATION)"
            f = get(link).text.split("\n")
            # Subcellular location does not have human proteins
            if f == ['']:
                print("\tNo gene in this category is found in humans")
                non_human_subcell_loc.write(subcellular_location + "\n")
                continue
            del f[-1]
            del f[0]
            # Write subcellular localization file and add proteins to dictionary
            with open(file, "w") as output:
                for l in f:
                    l = l.split("\t")
                    UniProtKb_to_Subcell_Loc_dict[l[0]].append(subcellular_location)
                    output.write(l[0] + "\n")