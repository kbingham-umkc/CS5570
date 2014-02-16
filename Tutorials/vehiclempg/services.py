from protorpc.wsgi import service

from REST import mpg_service

app = service.service_mappings([('/REST/mpg_service', mpg_service.PostService)])
