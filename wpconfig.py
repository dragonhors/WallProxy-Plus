# Copyright (C) 2010-2011 | GNU GPLv3
__author__ = 'd3d3LmVodXN0QGdtYWlsLmNvbQ=='.decode('base64')
__patcher__ = 'ZHRtYWppYUAxNjMuY29t'.decode('base64')

import os, traceback

def main_dir():
    import sys, imp
    if hasattr(sys, 'frozen') or imp.is_frozen('__main__'):
        return os.path.abspath(os.path.dirname(sys.executable))
    return os.path.abspath(os.path.dirname(sys.argv[0]))
main_dir = main_dir()
conf_file = os.path.join(main_dir, 'proxy.conf')

_default_config = 'x\x9c\x95\x93]o\x9b0\x18F\xff\xca\xee\x9c\xaa\x94@\x02\xa1i'\
'\xc4E S\xd9$\xd2|,m\xda\x08Y\xc66%\t\x0e\xae1i\xe8\xd4\xff\xbe\x16i\xbb\x18'\
'\x8d\x80;.\x9es,t\xf4B\x1b\xc2-\xe3\xa9\x90\x10v\x80@\x07\x922p\xa1f\x88\xf1'\
'\x84\x8e\xa0\r;\x9b\xdf \x17\t\xb8\x01\xb1\x94\xfc\xa6\xdb}\x8b2\xca"\x15q'\
'\x9e\xf1T\xaa8e\xdd\x88J\x1c\xab<\xe6@\x01{Z|l\x91\xa1\x11\r\x0f\x88iiC\xdc'\
'\x8b\xaeC\xf0\xae\xfc\xe7\xd9%B\xe6\xac\xc6\xe3F\xd8\xe1\xcbeN\x8f\xc2\xb9='\
'\xecWUM\x92\x9e$Kk4\x99\x10\x1e\xd7\xd9\xd4u\x12\xbcZ\xbbyU\x93\xa2\xdd\xfcI'\
'\xd6hB\xb6\xbe5\x9d\x1f\x87\x879\x89\xe6\xdb\xb7\xc7/4\xbb-\x96y\xedO\xed\x97'\
'\x89\x86_3\xcd\xf7\xfd\x89\xe1V5<\x7f\x111\xaa\xd1\xc4\xde\xde\xbb\xd7/\xf1'\
'/\x99\x8d\xddiH\xc0{\xa0\xf4/.\xab\xc5^z\xe1\x101\xeb\xa8ig\x8c\x95\xf7\xff'\
'\x11zk\xa2\xd7\x9a\xe8\xb7&\x8c\xd6\x84\xd9\x9a\x18\xb4&\xac\xd6\xc4ukbx\x8e'\
'\x08\x14\xe3\xab\xf4<\x0fE\xd88{\xb9n\x9c\xbc\\7\xce]\xae\x1b\xa7.\xd7\x8d3'\
'\x97\xeb\xc6\xc1\xcau\xe3X\xe5\xfal\xa8\xcf\x8b\x1b\xc1\x8d\x16\xa89\'H\xd2'\
'\x0e\x16\x05\x97\xa9\r\xc6\xdf\x97W\xae\xe3^\xf5{@a\xe8\x04e,("\x99m~\xce\xfb'\
'\xc1\xa6\xbc\xe1@\x81\x1b\xeb\xef\xb7\r^\xa7VA\xb2{gh=\x88\x8f+\x1fg\xbe\xf9x'\
'7\xa3\x93\x89\xff\xbc\x9b-\x06O?\xd9jv\xf0\xd6\xba\xb1.\x8a\xc5\x91\xe8\xf48]'\
'x\xc9\x04\x8c\x9e\x11\xe5"=\x156\x1c\x11\x9a|\x83\x7f\x00b\x04\xfe%'
_default_config = '''
import re
server, plugins = {}, {}
def __init__(plugin): pass
__del__ = set(['server', 'plugins', '__init__', '__del__'])
hosts = 'www.google.cn .appspot.com'
plugins['plugins.hosts'] = 'hosts'
def use_gae_https(gaeproxy):
    httpsproxy = []
    for s in gaeproxy:
        if isinstance(s, basestring): s = {'url': s}
        httpsproxy.append(s.copy())
        httpsproxy[-1]['url'] = httpsproxy[-1]['url'].replace('http:', 'https:')
    return httpsproxy
exec %r.decode('zlib')
__del__.add('use_gae_https'); plugins['plugins.gaeproxy'] = 'gaeproxy'
range_domain=set('c.youtube.com'.split('|'))
range_type='exe|msi|tar|dmg|flv|hlv|avi|mp3|mp4|zip|rar|7z|bz2|deb'
range_type=tuple('.'+i for i in set(range_type.split('|')))
def add_range(url, headers):
    if dnsDomainIs(url.hostname, range_domain) or url.path.endswith(range_type):
        return True
    return False
def print_result(func, key=lambda r,*a,**kw:r):
    def newfunc(*args, **kwargv):
        res = func(*args, **kwargv)
        print key(res, *args, **kwargv)
        return res
    return newfunc
__del__.update(('add_range', 'gaehost_http', 'gaehost_https', 'print_result'))
onlyone_domain=set()
def use_onlyone(hostname):
    if dnsDomainIs(hostname, onlyone_domain): return True
    return False
autoproxy = {}
autoproxy['PROXY 127.0.0.1:8086; DIRECT'] =[
['http://autoproxy-gfwlist.googlecode.com/svn/trunk/gfwlist.txt','http://127.0.0.1:8086'],
'file://userlist.ini']
autoproxy = autoproxy, 'proxy.pac'; __del__.add('autoproxy')
plugins['plugins.autoproxy'] = 'autoproxy'
rawproxy = (None,)
plugins['plugins.rawproxy'] = 'rawproxy'
fakehttps = None
plugins['plugins.fakehttps'] = 'fakehttps'
def check_client(ip, reqtype, args): return True
from util.httpheaders import HTTPHeaders as auth_headers
auth_headers = auth_headers('Proxy-Authenticate: Basic Realm="WallProxy"')
def request_auth(self):
    return self.write_response(407, auth_headers)
def find_sock_handler(reqtype, ip, port, cmd):
    if reqtype == 'https': return fakehttps
    return rawproxy[0]
def find_http_handler(method, url, headers):
    hostname = url.hostname
    if use_onlyone(hostname): return gaeproxy[-1]
    if dnsDomainIs(hostname, 'youtube.com'): return gaeproxy[3:]
    return gaeproxy
find_http_handler.__name__ = 'default_find_http_handler'
__del__.update(('check_client', 'request_auth', 'find_sock_handler', 'find_http_handler'))
def dnsDomainIs(host, domain):
    if isinstance(domain, basestring):
        if host == domain: return True
        if domain[0] != '.': domain = '.' + domain
    else:
        if host in domain: return True
        domain = tuple('.'+d if not d.startswith('.') else d for d in domain)
    return host.endswith(domain)
''' % _default_config

config = {}
def get_config():
    global config
    for key in config: config[key] = None #gc
    import __builtin__
    config = {
        '__builtins__': __builtin__, '__file__': conf_file,
        '__name__': __name__+'.conf',
    }
    exec _default_config in config
    try:
        execfile(conf_file, config)
    except:
        traceback.print_exc()
    return config['server']

def _init_plugin(plugins):
    init = config['__init__']
    plugins.sort(key=lambda x:x[0].init_time)
    for mod,cfg in plugins:
        try:
            if cfg in config:
                print 'Initializing "%s#%s" with "%s":'%(mod.__name__,
                      mod.__version__, cfg), mod.plugin_name
                config[cfg] = mod.init_plugin(config[cfg])
            else:
                print 'Initializing "%s":'%mod.__name__, mod.plugin_name
                mod.init_plugin()
            init(mod.__name__)
        except:
            traceback.print_exc()

def set_config(call_time):
    if call_time==2 or not call_time:
        global check_client, request_auth, find_sock_handler, find_http_handler
        check_client = config['check_client']
        request_auth = config['request_auth']
        find_sock_handler = config['find_sock_handler']
        find_http_handler = config['find_http_handler']
        plugins = [], []
        for mod,cfg in config['plugins'].iteritems():
            try:
                mod = __import__(mod, fromlist='x')
                plugins[int(mod.init_time>=50)].append((mod, cfg))
            except ImportError, e:
                print 'ImportError:', e
        _init_plugin(plugins[0])
        config['plugins'] = plugins[1]
    if call_time:
        _init_plugin(config['plugins'])
        for k in config['__del__']:
            if k in config:
                del config[k]

def watch_config(msg='', interval=5):
    import time
    def getmtime():
        try: return os.path.getmtime(conf_file)
        except: return 0
    mtime = getmtime()
    while True:
        time.sleep(interval)
        _mtime = getmtime()
        if mtime != _mtime:
            print msg
            get_config(); set_config(2)
            print msg
            mtime = _mtime

def get_logger(filename, format, maxKB, backupCount):
    if filename == '':
        class Logger:
            def __getattr__(self, name):
                return lambda *args, **kwargs: None
        return Logger()
    import logging
    import logging.handlers
    logger = logging.getLogger('WallProxy')
    logger.setLevel(logging.INFO)
    if filename:
        filename = os.path.join(main_dir, filename)
        handler = logging.handlers.RotatingFileHandler(filename,
                    maxBytes=maxKB*1024, backupCount=backupCount)
    else:
        handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(format))
    logger.addHandler(handler)
    return logger
