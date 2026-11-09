"""
Paginación de GET /pedidos, en el formato que pide openapi_equipo.yaml:
    {resultados, total, pagina, tamano_pagina}
en vez del formato por defecto de DRF ({count, next, previous, results}).
Una página posterior a la última responde 404 (comportamiento nativo de
PageNumberPagination; lo traduce api/exceptions.py al formato del contrato).
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PedidoPageNumberPagination(PageNumberPagination):
    page_query_param = "pagina"
    page_size_query_param = "tamano_pagina"
    page_size = 20
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "resultados": data,
                "total": self.page.paginator.count,
                "pagina": self.page.number,
                "tamano_pagina": self.get_page_size(self.request) or self.page_size,
            }
        )
