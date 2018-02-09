# ~*~ coding: utf-8 ~*~
#-
# OSMAlchemy - OpenStreetMap to SQLAlchemy bridge
# Copyright (c) 2016 Michael Bayer <mike_mp@zzzcomputing.com>
# Copyright (c) 2016 Dominik George <nik@naturalnet.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

def monkey_patch_sqlalchemy():
    from sqlalchemy.ext.associationproxy import AssociationProxy
    from sqlalchemy.util import memoized_property

    # Monkey patch support for chained association proxy queries into SQLAlchemy
    # https://bitbucket.org/zzzeek/sqlalchemy/issues/3769/chained-any-has-with-association-proxy
    if not hasattr(AssociationProxy, "_unwrap_target_assoc_proxy"):
        def _unwrap_target_assoc_proxy(self):
            attr = getattr(self.target_class, self.value_attr)
            if isinstance(attr, AssociationProxy):
                return attr, getattr(self.target_class, attr.target_collection)
            return None, None
        AssociationProxy._unwrap_target_assoc_proxy = memoized_property(_unwrap_target_assoc_proxy)

        orig_any = AssociationProxy.any
        def any_(self, criterion=None, **kwargs):
            target_assoc, inner = self._unwrap_target_assoc_proxy
            if target_assoc is not None:
                if target_assoc._target_is_object and target_assoc._uselist:
                    inner = inner.any(criterion=criterion, **kwargs)
                else:
                    inner = inner.has(criterion=criterion, **kwargs)
                return self._comparator.any(inner)
            orig_any(self, criterion, **kwargs)
        AssociationProxy.any = any_

        orig_has = AssociationProxy.has
        def has(self, criterion=None, **kwargs):
            target_assoc, inner = self._unwrap_target_assoc_proxy
            if target_assoc is not None:
                if target_assoc._target_is_object and target_assoc._uselist:
                    inner = inner.any(criterion=criterion, **kwargs)
                else:
                    inner = inner.has(criterion=criterion, **kwargs)
                return self._comparator.has(inner)
            orig_has(self, criterion, **kwargs)
        AssociationProxy.has = has

def monkey_patch_flask_restless():
    try:
        import flask_restless.helpers
    except:
        return

    # Monkey patch support for chained association proxy into Flask-Restless
    # https://github.com/jfinkels/flask-restless/issues/578
    if hasattr(flask_restless.helpers, "get_related_association_proxy_model"):
        from sqlalchemy.ext.associationproxy import AssociationProxy

        def _get_related_association_proxy_model(attr):
            if isinstance(attr.remote_attr, AssociationProxy):
                return _get_related_association_proxy_model(attr.remote_attr)
            else:
                prop = attr.remote_attr.property
                for attribute in ('mapper', 'parent'):
                    if hasattr(prop, attribute):
                        return getattr(prop, attribute).class_
                return None

        flask_restless.helpers.get_related_association_proxy_model = _get_related_association_proxy_model
