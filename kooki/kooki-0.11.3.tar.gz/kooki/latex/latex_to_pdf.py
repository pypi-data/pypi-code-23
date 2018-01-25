import subprocess, os, shutil, tempfile

from kooki.tools import write_file
import pretty_output


def latex_to_pdf(name, content):

    infos = []

    temp_dir = tempfile.mkdtemp()

    tex_file_name = '{0}.tex'.format(name)
    pdf_file_name = '{0}.pdf'.format(name.split('/')[-1])
    relative_output_path = '/'.join(name.split('/')[:-1])
    absolute_output_path = os.path.join(os.getcwd(), relative_output_path)

    tex_file_path = os.path.join(temp_dir, tex_file_name)
    pdf_file_path = os.path.join(temp_dir, pdf_file_name)

    if pretty_output._debug_policy:
        write_file(tex_file_name, content)

    write_file(tex_file_path, content)

    command = 'xelatex -interaction=nonstopmode -halt-on-error -output-directory={1} {0}'.format(tex_file_name, temp_dir)
    log_file = os.path.join(temp_dir, 'xelatex.log')

    with open(log_file, "w") as f:
        print('execute xelatex')
        subprocess.call(command, shell=True, stdout=f)
        subprocess.call(command, shell=True, stdout=f)

    if pretty_output._debug_policy:
        print('[debug] XeLaTeX output: cat {0}'.format(log_file))

    if os.path.isfile(pdf_file_path):
        shutil.copy(pdf_file_path, absolute_output_path)
        print('export {}'.format(pdf_file_name))
    else:
        print('the file {} is missing'.format(pdf_file_name))
