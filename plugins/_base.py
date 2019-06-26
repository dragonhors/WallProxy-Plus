# Copyright (C) 2010-2011 | GNU GPLv3
__author__ = 'd3d3LmVodXN0QGdtYWlsLmNvbQ=='.decode('base64')
__patcher__ = 'ZHRtYWppYUAxNjMuY29t'.decode('base64')

from util import crypto as _crypto, httpheaders, proxylib, urlfetch, urlinfo
import time, re, random, threading, socket, os
time_clock = time.clock if os.name=='nt' else time.time

class GaeHost(object):
    o_create_connection = staticmethod(proxylib.create_connection)

    def __init__(self, http, https):
        self.config, self.hosts = {}, {}
        if http:
            self.config[80] = set(http)
            self._convert(80)
        if https:
            self.config[443] = set(https)
            self._convert(443)
        self.threaded = threading.local()
        proxylib.create_connection = self.create_connection

    def _convert(self, port):
        ipset = set()
        for host in self.config[port]:
            try: ipset.update(socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM))
            except: pass
        print ' gaehost@%d: %s' % (port, [i[-1][0] for i in ipset])
        self.hosts[port] = [ipset, {}, None]

    def create_connection(self, address, timeout=-1):
        host, port = address
        if host.endswith('.appspot.com') and port in self.hosts:
            return self.connect(port, timeout)
        return self.o_create_connection(address, timeout)

    def _get_best(self, score):
        addrinfo = min(score.keys(), key=lambda k:score[k])
        print 'Select %s for .appspot.com' % str(addrinfo[-1])
        return addrinfo

    def _reget_best(self, score, addrinfo, hosts):
        if score.pop(addrinfo, None):
            print 'Remove %s for .appspot.com' % str(addrinfo[-1])
            if hosts[-1]==addrinfo and score:
                hosts[-1] = self._get_best(score)
        return hosts[-1]

    def remove_bad(self):
        try:
            addrinfo = self.threaded.addrinfo
            hosts = self.hosts[addrinfo[-1][1]]; score = hosts[1]
            self._reget_best(score, addrinfo, hosts)
        except:
            pass

    def connect(self, port, timeout=-1):
        hosts = self.hosts[port]; ipset, score, addrinfo = hosts
        if addrinfo:
            while score:
                try:
                    return self._connect(addrinfo, timeout)
                except:
                    addrinfo = self._reget_best(score, addrinfo, hosts)
            self._convert(port)
            raise Exception('ip exhausted(port %d)' % port)
        while ipset:
            addrinfo = ipset.pop()
            t = time_clock()
            try:
                sock = self._connect(addrinfo, 5)
                score[addrinfo] = time_clock() - t
                return sock
            except:
                pass
        hosts[-1] = score and self._get_best(score) or True
        return self.connect(port, timeout)

    def _connect(self, addrinfo, timeout=-1):
        af, socktype, proto, canonname, sa = addrinfo
        sock = None
        try:
            sock = socket.socket(af, socktype, proto)
            if timeout is None or timeout>=0:
                sock.settimeout(timeout)
            sock.connect(sa)
            self.threaded.addrinfo = addrinfo
            return sock
        except socket.error:
            if sock is not None: sock.close()
            raise

class Handler(object):
    _dirty_headers = ('connection', 'proxy-connection', 'proxy-authorization',
                     'content-length', 'host', 'vary', 'via', 'x-forwarded-for')
    _range_re = re.compile(r'(\d+)?-(\d+)?')
    _crange_re = re.compile(r'bytes\s+(\d+)-(\d+)/(\d+)')
    crypto = _crypto.Crypto('XOR--32'); key = ''
    proxy = proxylib.Proxy()
    headers = httpheaders.HTTPHeaders('Content-Type: application/octet-stream')
    range0 = 100000; range = 500000; max_threads = 10

    def __init__(self, config):
        dic = {'crypto': _crypto.Crypto, 'key': lambda v:v,
               'proxy': proxylib.Proxy, 'headers': httpheaders.HTTPHeaders,
               'range0': lambda v:v if v>=10000 else self.__class__.range0,
               'range': lambda v:v if v>=100000 else self.__class__.range,
               'max_threads': lambda v:v if v>0 else self.__class__.max_threads,}
        self.url = urlinfo.URL(config['url'])
        for k,v in dic.iteritems():
            if k in config:
                setattr(self.__class__, k, v(config[k]))
            setattr(self, k, getattr(self.__class__, k))
        opener_cls = urlfetch.HTTPSFetch if (self.url.scheme == 
                'https') else urlfetch.HTTPFetch
        self.opener = opener_cls(self.proxy, True)
        del self.proxy

    def __str__(self):
        return ' %s %s %d %d %d' % (self.url.geturl(), self.crypto.getmode(),
                self.range0, self.range, self.max_threads)

    def dump_data(self, data):
        raise NotImplementedError

    def load_data(self, data):
        raise NotImplementedError

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
        request = {'url':req.url.geturl(), 'method':req.command,
                   'headers':headers, 'payload':data, 'range':range}
        return request, rawrange

    def _process_range(self, headers):
        range = headers.get('Range', '')
        m = self._range_re.search(range)
        if m:
            m = m.groups()
            if m[0] is None:
                if m[1] is None: m = None
                else:
                    m = 1, int(m[1])
                    if m[1] > self.range0: range = 'bytes=-1024'
            else:
                if m[1] is None:
                    m = 0, int(m[0])
                    range = 'bytes=%d-%d' % (m[1], m[1]+self.range0-1)
                else:
                    m = 2, int(m[0]), int(m[1])
                    if m[2]-m[1]+1 > self.range0:
                        range = 'bytes=%d-%d' % (m[1], m[1]+self.range0-1)
        if m is None:
            range = 'bytes=0-%d' % (self.range0 - 1)
        return m, range

    def _fetch(self, data):
        data = self.crypto.encrypt(data, self.key)
        try:
            resp = self.opener.open(self.url, data, 'POST', self.headers)
        except proxylib.ProxyError, e:
            return -1, 'Connect proxy/host failed'
        except Exception, e:
            return -1, e
        if resp.status != 200:
            self.opener.close()
            return -1, '%s: %s' % (resp.status, resp.reason)
        return 0, resp

    def fetch(self, data):
        raise NotImplementedError

    def read_data(self, type, data):
        if type == 1: return data
        resp, crypto = data
        data = self.crypto.unpaddata(crypto.decrypt(resp.read()))
        resp.close()
        return data

    def write_data(self, req, type, data):
        try:
            if type == 1:
                req.wfile.write(data)
            else:
                resp, crypto = data
                size = self.crypto.getsize(16384)
                data = crypto.decrypt(resp.read(size))
                req.wfile.write(self.crypto.unpaddata(data))
                data = resp.read(size)
                while data:
                    req.wfile.write(crypto.decrypt(data))
                    data = resp.read(size)
                resp.close()
        except socket.error:
            req.wfile.close()
            raise

    def _need_range_fetch(self, req, res, range):
        headers = res[2]
        m = self._crange_re.search(headers.get('Content-Range', ''))
        if not m: return None
        m = map(int, m.groups())#bytes %d-%d/%d
        if range is None:
            start=0; end=m[2]-1
            code = 200
            del headers['Content-Range']
        else:
            if range[0] == 0: #bytes=%d-
                start=range[1]; end=m[2]-1
            elif range[0] == 1: #bytes=-%d
                start=m[2]-range[1]; end=m[2]-1
            else: #bytes=%d-%d
                start=range[1]; end=range[2]
            code = 206
            headers['Content-Range'] = 'bytes %d-%d/%d' % (start, end, m[2])
        headers['Content-Length'] = str(end-start+1)
        req.write_response(code, headers, size=headers['Content-Length'])
        if start == m[0]: #Valid
            self.write_data(req, res[0], res[3])
            start = m[1] + 1
        return start, end

    def range_fetch(self, req, handler, request, start, end):
        t = time.time()
        if self._range_fetch(req, handler, request, start, end):
            t = time.time() - t
            t = (end - start + 1) / 1000.0 / t
            print '>>>>>>>>>> Range Fetch ended (all @ %sKB/s)' % t
        else:
            req.close_connection = 1
            print '>>>>>>>>>> Range Fetch failed'

    def _range_fetch(self, req, handler, request, start, end):
        request['range'] = '' # disable server auto-range-fetch
        i, s, thread_size, tasks = 0, start, 10, []
        while s <= end:
            e = s + (i < thread_size and self.range0 or self.range) - 1
            if e > end: e = end
            tasks.append((i, s, e))
            i += 1; s = e + 1
        task_size = len(tasks)
        thread_size = min(task_size, len(handler)*2, self.max_threads)
        print ('>>>>>>>>>> Range Fetch started: threads=%d blocks=%d '
                'bytes=%d-%d' % (thread_size, task_size, start, end))
        if thread_size == 1:
            return self._single_fetch(req, handler, request, tasks)
        handler = list(handler); random.shuffle(handler)
        if thread_size > len(handler): handler *= 2
        results = [None] * task_size
        mutex = threading.Lock()
        threads = {}
        for i in xrange(thread_size):
            t = threading.Thread(target=handler[i]._range_thread,
                    args=(request, tasks, results, threads, mutex))
            threads[t] = set()
            t.setDaemon(True)
        for t in threads: t.start()
        i = 0; t = False
        while i < task_size:
            if results[i] is not None:
                try:
                    self.write_data(req, 1, results[i])
                    results[i] = None
                    i += 1
                    continue
                except:
                    mutex.acquire()
                    del tasks[:]
                    mutex.release()
                    break
            if not threads: #All threads failed
                if t: break
                t = True; continue
            time.sleep(1)
        else:
            return True
        return False

    def _single_fetch(self, req, handler, request, tasks):
        try:
            for task in tasks:
                request['headers']['Range'] = 'bytes=%d-%d' % task[1:]
                data = self.dump_data(request)
                for i in xrange(3):
                    self = random.choice(handler)
                    res = self.fetch(data)
                    if res[0] == -1:
                        time.sleep(2)
                    elif res[1] == 206:
                        #print res[2]
                        print '>>>>>>>>>> block=%d bytes=%d-%d' % task
                        self.write_data(req, res[0], res[3])
                        break
                else:
                    raise StopIteration('Failed')
        except:
            return False
        return True

    def _range_thread(self, request, tasks, results, threads, mutex):
        ct = threading.current_thread()
        while True:
            mutex.acquire()
            try:
                if threads[ct].intersection(*threads.itervalues()):
                    raise StopIteration('All threads failed')
                for i,task in enumerate(tasks):
                    if task[0] not in threads[ct]:
                        task = tasks.pop(i)
                        break
                else:
                    raise StopIteration('No task for me')
                request['headers']['Range'] = 'bytes=%d-%d' % task[1:]
                data = self.dump_data(request)
            except StopIteration, e:
                #print '>>>>>>>>>> %s: %s' % (ct.name, e)
                del threads[ct]
                break
            finally:
                mutex.release()
            success = False
            for i in xrange(2):
                res = self.fetch(data)
                if res[0] == -1:
                    time.sleep(2)
                elif res[1] == 206:
                    try: data = self.read_data(res[0], res[3])
                    except: continue
                    if len(data) == task[2]-task[1]+1:
                        success = True
                        break
            mutex.acquire()
            if success:
                print '>>>>>>>>>> block=%d bytes=%d-%d'%task, len(data)
                results[task[0]] = data
            else:
                threads[ct].add(task[0])
                tasks.append(task)
                tasks.sort(key=lambda x: x[0])
            mutex.release()

    def handle(self, handler, req):
        if not isinstance(handler, (list, tuple)):
            handler = handler,
        if len(handler) == 1:
            handlers = handler[0], handler[0]
        else:
            handlers = random.sample(handler, 2)
        request, range = self.process_request(req)
        data = self.dump_data(request)
        errors = []
        for self in handlers:
            res = self.fetch(data)
            if res[0] != -1: break
            e = res[1]; es = str(e); errors.append(es)
            if not self.url.hostname.endswith('.appspot.com'): continue
            if self.gaehost and not es.startswith('Server: '):
                self.gaehost.remove_bad()
            elif (isinstance(e, socket.error) and e[0] in (10054, 10060, 104)
                and self.url.scheme != 'https'):
                print 'Use https instead of http automatically.'
                for h in handler:
                    h.url.scheme = 'https'
                    if h.url.port == 80: h.url.port = 443
                    h.opener = urlfetch.HTTPSFetch(h.opener.proxy)
                hosts = proxylib.hosts[1]
                try:
                    i = hosts.index(('.appspot.com', 'www.google.cn'))
                except ValueError:
                    pass
                else:
                    hosts[i] = ('.appspot.com', 'www.google.com.hk')
                #print handler[0], proxylib.map_hosts('.appspot.com')
        else:
            return req.send_error(502, str(errors))
        if res[1]==206 and req.command=='GET':
            data = self._need_range_fetch(req, res, range)
            if data:
                start, end = data
                if start > end: return #end
                return self.range_fetch(req, handler, request, start, end)
        req.write_response(res[1], res[2], size=res[2].get('Content-Length','0'))
        self.write_data(req, res[0], res[3])


def init(cls, config):
    import traceback; from wpconfig import config as wpconfig
    add_range = wpconfig.get('add_range')
    if add_range:
        wpconfig['add_range'] = False
        Handler.add_range = lambda self,u,h: add_range(u,h)
    elif add_range != False:
        Handler.add_range = lambda self,u,h: False
    gaehost_http = wpconfig.get('gaehost_http')
    gaehost_https = wpconfig.get('gaehost_https')
    if gaehost_http or gaehost_https:
        wpconfig['gaehost_http'] = wpconfig['gaehost_https'] = False
        Handler.gaehost = GaeHost(gaehost_http, gaehost_https)
    elif gaehost_http!=False or gaehost_https!=False:
        Handler.gaehost = None
        proxylib.create_connection = GaeHost.o_create_connection
    server = [None] * len(config)
    for i,v in enumerate(config):
        if isinstance(v, basestring):
            v = {'url': v}
        try:
            server[i] = cls(v)
            print server[i]
        except:
            traceback.print_exc()
    return server
