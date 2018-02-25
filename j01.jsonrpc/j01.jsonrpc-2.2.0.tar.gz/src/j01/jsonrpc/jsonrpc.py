##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

"""
$Id: __init__.py 6 2006-04-16 01:28:45Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

from z3c.jsonrpc.publisher import MethodPublisher


class J01LoadContent(MethodPublisher):
    """Can load content via JSONRPC.

    Note: This method publisher must be able to traverse the context which is
    a view or a form. Our default JSON-RPC tarverser could be used.
    See: JSONRPCTraversablePage

    Note: This method is registered with zope.Public permission and will run
    into Unauthorized if the principal does not have the permission to traverse
    the view.

    This method supports the browser history api based on the j01.history.js
    concept.

    Note: it's important that you only provide a stateURL for pages which are
    available as standalone page and can get loaded with a browser request.
    Use the cbStateURL if your page is only loadable with a jsonrpc request.

    """

    def j01LoadContent(self):
        self.context.update()
        if self.context.nextURL is None and self.context.nextContentURL is None:
            content = self.context.render()
        else:
            # skip rendering if a next url is given
            content = None
        # setup response data after render
        data = {
            # url is not used by default callback concept
            'url': self.context.pageURL,
            # redirect url
            'nextURL': self.context.nextURL,
            # load content url
            'nextContentURL': self.context.nextContentURL,
            # content for rendering
            'content': content,
            # jquery content target expression
            'contentTargetExpression': self.context.contentTargetExpression,
            # callback rendering concept, used for invoke javascript rendering
            # if the default content and contentTargetExpression is not enough
            'contentRenderMethodName': getattr(self.context,
                'contentRenderMethodName', None),
            }
        # setup layout helper css classes
        if self.context.cssBodyClass is not None:
            data['cssBodyClass'] = self.context.cssBodyClass
        if self.context.cssHTMLClass is not None:
            data['cssHTMLClass'] = self.context.cssHTMLClass
        if self.context.cssBodyId is not None:
            data['cssBodyId'] = self.context.cssBodyId
        if self.context.cssHTMLId is not None:
            data['cssHTMLId'] = self.context.cssHTMLId
        # setup optional animation
        if self.context.scrollToExpression is not None:
            data['scrollToExpression'] = self.context.scrollToExpression
            data['scrollToOffset'] = self.context.scrollToOffset
            data['scrollToSpeed'] = self.context.scrollToSpeed
        # setup optinal navigation hash useable for for custom navigation
        # concepts (not used in j01.jsonrpc.js but usable for mobile concepts)
        if self.context.nextHash is not None:
            data['nextHash'] = self.context.nextHash
        # setup history state data
        if not self.context.skipState:
            data['state'] = {
                'url': self.context.stateURL,
                'title': self.context.stateTitle,
                'cbURL': self.context.cbStateURL,
                'method': self.context.cbStateMethod,
                'params': self.context.cbStateParams,
                'onSuccess': self.context.cbStateSuccess,
                'onError': self.context.cbStateError,
                'onTimeout': self.context.cbStateTimeout,
                }
        return data


class J01FormProcessor(MethodPublisher):
    """Can process a form button handler via JSONRPC.

    Note: This method publisher must be able to traverse the context which is
    a view or a form. Our default JSON-RPC tarverser could be used.
    See: JSONRPCTraversablePage

    Note: This method is registered with zope.Public permission and will run
    into Unauthorized if the principal does not have the permission to traverse
    the view.
    """

    def j01FormProcessor(self):
        self.context.update()
        if self.context.nextURL is None and self.context.nextContentURL is None:
            content = self.context.render()
        else:
            # skip rendering if a next url is given
            content = None
        # setup response data after render
        data = {
            'url': self.context.pageURL,
            'nextURL': self.context.nextURL,
            'nextContentURL': self.context.nextContentURL,
            'content': content,
            'contentTargetExpression': self.context.contentTargetExpression,
            # callback rendering concept, used for invoke javascript rendering
            # if the default content and contentTargetExpression is not enough
            'contentRenderMethodName': getattr(self.context,
                'contentRenderMethodName', None),
            }
        # setup layout helper css classes
        if self.context.cssBodyClass is not None:
            data['cssBodyClass'] = self.context.cssBodyClass
        if self.context.cssHTMLClass is not None:
            data['cssHTMLClass'] = self.context.cssHTMLClass
        # setup optinal animation
        if self.context.scrollToExpression is not None:
            data['scrollToExpression'] = self.context.scrollToExpression
            data['scrollToOffset'] = self.context.scrollToOffset
            data['scrollToSpeed'] = self.context.scrollToSpeed
        # setup optinal navigation hash useable for for custom navigation
        # concepts (not used in j01.jsonrpc.js but usable for mobile concepts)
        if self.context.nextHash is not None:
            data['nextHash'] = self.context.nextHash
        # setup history state data
        if not self.context.skipState:
            data['state'] = {
                'url': self.context.stateURL,
                'title': self.context.stateTitle,
                'cbURL': self.context.cbStateURL,
                'method': self.context.cbStateMethod,
                'params': self.context.cbStateParams,
                'onSuccess': self.context.cbStateSuccess,
                'onError': self.context.cbStateError,
                'onTimeout': self.context.cbStateTimeout,
                }
        return data
