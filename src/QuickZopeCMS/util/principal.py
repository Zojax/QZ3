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

from zope.component import getUtility
from zope.app.security.interfaces import IAuthentication

def getAuthenticatorPrefix(auth, principal):
    for name, authenticator in auth.getAuthenticatorPlugins():
        prefix = authenticator.prefix
        if prefix and prefix in principal.id:
            return prefix
    raise KeyError

def getUID(principal):
    auth = getUtility(IAuthentication)
    prefix = auth.prefix + getAuthenticatorPrefix(auth, principal)
    return int(principal.id[len(prefix):])

def getPrincipal(uid):
    auth = getUtility(IAuthentication)
    prefix = auth.prefix + u'zojax.pf'
    uid = unicode(uid)
    if len(uid) == 1:
        uid = u'0' + uid
    return auth.getPrincipal(prefix + uid)
