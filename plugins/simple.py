# Copyright (C) 2010-2011 | GNU GPLv3
__author__ = 'ZHRtYWppYUAxNjMuY29t'.decode('base64')
__version__ = '0.0.3'

import _base, gaeproxy, zlib
from binascii import a2b_hex, b2a_hex

class Handler(gaeproxy.Handler):
    def dump_data(self, dic):
        return zlib.compress('&'.join('%s=%s' % (k,b2a_hex(str(v))) for k,v in dic.iteritems()))

    def load_data(self, qs):
        return dict((k,a2b_hex(v)) for k,v in (x.split('=') for x in qs.split('&'))) if qs else {}

    def process_request(self, req):
        return _base.Handler.process_request(self, req)


init_time = 2
plugin_name = 'Simple packer for gaeproxy'

def init_plugin(config):
    return _base.init(Handler, config)
