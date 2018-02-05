import sys
import logging
import json

import click
import requests

from cluspro_api import CONFIG, make_sig

logger = logging.getLogger(__name__)

URL_SCHEME = "https"
API_ENDPOINT = "/api.php"
CP_CONFIG = CONFIG['cluspro']
FORM_KEYS = [
    'username', 'receptor', 'ligand', 'jobname', 'coeffs', 'rotations',
    'antibodymode', 'othersmode','masknoncdr', 'multimers',
    'pepmot', 'pepseq', 'pepexclusion'
]
for f in ('pdb', 'chains', 'attraction', 'mask'):
    FORM_KEYS.append("rec" + f)
    FORM_KEYS.append("lig" + f)
FORM_KEYS.append("dssprec")
FORM_KEYS.append("dssplig")
OPTIONAL_FILE_FIELDS = (
    ("coeffs", "coeff_file"),
    ("rotations", "rots_file"),
    ("restraints", "restraints_file"),
    ("saxs_file", "saxs_file"),
    ("recmask", "recrepulsionfile"),
    ("ligmask", "ligrepulsionfile"),
)

@click.command('submit', short_help="Submit a job to ClusPro.")
@click.option("--username", default=CP_CONFIG['username'])
@click.option("--secret", default=CP_CONFIG['api_secret'])
@click.option("--coeffs", type=click.Path(exists=True), default=None, help="Upload coefficients file [Advanced]")
@click.option("--rotations", type=click.Path(exists=True), default=None, help="Upload rotations file [Advanced]")
@click.option("-j", "--jobname", help="Will default to job number")
@click.option("-a", "--antibodymode", is_flag=True, default=None, help="Use Antibody mode [Advanced]")
@click.option("-o", "--othersmode", is_flag=True, default=None, help="Use Others mode [Advanced]")
@click.option("--receptor", type=click.Path(exists=True), help="Upload a PDB file")
@click.option("--ligand", type=click.Path(exists=True), help="Upload a PDB file")
@click.option("--recpdb", help="4-letter PDB code")
@click.option("--ligpdb", help="4-letter PDB code")
@click.option("--pepmot", help="peptide motif [Advanced]")
@click.option("--pepseq", help="peptide sequence [Advanced]")
@click.option("--pepexclusion", help="List of PDB ids to exclude from motif search [Advanced]")
@click.option("--rec-chains", "recchains", help='chains to use, for example "A B" (in double quotes)')
@click.option("--lig-chains", "ligchains", help='chains to use, for example "A B" (in double quotes)')
@click.option("--rec-mask", "recmask", type=click.Path(exists=True), default=None, help="Receptor mask [Advanced]")
@click.option("--lig-mask", "ligmask", type=click.Path(exists=True), default=None, help="Ligand mask [Advanced]")
@click.option("--rec-attraction", "recattraction", type=click.Path(exists=True), default=None, help="Receptor attraction [Advanced]")
@click.option("--lig-attraction", "ligattraction", type=click.Path(exists=True), default=None, help="Ligand attraction [Advanced]")
@click.option("--rec-dssp", "dssprec", is_flag=True, default=None, help="Remove unstructured terminal residues in receptor [Advanced]")
@click.option("--lig-dssp", "dssplig", is_flag=True, default=None, help="Remove unstructured terminal residues in ligand [Advanced]")
@click.option("--restraints", type=click.Path(exists=True), default=None, help="Upload restraints file [Advanced]")
@click.option("--saxs-file", type=click.Path(exists=True), default=None, help="Upload SAXS profile [Advanced]")
@click.option("--masknoncdr", is_flag=True, default=None, help="Automatically mask non-CDR regions [Advanced]")
@click.option("--multimers", type=click.Choice(['dimer', 'trimer']), default=None, help="Multimer mode [Advanced]")
def cli(username, secret, **kwargs):
    """Submit a job to ClusPro.

    Jobs are expected to be in one of three "modes": docking with a provided ligand
    PDB ID or PDB file, docking in multimer mode (using --multimer), or peptide docking
    (using --pepmot and --pepseq). If using multimer mode add --multimer and specify
    dimer or trimer (ex. --multimer dimer or --multimer trimer). If using peptide mode
    supply both the peptide motif and sequence (ex. --pepmot KXRRL --pepseq KGRRL).
    Mixing options from these three modes is not supported and will result in an error message.

    If submitting from an automated script, please have your script sleep 5-10 seconds between
    each job submission to avoid overloading the ClusPro server. In addition, please limit
    batches to 50 jobs at a time.
    """
    if username is None or username == "None" or secret is None or secret == "None":
        if username is None or username == "None":
            username = click.prompt("Please enter your cluspro username")
            CP_CONFIG['username'] = username
        if secret is None or secret == "None":
            secret = click.prompt("Please enter your cluspro api secret")
            CP_CONFIG['api_secret'] = secret
        CONFIG.write()

    if kwargs['receptor'] is None and kwargs['recpdb'] is None:
        raise click.BadOptionUsage("One of --receptor or --recpdb is required")

    ligand_options = {'ligand', 'ligpdb'}
    multimer_options = {'multimers'}
    peptide_options = {'pepmot', 'pepseq', 'pepexclusion'}
    all_mode_options = {
        "ligand": ligand_options,
        "multimer": multimer_options,
        "peptide": peptide_options}

    kwarg_keys = set(k for k, v in kwargs.items() if v is not None)
    matching_modes = [k for k, v in all_mode_options.items()
                      if v & kwarg_keys]

    if len(matching_modes) == 0:
        raise click.BadOptionUsage("no input options specified, please run with just --help to see how to use this script")
    if len(matching_modes) > 1:
        raise click.BadOptionUsage("multiple input modes detected: {}. Please run with --help".format(" and ".join(matching_modes)))

    mode = matching_modes[0]

    if mode == 'ligand':
        if kwargs['ligand'] is not None and kwargs['ligpdb'] is not None:
            raise click.BadOptionUsage("only one of --ligand or --ligpdb is expected")
    elif mode == 'multimer':
        pass  # nothing else to check for
    elif mode == 'peptide':
        # at this point we know at least one of pepmot, pepseq, and pepexclusion is not None
        if kwargs['pepmot'] is None:
            raise click.BadOptionUsage("--pepmot required in peptide mode")
        if kwargs['pepseq'] is None:
            raise click.BadOptionUsage("--pepseq required in peptide mode")

    if kwargs['multimers'] is not None:
        if kwargs['multimers'] == 'dimer':
            kwargs['multimers'] = '2'
        elif kwargs['multimers'] == 'trimer':
            kwargs['multimers'] = '3'

    form = {
        k: v
        for k, v in kwargs.items() if k in FORM_KEYS and v is not None
    }
    form['username'] = username

    files = {}
    if form.get("receptor") is not None:
        files['rec'] = open(form['receptor'], 'rb')
        form['userecpdbid'] = '0'
    else:
        form['userecpdbid'] = '1'
    if form.get("ligand") is not None:
        files['lig'] = open(form['ligand'], 'rb')
        form['useligpdbid'] = '0'
    else:
        form['useligpdbid'] = '1'
    if form.get('pepmot') is not None and form.get('pepseq') is not None:
        form['peptidemode'] = '1'
        form['usepeptide'] = '1'
    else:
        form['peptidemode'] = '0'
        form['usepeptide'] = '0'

    for form_key, files_key in OPTIONAL_FILE_FIELDS:
        if form.get(form_key) is not None:
            files[files_key] = open(form[form_key], 'rb')

    form['sig'] = make_sig(form, secret)

    api_address = "{0}://{1}{2}".format(URL_SCHEME, CP_CONFIG['server'], API_ENDPOINT)

    try:
        r = requests.post(api_address, data=form, files=files)
        result = json.loads(r.text)
        if result['status'] == 'success':
            print(result['id'])
        else:
            print(result['errors'])
            sys.exit(1)
    except Exception as ex:
        logger.error("Error submitting job: {}".format(ex))
