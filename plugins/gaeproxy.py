# Copyright (C) 2010-2011 | GNU GPLv3
__author__ = 'd3d3LmVodXN0QGdtYWlsLmNvbQ=='.decode('base64')
__patcher__ = 'ZHRtYWppYUAxNjMuY29t'.decode('base64')
__version__ = '0.0.8'

from util import httpheaders
import _base, zlib, struct, cPickle as pickle

class Handler(_base.Handler):
    def dump_data(self, data):
        return zlib.compress(pickle.dumps(data, 1))

    def load_data(self, data):
        return pickle.loads(data)

    def process_request(self, req):
        data, headers = req.read_body(), req.headers
        for k in self._dirty_headers:
            del headers[k]
        if req.command == 'GET':
            rawrange, range = self._process_range(req.headers)
            if self.add_range(req.url, req.headers):
                headers['Range'] = range
        else:
            rawrange, range = '', ''
        headers = httpheaders.HTTPHeaders(req.headers).__getstate__()
        request = {'url':req.url.geturl(), 'method':req.command,
                   'headers':headers, 'payload':data, 'range':range}
        return request, rawrange

    def fetch(self, data):
        data, resp = self._fetch(data)
        if data == -1: return data, resp
        crypto = self.crypto.getcrypto(self.key)
        headers = httpheaders.HTTPHeaders()
        try:
            raw_data = resp.read(7)
            zip, code, hlen = struct.unpack('>BHI', raw_data)
            if zip == 1:
                data = self.crypto.unpaddata(crypto.decrypt(resp.read()))
                data = zlib.decompress(data)
                content = data[hlen:]
                if code == 555:
                    raise ValueError('Server: '+content)
                headers.__setstate__(self.load_data(data[:hlen]))
                resp.close()
                return 1, code, headers, content
            elif zip == 0:
                h = crypto.decrypt(resp.read(hlen))
                headers.__setstate__(self.load_data(self.crypto.unpaddata(h)))
                if code == 555:
                    content = crypto.decrypt(resp.read())
                    raise ValueError('Server: '+self.crypto.unpaddata(content))
                return 0, code, headers, (resp, crypto)
            else:
                raw_data += resp.read()
                raise ValueError('Data format not match(%s:%s)'%(self.url.geturl(), raw_data))
        except Exception, e:
            resp.close()
            return -1, e


init_time = 1
plugin_name = 'Proxy based on GAE'

def init_plugin(config):
    return _base.init(Handler, config)
