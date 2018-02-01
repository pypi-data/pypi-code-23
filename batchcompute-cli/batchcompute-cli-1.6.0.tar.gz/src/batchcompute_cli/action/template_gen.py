

import os
from ..util import client, zip,oss_client,config
from terminal import green,white
import re
import json
import tarfile
from batchcompute_cli.const import CMD
import shutil
from ..const import TEMPLATE_GATK_BUCKETS


def trans_jobId(job=None):
    if not job or not job.startswith('job-'):
        raise Exception('Invalid job_id: %s' % job)
    return job

def trans_type(type=None):
    if not type:
        return 'empty'

    arr = ['java','python','shell','empty','gatk','wdl']
    if(type.lower() in arr):
        return type.lower()

    raise Exception('Invalid type: %s, it must be in [%s] or an available oss path' % (type, '|'.join(arr) ))


def gen(location=None, type="empty"):

    dist = __get_location(location)

    cur_path = os.path.split(os.path.realpath(__file__))[0]

    src = os.path.join(cur_path, '../templates/%s' % type)

    print('init with [%s] template at: %s' % ( 'python' if type=='empty' else type, dist))

    zip.unzip_file('%s.zip' % src, dist)

    if type=='empty' or type=='python':
        # add oss2 to src
        add_oss2(cur_path, dist)


    if type=='gatk':
        replaceTemplate4GATK(dist)
    elif type=='wdl':
        replaceTemplate4WDL(dist)
    else:
        # update job.json set imageId: m-28sm4m6ez
        update_image_n_instype(os.path.join(dist,'job.json'))

    print(green('Done'))




def update_image_n_instype(p):
    obj = {}
    with open(p, 'r') as f:
        obj = json.loads(f.read())

    if obj.get('Type') == 'DAG':
        with open(p, 'w') as f:
            ts = obj['DAG']['Tasks']

            img_id = config.get_default_image()
            ins_type = config.get_default_instance_type()

            for k in ts:
                ts[k]['AutoCluster']['ImageId']=img_id
                ts[k]['AutoCluster']['InstanceType']=ins_type

            f.write(json.dumps(obj, indent=2))



def download_worker(packageUri, dist):
    src = os.path.join(dist, 'src')
    os.mkdir(src)
    tarpath = os.path.join(dist,'worker.tar.gz')

    oss_client.download_file(packageUri, tarpath)

    with tarfile.open(tarpath, 'r|gz') as f:
        f.extractall(src)

def add_oss2(cur_path, dist):
    src = os.path.join(cur_path, '../lib/oss2')
    target = os.path.join(dist,'src/oss2')
    if not os.path.exists(target):
        shutil.copytree(src, target, True)




def __parse_type_from_cmd_line(cmd_line):
    if 'java ' in cmd_line:
        return 'java'
    elif 'python ' in cmd_line:
        return 'python'
    elif 'wdl' in cmd_line:
        return 'wdl'
    else:
        return 'shell'



def __get_location(location):

    if not location:
        return os.getcwd()

    elif location.startswith('/') or location.startswith('~') or re.match(r'^\w\:',location):
        return location
    else:
        return os.path.join(os.getcwd(), location)

##############################


def get_instance_type(arr, cpu,mem):

    for n in arr:
       if n.get('cpu')>= int(cpu) and n.get('memory') >= int(mem):
           return n.get('name')
    return arr[-1].get('name')

def _ins_types_cmp(a,b):
    if 'bcs.' in a.get('name'):
        return 1
    if 'sn1.' in b.get('name') or 'sn2.' in b.get('name'):
        return 1
    return -1


def replaceTemplate4GATK(dist):

    # main.sh
    _replace_template(os.path.join(dist, 'gatk4-data-processing', 'main.sh'))
    # inputs
    _replace_template(os.path.join(dist, 'gatk4-data-processing','src',
                                   'processing-for-variant-discovery-gatk4.hg38.wgs.inputs.json'))

    # main.sh2
    _replace_template(os.path.join(dist, 'gatk4-germline-snps-indels', 'haplotypecaller-gvcf-gatk4-main.sh'))
    # inputs2
    _replace_template(os.path.join(dist, 'gatk4-germline-snps-indels','src',
                           'haplotypecaller-gvcf-gatk4.hg38.wgs.inputs.json'))

    # main.sh3
    _replace_template(os.path.join(dist, 'gatk4-germline-snps-indels', 'joint-discovery-gatk4-main.sh'))
    # inputs3
    _replace_template(os.path.join(dist, 'gatk4-germline-snps-indels', 'src',
                                   'joint-discovery-gatk4.hg38.wgs.inputs.json'))


def replaceTemplate4WDL(dist):


    # main.sh
    _replace_template(os.path.join(dist, 'main.sh'))


def _replace_template(p):
    ins_types = (client.list_instance_types() or [])

    # sort
    ins_types.sort(cmp=_ins_types_cmp)

    bucket = TEMPLATE_GATK_BUCKETS.get(config.getRegion())

    if not bucket:
        raise Exception("This region do not support WDL")



    with open(p) as f:
        str = f.read()

        str = str.replace('#{{INSTANCE_TYPE:4:8}}', get_instance_type(ins_types, 4, 8))
        str = str.replace('#{{INSTANCE_TYPE:4:16}}', get_instance_type(ins_types, 4, 16))
        str = str.replace('#{{INSTANCE_TYPE:8:16}}', get_instance_type(ins_types, 8, 16))
        str = str.replace('#{{INSTANCE_TYPE:16:32}}', get_instance_type(ins_types, 16, 32))
        str = str.replace('#{{INSTANCE_TYPE:8:32}}', get_instance_type(ins_types, 8, 32))
        str = str.replace('#{{INSTANCE_TYPE:32:128}}', get_instance_type(ins_types, 32, 128))

        str = str.replace('#{{GENOMICS_PUBLIC_BUCKET}}', bucket)

    with open(p, 'w') as f:
        f.write(str)
