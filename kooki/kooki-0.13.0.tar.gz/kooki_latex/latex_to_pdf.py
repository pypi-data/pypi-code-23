import subprocess, os, shutil, tempfile

from kooki.tools import write_file
import pretty_output, textwrap


def latex_to_pdf(name, content):

    current = os.getcwd()
    temp_dir = tempfile.mkdtemp()

    os.chdir(temp_dir)

    tex_file_name = '{0}.tex'.format(name)
    pdf_file_name = '{0}.pdf'.format(name.split('/')[-1])
    relative_output_path = '/'.join(name.split('/')[:-1])
    absolute_output_path = os.path.join(current, relative_output_path)

    tex_file_path = os.path.join(temp_dir, tex_file_name)
    pdf_file_path = os.path.join(temp_dir, pdf_file_name)

    write_file(tex_file_path, content)

    command = textwrap.dedent('''\
        xelatex -interaction=nonstopmode -halt-on-error -output-directory={1} {0}\
        ''').format(tex_file_path, temp_dir)

    log_file = os.path.join(temp_dir, 'xelatex.log')
    command_bib = 'bibtex {}'.format(name)

    command_glossary = 'makeglossaries {}'.format(name)

    with open(log_file, 'w') as f:
        print('execute xelatex')
        subprocess.call(command, shell=True, stdout=f)
        subprocess.call(command_bib, shell=True, stdout=f)
        subprocess.call(command_glossary, shell=True, stdout=f)
        subprocess.call(command, shell=True, stdout=f)
        subprocess.call(command, shell=True, stdout=f)


    if not os.path.isdir(absolute_output_path):
        os.makedirs(absolute_output_path)

    if pretty_output._debug_policy:
        print('[debug] XeLaTeX output: cat {0}'.format(log_file))
        tex_file_name = os.path.join(absolute_output_path, tex_file_name)
        write_file(tex_file_name, content)
        print('export {}'.format(tex_file_name, absolute_output_path))

    if os.path.isfile(pdf_file_path):
        shutil.copy(pdf_file_path, absolute_output_path)
        print('export {} to {}'.format(pdf_file_name, absolute_output_path))
    else:
        print('the file {} is missing'.format(pdf_file_name))

    # shutil.rmtree(temp_dir)
    os.chdir(current)
