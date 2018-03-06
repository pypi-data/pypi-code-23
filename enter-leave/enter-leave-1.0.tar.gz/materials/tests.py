# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from . import models
from .test_data import material_data

from comm.testcase import PublicBaseClass
import json


# Create your tests here.


class TestMaterialViewCase(PublicBaseClass):
    @classmethod
    def setUpTestData(cls):
        cls.material = models.Material.objects.create(**material_data.material_create_data)
        material_data.material_spec_create_data['material'] = cls.material
        cls.material_spec = models.MaterialSpecification.objects.create(**material_data.material_spec_create_data)
        material_data.material_entry_create_data['material_spec'] = cls.material_spec
        cls.material_entry = models.MaterialsEntry.objects.create(**material_data.material_entry_create_data)

    def test_material_list(self):
        # get
        r = self.operations(url=material_data.material_list)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data[0].get('name'), self.material.name)

        # post
        material_data.material_create_data['code'] = 'test'
        r = self.operations(url=material_data.material_list, method=material_data.post_method,
                            params=material_data.material_create_data, status_code=material_data.created_status_code)
        self.assertEqual(r.status_code, material_data.created_status_code)
        self.assertEqual(r.data['code'], 'test')

    def test_material_detail(self):
        url = material_data.material_detail.format(pk=self.material.id)
        # get
        r = self.operations(url=url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data.get('code'), self.material.code)

        # put
        material_data.material_create_data['name'] = 'test'
        r = self.operations(url=url,
                            method=material_data.put_method, params=material_data.material_create_data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['name'], 'test')

        # patch
        patch_param = {
            'name': 'test_01'
        }
        r = self.operations(url=url, method=material_data.patch_method, params=patch_param)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['name'], 'test_01')

        # delete
        r = self.operations(url=url,
                            method=material_data.delete_method, status_code=material_data.delete_status_code)
        self.assertEqual(r.status_code, material_data.delete_status_code)

    def test_material_spec_list(self):
        url = material_data.material_spec_list
        # get
        r = self.operations(url=url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data[0].get('name'), self.material_spec.name)

        # post
        material_data.material_spec_create_data['code'] = 'test_spec'
        material_data.material_spec_create_data['material'] = self.material.id
        r = self.operations(url=url, method=material_data.post_method,
                            params=material_data.material_spec_create_data,
                            status_code=material_data.created_status_code)
        self.assertEqual(r.status_code, material_data.created_status_code)
        self.assertEqual(r.data['code'], 'test_spec')

    def test_material_spec_detail(self):
        url = material_data.material_spec_detail.format(pk=self.material_spec.id)
        # get
        r = self.operations(url=url)
        print r.status_code
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data.get('code'), self.material_spec.code)

        # put
        material_data.material_spec_create_data['name'] = 'test_spec'
        r = self.operations(url=url,
                            method=material_data.put_method, params=material_data.material_create_data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['name'], 'test')

        # patch
        patch_param = {
            'name': 'test_spec_01'
        }
        r = self.operations(url=url, method=material_data.patch_method, params=patch_param)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['name'], 'test_spec_01')

        # delete
        r = self.operations(url=url,
                            method=material_data.delete_method, status_code=material_data.delete_status_code)
        self.assertEqual(r.status_code, material_data.delete_status_code)

    def test_material_entry_list(self):
        url = material_data.material_entry_list
        # get
        r = self.operations(url=url)
        self.assertEqual(r.status_code, 200)
        print r.data[0]['material']
        print r.data[0]['material_spec']
        self.assertEqual(r.data[0]['material_spec']['code'], self.material_spec.code)

        # post
        material_data.material_entry_create_data['material_spec'] = self.material_spec.id
        r = self.operations(url=url, method=material_data.post_method,
                            params=material_data.material_entry_create_data,
                            status_code=material_data.created_status_code)
        self.assertEqual(r.status_code, material_data.created_status_code)
        self.assertEqual(r.data['material']['name'], self.material.name)

    def test_material_entry_detail(self):
        url = material_data.material_entry_detail.format(pk=self.material_entry.id)
        # get
        r = self.operations(url=url)
        print r.status_code
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data.get('lot_number'), self.material_entry.lot_number)

        # put
        material_data.put_data['lot_number'] = 'test_number'
        r = self.operations(url=url, method=material_data.put_method, params=material_data.put_data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['lot_number'], 'test_number')

        # patch
        patch_param = {
            'material': {
                'name': "",
                'code': "",
                'unit': "",
            },
            'lot_number': 'test_number_01',
            'material_spec': self.material_spec.id
        }
        r = self.operations(url=url, method=material_data.patch_method, params=patch_param)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['lot_number'], 'test_number_01')

        # delete
        r = self.operations(url=url,
                            method=material_data.delete_method, status_code=material_data.delete_status_code)
        print r.data
        self.assertEqual(r.status_code, material_data.delete_status_code)
