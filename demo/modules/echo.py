# -*- encoding: utf-8 -*-
'''
@ 2009 by Uche ogbuji <uche@ogbuji.net>

This file is part of the open source Akara project,
provided under the Apache 2.0 license.
See the files LICENSE and NOTICE for details.
Project home, documentation, distributions: http://wiki.xml3k.org/Akara

 Module name:: echo
 
Responds to POST with the same body content as sent in the request

= Defined REST entry points =

http://purl.org/akara/services/builtin/echo (akara.echo) Handles POST

= Configuration =

No configuration required

= Notes on security =

This module only sends information available in the request.  No security implications.
'''

import amara
from akara.services import simple_service

ECHO_SERVICE_ID = 'http://purl.org/akara/services/builtin/echo'


@simple_service('POST', ECHO_SERVICE_ID, 'akara.echo')
def akara_xslt(body, ctype, **params):
    '''
    Sample request:
    curl --request POST --data-binary "@foo.dat" --header "http://localhost:8880/akara.echo"
    '''
    return body

