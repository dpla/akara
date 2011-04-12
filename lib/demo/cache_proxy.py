# -*- encoding: utf-8 -*-
'''
@ 2011 by Uche ogbuji <uche@ogbuji.net>

This file is part of the open source Akara project,
provided under the Apache 2.0 license.
See the files LICENSE and NOTICE for details.
Project home, documentation, distributions: http://wiki.xml3k.org/Akara

 Module name:: akara.demo.cache_proxy

Proxies a remote URL to add cache headers to GET requests

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

= Notes on security =

This module makes a remote GET request, and rewrites their headers

= Notes on security =

'''

import amara
from amara.thirdparty import httplib2

import akara
from akara.services import simple_service
from akara import response
from akara import logger

MAXLEN = akara.module_config().get('maxlen')
if None in MAXLEN:
    DEFAULT_MAXLEN = MAXLEN[None]
    del MAXLEN[None]
else:
    DEFAULT_MAXLEN = 3600

CACHE_PROXY_SERVICE_ID = 'http://purl.org/xml3k/akara/services/demo/cache-proxy'

#FIXME: recycle after N uses
H = httplib2.Http()


@simple_service('GET', CACHE_PROXY_SERVICE_ID, 'akara.cache-proxy')
def akara_cache_proxy(url=None):
    '''
    Sample request:
    curl -I "http://localhost:8880/akara.cache-proxy?url=http://poemtree.com/poems/UsefulAdvice.htm"
    '''
    if not url:
        raise ValueError('url query parameter required')
    resp, content = H.request(url)
    
    for k in MAXLEN:
        #XXX url normalize?
        if url.startswith(k):
            response.add_header("Cache-Control", "max-age={0}".format(MAXLEN[k]))
            break
    else:
        response.add_header("Cache-Control", "max-age={0}".format(DEFAULT_MAXLEN))

    logger.debug('remote response headers {0}: '.format(repr(resp)))
    #Oof. What about 'transfer-encoding' and other such headers
    for k in resp:
        if k not in ('status',):
            response.add_header(k, resp[k])
    #response.add_header(k, resp[k])
    return content

