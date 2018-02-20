
"""
Copied from https://bitbucket.org/mverleg/django_tex_response/src/a7859552519d7145473951d6ac2109e72067a4b5?at=master
"""

from os import remove, listdir, symlink
from os.path import dirname, join, abspath, exists, basename
from re import findall
from shutil import copy2, rmtree, copyfile
from subprocess import PIPE, Popen
from tempfile import mkdtemp, mkstemp

from django.conf import settings
from django.apps import apps
from django.http.response import HttpResponse
from django.template.loader import render_to_string


class LatexException(Exception):
	""" something went wrong while rendering a tex file """


def derive_static_dirs():
	dirs = list(settings.STATICFILES_DIRS)
	for mod in apps.app_configs:
		pth = join(settings.BASE_DIR, mod, 'static')
		if exists(pth):
			dirs.append(pth)
	return tuple(abspath(pth) for pth in dirs)


def make_graphics_path():
	# The spaces between { { are important to prevent interpreting at template tags.
	return '\graphicspath{ {' + '}{'.join(derive_static_dirs()) + '} }'


def link_imgs(target_dir, imgsources):
	# From https://github.com/mverleg/bardeen/blob/master/bardeen/system.py
	for srcpth in imgsources:
		for resource in listdir(srcpth):
			try:
				symlink(join(srcpth, resource), join(target_dir, basename(resource)))
			except OSError:
				copyfile(join(srcpth, resource), join(target_dir, basename(resource)))


def render_tex(request, template, context):
	"""
	Render template to .tex file.
	"""
	tex_input = render_to_string(template, context, request)
	tmp_dir = mkdtemp()
	in_file = join(tmp_dir, 'input.tex')
	with open(in_file, 'w+') as fh:
		fh.write(tex_input)
	return in_file


def tex_to_pdf(tex_file, destination=mkstemp(suffix='.pdf')[1],
		tex_cmd='lualatex', flags=('-interaction=nonstopmode', '-halt-on-error',),
		do_link_imgs=True):
	"""
	Render .tex file to .pdf.
	"""
	tmp_dir = dirname(tex_file)
	if do_link_imgs:
		link_imgs(tmp_dir, derive_static_dirs())
	out_file = join(tmp_dir, 'output.pdf')
	cmd = 'cd {dir:s}; {cmd:s} {flags:s} -jobname=output input.tex'.format(
		dir=tmp_dir, cmd=tex_cmd, flags=' '.join(flags))
	proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
	outp, err = proc.communicate()
	if b'error occurred' in outp:
		msgs = findall(r'[eE]rror:([^\n]*)\n', outp.decode('ascii'))
		raise LatexException('{0:}\n\nFull log: {1:}'.format(
			'\n'.join(msg.strip() for msg in msgs),
			outp[-800:]
		))
	if err:
		raise LatexException(err)
	try:
		copy2(out_file, destination)
	except IOError:
		raise LatexException(('{0:s} produced no error but failed to produce a'
			' pdf file; output: {1:s}').format(tex_cmd, outp))
	rmtree(tmp_dir)
	return destination


def render_pdf(request, template, context, filename='file.pdf',
		tex_cmd='lualatex', flags=('-interaction=nonstopmode', '-halt-on-error',),
		do_link_imgs=True):
	"""
	Render template to pdf-response (by using the above functions).
	"""
	tex_file = render_tex(request, template, context)
	pdf_file = tex_to_pdf(tex_file, tex_cmd=tex_cmd, flags=flags, do_link_imgs=do_link_imgs)
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename="%s"' % filename
	with open(pdf_file, 'rb') as fh:
		response.write(fh.read())
	remove(pdf_file)
	return response

