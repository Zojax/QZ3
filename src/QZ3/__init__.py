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

from zope.i18nmessageid import MessageFactory
_ = MessageFactory(u'QZ3')

from z3c.schema.email import interfaces


class NotValidRFC822MailAdress(interfaces.NotValidRFC822MailAdress):
    __doc__ = _("""Not a valid email address""")


interfaces.NotValidRFC822MailAdress = NotValidRFC822MailAdress
