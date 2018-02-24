# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.blok import Blok


class AttachmentBlok(Blok):
    """Add attachment in AnyBlok"""

    version = '1.0.0'
    required = ['anyblok-core']
    author = 'Suzanne Jean-Sébastien'

    @classmethod
    def import_declaration_module(cls):
        from . import attachment  # noqa
        from . import document  # noqa

    @classmethod
    def reload_declaration_module(cls, reload):
        from . import attachment
        reload(attachment)
        from . import document
        reload(document)
