import copy
import fnmatch
import json
import os
import plistlib
import re
import shutil
import uuid
from distutils.dir_util import copy_tree
from os import path
from os.path import basename, isdir
from subprocess import call

from PIL import Image


class IOSStickersExtension:
    packge_dir_path = os.path.dirname(__file__)
    resources_dir_path = path.join(packge_dir_path, 'resources')
    xcode_proj_file_path = None
    scheme = None
    sticker_images_dir_path = None
    pbxproj_project_plist = None
    pbxproj_additions_plist = None
    pbxproj_file_path = None
    build_configuration = None
    info_plist = None
    proj_dir_path = None
    stickers_dir_path = None
    xc_build_configurations = None
    build_configuration = None

    def __init__(self, xcode_proj_file_path, scheme, sticker_images_dir_path, build_configuration):
        self.xcode_proj_file_path = xcode_proj_file_path
        self.scheme = scheme
        self.sticker_images_dir_path = sticker_images_dir_path
        self.pbxproj_file_path = path.join(self.xcode_proj_file_path, 'project.pbxproj')
        self.proj_dir_path = path.dirname(self.xcode_proj_file_path)
        self.stickers_dir_path = path.join(self.proj_dir_path, 'tt-stickers')
        self.build_configuration = build_configuration

    def install(self):
        self.init()
        if not self.exists_sticker_images():
            return True
        if not self.add_sticker_images():
            return False
        if not self.add_sticker_icons():
            return False
        if not self.update_pbxproj_file():
            return False
        if not self.update_info_plist():
            return False
        return True

    def get_pbxproj_additions_plist(self):
        if self.pbxproj_additions_plist is not None:
            return self.pbxproj_additions_plist

        pbxproj_additions_plist_file_path = path.join(self.resources_dir_path, 'pbxproj-additions.plist')
        self.pbxproj_additions_plist = plistlib.readPlist(pbxproj_additions_plist_file_path)
        return self.pbxproj_additions_plist

    def get_pbxproj_project_plist(self):
        if self.pbxproj_project_plist is not None:
            return self.pbxproj_project_plist
        if self.init_pbxproj_project_plist():
            return self.pbxproj_project_plist
        return None

    def init_pbxproj_project_plist(self):
        if self.pbxproj_project_plist is not None:
            return True

        convert_plist_to_xml_cmd = ['plutil', '-convert', 'xml1', self.pbxproj_file_path]
        ret_code = call(convert_plist_to_xml_cmd)
        if ret_code != 0:
            print 'Failed to run command: ' + ' '.join(convert_plist_to_xml_cmd)
            return False

        self.pbxproj_project_plist = plistlib.readPlist(self.pbxproj_file_path)
        return True

    def init(self):
        if path.isdir(self.stickers_dir_path):
            print 'Remove dir: ' + self.stickers_dir_path
            shutil.rmtree(self.stickers_dir_path)

        tt_stickers_dir_path = path.join(self.resources_dir_path, 'tt-stickers')
        shutil.copytree(tt_stickers_dir_path, self.stickers_dir_path)

    def add_sticker_images(self):
        sticker_images_file_names = os.listdir(self.sticker_images_dir_path)
        sticker_pack_dir_path = path.join(self.stickers_dir_path, "TT-Stickers.xcassets/Sticker Pack.stickerpack")
        example_sticker_dir_path = path.join(self.resources_dir_path, 'example.sticker')
        for file_name in sticker_images_file_names:
            file_path = path.join(self.sticker_images_dir_path, file_name)
            if not path.isfile(file_path) or file_name == '.DS_Store':
                continue
            sticker_dir_path = path.join(sticker_pack_dir_path, path.splitext(file_name)[0] + '.sticker')
            copy_tree(example_sticker_dir_path, sticker_dir_path)
            shutil.copy2(file_path, sticker_dir_path)

            with open(path.join(sticker_pack_dir_path, 'Contents.json'), "r+") as json_file:
                data = json.load(json_file)
                data['stickers'].append({'filename': basename(sticker_dir_path)})
                json_file.seek(0)
                json.dump(data, json_file)
                json_file.truncate()

            with open(path.join(sticker_dir_path, 'Contents.json'), "r+") as json_file:
                data = json.load(json_file)
                data['properties']['filename'] = file_name
                json_file.seek(0)
                json.dump(data, json_file)
                json_file.truncate()

        return True

    def add_sticker_icons(self):
        icon_file_paths = []
        assetcatalog_compiler_appicon_name = self.get_value_by_key_from_xc_build_configuration(
            'ASSETCATALOG_COMPILER_APPICON_NAME')
        if assetcatalog_compiler_appicon_name is not None:
            appiconset_dir_paths = self.find_dirs(assetcatalog_compiler_appicon_name + '.appiconset')
            if appiconset_dir_paths:
                appiconset_dir_path = appiconset_dir_paths[0]
                print 'Get icons for sticker from: ' + appiconset_dir_path
                for file in os.listdir(appiconset_dir_path):
                    if not file.endswith('.json'):
                        icon_file_paths.append(os.path.join(appiconset_dir_path, file))

        if not icon_file_paths:
            info_plist = self.get_info_plist()
            if 'CFBundleIconFiles' not in info_plist:
                print 'Failed to get "CFBundleIconFiles" key from Info.plist'
                return False
            if not info_plist['CFBundleIconFiles']:
                print 'CFBundleIconFiles is empty'
                return False
            print 'Get icons for sticker from: ' + self.proj_dir_path
            icon_file_paths = [path.join(self.proj_dir_path, icon_name) for icon_name in
                               info_plist['CFBundleIconFiles']]

        icon_image_max_resolution = None
        for icon_file_path in icon_file_paths:
            icon_file_path_vars = re.findall('\$\{(.*?)\}', icon_file_path)
            is_icon_file_path_parsed = True
            for icon_file_path_var in icon_file_path_vars:
                icon_file_path_var_value = self.get_value_by_key_from_xc_build_configuration(icon_file_path_var)
                if icon_file_path_var_value is None:
                    print 'Failed to find the var: %s' % icon_file_path_var
                    is_icon_file_path_parsed = False
                    break
                icon_file_path = icon_file_path.replace('${' + icon_file_path_var + '}', icon_file_path_var_value)
            if not is_icon_file_path_parsed:
                continue

            if not path.isfile(icon_file_path):
                continue
            icon_image = Image.open(icon_file_path)

            if icon_image_max_resolution is None:
                icon_image_max_resolution = icon_image
                continue

            if (icon_image.height * icon_image.width) > (
                        icon_image_max_resolution.height * icon_image_max_resolution.width):
                icon_image_max_resolution = icon_image

        if icon_image_max_resolution is None:
            print 'Failed to find icon for stickers'
            return False

        icon_image_max_resolution_file_extension = str.lower(icon_image_max_resolution.format)
        stickers_icon_set_dir_path = path.join(self.proj_dir_path, 'tt-stickers', 'TT-Stickers.xcassets',
                                               'iMessage App Icon.stickersiconset')
        sticker_icon_sizes = [(120, 90), (180, 135), (134, 100), (148, 110), (54, 40), (81, 60), (64, 48), (96, 72),
                              (1024, 768)]
        sticker_icon_file_names = []
        for sticker_icon_size in sticker_icon_sizes:
            sticker_icon_file_name = 'sticker_icon-' + str(sticker_icon_size[0]) + 'X' + str(sticker_icon_size[1]) + \
                                     '.' + icon_image_max_resolution_file_extension
            sticker_icon_file_path = path.join(stickers_icon_set_dir_path, sticker_icon_file_name)
            sticker_icon_file_names.append(sticker_icon_file_name)
            icon_image_max_resolution_copy = copy.copy(icon_image_max_resolution)
            icon_image_max_resolution_copy = icon_image_max_resolution_copy.resize(sticker_icon_size, Image.ANTIALIAS)
            icon_image_max_resolution_copy.save(sticker_icon_file_path)

        with open(path.join(stickers_icon_set_dir_path, 'Contents.json'), "r+") as json_file:
            data = json.load(json_file)
            index = 0
            for sticker_icon_file_name in sticker_icon_file_names:
                data['images'][index]['filename'] = sticker_icon_file_name
                index += 1

            json_file.seek(0)
            json.dump(data, json_file)
            json_file.truncate()

        return True

    def update_pbxproj_file(self):
        pbxproj_project_plist = self.get_pbxproj_project_plist()
        if pbxproj_project_plist is None:
            return False

        pbxproj_objects = pbxproj_project_plist['objects']
        pbxproj_additions_plist = self.get_pbxproj_additions_plist()

        bundle_id = self.get_bundle_id()
        if bundle_id is None:
            return False

        pbx_container_item_proxy = pbxproj_additions_plist['E42E6D631EBFA912002B331A']
        pbx_container_item_proxy['containerPortal'] = pbxproj_project_plist['rootObject']
        pbxproj_objects['E42E6D631EBFA912002B331A'] = pbx_container_item_proxy

        pbx_native_target = pbxproj_additions_plist['E42E6D5D1EBFA911002B331A']
        pbxproj_objects['E42E6D5D1EBFA911002B331A'] = pbx_native_target

        pbx_resources_build_phase = pbxproj_additions_plist['E42E6D5C1EBFA911002B331A']
        pbxproj_objects['E42E6D5C1EBFA911002B331A'] = pbx_resources_build_phase

        pbx_file_reference = pbxproj_additions_plist['E42E6D5E1EBFA911002B331A']
        pbxproj_objects['E42E6D5E1EBFA911002B331A'] = pbx_file_reference

        pbx_file_reference = pbxproj_additions_plist['E42E6D601EBFA912002B331A']
        pbxproj_objects['E42E6D601EBFA912002B331A'] = pbx_file_reference

        pbx_file_reference = pbxproj_additions_plist['E42E6D621EBFA912002B331A']
        pbxproj_objects['E42E6D621EBFA912002B331A'] = pbx_file_reference

        pbx_build_file = pbxproj_additions_plist['E42E6D611EBFA912002B331A']
        pbxproj_objects['E42E6D611EBFA912002B331A'] = pbx_build_file

        pbx_build_file = pbxproj_additions_plist['E42E6D651EBFA912002B331A']
        pbxproj_objects['E42E6D651EBFA912002B331A'] = pbx_build_file

        pbx_copy_files_build_phase = pbxproj_additions_plist['E42E6D711EBFA912002B331A']
        pbxproj_objects['E42E6D711EBFA912002B331A'] = pbx_copy_files_build_phase

        pbx_group = pbxproj_additions_plist['E42E6D5F1EBFA911002B331A']
        pbxproj_objects['E42E6D5F1EBFA911002B331A'] = pbx_group

        pbx_target_dependency = pbxproj_additions_plist['E42E6D641EBFA912002B331A']
        pbxproj_objects['E42E6D641EBFA912002B331A'] = pbx_target_dependency

        # Set build configurations
        xc_configuration_list = self.get_first_dict_by_key('XCConfigurationList').values()[0]
        if xc_configuration_list is None:
            print 'Failed to get "XCConfigurationList"'
            return False

        xc_configuration_list_additions_plist = pbxproj_additions_plist['E42E6D701EBFA912002B331A']
        build_configurations = xc_configuration_list['buildConfigurations']
        for build_configuration in build_configurations:
            xc_build_configuration_additions_plist = copy.deepcopy(pbxproj_additions_plist['E42E6D681EBFA912002B331A'])
            xc_build_configuration_additions_plist['name'] = pbxproj_objects[build_configuration]['name']
            xc_build_configuration_additions_plist['buildSettings'][
                'PRODUCT_BUNDLE_IDENTIFIER'] = bundle_id + '.stickers'
            id = self.generate_id()
            pbxproj_objects[id] = xc_build_configuration_additions_plist
            xc_configuration_list_additions_plist["buildConfigurations"].append(id)

        pbxproj_objects['E42E6D701EBFA912002B331A'] = xc_configuration_list_additions_plist

        # Remove old configurations
        xc_build_configurations = self.get_dicts_by_key('XCBuildConfiguration')
        for key, xc_build_configuration in xc_build_configurations.iteritems():
            if key not in xc_configuration_list_additions_plist['buildConfigurations'] and \
                            'PRODUCT_NAME' in xc_build_configuration['buildSettings'] and \
                            xc_build_configuration['buildSettings']['PRODUCT_NAME'] == 'tt-stickers':
                print 'remove' + key
                pbxproj_objects.pop(key)

        # Add stickers target to PBXProject
        pbx_project = self.get_first_dict_by_key('PBXProject').values()[0]
        if pbx_project is None:
            print 'Failed to get "PBXProject"'
            return False
        if 'targets' not in pbx_project:
            print 'Failed to get "targets"'
            return False

        if 'E42E6D5D1EBFA911002B331A' not in pbx_project['targets']:
            pbx_project['targets'].append('E42E6D5D1EBFA911002B331A')

        # Add stickers group to mainGroup
        main_group = pbx_project['mainGroup']
        if 'E42E6D5F1EBFA911002B331A' not in pbxproj_objects[main_group]['children']:
            pbxproj_objects[main_group]['children'].append('E42E6D5F1EBFA911002B331A')

        # Add stickers product to productRefGroup
        if 'productRefGroup' in pbx_project:
            products_key = pbx_project['productRefGroup']
        else:
            products_key = self.get_first_dict_by_key('Products', 'name').keys()[0]

        if 'E42E6D5E1EBFA911002B331A' not in pbxproj_objects[products_key]['children']:
            pbxproj_objects[products_key]['children'].append('E42E6D5E1EBFA911002B331A')

        # Add stickers as dependency to PBXNativeTarget
        pbx_native_targets = self.get_dicts_by_key('PBXNativeTarget')
        dependency_added = False
        for pbx_native_target in pbx_native_targets.itervalues():
            if pbx_native_target['name'] != 'tt-stickers':
                if 'E42E6D641EBFA912002B331A' not in pbx_native_target['dependencies']:
                    pbx_native_target['dependencies'].append('E42E6D641EBFA912002B331A')
                if 'E42E6D711EBFA912002B331A' not in pbx_native_target['buildPhases']:
                    pbx_native_target['buildPhases'].append('E42E6D711EBFA912002B331A')
                dependency_added = True

        if not dependency_added:
            print 'Stickers not added as dependency to PBXNativeTarget'
            return False

        plistlib.writePlist(pbxproj_project_plist, self.pbxproj_file_path)
        return True

    def update_info_plist(self):
        info_plist = self.get_info_plist()
        if 'CFBundleDisplayName' not in info_plist:
            print 'Failed to get "CFBundleIconFiles" key from Info.plist'
            return False

        sticker_info_plist_path = path.join(self.stickers_dir_path, 'Info.plist')
        sticker_info_plist = plistlib.readPlist(sticker_info_plist_path)
        sticker_info_plist['CFBundleDisplayName'] = info_plist['CFBundleDisplayName'] + ' Stickers'
        sticker_info_plist['CFBundleVersion'] = info_plist['CFBundleVersion']
        sticker_info_plist['CFBundleShortVersionString'] = info_plist['CFBundleShortVersionString']
        plistlib.writePlist(sticker_info_plist, sticker_info_plist_path)
        return True

    # def get_build_configuration(self):
    #     scheme_file_path = path.join(self.xcode_proj_file_path, 'xcshareddata', 'xcschemes', self.scheme + '.xcscheme')
    #     if not path.isfile(scheme_file_path):
    #         print 'The scheme file: %s does not exists' % scheme_file_path
    #         self.build_configuration = None
    #         return self.build_configuration
    #
    #     tree = ET.parse(scheme_file_path)
    #     root_node = tree.getroot()
    #     launch_action_node = root_node.find('./LaunchAction')
    #     if launch_action_node is None:
    #         print 'Failed to find "LaunchAction" tag in scheme file: ' + scheme_file_path
    #         self.build_configuration = None
    #         return self.build_configuration
    #
    #     self.build_configuration = launch_action_node.get('buildConfiguration')
    #     if self.build_configuration is None:
    #         print 'Failed to find "LaunchAction[buildConfiguration]" attr in scheme file: ' + scheme_file_path
    #         self.build_configuration = None
    #         return self.build_configuration
    #
    #     return self.build_configuration

    def get_value_by_key_from_xc_build_configuration(self, key):
        build_configuration = self.build_configuration
        xc_build_configurations = self.get_dicts_by_key('XCBuildConfiguration')

        for xc_build_configuration in xc_build_configurations.itervalues():
            if xc_build_configuration['name'] == build_configuration and \
                            key in xc_build_configuration['buildSettings']:
                if key == 'INFOPLIST_FILE' and \
                                basename(path.dirname(
                                    xc_build_configuration['buildSettings']['INFOPLIST_FILE'])) == 'tt-stickers':
                    continue
                return xc_build_configuration['buildSettings'][key]

        return None

    def get_info_plist(self):
        if self.info_plist is not None:
            return self.info_plist

        info_plist_file_path = self.get_value_by_key_from_xc_build_configuration('INFOPLIST_FILE')
        self.info_plist = plistlib.readPlist(path.join(path.dirname(self.xcode_proj_file_path), info_plist_file_path))
        return self.info_plist

    def get_bundle_id(self):
        info_plist = self.get_info_plist()
        bundle_id = info_plist['CFBundleIdentifier']
        bundle_id_vars = re.findall('\$\{(.*?)\}', bundle_id)

        for bundle_id_var in bundle_id_vars:
            bundle_id_var_value = self.get_value_by_key_from_xc_build_configuration(bundle_id_var)
            if bundle_id_var_value is None:
                print 'Failed to find the var: %s' % bundle_id_var
                return None

            bundle_id = bundle_id.replace('${' + bundle_id_var + '}', bundle_id_var_value)
        return bundle_id

    def get_first_dict_by_key(self, value_attr, key_attr='isa'):
        pbxproj_project_plist = self.get_pbxproj_project_plist()
        if pbxproj_project_plist is None:
            return None

        pbxproj_objects = pbxproj_project_plist['objects']
        for key, value in pbxproj_objects.iteritems():
            if type(value) is plistlib._InternalDict:
                if key_attr in value and value[key_attr] == value_attr:
                    return {key: value}
        return None

    def get_dicts_by_key(self, value_attr, key_attr='isa'):
        pbxproj_project_plist = self.get_pbxproj_project_plist()
        if pbxproj_project_plist is None:
            return None

        pbxproj_objects = pbxproj_project_plist['objects']
        dict = {}
        for key, value in pbxproj_objects.iteritems():
            if type(value) is plistlib._InternalDict:
                if key_attr in value and value[key_attr] == value_attr:
                    dict[key] = value
        return dict

    @staticmethod
    def generate_id():
        return ''.join(str(uuid.uuid4()).upper().split('-')[1:])

    def find_dirs(self, dir_pattern):
        matches = []
        for root, dir_names, file_names in os.walk(os.path.expanduser(self.proj_dir_path)):
            for dir_name in fnmatch.filter(dir_names, dir_pattern):
                matches.append(os.path.join(root, dir_name))
        return matches

    def exists_sticker_images(self):
        if not isdir(self.sticker_images_dir_path):
            print 'The dir: %s does not exists' % self.sticker_images_dir_path
            return False

        sticker_images_file_names = os.listdir(self.sticker_images_dir_path)
        if len(sticker_images_file_names) == 0:
            print 'The dir: %s not contains any files' % self.sticker_images_dir_path
            return False

        return True
