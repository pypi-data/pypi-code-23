from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import *  # NOQA
from unittest.case import TestCase

import models

from zsl_openapi.api import ApiDescription
from zsl_openapi.builders.models import PersistentModelsApiDescriptionBuilder


class ModelBuilderTestCase(TestCase):
    def testBuild(self):
        builder = self.givenBuilderWithModels()
        description = self.whenGeneratingApiDescription(builder)
        self.thenApiDescriptionShouldBeCorrect(description)

    def givenBuilderWithModels(self):
        # type: ()->PersistentModelsApiDescriptionBuilder
        return PersistentModelsApiDescriptionBuilder(models)

    def whenGeneratingApiDescription(self, builder):
        # type: (PersistentModelsApiDescriptionBuilder)->ApiDescription
        description = ApiDescription()
        builder.build(description)
        return description

    def thenApiDescriptionShouldBeCorrect(self, description):
        # type: (ApiDescription)->None
        self.assertEquals(1, len(description.definitions), "One model should be added.")
        model = description.definitions['User']
        self.assertEquals("User", model.name, "Name of the model must be correct.")
        self.assertEquals("object", model.type, "Type of the model must be object.")

        self.assertEquals(4, len(model.properties), "There are 3 properties of the model.")

        email_property = model.properties['email']
        self.assertEquals("email", email_property.name, "Email property must have the correct name")
        self.assertEquals("string", email_property.type, "Email property must have the correct type")
        self.assertIsNone(email_property.format, "Email property must have no format")

        id_property = model.properties['id']
        self.assertEquals("id", id_property.name, "Id property must have the correct name")
        self.assertEquals("integer", id_property.type, "Id property must have the correct type")
        self.assertIsNone(id_property.format, "Id property must have no format")

        created_property = model.properties['created']
        self.assertEquals("created", created_property.name, "Created property must have the correct name")
        self.assertEquals("string", created_property.type, "Created property must have the correct type")
        self.assertEquals("date-time", created_property.format, "Created property must have date-time format")
