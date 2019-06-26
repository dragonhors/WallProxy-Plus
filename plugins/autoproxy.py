# Copyright (C) 2010-2011 | GNU GPLv3
__author__ = 'd3d3LmVodXN0QGdtYWlsLmNvbQ=='.decode('base64')
__version__ = '0.0.2'

import re, os.path as ospath
from wpconfig import main_dir
from util import urlinfo, urlfetch

def _sumRule(keyword, hash, share):
    k = map(len, keyword)
    hk = map(len, hash)
    hv = [sum([len(v) for v in t.itervalues()]) for t in hash]
    s = map(len, share)
    num = 'k%d|%d|%d+h%d:%d|%d:%d|%d:%d+s%d|%d|%d=%d' % (k[0], k[1], k[2], hk[0], hv[0],
        hk[1], hv[1], hk[2], hv[2], s[0], s[1], s[2], sum(k+hv+s))
    return num

def _parseRule(rule):
    valid = []
    keyword = set(), set(), set()
    hash = {}, {}, {}
    share = set(), set(), set()
    for line in rule.splitlines()[1:]:
        # Ignore the first line ([AutoProxy x.x]), empty lines and comments
        rule = line = line.strip().lower()
        if not rule or rule[0] in ('[','!','#'):
            continue
        rule_type = 1
        if rule.startswith('@@'): # White Exceptions
            rule = rule[2:]
            rule_type = 0
        elif rule.startswith('@'): # Black Exceptions
            rule = rule[1:]
            rule_type = 2
        if rule[0]=='/' and rule[-1]=='/': # Regular expressions
            rule = rule[1:-1]
        else:
            # Strictly mapping to keyword blocking
            rule = re.sub(r'^(https?:)', r'|\1', rule)
            if rule[0]!='|' and '*' not in rule: # Maybe keyword
                i1 = rule.find('.'); i2 = rule.find('/'); i3 = rule.find('?')
                if i1==-1 or (i2!=-1 and i2<i1) or (i2==-1 and i3!=-1):
                    keyword[rule_type].add(rule)
                    valid.append(line)
                    continue
            # Remove multiple wildcards
            rule = re.sub(r'\*+', '*', rule)
            # Remove anchors following separator placeholder
            rule = re.sub(r'\^\|$', '^', rule, 1)
            # Escape special symbols
            rule = re.sub(r'(\W)', r'\\\1', rule)
            # Replace wildcards by .*
            rule = re.sub(r'\\\*', '.*', rule)
            # Process separator placeholders
            rule = re.sub(r'\\\^', r'(?:[^\w\-.%\u0080-\uFFFF]|$)', rule)
            # Process extended anchor at expression start
            rule = re.sub(r'^\\\|\\\|', r'^[\w\-]+:\/+(?!\/)(?:[^\/]+\.)?', rule, 1)
            # Process anchor at expression start
            rule = re.sub(r'^\\\|', '^', rule, 1)
            # Process anchor at expression end
            rule = re.sub(r'\\\|$', '$', rule, 1)
            # Remove leading wildcards
            rule = re.sub(r'^(?:\.\*)', '', rule, 1)
            # Remove trailing wildcards
            rule = re.sub(r'(?:\.\*)$', '', rule, 1)
        if not rule: continue # Invalid
        # Regular expressions
        idot = rule.find('\\.')
        if idot == -1: hash_key = None
        else:
            # Find domain field
            istart = rule.find(':') + 1
            if istart > idot: istart = 0
            iend = rule.find('\\/', idot+2)
            if iend == -1: iend = rule.find('.*', idot+2)
            tmp = rule[istart:iend if iend!=-1 else None].replace('\\-', '-')
            # Remove uncertain field
            tmp = re.sub(r'(?:\(.*?\)\?)|(?:\(.*?\|.*?\))', '()', tmp)
            tmp = re.sub(r'(?:[\w-]+\.?)?(?:\*|\?|\|)(?:[\w-]+)?', '.*', tmp)
            tmp = re.findall(r'[\w-]{2,}', tmp)
            # Try get a hash word
            try:
                hash_key = tmp.pop()
                if tmp: hash_key = max(tmp, key=lambda x:len(x))
            except IndexError:
                hash_key = None
        if hash_key:
            if hash_key in hash[rule_type]:
                hash[rule_type][hash_key].add(rule)
            else:
                hash[rule_type][hash_key] = set([rule])
        else:
            share[rule_type].add(rule)
        valid.append(line)
    valid = '\n'.join(valid)
    return valid, (keyword,hash,share), _sumRule(keyword, hash, share)

def _fetchRule(default, url, proxy):
    url = urlinfo.URL(url)
    try:
        if url.scheme == 'file':
            url.path = ospath.join(main_dir, url.path)
            fp = open(url.path, 'rb')
            date = None
        else:
            for i in xrange(2):
                try:
                    fp = urlfetch.fetch(url, proxy=proxy)
                    if fp.status == 200: break
                    fp.close()
                    raise ValueError
                except:
                    import time
                    time.sleep(15)
            else:
                raise ValueError
            date = fp.msg.getheader('last-modified')
        rule = fp.read()
        fp.close()
    except:
        rule = '\n' + default
        date = 'failed'
    try:
        tmp = rule.decode('base64')
        tmp[5:15].decode('ascii')
        rule = tmp
    except:
        pass
    default, rule, num = _parseRule(rule)
    return default, rule, '%s %s' % (num, date) if date else num

def initRule(rulelist):
    try:
        fp = open(ospath.join(main_dir, 'listbak.ini'))
        listbak = fp.read()
        fp.close()
    except IOError:
        listbak = ''
    listbak2 = []
    keyword = [set(), set(), set()]
    hash = [{}, {}, {}]
    share = [set(), set(), set()]
    info = []
    if isinstance(rulelist, basestring):
        rulelist = (rulelist,)
    for rule in rulelist:
        if not rule: continue
        if isinstance(rule, basestring):
            url, proxy = rule, None
        elif len(rule) == 1:
            url, proxy = rule[0], None
        else:
            url, proxy = rule[0], rule[1]
        default = ''
        if listbak:
            default = re.search(r'(?ms)^\s*%s\s*(^.*$)\s*%s\s*$' % (
                re.escape('[%s start]'%url), re.escape('[%s end]'%url)), listbak)
            if default: default = default.group(1)
        default, rule, num = _fetchRule(default, url, proxy)
        info.append((url, num))
        kw, hh, sh = rule
        for i in xrange(3):
            keyword[i] |= kw[i]
            for k,v in hh[i].iteritems():
                if k in hash[i]: hash[i][k] |= v
                else: hash[i][k] = v
            share[i] |= sh[i]
        listbak2.append('[%s start]\n%s\n[%s end]\n' % (url, default, url))
    info.append(('Total', _sumRule(keyword, hash, share)))
    try:
        fp = open(ospath.join(main_dir, 'listbak.ini'), 'w')
        fp.write('\n'.join(listbak2))
        fp.close()
    except IOError:
        pass
    return (keyword,hash,share), info

class jsRegExp:
    def __init__(self, r):
        self.r = r
    def __json__(self):
        return '/%s/' % self.r

def dump2js(o):
    def iterdump(o):
        if isinstance(o, (list, tuple, set)):
            yield '['
            i = len(o)
            for v in o:
                for v in iterdump(v): yield v
                i -= 1
                if i > 0: yield ', '
            yield ']'
        elif isinstance(o, dict):
            yield '{'
            i = len(o)
            for k,v in o.iteritems():
                for k in iterdump(k): yield k
                yield ': '
                for v in iterdump(v): yield v
                i -= 1
                if i > 0: yield ', '
            yield '}'
        elif isinstance(o, basestring):
            yield '"%s"' % o.encode('string-escape')
        elif isinstance(o, (int, long, float)):
            yield str(o)
        elif o is True: yield 'true'
        elif o is False: yield 'false'
        elif o is None: yield 'null'
        else:
            yield o.__json__()
    return ''.join(iterdump(o))

def initRules(ruledict, callback, prefix1, prefix2):
    infos = []
    for key,rulelist in ruledict.iteritems():
        rule, info = initRule(rulelist)
        kw, hh, sh = rule
        for i in xrange(3):
            for k,v in hh[i].iteritems():
                hh[i][k] = [callback(r) for r in v]
            sh[i] = [callback(r) for r in sh[i]]
        ruledict[key] = kw + hh + sh
        for i,v in enumerate(info):
            info[i] = '%s%s: %s' % (prefix2, v[0], v[1])
        info = '\n'.join(info)
        infos.append('%sRuleinfo for %s:\n%s' % (prefix1, key, info))
    return '\n'.join(infos)

def generatePAC(ruledict, pacFile):
    rulesBegin = '// AUTO-GENERATED RULES, DO NOT MODIFY!'
    rulesEnd = '// END OF AUTO-GENERATED RULES'
    defaultPacTemplate = '''//Proxy Auto Configuration

function FindProxyForURL(url, host) {
    for (var p in RULES)
        if (inAutoProxy(p, url, host)) return p;
    return 'DIRECT';
}

function dnsDomainIs(host, domain) {
    if (host == domain) return true;
    if (domain.charAt(0) != '.') domain = '.' + domain;
    return (host.length >= domain.length &&
            host.substring(host.length - domain.length) == domain);
}

%(rulesBegin)s
%(rulesCode)s
%(rulesEnd)s

function inAutoProxy(r,u,h){u=u.toLowerCase();r=RULES[r];var s=u.split(":",1),k,i;if(s=="http"){k=r[2];i=k.length;while(--i>=0)if(u.indexOf(k[i])!=-1)return true}h=h.split(".");var j,t;k=r[5];j=h.length;while(--j>=0){i=h[j];if(i in k&&k[i].constructor==Array){t=k[i];i=t.length;while(--i>=0)if(t[i].test(u))return true}}k=r[8];i=k.length;while(--i>=0)if(k[i].test(u))return true;if(s=="http"){k=r[0];i=k.length;while(--i>=0)if(u.indexOf(k[i])!=-1)return false}k=r[3];j=h.length;while(--j>=0){i=h[j]; if(i in k&&k[i].constructor==Array){t=k[i];i=t.length;while(--i>=0)if(t[i].test(u))return false}}k=r[6];i=k.length;while(--i>=0)if(k[i].test(u))return false;if(s=="http"){k=r[1];i=k.length;while(--i>=0)if(u.indexOf(k[i])!=-1)return true}k=r[4];j=h.length;while(--j>=0){i=h[j]; if(i in k&&k[i].constructor==Array){t=k[i];i=t.length;while(--i>=0)if(t[i].test(u))return true}}k=r[7];i=k.length;while(--i>=0)if(k[i].test(u))return true;return false};'''
    args = re.escape(rulesBegin), re.escape(rulesEnd)
    pattern = re.compile(r'(?ms)^(\s*%s\s*)^.*$(\s*%s\s*)$' % args)
    info = initRules(ruledict, jsRegExp, '// ', '// ')
    args = {'rulesBegin': rulesBegin, 'rulesEnd': rulesEnd,
            'rulesCode': '%s\nvar RULES = %s;' % (info, dump2js(ruledict))}
    print ' Writing PAC to file...'
    for pacFile in pacFile:
        try:
            fp = open(pacFile, 'r')
            template = fp.read().replace('%','%%')
            fp.close()
        except IOError:
            template = defaultPacTemplate
        else:
            template, n = re.subn(pattern, r'\1%(rulesCode)s\2', template)
            if n==0: template = defaultPacTemplate
        fp = open(pacFile, 'w')
        fp.write(template % args)
        fp.close()
    print ' Done!'

class Handler:
    def __init__(self, ruledict):
        print initRules(ruledict, re.compile, ' ', '  ')
        self.ruledict = ruledict

    def __call__(self, rule, url):
        rule = self.ruledict[rule]
        scheme = url.scheme
        tokens = url.hostname.split('.')
        url = url.geturl().lower()
        if scheme == 'http':
            for k in rule[2]:
                if k in url:
                    return True
        r = rule[5]
        for k in tokens:
            if k in r:
                for k in r[k]:
                    if k.search(url):
                        return True
        for k in rule[8]:
            if k.search(url):
                return True
        if scheme == 'http':
            for k in rule[0]:
                if k in url:
                    return False
        r = rule[3]
        for k in tokens:
            if k in r:
                for k in r[k]:
                    if k.search(url):
                        return False
        for k in rule[6]:
            if k.search(url):
                return False
        if scheme == 'http':
            for k in rule[1]:
                if k in url:
                    return True
        r = rule[4]
        for k in tokens:
            if k in r:
                for k in r[k]:
                    if k.search(url):
                        return True
        for k in rule[7]:
            if k.search(url):
                return True
        return False
    test = __call__


init_time = 100
plugin_name = 'AutoProxy'

def init_plugin(config):
    if isinstance(config, dict):
        return Handler(config)
    if len(config) < 2: return
    if isinstance(config[1], basestring):
        pacFile = [ospath.join(main_dir, config[1])]
    else:
        pacFile = [ospath.join(main_dir, i) for i in config[1]]
    generatePAC(config[0], pacFile)
