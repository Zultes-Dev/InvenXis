"""CUFE (Código Único de Factura Electrónica) — algoritmo estilo DIAN.

SHA-384 sobre la concatenación de campos clave + clave técnica.
Ver resolución DIAN vigente para el orden exacto de campos en producción.
"""
import hashlib


def generar_cufe(*, numero, fecha, nit_emisor, doc_adquiriente,
                 total, iva, clave_tecnica='demo-clave-tecnica'):
    """Genera el CUFE. `fecha`: 'YYYY-MM-DD HH:MM:SS'."""
    base = (
        f"{numero}{fecha}{nit_emisor}{doc_adquiriente}"
        f"{total}{iva}01{iva}{clave_tecnica}"
    )
    return hashlib.sha384(base.encode('utf-8')).hexdigest()
