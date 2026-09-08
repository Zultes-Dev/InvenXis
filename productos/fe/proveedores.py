"""Proveedores de emisión electrónica.

`FE_PROVEEDOR` (settings): 'mock' para demo/tests.
Para producción real, implementar `ProveedorFE` contra el proveedor
tecnológico (o DIAN directo) con certificado digital y firmar el UBL.
"""
import uuid
from dataclasses import dataclass, field


@dataclass
class ResultadoEmision:
    aceptado: bool
    track_id: str = ''
    mensaje: str = ''
    payload: dict = field(default_factory=dict)


class ProveedorFE:
    def emitir(self, factura, xml_ubl: str) -> ResultadoEmision:
        raise NotImplementedError


class ProveedorFEMock(ProveedorFE):
    """Simula la DIAN: acepta si hay CUFE y total > 0."""

    def emitir(self, factura, xml_ubl: str) -> ResultadoEmision:
        if not factura.cufe:
            return ResultadoEmision(False, mensaje='Sin CUFE')
        if factura.total <= 0:
            return ResultadoEmision(False, mensaje='Total inválido')
        track = f"TRACK-{uuid.uuid4().hex[:12].upper()}"
        return ResultadoEmision(
            True, track_id=track, mensaje='Documento validado',
            payload={'trackId': track, 'resultado': 'aceptado'})


def get_proveedor(nombre='mock') -> ProveedorFE:
    if nombre == 'mock':
        return ProveedorFEMock()
    raise ValueError(f"Proveedor FE desconocido: {nombre}")
