# -*- coding: utf-8 -*-
#
# (c) 2019, Felix Fontein <felix@fontein.de>
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, division, print_function
__metaclass__ = type


import base64

from ansible.module_utils._text import to_bytes, to_text

try:
    import OpenSSL
except ImportError:
    # Error handled in the calling module.
    pass

from ._objects import (
    NORMALIZE_NAMES_SHORT,
    NORMALIZE_NAMES,
)

from ._obj2txt import obj2txt


def pyopenssl_normalize_name(name, short=False):
    nid = OpenSSL._util.lib.OBJ_txt2nid(to_bytes(name))
    if nid != 0:
        b_name = OpenSSL._util.lib.OBJ_nid2ln(nid)
        name = to_text(OpenSSL._util.ffi.string(b_name))
    if short:
        return NORMALIZE_NAMES_SHORT.get(name, name)
    else:
        return NORMALIZE_NAMES.get(name, name)


def pyopenssl_get_extensions_from_cert(cert):
    # While pyOpenSSL allows us to get an extension's DER value, it won't
    # give us the dotted string for an OID. So we have to do some magic to
    # get hold of it.
    result = dict()
    ext_count = cert.get_extension_count()
    for i in range(0, ext_count):
        ext = cert.get_extension(i)
        entry = dict(
            critical=bool(ext.get_critical()),
            value=base64.b64encode(ext.get_data()),
        )
        oid = obj2txt(
            OpenSSL._util.lib,
            OpenSSL._util.ffi,
            OpenSSL._util.lib.X509_EXTENSION_get_object(ext._extension)
        )
        # This could also be done a bit simpler:
        #
        #   oid = obj2txt(OpenSSL._util.lib, OpenSSL._util.ffi, OpenSSL._util.lib.OBJ_nid2obj(ext._nid))
        #
        # Unfortunately this gives the wrong result in case the linked OpenSSL
        # doesn't know the OID. That's why we have to get the OID dotted string
        # similarly to how cryptography does it.
        result[oid] = entry
    return result


def pyopenssl_get_extensions_from_csr(csr):
    # While pyOpenSSL allows us to get an extension's DER value, it won't
    # give us the dotted string for an OID. So we have to do some magic to
    # get hold of it.
    result = dict()
    for ext in csr.get_extensions():
        entry = dict(
            critical=bool(ext.get_critical()),
            value=base64.b64encode(ext.get_data()),
        )
        oid = obj2txt(
            OpenSSL._util.lib,
            OpenSSL._util.ffi,
            OpenSSL._util.lib.X509_EXTENSION_get_object(ext._extension)
        )
        # This could also be done a bit simpler:
        #
        #   oid = obj2txt(OpenSSL._util.lib, OpenSSL._util.ffi, OpenSSL._util.lib.OBJ_nid2obj(ext._nid))
        #
        # Unfortunately this gives the wrong result in case the linked OpenSSL
        # doesn't know the OID. That's why we have to get the OID dotted string
        # similarly to how cryptography does it.
        result[oid] = entry
    return result
