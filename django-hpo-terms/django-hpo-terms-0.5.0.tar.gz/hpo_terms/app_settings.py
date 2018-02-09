from django.conf import settings


hpo_purl = 'http://purl.obolibrary.org/obo/hp.obo'
HPO_URL = getattr(settings, 'HPO_URL', hpo_purl)

hpo_diseases = 'http://compbio.charite.de/jenkins/job/hpo.annotations/'
hpo_diseases += 'lastSuccessfulBuild/artifact/misc/phenotype_annotation.tab'
HPO_DISEASES_URL = getattr(settings, 'HPO_PHENOTYPES_URL', hpo_diseases)

hpo_disease_genes = 'http://compbio.charite.de/jenkins/job/hpo.annotations.monthly/'
hpo_disease_genes += 'lastSuccessfulBuild/artifact/annotation/genes_to_diseases.txt'
HPO_DISEASE_GENES_URL = getattr(settings, 'HPO_DISEASE_GENES_URL', hpo_disease_genes)
