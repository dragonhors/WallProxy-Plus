# Copyright (C) 2010-2011 | GNU GPLv3
__author__ = 'ZHRtYWppYUAxNjMuY29t'.decode('base64')
__version__ = '0.0.1'

from util.httpheaders import HTTPHeaders
import _base, struct, marshal

class Handler(_base.Handler):
    def dump_data(self, data):
        return marshal.dumps(tuple((k,str(v)) for k,v in data.iteritems()))

    def load_data(self, data):
        return dict(marshal.loads(data))

    def fetch(self, data):
        data, resp = self._fetch(data)
        if data == -1: return data, resp
        crypto = self.crypto.getcrypto(self.key)
        try:
            raw_data = resp.read(7)
            mix, code, hlen = struct.unpack('>BHI', raw_data)
            if mix == 0:
                headers = self.crypto.unpaddata(crypto.decrypt(resp.read(hlen)))
                if code == 555:
                    content = self.crypto.unpaddata(crypto.decrypt(resp.read()))
                    raise ValueError('Server: '+content)
                headers = HTTPHeaders(headers)
                return 0, code, headers, (resp, crypto)
            elif mix == 1:
                data = self.crypto.unpaddata(crypto.decrypt(resp.read()))
                content = data[hlen:]
                if code == 555:
                    raise ValueError('Server: '+content)
                headers = HTTPHeaders(data[:hlen])
                resp.close()
                return 1, code, headers, content
            else:
                raw_data += resp.read()
                raise ValueError('Data format not match(%s:%s)'%(self.url.geturl(), raw_data))
        except Exception, e:
            resp.close()
            return -1, e

init_time = 1
plugin_name = 'Simple2 for GAE'

def init_plugin(config):
    return _base.init(Handler, config)
