# -*- encoding: utf-8 -*-
'''
@ 2011 by Uche ogbuji <uche@ogbuji.net>

This file is part of the open source Akara project,
provided under the Apache 2.0 license.
See the files LICENSE and NOTICE for details.
Project home, documentation, distributions: http://wiki.xml3k.org/Akara

 Module name:: akara.demo.cache_proxy

Proxies a remote URL to improve the cacheability of GET requests

= Defined REST entry points =

http://purl.org/akara/services/demo/cache-proxy (akara.cache-proxy) Handles GET

= Configuration =

class cache_proxy:
    maxlen = {
      None: 3600,
      "http://poems.com": 24*3600,
      "http://poemtree.com": 24*3600,
      "http://www.poemtree.com": 24*3600,
    }
    override_stale = 1

= Notes on security =

This module makes a remote GET request, and rewrites the response headers 

= Behaviour =

If 'override_stale' is 1, the module will make the response cacheable
independent of the desires of the downstream server as expressed in its response
headers.  If 0 (the default), any attempt by the downstream server to
explicitly mark a response as stale will be respected (passed upstream), but
otherwise the TTLs will be replaced by those declared in 'maxlen'.

Since the intent of this module is to improve cacheability, if the response's TTL
is greater than that specified in the maxlen configuration, then we'll use the
former.

Note: for simplicity of implementation, incoming Expires headers are converted to
the equivalent Cache-Control max-age directive.
'''

import amara
from amara.thirdparty import httplib2

import akara
from akara.services import simple_service
from akara import response
from akara import logger
from akara.util import normalize_http_header_name

import calendar
import email
import email.Utils
import time

MAXLEN = akara.module_config().get('maxlen')
if None in MAXLEN:
    DEFAULT_MAXLEN = MAXLEN[None]
    del MAXLEN[None]
else:
    DEFAULT_MAXLEN = 3600

OVERRIDE_STALE = akara.module_config().get('override_stale',0)

CACHE_PROXY_SERVICE_ID = 'http://purl.org/xml3k/akara/services/demo/cache-proxy'

MAXAGE_HEADER = lambda age: ('Cache-Control','max-age={0}'.format(age))

#FIXME: recycle after N uses
H = httplib2.Http()

def get_max_age(url):
    for k in MAXLEN:
        #XXX url normalize?
        if url.startswith(k):
            return MAXLEN[k]
            break
    else:
        return DEFAULT_MAXLEN

def is_fresh(resp):
    """
    Returns a tuple, the first element a boolean whether the response can be
    considered (for our purposes) fresh or not, and the second the freshness
    lifetime of the response.

    Much of this is reworked from httplib2._entry_disposition. We can't reuse it
    directly since it assumes responses are stale unless otherwise marked as
    fresh, and we want to do the opposite.
    """
    fresh = True
    freshness_lifetime = 0

    cc_response = httplib2._parse_cache_control(resp)
    if 'no-cache' in cc_response or 'private' in cc_response:
        fresh = False
    elif 'date' in resp:
        date = calendar.timegm(email.Utils.parsedate_tz(resp['date']))
        now = time.time()
        current_age = max(0, now - date - 5) # Give us 5 seconds to get this far
        if 'max-age' in cc_response:
            try:
                freshness_lifetime = int(cc_response['max-age'])
            except ValueError:
                freshness_lifetime = 0

        elif 'expires' in resp:
            expires = email.Utils.parsedate_tz(resp['expires'])
            if expires == None:
                freshness_lifetime = 0
            else:
                freshness_lifetime = calendar.timegm(expires) - date
        else:
            freshness_lifetime = 0

        if freshness_lifetime < current_age:
            logger.debug('lifetime = {0}, age = {1}, so marking explicitly stale'.format(freshness_lifetime,current_age))
            fresh = False

    return fresh, freshness_lifetime

@simple_service('GET', CACHE_PROXY_SERVICE_ID, 'akara.cache-proxy')
def akara_cache_proxy(url=None):
    '''
    Sample request:
    curl -I "http://localhost:8880/akara.cache-proxy?url=http://poemtree.com/poems/UsefulAdvice.htm"
    '''
    logger.debug('remote URL {0}: '.format(repr(url)))
    if not url:
        raise ValueError('url query parameter required')
    resp, content = H.request(url)

    if OVERRIDE_STALE:
        response.add_header(*MAXAGE_HEADER(get_max_age(url)))
    else:
        (fresh, lifetime) = is_fresh(resp)
        if fresh:
            response.add_header(*MAXAGE_HEADER( max(get_max_age(url),lifetime) ))
        else:
            response.add_header(*MAXAGE_HEADER(0))
    
    logger.debug('remote response headers {0}: '.format(repr(resp)))
    #Oof. What about 'transfer-encoding' and other such headers
    for k in resp:
        if k not in ('server','status', 'transfer-encoding', 'content-length','cache-control','expires','date'):
            response.add_header(normalize_http_header_name(k), resp[k])
    #response.add_header(k, resp[k])
    #FIXME: This might distort return encoding, which would of course throw off content length & encoding.  Workaround for now is removal of e.g. transfer-encoding (above)

    return content
