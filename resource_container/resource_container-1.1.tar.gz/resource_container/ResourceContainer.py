import os
import yaml
import codecs
from general_tools.file_utils import write_file


class RC:
    def __init__(self, directory):
        """
        :param string directory:
        """
        self.dir = directory

        manifest_file = os.path.join(directory, 'manifest.yaml')
        self.manifest = self.__read_yaml_file(manifest_file)

        if type(self.dir) is not str and type(self.dir) is not unicode:
            raise Exception('Missing string parameter: dir')

    def __read_yaml_file(self, file):
        """
        Attemts to load a yaml file. If the file is missing or cannot be read None is returned
        :param file: the yaml file to be loaded
        :return: the yaml object or None
        """
        if os.access(file, os.R_OK):
            with codecs.open(file, 'r', encoding='utf-8') as stream:
                try:
                    return yaml.load(stream)
                except yaml.YAMLError as exc:
                    print(exc)
                    return None

    @property
    def path(self):
        return self.dir

    @property
    def type(self):
        return self.manifest['dublin_core']['type']

    @property
    def language(self):
        return self.manifest['dublin_core']['language']

    @property
    def resource(self):
        return self.manifest['dublin_core']

    @property
    def conforms_to(self):
        if type(self.manifest['dublin_core']['conformsto']) is str:
            return self.manifest['dublin_core']['conformsto'].replace('rc', '')
        else:
            return None

    @property
    def chunk_ext(self):
        return {
            'text/usx': 'usx',
            'text/usfm': 'usfm',
            'text/markdown': 'md'
        }.get(self.manifest['dublin_core']['format'], 'txt')

    def project(self, identifier=None):
        """
        Retrieves a project from the RC.

        You can exclude the parameter if the RC only has one project.

        :param identifier:
        :return:
        """
        if identifier:
            for p in self.manifest['projects']:
                if p['identifier'] == identifier:
                    return p
        else:
            if len(self.manifest['projects']) == 1:
                return self.manifest['projects'][0]
            elif len(self.manifest['projects']) > 1:
                raise Exception('Multiple projects found. Specify the project identifier.')

    @property
    def project_count(self):
        return len(self.manifest['projects'])

    @property
    def project_ids(self):
        identifiers = []
        for p in self.manifest['projects']:
            identifiers.append(p['identifier'])
        return identifiers

    def chapters(self, identifier=None):
        """
        Returns an array of chapters in this resource container.

        You can exclude the parameter if this RC only has one project.

        :param identifier: The project identifier
        :return array:
        """
        p = self.project(identifier)
        if p is None:
            return []
        else:
            directory = os.path.join(self.dir, p['path'])
            files = os.listdir(directory)
            if 'config.yaml' in files:
                files.remove('config.yaml')
            return files

    def chunks(self, project_identifier, chapter_identifier=None):
        if chapter_identifier is None:
            chapter_identifier = project_identifier
            project_identifier = 0

        p = self.project(project_identifier)
        if p is None:
            return []

        directory = os.path.join(self.dir, p['path'], chapter_identifier)
        return os.listdir(directory)

    def read_chunk(self, project_identifier, chapter_identifier, chunk_identifier=None):
        if chunk_identifier is None:
            chunk_identifier = chapter_identifier
            chapter_identifier = project_identifier
            project_identifier = None

        p = self.project(project_identifier)
        if p is None:
            return []

        file_path = os.path.join(self.dir, p['path'], chapter_identifier, chunk_identifier + '.' + self.chunk_ext)

        if os.access(file_path, os.R_OK):
            contents = open(file_path).read()
        else:
            contents = None
        return contents

    def write_chunk(self, project_identifier, chapter_identifier, chunk_identifier, content=None):
        if content is None:
            content = chunk_identifier
            chunk_identifier = chapter_identifier
            chapter_identifier = project_identifier
            project_identifier = None

        p = self.project(project_identifier)
        if p is None:
            return

        # We need to remove the chunk if no content is specified.
        if content == '':
            file_path = os.path.join(self.dir, p['path'], chapter_identifier, chunk_identifier + '.' + self.chunk_ext)
            if os.access(file_path, os.R_OK):
                os.remove(file_path)
        else:
            directory_path = os.path.join(self.dir, p['path'], chapter_identifier)
            file_path = os.path.join(directory_path, chunk_identifier + '.' + self.chunk_ext)

            if not os.path.isdir(directory_path):
                os.makedirs(directory_path)

            write_file(file_path, content)

    def write_toc(self, project_identifier, content=None):
        if content is None:
            content = project_identifier
            project_identifier = None

        p = self.project(project_identifier)
        if p is None:
            return

        file_path = os.path.join(self.dir, p['path'], 'toc.yaml')
        if content == '':
            if os.access(file_path, os.R_OK):
                os.remove(file_path)
        else:
            write_file(file_path, yaml.dump(content, default_flow_style=False))

    def write_config(self, project_identifier, content=None):
        if content is None:
            content = project_identifier
            project_identifier = None

        p = self.project(project_identifier)
        if p is None:
            return

        file_path = os.path.join(self.dir, p['path'], 'config.yaml')
        if content == '':
            if os.access(file_path, os.R_OK):
                os.remove(file_path)
        else:
            write_file(file_path, yaml.dump(content, default_flow_style=False))

    def config(self, project_identifier=None):
        p = self.project(project_identifier)
        if p is None:
            return None

        file_path = os.path.join(self.dir, p['path'], 'config.yaml')
        return self.__read_yaml_file(file_path)

    def toc(self, project_identifier=None):
        p = self.project(project_identifier)
        if p is None:
            return None

        file_path = os.path.join(self.dir, p['path'], 'toc.yaml')
        return self.__read_yaml_file(file_path)
