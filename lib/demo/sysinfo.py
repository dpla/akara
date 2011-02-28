# -*- encoding: utf-8 -*-
'''
@ 2011 by Uche ogbuji <uche@ogbuji.net>

This file is part of the open source Akara project,
provided under the Apache 2.0 license.
See the files LICENSE and NOTICE for details.
Project home, documentation, distributions: http://wiki.xml3k.org/Akara

 Module name:: sysinfo
 
Responds to get with debug info about the system

= Defined REST entry points =

http://purl.org/akara/services/demo/sysinfo (akara.sysinfo) Handles GET

= Configuration =

No configuration required, but any config is reflected in the return messages

= Notes on security =

This module can be a huge security risk.  Please do not deploy it on any sensitive server beyond a debug period.
'''

import amara
from akara import global_config, request
from akara.services import simple_service
import pprint

SYSINFO_SERVICE_ID = 'http://purl.org/xml3k/akara/services/demo/sysinfo'


@simple_service('GET', SYSINFO_SERVICE_ID, 'akara.sysinfo', 'text/plain')
def akara_sysinfo():
    '''
    Sample request:
    curl "http://localhost:8880/akara.sysinfo"
    '''
    gdict = dict( (k, v) for (k, v) in global_config.__dict__.items() if k not in ['__builtins__', '__file__', '__name__', '__package__', '__doc__'])
    body = 'environ'
    body += '\n'
    body += pprint.pformat(request.environ)
    body += '\n\n'
    body += 'global_config'
    body += '\n'
    body += pprint.pformat(gdict)
    body += '\n'
    #pprint.pformat(request.environ)
    return body

