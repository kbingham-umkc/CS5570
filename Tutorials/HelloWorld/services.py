from protorpc.wsgi import service

import postservice

app = service.service_mappings([('/PostService', postservice.PostService)])
