import os
import shutil
from unittest import TestCase
from resource_container import factory
from general_tools.file_utils import write_file
import pytest
import yaml

DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')


def make_rc(dir, multi=False):
    manifest = {
        'dublin_core': {
            'type': 'book',
            'conformsto': 'rc0.2',
            'format': 'text/usfm',
            'identifier': 'en-ulb',
            'title': 'Unlocked Literal Bible',
            'subject': 'Bible translation',
            'description': 'The Unlocked Literal Bible is an open-licensed version of the Bible that is intended to provide a form-centric translation of the Bible.',
            'language': {
                'identifier': 'en',
                'title': 'English',
                'direction': 'ltr'
            },
            'source': [{
                'language': 'en',
                'identifier': 'en-asv',
                'version': '1990'
            }],
            'rights': 'CC BY-SA 4.0',
            'creator': 'Wycliffe Associates',
            'contributor': [
                'Wycliffe Associates'
            ],
            'relation': [
                'en-udb',
                'en-tn'
            ],
            'publisher': 'Door43',
            'issued': '2015-12-17',
            'modified': '2015-12-22',
            'version': '3'
        },
        'checking': {
            'checking_entity': [
                'Wycliffe Associates',
            ],
            'checking_level': '3'
        },
        'projects': [{
            'identifier': 'gen',
            'title': 'Genesis',
            'versification': 'kjv',
            'sort': 1,
            'path': './gen',
            'categories': [
                'bible-ot'
            ]
        }]
    }

    if multi is True:
        manifest['projects'].append({
            'identifier': 'exo',
            'title': 'Exodus',
            'versification': 'kjv',
            'sort': 2,
            'path': './exo',
            'categories': [
                'bible-ot'
            ]
        })

    rc = factory.create(dir, manifest)
    write_file(os.path.join(dir, 'gen', '01', '01.usfm'), 'gen 1:1')
    write_file(os.path.join(dir, 'gen', '01', '02.usfm'), 'gen 1:2')
    write_file(os.path.join(dir, 'gen', '01', '03.usfm'), 'gen 1:3')
    write_file(os.path.join(dir, 'gen', '02', '01.usfm'), 'gen 2:1')
    write_file(os.path.join(dir, 'gen', '02', '02.usfm'), 'gen 2:2')

    if multi is True:
        write_file(os.path.join(dir, 'exo', '01', '01.usfm'), 'exo 1:1')
        write_file(os.path.join(dir, 'exo', '01', '02.usfm'), 'exo 1:2')
        write_file(os.path.join(dir, 'exo', '01', '03.usfm'), 'exo 1:3')
        write_file(os.path.join(dir, 'exo', '02', '01.usfm'), 'exo 2:1')
        write_file(os.path.join(dir, 'exo', '02', '02.usfm'), 'exo 2:2')

class TestResourceContainer(TestCase):

    @classmethod
    def setUpClass(cls):
        directory = os.path.join(DATA_DIR, 'temp')
        if os.path.exists(directory):
            shutil.rmtree(directory)

    def test_load_a_single_book_rc(self):
        directory = os.path.join(DATA_DIR, 'temp', 'single')
        make_rc(directory)

        rc = factory.load(directory)
        assert rc.path == directory
        assert len(rc.chapters()) == 2
        assert len(rc.chunks('01')) == 3
        assert len(rc.chunks('02')) == 2
        assert rc.read_chunk('01', '03') == 'gen 1:3'

    def test_load_a_multi_book_rc(self):
        directory = os.path.join(DATA_DIR, 'temp', 'multi')
        make_rc(directory, True)

        rc = factory.load(directory)
        assert rc.project_count == 2
        assert rc.path == directory
        assert len(rc.chapters('gen')) == 2
        assert len(rc.chunks('gen', '01')) == 3
        assert len(rc.chunks('gen', '02')) == 2
        assert rc.read_chunk('gen', '01', '03') == 'gen 1:3'

        assert len(rc.chapters('exo')) == 2
        assert len(rc.chunks('exo', '01')) == 3
        assert len(rc.chunks('exo', '02')) == 2
        assert rc.read_chunk('exo', '01', '03') == 'exo 1:3'

    def test_should_fail_to_load_missing_rc(self):
        directory = os.path.join(DATA_DIR, 'temp', 'missing')
        os.mkdir(directory)
        rc = None
        with pytest.raises(Exception) as my_error:
            rc = factory.load(directory)
        assert 'Not a resource container. Missing manifest.yaml' in str(my_error.value)
        assert rc is None

    def test_should_load_a_missing_rc_when_not_in_strict_mode(self):
        directory = os.path.join(DATA_DIR, 'temp', 'missing')
        if os.path.isdir(directory):
            os.rmdir(directory)
        os.mkdir(directory)
        rc = factory.load(directory, False)
        assert rc is not None

    def test_updating_a_rc(self):
        directory = os.path.join(DATA_DIR, 'temp', 'updated_container')
        chunk_text = 'Hello world!'

        make_rc(directory)

        rc = factory.load(directory)
        rc.write_chunk('02', '03', chunk_text)
        rc.write_chunk('03', '01', chunk_text)
        assert rc.read_chunk('02', '03') == chunk_text
        assert rc.read_chunk('03', '01') == chunk_text

    def test_creating_a_rc(self):
        directory = os.path.join(DATA_DIR, 'temp', 'new_rc')
        manifest = {
            'dublin_core': {
                'type': 'book',
                'format': 'text/usfm',
                'identifier': 'en-me',
                'language': {
                    'identifier': 'en',
                    'title': 'English',
                    'direction': 'ltr'
                },
                'rights': 'CC BY-SA 4.0'
            }
        }
        rc = factory.create(directory, manifest)
        assert rc.conforms_to == factory.current_version
        assert rc.type == 'book'

    def test_not_opening_a_rc_that_is_too_old(self):
        directory = os.path.join(DATA_DIR, 'temp', 'old_rc')
        manifest = {
            'dublin_core': {
                'type': 'book',
                'conformsto': 'rc0.1',
                'format': 'text/usfm',
                'identifier': 'en-ulb',
                'language': {
                    'identifier': 'en',
                    'title': 'English',
                    'direction': 'ltr'
                },
            },
            'projects': []
        }
        write_file(os.path.join(directory, 'manifest.yaml'), yaml.dump(manifest, default_flow_style=False))
        rc = None
        with pytest.raises(Exception) as my_error:
            rc = factory.load(directory)
        assert 'Unsupported resource container version. Found 0.1 but expected 0.2' in str(my_error.value)
        assert rc is None

    def test_not_opening_rc_that_is_too_new(self):
        directory = os.path.join(DATA_DIR, 'temp', 'too_new_rc')
        manifest = {
            'dublin_core': {
                'type': 'book',
                'conformsto': 'rc999.1',
                'format': 'text/usfm',
                'identifier': 'en-ulb',
                'language': {
                    'identifier': 'en',
                    'title': 'English',
                    'direction': 'ltr'
                },
            },
            'projects': []
        }
        write_file(os.path.join(directory, 'manifest.yaml'), yaml.dump(manifest, default_flow_style=False))
        rc = None
        with pytest.raises(Exception) as my_error:
            rc = factory.load(directory)
        assert 'Unsupported resource container version. Found 999.1 but expected 0.2' in str(my_error.value)
        assert rc is None

    def test_thowing_an_error_when_not_specifying_project_in_multi_project_rc(self):
        directory = os.path.join(DATA_DIR, 'temp', 'big_container')

        make_rc(directory, True)

        rc = factory.load(directory)
        with pytest.raises(Exception) as my_error:
            rc.chapters()
        assert 'Multiple projects found. Specify the project identifier.' in str(my_error.value)
        with pytest.raises(Exception) as my_error2:
            rc.chunks('01')
        assert 'Multiple projects found. Specify the project identifier.' in str(my_error2.value)
        with pytest.raises(Exception) as my_error3:
            rc.read_chunk('01', '01')
        assert 'Multiple projects found. Specify the project identifier.' in str(my_error3.value)
        with pytest.raises(Exception) as my_error4:
            rc.write_chunk('01', '01', 'test')
        assert 'Multiple projects found. Specify the project identifier.' in str(my_error4.value)

    def test_open_project(self):
        dir = os.path.join(DATA_DIR, 'existing-rc', 'en-obs')
        rc = factory.load(dir)
        project = rc.project()
        assert project['identifier'] == 'obs'
        assert rc.conforms_to == '0.2'
        assert type(rc.chapters()) == list
        assert rc.language['identifier'] == 'en'
        assert rc.chunks('01') == ['01.md']
        assert rc.read_chunk('01', '01').split('\n', 1)[0] == '# 1. The Creation'
        assert rc.type == 'book'
        assert rc.config()['content']['10']['10']['dict'][0] == '/en/tw/bible/god'
        assert rc.toc() is None

    def test_write_and_remove_chunk(self):
        dir = os.path.join(DATA_DIR, 'existing-rc', 'en-obs')
        rc = factory.load(dir)
        my_chunk = 'this is a test'
        rc.write_chunk('test', 'test', my_chunk)
        assert rc.read_chunk('test', 'test') == my_chunk
        rc.write_chunk('test', 'test', '')
        assert rc.read_chunk('test', 'test') is None

    def test_create_resource_container(self):
        dir = os.path.join(DATA_DIR, 'temp', 'new-rc', 'en-obs')
        container = factory.create(dir, {
            'dublin_core': {
                'type': 'book',
                'format': 'text/markdown',
                'identifier': 'obs',
                'language': {
                    'direction': 'ltr',
                    'identifier': 'en',
                    'title': 'English'
                },
                'rights': 'CC BY-SA 4.0'
            },
            'checking': {
                'checking_entity': [
                    'Wycliffe Associates',
                ],
                'checking_level': '3'
            },
            'projects': [{
                'identifier': 'gen',
                'title': 'Genesis',
                'versification': 'kjv',
                'sort': 1,
                'path': './gen',
                'categories': [
                    'bible-ot'
                ]
            }]
        })
        assert container.conforms_to == '0.2'
        assert container.project_count == 1
        assert container.manifest['checking']['checking_entity'][0] == 'Wycliffe Associates'
        assert container.manifest['projects'][0]['identifier'] == 'gen'

    def test_writing_and_removing_toc_file(self):
        directory = os.path.join(DATA_DIR, 'temp', 'toc-rc', 'en-obs')
        make_rc(directory, False)
        rc = factory.load(directory)

        toc = {
            'title': 'My Title',
            'sub-title': 'My sub-title',
            'link': 'my-link',
            'sections': []
        }
        rc.write_toc(toc)
        written_toc = rc.toc()
        assert written_toc['title'] == 'My Title'

        # Remove the toc
        rc.write_toc('')
        assert rc.toc() is None

        directory = os.path.join(DATA_DIR, 'temp', 'toc-rc-multi', 'en-obs')
        make_rc(directory, True)
        rc = factory.load(directory)

        rc.write_toc('gen', toc)

        written_toc = rc.toc('gen')
        assert written_toc['title'] == 'My Title'

        # Remove the toc
        rc.write_toc('gen', '')
        assert rc.toc('gen') is None

    def test_writing_and_removing_config_file(self):
        directory = os.path.join(DATA_DIR, 'temp', 'config-rc', 'en-obs')
        make_rc(directory, False)
        rc = factory.load(directory)

        config = {
            'content': {
                '01': {
                    '01': {
                        'dict': [
                            '//tw/bible/dict/creation',
                            '//tw/bible/dict/god'
                        ]
                    }
                }
            }
        }
        rc.write_config(config)
        written_config = rc.config()
        assert written_config['content']['01']['01']['dict'][1] == '//tw/bible/dict/god'

        # Remove the config
        rc.write_config('')
        assert rc.config() is None

        directory = os.path.join(DATA_DIR, 'temp', 'config-rc-multi', 'en-obs')
        make_rc(directory, True)
        rc = factory.load(directory)

        rc.write_config('gen', config)

        written_config = rc.config('gen')
        assert written_config['content']['01']['01']['dict'][1] == '//tw/bible/dict/god'

        # Remove the toc
        rc.write_config('gen', '')
        assert rc.config('gen') is None

    def test_project_ids_property(self):
        directory = os.path.join(DATA_DIR, 'temp', 'project-ids-rc', 'en-obs')
        make_rc(directory, True)
        rc = factory.load(directory)
        assert rc.project_ids[0] == 'gen'
        assert rc.project_ids[1] == 'exo'