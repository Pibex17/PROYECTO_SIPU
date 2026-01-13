from sqlalchemy import text
from DataBase import db


class OfertasFacade:

    def __init__(self):
        self._repo = OfertaRepository()
        self._service = OfertaService(self._repo)

    def crear_tablas(self):
        self._repo.crear_tablas()

    def crear_oferta(self, nombre, id_periodo, detalles, estado="Activa"):
        oferta = OfertaFactory.crear(
            nombre=nombre,
            id_periodo=id_periodo,
            detalles=detalles,
            estado=estado
        )
        return self._service.crear_oferta(oferta)

    def listar_ofertas(self, id_periodo=None):
        return self._service.listar_ofertas(id_periodo)

    def eliminar_oferta(self, id_oferta):
        self._service.eliminar_oferta(id_oferta)
