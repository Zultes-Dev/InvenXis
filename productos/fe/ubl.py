"""UBL 2.1 mínimo para factura electrónica (estructura válida y parseable)."""
from decimal import Decimal
import xml.etree.ElementTree as ET
from xml.dom import minidom

NS = {
    '': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
}


def _el(parent, tag, text=None, ns='cbc'):
    el = ET.SubElement(parent, f'{{{NS[ns]}}}{tag}')
    if text is not None:
        el.text = str(text)
    return el


def construir_ubl(factura, nit_emisor='900123456', nombre_emisor='InvenXis S.A.S.'):
    """Construye el XML UBL de la factura (incluye CUFE en extensiones)."""
    for prefix, uri in NS.items():
        ET.register_namespace(prefix, uri)
    inv = ET.Element(f"{{{NS['']}}}Invoice")

    exts = ET.SubElement(inv, '{%s}UBLExtensions' % NS['ext'])
    ext = ET.SubElement(exts, '{%s}UBLExtension' % NS['ext'])
    content = ET.SubElement(ext, '{%s}ExtensionContent' % NS['ext'])
    sts = ET.SubElement(content, '{%s}DianExtensions' % NS['cac'])
    _el(sts, 'CUFE', factura.cufe, ns='cac')

    _el(inv, 'UBLVersionID', 'UBL 2.1')
    _el(inv, 'ID', factura.numero)
    _el(inv, 'IssueDate', factura.fecha.strftime('%Y-%m-%d'))
    _el(inv, 'IssueTime', factura.fecha.strftime('%H:%M:%S'))
    _el(inv, 'InvoiceTypeCode', '01')
    _el(inv, 'DocumentCurrencyCode', 'COP')

    supplier = _el(inv, 'AccountingSupplierParty', ns='cac')
    party = ET.SubElement(supplier, '{%s}Party' % NS['cac'])
    _el(party, 'EndpointID', nit_emisor, ns='cbc')
    pname = ET.SubElement(party, '{%s}PartyName' % NS['cac'])
    _el(pname, 'Name', nombre_emisor, ns='cbc')

    customer = _el(inv, 'AccountingCustomerParty', ns='cac')
    cparty = ET.SubElement(customer, '{%s}Party' % NS['cac'])
    _el(cparty, 'EndpointID', factura.cliente_documento, ns='cbc')
    cpname = ET.SubElement(cparty, '{%s}PartyName' % NS['cac'])
    _el(cpname, 'Name', factura.cliente_nombre, ns='cbc')

    tax = _el(inv, 'TaxTotal', ns='cac')
    _el(tax, 'TaxAmount', f"{factura.iva:.2f}", ns='cbc')

    legal = _el(inv, 'LegalMonetaryTotal', ns='cac')
    _el(legal, 'LineExtensionAmount', f"{factura.subtotal:.2f}", ns='cbc')
    _el(legal, 'TaxInclusiveAmount', f"{factura.total:.2f}", ns='cbc')
    _el(legal, 'PayableAmount', f"{factura.total:.2f}", ns='cbc')

    for i, linea in enumerate(factura.lineas or [], start=1):
        item = _el(inv, 'InvoiceLine', ns='cac')
        _el(item, 'ID', i, ns='cbc')
        _el(item, 'InvoicedQuantity', linea.get('cantidad'), ns='cbc')
        _el(item, 'LineExtensionAmount', f"{Decimal(linea.get('subtotal', 0)):.2f}", ns='cbc')
        ie = ET.SubElement(item, '{%s}Item' % NS['cac'])
        _el(ie, 'Description', linea.get('descripcion', ''), ns='cbc')

    rough = ET.tostring(inv, encoding='utf-8', xml_declaration=True)
    reparsed = minidom.parseString(rough)
    return reparsed.toprettyxml(indent='  ', encoding='utf-8').decode('utf-8')
