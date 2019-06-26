//Proxy Auto Configuration

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

// AUTO-GENERATED RULES, DO NOT MODIFY!
// Ruleinfo for PROXY 127.0.0.1:8086; DIRECT:
// http://autoproxy-gfwlist.googlecode.com/svn/trunk/gfwlist.txt: k0|0|0+h0:0|0:0|0:0+s0|0|0=0 failed
// file://userlist.ini: k0|0|0+h0:0|1:1|0:0+s0|0|0=1
// Total: k0|0|0+h0:0|1:1|0:0+s0|0|0=1
var RULES = {"PROXY 127.0.0.1:8086; DIRECT": [[], [], [], {}, {"googleusercontent": [/^https\:\/\/.*\.googleusercontent\.com\//]}, {}, [], [], []]};
// END OF AUTO-GENERATED RULES

function inAutoProxy(r,u,h){u=u.toLowerCase();r=RULES[r];var s=u.split(":",1),k,i;if(s=="http"){k=r[2];i=k.length;while(--i>=0)if(u.indexOf(k[i])!=-1)return true}h=h.split(".");var j,t;k=r[5];j=h.length;while(--j>=0){i=h[j];if(i in k&&k[i].constructor==Array){t=k[i];i=t.length;while(--i>=0)if(t[i].test(u))return true}}k=r[8];i=k.length;while(--i>=0)if(k[i].test(u))return true;if(s=="http"){k=r[0];i=k.length;while(--i>=0)if(u.indexOf(k[i])!=-1)return false}k=r[3];j=h.length;while(--j>=0){i=h[j]; if(i in k&&k[i].constructor==Array){t=k[i];i=t.length;while(--i>=0)if(t[i].test(u))return false}}k=r[6];i=k.length;while(--i>=0)if(k[i].test(u))return false;if(s=="http"){k=r[1];i=k.length;while(--i>=0)if(u.indexOf(k[i])!=-1)return true}k=r[4];j=h.length;while(--j>=0){i=h[j]; if(i in k&&k[i].constructor==Array){t=k[i];i=t.length;while(--i>=0)if(t[i].test(u))return true}}k=r[7];i=k.length;while(--i>=0)if(k[i].test(u))return true;return false};