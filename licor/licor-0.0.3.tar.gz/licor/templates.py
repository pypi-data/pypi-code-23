# Copyright (c) 2017 Daniel Knüttel                                           #
#                                                                             #
# This file is part of licor.                                                 #
#                                                                             #
# licor is free software: you can redistribute it and/or modify               #
# it under the terms of the GNU Affero General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# licor is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU Affero General Public License    #
# along with licor.  If not, see <http://www.gnu.org/licenses/>.              #
#                                                                             #
#                                                                             #


import pkg_resources, json
from itertools import permutations
from string import Template

class TemplateException(Exception): 
	pass

def get_resource_string(name, is_global = True):
	"""
	Return the resource string with the given name UTF-8 encoded.
	"""
	if(is_global):
		return pkg_resources.resource_string(__name__,"templates/" + name).decode("UTF-8")
	else:
		start = name[0].lower()
		path = "templates/" + start + "/" + name
		return pkg_resources.resource_string(__name__, path).decode("UTF-8")


def get_template(name, modifiers = []):
	"""
	Return a ``dict`` containing all necessary information for 
	filling a license template::

		{
			"name": <template-name>,
			"keywords": ["author", "date", ...],
			"text": <template string>
		}

	``modifiers`` is a list specifying the template. 
	A typical call might be::

		get_template("AGPL", modifiers = ["single-file"])
	"""

	templates_avail = get_templates_available()

	if( not name in templates_avail):
		raise TemplateException("Unknown license: {}".format(name))

	unsupported = [mod for mod in modifiers if not mod in templates_avail[name]["modifiers"]]
	if(unsupported):
		raise TemplateException("Unknown modifiers: {}. Supported are: {}".format(
					",".join(unsupported), ",".join(templates_avail[name]["modifiers"])))
	
	for perm in permutations(modifiers):
		mods = ".".join(perm)
		if(mods):
			meta_name =  ".".join((name, mods, "meta"))
			data_name = ".".join((name, mods, "tx"))
		else:
			meta_name = ".".join((name, "meta"))
			data_name = ".".join((name, "tx"))
		try:
			meta = json.loads(get_resource_string(meta_name, False))
		except:
			continue

		data = get_resource_string(data_name, False)

		meta.update({"text": data})
		return meta

	raise TemplateException("Database licenses_avail.json is desynced. Unable to locate resource.")

def get_template_meta(name, modifiers = []):
	"""
	Return a ``dict`` containing all necessary information for 
	filling a license template::

		{
			"name": <template-name>,
			"keywords": ["author", "date", ...]
		}

	``modifiers`` is a list specifying the template. 
	A typical call might be::

		get_template_meta("AGPL", modifiers = ["single-file"])
	"""

	templates_avail = get_templates_available()

	if( not name in templates_avail):
		raise TemplateException("Unknown license: {}".format(name))

	unsupported = [mod for mod in modifiers if not mod in templates_avail[name]["modifiers"]]
	if(unsupported):
		raise TemplateException("Unknown modifiers: {}. Supported are: {}".format(
					",".join(unsupported), ",".join(templates_avail[name]["modifiers"])))
	
	for perm in permutations(modifiers):
		mods = ".".join(perm)
		if(mods):
			meta_name =  ".".join((name, mods, "meta"))
		else:
			meta_name = ".".join((name, "meta"))
		try:
			meta = json.loads(get_resource_string(meta_name, False))
		except:
			continue

		return meta

	raise TemplateException("Database licenses_avail.json is desynced. Unable to locate resource.")


def format_template(name, data, modifiers = []):
	"""
	Return a formatted version of the license Template.
	This text is ready to be uncommented an placed into a source file.
	"""
	template = get_template(name, modifiers)

	missing = [k for k in template["keywords"] if not k in data]
	if(missing):
		raise TemplateException("missing keywords: {}".format(",".join(missing)))
	
	return Template(template["text"]).substitute(data)

def get_templates_available():
	"""
	Return a ``dict`` containing information about the available templates.
	"""
	return json.loads(get_resource_string("licenses_avail.json"))
