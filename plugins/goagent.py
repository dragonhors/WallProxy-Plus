# Copyright (C) 2010-2011 | GNU GPLv3
__author__ = 'ZHRtYWppYUAxNjMuY29t'.decode('base64')
__version__ = '0.0.2'

import forold, zlib
from binascii import a2b_hex, b2a_hex

class Handler(forold.Handler):
    crypto = forold._crypto.Crypto('XOR--0'); key = ''

    def dump_data(self, dic):
        return zlib.compress('&'.join('%s=%s' % (k,b2a_hex(str(v))) for k,v in dic.iteritems()))

    def load_data(self, qs):
        return dict((k,a2b_hex(v)) for k,v in (x.split('=') for x in qs.split('&')))

    def __init__(self, config):
        config.pop('crypto', None)
        self.password = config.pop('key', '')
        super(Handler, self).__init__(config)

    def process_request(self, req):
        request, rawrange = forold.Handler.process_request(self, req)
        request['password'] = self.password
        return request, rawrange

init_time = 3
plugin_name = 'Plugin for GoAgent'

def init_plugin(config):
    return forold._base.init(Handler, config)
