##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
$Id$
"""

from z3c.configurator import ConfigurationPluginBase

from zope.app.component.hooks import setSite
from zope.app.zapi import adapts, getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.security.proxy import getObject

from zojax.blogger.interfaces import IBloggerProduct
from zojax.portal.interfaces import IPortal
from zojax.richtext.interfaces import IContentEditorConfiglet
from zojax.skintool.interfaces import ISkinTool



class ConfigurationPlugin(ConfigurationPluginBase):
    adapts(IPortal)

    dependencies = ('basic',)

    def __call__(self, *args):
        site  = getObject(self.context)
        #sm = site.getSiteManager()
        setSite(site)

        # install blogger product
        blogger = getUtility(IBloggerProduct)
        if not blogger.__installed__:
            blogger.install()

        # set wysiwyg editor
        configlet = getUtility(IContentEditorConfiglet)
        configlet.default_editor = 'tinymce'
        notify(ObjectModifiedEvent(configlet))

        # set skin
        skintool = getUtility(ISkinTool)
        skintool.skin = 'quick.theme.sample'
        notify(ObjectModifiedEvent(skintool))
