#!/usr/bin/env python
#
#   Copyright (c) 2014-2018 eGauge Systems LLC
#	4730 Walnut St, Suite 110
#	Boulder, CO 80301
#	voice: 720-545-9767
#	email: davidm@egauge.net
#
#   All rights reserved.
#
#   This code is the property of eGauge Systems LLC and may not be
#   copied, modified, or disclosed without any prior and written
#   permission from eGauge Systems LLC.
#
'''This is a KiCad Eeschema plugin that converts a KiCad XML to:

	1) a bill-of-materials (BOM), output as CSV text file
	   (comma-separated values)
	2) an EPIC part (assembly) that consists of the BOM components

The EPIC assembly created by this tool will have its manufacturer set
to django.conf.EPIC_MANUFACTURER and the manufacturer's part-number
will be set to 'bom:' with the name of the schematic and flavor-name
(if any) appended.  If an assembly with that part-number already
exists, it will be updated unless the BOM was edited manually inside
EPIC.  In the latter case, you can force overwriting the manually
edited BOM pass passing this script the --force-overwrite command-line
option.

This tool also updates the Eeschema schematic files with the footprint
info in the EPIC database.  The original schematic files are backed up
in files with a tilde (~) appended to the original filename.  If the
footprint in a schematic file changes, the tool will warn you about
that and remind you to re-generate the net list file and potentially
update the PCB.

This tool extracts part number an installation information from the
XML file using the following component field names:

	Field Name:	Purpose:
	------------	---------------------------------------------
	EP		Specifies the EPIC part number to use for the
			component.

	Installation	If the value of this field is "DNP" (Do Not Place),
			then the component is omitted from the BOM.
			In the CSV output file, do-not-place components
			are listed separately at the end of the file.

A single Eeschema file may define multiple flavors (versions) of a
BOM.  This is done by appending the flavor name to the above field
names, separated by a dash (-).  For example, to define a flavor
called `lite', you'd use field names `EP-lite' and/or
`Installation-lite' when a particular component needs to have a
different EPIC part number or a different installation method for that
flavor.  Use command-line option --flavor to specify which flavor to
generate the a BOM for.

'''

from __future__ import print_function

from argparse import RawDescriptionHelpFormatter as RawDescHelpFormatter
from types import SimpleNamespace

import argparse
import io
import os
import re
import sys
import tempfile
import xml.etree.ElementTree as ET

# Please replace 'epic-sample' with the name of your Django project:
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'epic-sample.epic-sample.settings')

import django
django.setup()

from django.conf import settings as cfg
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from epic.models import Part, format_part_number, Assembly_Item, strchoice, \
    Vendor

from os import path

MY_TOOL_NAME = 'kicad-to-epic-bom'

manufacturer = cfg.EPIC_MANUFACTURER

class Component:
    def __init__(self, part_id=None, refdes=None, value=None, footprint=None,
                 mfg=None, mfg_pn=None, part=None):
        self.part_id = part_id
        self.part = part
        self.refdes = refdes
        self.value = value
        self.footprint = footprint
        self.mfg = mfg
        self.mfg_pn = mfg_pn

    def __str__(self):
        res = 'Component('
        sep = ''
        for f in dir(self):
            if f[0] == '_':
                continue
            val = self.__dict__[f]
            if val != None:
                res += '%s%s=%s' % (sep, f, val)
                sep = ','
        res += ')'
        return res

def quote(str):
    str = str.replace('"', '\"')
    # Replace comma by colon.  DigiKey doesn't
    # handle commas correctly even if they're inside double quotes...
    str = str.replace(',', ':')
    return '"' + str + '"'

@transaction.atomic
def save_assembly(assembly_part, bom):
    created = assembly_part.id is None

    assembly_part.last_bom_mod_type = Part.LAST_MOD_TYPE_TOOL
    assembly_part.last_bom_mod_name = MY_TOOL_NAME
    assembly_part.save()

    Assembly_Item.objects.filter(assy_id=assembly_part.id).delete()

    for components in bom:
        comp = components[0]
        refdes = ','.join(c.refdes for c in components)
        item = Assembly_Item(assy_id=assembly_part.id,
                             comp_id=comp.part_id,
                             qty=len(components),
                             refdes=refdes)
        item.save()
    print('%s: info: %s part %s (%s %s) with %d components' \
          % (MY_TOOL_NAME, 'created' if created else 'updated',
             format_part_number(assembly_part.id),
             assembly_part.mfg, assembly_part.mfg_pn, len(bom)),
          file=sys.stderr)

def update_comp(comp):
    footprint_field_index = part_number = None
    has_changed = False
    refdes = ''
    for index, line in enumerate(comp):
        m = re.match(r'F\s+(\d+)\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+'
                     '\s+\S+(\s+(\S+))?$', line)
        if m:
            if m.group(1) == '0':
                if m.lastindex >= 2:
                    refdes = m.group(2)[1:-1] + ' '
            elif m.group(1) == '2':
                footprint_field_index = index
            elif m.lastindex >= 3 and m.group(4) == '"EP"':
                try:
                    part_str = m.group(2)[1:-1]
                    part_number = int(part_str)
                except ValueError:
                    print('%s: warn: invalid EPIC part number "%s"' %
                          (MY_TOOL_NAME, part_str), file=sys.stderr)
    if footprint_field_index is not None and part_number is not None:
        try:
            part = Part.objects.get(pk=part_number)
        except ObjectDoesNotExist:
            print('%s: error: Part %s does not exist' %
                  (MY_TOOL_NAME, format_part_number(part_number)),
                  file=sys.stderr)
            return False
        if part.footprint is None or part.footprint == '':
            if part.mounting != Part.MOUNTING_CHASSIS \
               and part.mounting != Part.MOUNTING_FREE:
                print('%s: warn: EPIC part %s has no footprint defined' %
                      (MY_TOOL_NAME, format_part_number(part.id)),
                      file=sys.stderr)
        else:
            old = comp[footprint_field_index]
            m = re.match(r'F\s+2\s+"([^"]*)"+\s+(.*)', old)
            if m:
                old_footprint = m.group(1)
                rest = m.group(2)
                new_footprint = part.footprint
                new = 'F 2 \"%s\" %s\n' % (new_footprint, rest)
                comp[footprint_field_index] = new
                if old_footprint != new_footprint:
                    print('%s: warn: %sfootprint changed from %s to %s.'
                          % (MY_TOOL_NAME, refdes, old_footprint,
                             new_footprint))
                    has_changed = True
                else:
                    has_changed = False
    return has_changed

def update_schematic(dirname, filename):
    '''Update schematic file FILENAME residing in directory DIRNAME with
    footprints from the EPIC database.

    '''
    schem_path = os.path.join(dirname, filename)
    has_changes = False
    with tempfile.NamedTemporaryFile(dir=dirname) as out:
        with io.open(schem_path, 'r', encoding='utf-8') as schem_file:
            inside_comp = False
            for line in schem_file:
                if line.rstrip() == '$Comp':
                    inside_comp = True
                    curr_comp = [line]
                elif line.rstrip() == '$EndComp':
                    inside_comp = False
                    curr_comp.append(line)
                    has_changes |= update_comp(curr_comp)
                    for comp_line in curr_comp:
                        out.write(comp_line.encode('utf-8'))
                elif inside_comp:
                    curr_comp.append(line)
                else:
                    out.write(line.encode('utf-8'))
        if has_changes:
            os.rename(schem_path, schem_path + '~')
            os.link(os.path.join(dirname, out.name), schem_path)
            print('%s: info: %s updated.  Use kicad to update net list and PCB'
                  % (MY_TOOL_NAME, schem_path))

def bom_append(bom, component):
    if component.part_id not in bom:
        bom[component.part_id] = []
    bom[component.part_id].append(component)

def bom_sort(bom):
    bom_list = []
    for part_id in bom:
        bom_list.append(bom[part_id])
    bom_list.sort(key=lambda x: x[0].part_id)
    return bom_list

def output_csv(outfile, bom_list, with_vendor_pn=False, preferred_vendors=None):
    for components in bom_list:
        qty = len(components)
        refdes = ','.join(c.refdes for c in components)
        c = components[0]

        substitutes = ''
        if c.part:
            sep = ''
            for sub in c.part.equivalent_parts():
                if sub == c.part:
                    continue
                substitutes += sep
                substitutes += '%s (%s %s)' % (format_part_number(sub.id),
                                               sub.mfg, sub.mfg_pn)
                sep = ', '


        row = '%s,%s,%s,%s,%s,%s,%s,%s' % \
              (qty, c.value, c.footprint, format_part_number(c.part_id),
               c.mfg, quote(c.mfg_pn), quote(substitutes), quote(refdes))

        if with_vendor_pn:
            vp = c.part.best_vendor_part(preferred_vendors)
            if vp is None:
                vendor = 'n/a'
                vendor_pn = 'n/a'
            else:
                vendor = vp.vendor
                vendor_pn = vp.vendor_pn
            row += ',%s,%s' % (vendor, vendor_pn)
        print(row, file=outfile)

def update(res, field, desired_flavor, detected_flavors):
    '''Process RES by matching FIELD.attrib['name'] against RES.PATTERN.
    If there is a match M, M.group(2) must evaluate to the name of the
    flavor of the field.  If this flavor matches the specified flavor,
    we have an exact match and RES.value is set to field.text, RES.name
    is set to field.attrib['name'].
    If the flavor of the field is empty and RES.value is None we have a
    default match and RES is updated like for an exact match.
    DETECTED_FLAVOR is a set of flavors found.
    '''
    m = res.pattern.match(field.attrib['name'])
    if m is None:
        return

    this_flavor = None
    if m.lastindex is not None:
        this_flavor = m.group(2)
        detected_flavors |= {this_flavor} # update set of all detected flavors

    if this_flavor == desired_flavor \
       or (this_flavor is None and res.value is None):
        res.name = field.attrib['name']
        res.value = field.text

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=RawDescHelpFormatter)
    parser.add_argument('input-file', nargs=1, help='Name of XML file '
                        'generated by KiCad\'s \"Generate BOM\" command.')
    parser.add_argument('output-file', nargs=1, help='Name of output file '
                        'that will contain the bill-of-materials (BOM) in '
                        'a comma-separated-values (CSV) file.')
    parser.add_argument('--flavor', nargs=1, default=None,
                        help='Select PCB flavor for which to generate BOM '
                        'for.')
    parser.add_argument('-f', '--force-overwrite', action='store_true',
                        help='Force overwriting of existing EPIC BOM '
                        '(assembly) part even if the part appears to '
                        'have been modified manually.')
    parser.add_argument('-V', '--with-vendor-pn', action='store_true',
                        help='Include Vendor and Vendor part-number in the '
                        'CSV output.')
    parser.add_argument ('-p', '--prefer-vendor', nargs='+', default=[],
                         help='Prefer the specified vendor(s), even if those '
                         'do not have the lowest cost for a given part. '
                         'Non-preferred vendors are used only for parts that '
                         'could be ordered otherwise.')
    parser.add_argument('-n', '--no-update-footprints', action='store_true',
                        help='By default, this program will update the '
                        'schematic files with the footprint information '
                        'found in the parts database.  This option can be '
                        'specified to skip this step.')
    parser.add_argument('--no-db-save', action='store_true',
                        help='Skip creating (or updating) the EPIC database '
                        'with the new BOM. '
                        'This is intended mainly for testing.')
    args = parser.parse_args()

    flavor = None
    if args.flavor is not None:
        flavor = args.flavor[0]

    preferred_vendors = None
    for vendor_name in args.prefer_vendor:
        vendors = Vendor.objects.filter(name__istartswith=vendor_name)
        if len(vendors) < 1:
            print('%s: error: vendor `%s\' cannot be found' %
                  (MY_TOOL_NAME, vendor_name), file=sys.stderr)
            sys.exit(1)
        elif len(vendors) > 1:
            print('%s: error: vendor name `%s\' not unique, matches: %s' %
                  (MY_TOOL_NAME, vendor_name,
                   ', '.join(['`%s\'' % v.name for v in vendors])),
                  file=sys.stderr)
            sys.exit(1)
        if preferred_vendors is None:
            preferred_vendors = []
        preferred_vendors.append(vendors[0])

    output_filename = args.__dict__['output-file'][0]
    input_filename = args.__dict__['input-file'][0]

    xml = ET.parse(input_filename)

    schematic_name = 'unknown'
    revision = ''
    design = xml.find('design')
    sources = []
    source_path = path.dirname(input_filename)
    if design is not None:
        source = design.find('source')
        if source is not None:
            schematic_name = path.splitext(path.basename(source.text))[0]
        sheet = design.find('sheet')
        for sheet in design.iter('sheet'):
            title_block = sheet.find('title_block')
            if title_block is not None:
                if revision == '':
                    rev = title_block.find('rev')
                    if rev is not None:
                        revision = '-rev' + rev.text.lstrip().rstrip()
                sources.append(title_block.find('source').text)

    if not args.no_update_footprints:
        for schematic in sources:
            update_schematic(source_path, schematic)

    assembly_name = 'bom:' + schematic_name + revision
    if flavor is not None:
        assembly_name += '-' + flavor
    qs = Part.objects.filter(mfg=manufacturer).filter(mfg_pn=assembly_name)
    if qs.exists():
        assembly_part = qs[0]
        if assembly_part.last_bom_mod_type != Part.LAST_MOD_TYPE_TOOL \
           or assembly_part.last_bom_mod_name != MY_TOOL_NAME:
            print('%s: info: part %s %s was last modified by %s %s' %
                  (MY_TOOL_NAME, manufacturer, assembly_name,
                   strchoice(Part.LAST_MOD_CHOICES,
                             assembly_part.last_bom_mod_type),
                   assembly_part.last_bom_mod_name), file=sys.stderr)
            if args.force_overwrite:
                print('%s: info: overwriting existing part due to '
                      '--force-overwrite'
                      % MY_TOOL_NAME, file=sys.stderr)
            else:
                print('%s: error: refusing to overwrite part %s; '
                      'use --force-overwrite if desired' \
                      % (MY_TOOL_NAME, format_part_number(assembly_part.id)),
                      file=sys.stderr)
                sys.exit(1)
    else:
        desc = 'BOM for %s' % schematic_name
        if flavor is not None:
            desc += (flavor + ' flavor')
        assembly_part = Part(descr=desc,
                             mfg=manufacturer, mfg_pn=assembly_name,
                             mounting=Part.MOUNTING_CHASSIS,
                             target_price=1000,
                             overage=1, spq=1, lead_time=4,
                             status=Part.STATUS_PREVIEW)

    ep_pat = re.compile(r'EP(-(.*))?')
    inst_pat = re.compile(r'Installation(-(.*))?')

    bom = {}    # regular bom
    dnp = {}    # do-not-place bom
    # part number & refdes used to refer to a particular part:
    src_part_dict = {}
    detected_flavors = set()
    for comp in xml.find('components'):
        refdes = comp.attrib.get('ref')

        part = SimpleNamespace(name=None, value=None, pattern=ep_pat)
        inst = SimpleNamespace(name=None, value=None, pattern=inst_pat)
        fields = comp.find('fields')
        if fields is not None:
            for field in fields:
                update(part, field, flavor, detected_flavors)
                update(inst, field, flavor, detected_flavors)

        do_not_place = (inst.value == 'DNP')

        if part.value is None:
            if not do_not_place:
                print('%s: warn: %s skipped due to missing '
                      'EPIC Part Number ("EP" field)'
                      % (MY_TOOL_NAME, refdes), file=sys.stderr)
            continue

        if do_not_place:
            print('%s: info: %s marked as do-not-place ("%s=DNP")'
                  % (MY_TOOL_NAME, refdes, inst.name), file=sys.stderr)

        try:
            part_id = int(part.value)
        except ValueError:
            print('%s: warn: %s has invalid EPIC part number "%s"' %
                  (MY_TOOL_NAME, refdes, part.value), file=sys.stderr)
            continue

        try:
            src_part = Part.objects.get(pk=part_id)
        except ObjectDoesNotExist:
            print('%s: warn: part %s not found in database' %
                  (MY_TOOL_NAME, format_part_number(part_id)), file=sys.stderr)
            continue

        c = Component(part_id, part=src_part, refdes=refdes,
                      value=comp.findtext('value', default='n/a'))
        best_part = src_part.best_part()

        # keep a list of part names used to refer to best part:
        if best_part.id not in src_part_dict:
            src_part_dict[best_part.id] = [src_part.id, c.refdes]
        elif src_part.id != src_part_dict[best_part.id][0]:
            print('%s: warn: %s uses %s instead '
                  'of equivalent %s used by %s' % \
                  (MY_TOOL_NAME, c.refdes,
                   format_part_number(src_part.id),
                   format_part_number(src_part_dict[best_part.id][0]),
                   src_part_dict[best_part.id][1]))

        if c.value != c.part.val:
            print('%s: warn: %s has value %s but part %s has value %s'
                  % (MY_TOOL_NAME, c.refdes, c.value,
                     format_part_number(part_id), c.part.val), file=sys.stderr)
        c.footprint = c.part.footprint
        c.mfg = c.part.mfg
        c.mfg_pn = c.part.mfg_pn

        if do_not_place:
            bom_append(dnp, c)
        else:
            bom_append(bom, c)

    if len(detected_flavors) == 0:
        detected_flavors_str = 'no flavors'
    else:
        if len(detected_flavors) > 1:
            detected_flavors_str = 'flavors: '
        else:
            detected_flavors_str = 'flavor: '
        detected_flavors_str += ', '.join(sorted(detected_flavors))

    if flavor is not None and flavor not in detected_flavors:
        print('%s: error: flavor `%s\' not defined by this schematic; '
              'detected %s'
              % (MY_TOOL_NAME, flavor, detected_flavors_str),
              file=sys.stderr)
        sys.exit(1)
    elif len(detected_flavors) > 0:
        print('%s: info: this schematic defines %s'
              % (MY_TOOL_NAME, detected_flavors_str), file=sys.stderr)

    bom_list = bom_sort(bom)
    dnp_list = bom_sort(dnp)

    out = io.open(output_filename, 'w', encoding='utf-8')
    hdr = (u'Qty,Value,Footprint,%s PN,Mfg,Mfg PN,Approved Substitutes,Refdes' %
           manufacturer)
    if args.with_vendor_pn:
        hdr += u',Vendor,Vendor PN'
    print(hdr, file=out)

    output_csv(out, bom_list, args.with_vendor_pn, preferred_vendors)

    if len(dnp_list) > 0:
        print('\nDO NOT PLACE parts:', file=out)
        output_csv(out, dnp_list, args.with_vendor_pn, preferred_vendors)

    if not args.no_db_save:
        save_assembly(assembly_part, bom_list)

if __name__ == '__main__':
    main()
