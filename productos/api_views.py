"""API REST views for InvenXis - Módulo de Productos, Proveedores, Pedidos, Ventas y Reportes."""

import json
import logging
from decimal import Decimal
from io import BytesIO

from django.db import models
from django.db.models import Sum, Count, F, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from .models import (
    Producto, Proveedor, Pedido, DetallePedido, Venta, DetalleVenta,
    Factura, NotaCredito,
)
from .serializers import (
    ProductoSerializer, ProductoListSerializer,
    ProveedorSerializer, ProveedorListSerializer,
    PedidoSerializer, PedidoCreateSerializer,
    DetallePedidoSerializer,
    VentaSerializer, VentaCreateSerializer,
    FacturaSerializer, NotaCreditoSerializer,
)
from productos.fe.servicios import (
    crear_factura, emitir_factura, anular_factura, es_admin_fe,
)

logger = logging.getLogger(__name__)


# =============================================================================
# MIXINS / HELPERS
# =============================================================================

class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'success': True,
            'count': self.page.paginator.count,
            'page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'total_pages': self.page.paginator.num_pages,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })


def api_response(data=None, status_code=status.HTTP_200_OK, success=True, errors=None):
    """Standard API response format."""
    payload = {'success': success}
    if data is not None:
        payload['data'] = data
    if errors:
        payload['errors'] = errors
    return Response(payload, status=status_code)


def invalidate_dashboard():
    """Invalida el caché del dashboard tras escrituras de inventario."""
    from django.core.cache import cache
    cache.delete('dashboard_api:v1')


# =============================================================================
# AUTH
# =============================================================================

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import LoginSerializer


class LoginRateThrottle(AnonRateThrottle):
    scope = 'login'


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@throttle_classes([LoginRateThrottle])
def api_login(request):
    """Autenticación de usuario. Retorna tokens JWT."""
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = authenticate(
        username=serializer.validated_data['username'],
        password=serializer.validated_data['password']
    )

    if not user:
        return api_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            success=False,
            errors=[{'message': 'Credenciales inválidas', 'code': 'invalid_credentials'}]
        )

    refresh = RefreshToken.for_user(user)
    return api_response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
        }
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def api_refresh_token(request):
    """Refresh JWT token."""
    from rest_framework_simplejwt.tokens import RefreshToken
    from rest_framework_simplejwt.exceptions import TokenError

    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return api_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False,
            errors=[{'message': 'Refresh token requerido', 'code': 'missing_token'}]
        )

    try:
        refresh = RefreshToken(refresh_token)
        return api_response({
            'access': str(refresh.access_token),
        })
    except TokenError as e:
        return api_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            success=False,
            errors=[{'message': str(e), 'code': 'invalid_token'}]
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def api_logout(request):
    """Logout: blacklista el refresh token."""
    from rest_framework_simplejwt.tokens import RefreshToken
    from rest_framework_simplejwt.exceptions import TokenError

    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return api_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False,
            errors=[{'message': 'Refresh token requerido', 'code': 'missing_token'}]
        )
    try:
        RefreshToken(refresh_token).blacklist()
    except TokenError as e:
        return api_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False,
            errors=[{'message': str(e), 'code': 'invalid_token'}]
        )
    return api_response(data={'message': 'Sesión cerrada'})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_health(request):
    """Health check público para monitoreo/orquestadores."""
    from django.db import connection
    try:
        with connection.cursor() as cur:
            cur.execute('SELECT 1')
        db = 'ok'
    except Exception:  # noqa: BLE001 - health nunca debe romper
        logger.exception('Healthcheck: DB no disponible')
        db = 'error'
    payload = {'status': 'ok' if db == 'ok' else 'degraded', 'db': db, 'version': '1.0.0'}
    return api_response(
        payload,
        status_code=status.HTTP_200_OK if db == 'ok' else status.HTTP_503_SERVICE_UNAVAILABLE,
    )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def api_me(request):
    """Obtener información del usuario autenticado."""
    user = request.user
    return api_response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_staff': user.is_staff,
    })


# =============================================================================
# PRODUCTOS
# =============================================================================

class ProductoListCreateView(APIView):
    """
    GET /api/productos/ - Listar productos (con filtros, búsqueda, paginación)
    POST /api/productos/ - Crear producto
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = Producto.objects.select_related('proveedor').all()

        # Filtros
        categoria = request.query_params.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria__iexact=categoria)

        estado_stock = request.query_params.get('estado_stock')
        if estado_stock == 'normal':
            queryset = queryset.filter(cantidad__gt=F('stock_min'))
        elif estado_stock == 'bajo':
            queryset = queryset.filter(cantidad__gt=0, cantidad__lte=F('stock_min'))
        elif estado_stock == 'sin_stock':
            queryset = queryset.filter(cantidad=0)

        estado = request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)

        proveedor_id = request.query_params.get('proveedor')
        if proveedor_id:
            queryset = queryset.filter(proveedor_id=proveedor_id)

        busqueda = request.query_params.get('q')
        if busqueda:
            queryset = queryset.filter(
                Q(nombre__icontains=busqueda) | Q(categoria__icontains=busqueda) | Q(descripcion__icontains=busqueda)
            )

        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ProductoListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ProductoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        producto = serializer.save()
        invalidate_dashboard()
        logger.info("Producto creado: %s (ID: %d)", producto.nombre, producto.pk)
        return api_response(
            data=ProductoSerializer(producto).data,
            status_code=status.HTTP_201_CREATED
        )


class ProductoDetailView(APIView):
    """
    GET /api/productos/:id/ - Ver detalle de producto
    PUT /api/productos/:id/ - Actualizar producto completo
    PATCH /api/productos/:id/ - Actualizar producto parcial
    DELETE /api/productos/:id/ - Eliminar producto
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Producto.objects.select_related('proveedor'), pk=pk)

    def get(self, request, pk):
        producto = self.get_object(pk)
        serializer = ProductoSerializer(producto)
        return api_response(serializer.data)

    def put(self, request, pk):
        producto = self.get_object(pk)
        serializer = ProductoSerializer(producto, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        invalidate_dashboard()
        logger.info("Producto actualizado: %s (ID: %d)", producto.nombre, pk)
        return api_response(serializer.data)

    def patch(self, request, pk):
        producto = self.get_object(pk)
        serializer = ProductoSerializer(producto, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        invalidate_dashboard()
        return api_response(serializer.data)

    def delete(self, request, pk):
        producto = self.get_object(pk)
        nombre = producto.nombre
        producto.delete()
        invalidate_dashboard()
        logger.info("Producto eliminado: %s (ID: %d)", nombre, pk)
        return api_response(status_code=status.HTTP_204_NO_CONTENT, data={'message': f'Producto "{nombre}" eliminado'})


# =============================================================================
# PROVEEDORES
# =============================================================================

class ProveedorListCreateView(APIView):
    """
    GET /api/proveedores/ - Listar proveedores
    POST /api/proveedores/ - Crear proveedor
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = Proveedor.objects.annotate(
            productos_count=Count('productos', distinct=True),
            pedidos_count=Count('pedidos', distinct=True),
        ).order_by('-fecha_creacion')

        estado = request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)

        categoria = request.query_params.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria__iexact=categoria)

        busqueda = request.query_params.get('q')
        if busqueda:
            queryset = queryset.filter(
                Q(razon_social__icontains=busqueda) | Q(nit__icontains=busqueda) |
                Q(contacto__icontains=busqueda) | Q(email__icontains=busqueda)
            )

        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ProveedorSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ProveedorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        proveedor = serializer.save()
        invalidate_dashboard()
        logger.info("Proveedor creado: %s (ID: %d)", proveedor.razon_social, proveedor.pk)
        return api_response(
            data=ProveedorSerializer(proveedor).data,
            status_code=status.HTTP_201_CREATED
        )


class ProveedorDetailView(APIView):
    """
    GET /api/proveedores/:id/ - Ver detalle de proveedor
    PUT /api/proveedores/:id/ - Actualizar proveedor
    PATCH /api/proveedores/:id/ - Actualizar proveedor parcial
    DELETE /api/proveedores/:id/ - Eliminar proveedor
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(
            Proveedor.objects.annotate(
                productos_count=Count('productos', distinct=True),
                pedidos_count=Count('pedidos', distinct=True),
            ),
            pk=pk
        )

    def get(self, request, pk):
        proveedor = self.get_object(pk)
        serializer = ProveedorSerializer(proveedor)
        return api_response(serializer.data)

    def put(self, request, pk):
        proveedor = self.get_object(pk)
        serializer = ProveedorSerializer(proveedor, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        invalidate_dashboard()
        return api_response(serializer.data)

    def patch(self, request, pk):
        proveedor = self.get_object(pk)
        serializer = ProveedorSerializer(proveedor, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        invalidate_dashboard()
        return api_response(serializer.data)

    def delete(self, request, pk):
        proveedor = self.get_object(pk)
        nombre = proveedor.razon_social
        proveedor.delete()
        invalidate_dashboard()
        logger.info("Proveedor eliminado: %s (ID: %d)", nombre, pk)
        return api_response(status_code=status.HTTP_204_NO_CONTENT, data={'message': f'Proveedor "{nombre}" eliminado'})


# =============================================================================
# PEDIDOS (Historial por proveedor)
# =============================================================================

class PedidoListCreateView(APIView):
    """
    GET /api/proveedores/:id/pedidos/ - Listar pedidos de un proveedor
    POST /api/proveedores/:id/pedidos/ - Crear pedido para un proveedor
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, proveedor_pk):
        proveedor = get_object_or_404(Proveedor, pk=proveedor_pk)
        queryset = Pedido.objects.filter(proveedor=proveedor).prefetch_related(
            'detalles__producto', 'detalles'
        )

        estado = request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)

        desde = request.query_params.get('desde')
        hasta = request.query_params.get('hasta')
        if desde:
            queryset = queryset.filter(fecha_pedido__gte=desde)
        if hasta:
            queryset = queryset.filter(fecha_pedido__lte=hasta)

        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = PedidoSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, proveedor_pk):
        proveedor = get_object_or_404(Proveedor, pk=proveedor_pk)
        data = request.data.copy()
        data['proveedor'] = proveedor.pk
        data['creado_por'] = request.user.pk

        serializer = PedidoCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        pedido = serializer.save(proveedor=proveedor, creado_por=request.user)
        pedido.calcular_total()

        logger.info("Pedido creado: %s para proveedor %s", pedido.numero_orden, proveedor.razon_social)
        return api_response(
            data=PedidoSerializer(pedido).data,
            status_code=status.HTTP_201_CREATED
        )


class PedidoDetailView(APIView):
    """
    GET /api/pedidos/:id/ - Ver detalle de pedido
    PUT /api/pedidos/:id/ - Actualizar pedido
    PATCH /api/pedidos/:id/ - Actualizar pedido parcial
    DELETE /api/pedidos/:id/ - Eliminar pedido
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(
            Pedido.objects.prefetch_related('detalles__producto', 'detalles'),
            pk=pk
        )

    def get(self, request, pk):
        pedido = self.get_object(pk)
        serializer = PedidoSerializer(pedido)
        return api_response(serializer.data)

    def patch(self, request, pk):
        pedido = self.get_object(pk)
        serializer = PedidoCreateSerializer(pedido, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        pedido.calcular_total()
        return api_response(PedidoSerializer(pedido).data)

    def delete(self, request, pk):
        pedido = self.get_object(pk)
        pedido.delete()
        return api_response(status_code=status.HTTP_204_NO_CONTENT, data={'message': 'Pedido eliminado'})


# =============================================================================
# VENTAS
# =============================================================================

class VentaListCreateView(APIView):
    """
    GET /api/ventas/ - Listar ventas
    POST /api/ventas/ - Crear venta (descuenta stock automáticamente)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = Venta.objects.prefetch_related('detalles__producto', 'detalles').all()

        desde = request.query_params.get('desde')
        hasta = request.query_params.get('hasta')
        if desde:
            queryset = queryset.filter(fecha_venta__gte=desde)
        if hasta:
            queryset = queryset.filter(fecha_venta__lte=hasta)

        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = VentaSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data['creado_por'] = request.user.pk

        serializer = VentaCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        venta = serializer.save(creado_por=request.user)
        invalidate_dashboard()

        return api_response(
            data=VentaSerializer(venta).data,
            status_code=status.HTTP_201_CREATED
        )


# =============================================================================
# REPORTES
# =============================================================================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def reporte_inventario_api(request):
    """Reporte de inventario actual con estadísticas."""
    productos = Producto.objects.select_related('proveedor').all()
    total_productos = productos.count()
    valor_total = productos.aggregate(total=Sum(F('cantidad') * F('precio')))['total'] or 0
    stock_normal = productos.filter(cantidad__gt=F('stock_min')).count()
    stock_bajo = productos.filter(cantidad__gt=0, cantidad__lte=F('stock_min')).count()
    sin_stock = productos.filter(cantidad=0).count()

    categorias = productos.values('categoria').annotate(
        cantidad=Count('id'),
    ).order_by('categoria')

    categorias_data = []
    for c in categorias:
        prods = productos.filter(categoria=c['categoria'])
        valor = prods.aggregate(total=Sum(F('cantidad') * F('precio')))['total'] or 0
        categorias_data.append({
            'nombre': c['categoria'],
            'cantidad': c['cantidad'],
            'valor': float(valor),
        })

    productos_bajo = ProductoListSerializer(
        productos.filter(cantidad__gt=0, cantidad__lte=F('stock_min')), many=True
    ).data

    productos_sin_stock = ProductoListSerializer(
        productos.filter(cantidad=0), many=True
    ).data

    return api_response({
        'resumen': {
            'total_productos': total_productos,
            'valor_total': float(valor_total),
            'stock_normal': stock_normal,
            'stock_bajo': stock_bajo,
            'sin_stock': sin_stock,
        },
        'categorias': categorias_data,
        'productos_bajo_stock': productos_bajo,
        'productos_sin_stock': productos_sin_stock,
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def reporte_mas_vendidos_api(request):
    """Reporte de productos más vendidos basado en ventas."""
    top_n = int(request.query_params.get('top', 10))
    desde = request.query_params.get('desde')
    hasta = request.query_params.get('hasta')

    detalles = DetalleVenta.objects.select_related('producto', 'venta').filter(
        venta__estado='completada'
    )

    if desde:
        detalles = detalles.filter(venta__fecha_venta__gte=desde)
    if hasta:
        detalles = detalles.filter(venta__fecha_venta__lte=hasta)

    ranking = detalles.values(
        'producto__id', 'producto__nombre', 'producto__categoria', 'producto__precio'
    ).annotate(
        total_vendido=Sum('cantidad'),
        total_ingresos=Sum('subtotal'),
        veces_vendido=Count('id'),
    ).order_by('-total_vendido')[:top_n]

    return api_response({
        'ranking': [
            {
                'producto_id': item['producto__id'],
                'nombre': item['producto__nombre'],
                'categoria': item['producto__categoria'],
                'precio': float(item['producto__precio']),
                'total_vendido': item['total_vendido'],
                'total_ingresos': float(item['total_ingresos']),
                'veces_vendido': item['veces_vendido'],
            }
            for item in ranking
        ],
        'filtros': {
            'top': top_n,
            'desde': desde,
            'hasta': hasta,
        }
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def reporte_ventas_api(request):
    """Reporte de ventas con estadísticas generales."""
    desde = request.query_params.get('desde')
    hasta = request.query_params.get('hasta')

    ventas = Venta.objects.filter(estado='completada')
    if desde:
        ventas = ventas.filter(fecha_venta__gte=desde)
    if hasta:
        ventas = ventas.filter(fecha_venta__lte=hasta)

    total_ventas = ventas.count()
    total_ingresos = ventas.aggregate(total=Sum('total'))['total'] or 0
    promedio_venta = float(total_ingresos / total_ventas) if total_ventas > 0 else 0

    return api_response({
        'resumen': {
            'total_ventas': total_ventas,
            'total_ingresos': float(total_ingresos),
            'promedio_venta': promedio_venta,
        },
        'ventas_recientes': VentaSerializer(
            ventas.prefetch_related('detalles__producto').order_by('-fecha_venta')[:5],
            many=True
        ).data,
    })


# =============================================================================
# EXPORTACIONES
# =============================================================================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def exportar_reporte_excel(request, tipo):
    """Exportar reporte a Excel (inventario, proveedores, ventas)."""
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    wb = openpyxl.Workbook()
    ws = wb.active

    amber_fill = PatternFill(start_color='E8A230', end_color='E8A230', fill_type='solid')
    header_font = Font(name='Calibri', bold=True, color='0D0E0F', size=11)
    data_font = Font(name='Calibri', size=10)
    thin_border = Border(
        left=Side(style='thin', color='252A2F'),
        right=Side(style='thin', color='252A2F'),
        top=Side(style='thin', color='252A2F'),
        bottom=Side(style='thin', color='252A2F'),
    )

    if tipo == 'inventario':
        ws.title = 'Inventario'
        headers = ['Producto', 'Categoría', 'Stock', 'Stock Mínimo', 'Proveedor', 'Precio Unitario', 'Valor Total', 'Estado']
        for col, h in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=h)
            cell.fill = amber_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')
            cell.border = thin_border

        for i, p in enumerate(Producto.objects.select_related('proveedor').all(), 2):
            estado = 'Sin Stock' if p.cantidad == 0 else ('Stock Bajo' if p.cantidad <= p.stock_min else 'Normal')
            vals = [p.nombre, p.categoria, p.cantidad, p.stock_min,
                    p.proveedor.razon_social if p.proveedor else '',
                    float(p.precio), float(p.cantidad * p.precio), estado]
            for col, v in enumerate(vals, 1):
                c = ws.cell(row=i, column=col, value=v)
                c.font = data_font
                c.border = thin_border

        ws.column_dimensions['A'].width = 30
        for c in 'BCDEFGH':
            ws.column_dimensions[c].width = 18

    elif tipo == 'proveedores':
        ws.title = 'Proveedores'
        headers = ['Razón Social', 'NIT', 'Categoría', 'Contacto', 'Teléfono', 'Email', 'Productos', 'Estado']
        for col, h in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=h)
            cell.fill = amber_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')
            cell.border = thin_border

        for i, p in enumerate(Proveedor.objects.annotate(
                prod_count=Count('productos')
        ).all(), 2):
            vals = [p.razon_social, p.nit, p.categoria, p.contacto, p.telefono,
                    p.email, p.prod_count, 'Activo' if p.estado == 'activo' else 'Inactivo']
            for col, v in enumerate(vals, 1):
                c = ws.cell(row=i, column=col, value=v)
                c.font = data_font
                c.border = thin_border

        ws.column_dimensions['A'].width = 30
        for c in 'BCDEFGH':
            ws.column_dimensions[c].width = 18

    elif tipo == 'ventas':
        ws.title = 'Ventas'
        headers = ['Factura', 'Cliente', 'Fecha', 'Total', 'Método Pago', 'Estado']
        for col, h in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=h)
            cell.fill = amber_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')
            cell.border = thin_border

        for i, v in enumerate(Venta.objects.all(), 2):
            vals = [v.numero_factura, v.cliente or 'N/A', v.fecha_venta.strftime('%Y-%m-%d'),
                    float(v.total), v.metodo_pago or 'N/A',
                    'Completada' if v.estado == 'completada' else v.estado]
            for col, v in enumerate(vals, 1):
                c = ws.cell(row=i, column=col, value=v)
                c.font = data_font
                c.border = thin_border

        ws.column_dimensions['A'].width = 20
        ws.column_dimensions['B'].width = 25
        ws.column_dimensions['C'].width = 15
        ws.column_dimensions['D'].width = 15
        ws.column_dimensions['E'].width = 15
        ws.column_dimensions['F'].width = 15

    else:
        return api_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False,
            errors=[{'message': f'Tipo de reporte inválido: {tipo}', 'code': 'invalid_report_type'}]
        )

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f'reporte_{tipo}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    response['Content-Disposition'] = f'attachment; filename={filename}'
    wb.save(response)
    return response


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def exportar_reporte_pdf(request, tipo):
    """Exportar reporte a PDF."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        spaceAfter=20,
        textColor=colors.HexColor('#E8A230'),
    )

    elements.append(Paragraph(f"InvenXis - Reporte de {tipo}", title_style))
    elements.append(Paragraph(f"Generado: {timezone.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))

    if tipo == 'inventario':
        productos = Producto.objects.select_related('proveedor').all()
        data = [['Producto', 'Categoría', 'Stock', 'Precio', 'Valor Total', 'Estado']]
        for p in productos:
            estado = 'Sin Stock' if p.cantidad == 0 else ('Stock Bajo' if p.cantidad <= p.stock_min else 'Normal')
            data.append([
                p.nombre, p.categoria, str(p.cantidad),
                f'${float(p.precio):,.0f}',
                f'${float(p.cantidad * p.precio):,.0f}',
                estado
            ])

        table = Table(data, colWidths=[2*inch, 1.2*inch, 0.8*inch, 1*inch, 1.2*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8A230')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0D0E0F')),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#252A2F')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ]))
        elements.append(table)

    elif tipo == 'proveedores':
        proveedores = Proveedor.objects.all()
        data = [['Razón Social', 'NIT', 'Contacto', 'Teléfono', 'Email', 'Estado']]
        for p in proveedores:
            data.append([p.razon_social, p.nit, p.contacto, p.telefono, p.email,
                        'Activo' if p.estado == 'activo' else 'Inactivo'])

        table = Table(data, colWidths=[1.8*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.5*inch, 0.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8A230')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0D0E0F')),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#252A2F')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ]))
        elements.append(table)

    elif tipo == 'ventas':
        ventas = Venta.objects.all()
        data = [['Factura', 'Cliente', 'Fecha', 'Total', 'Estado']]
        for v in ventas:
            data.append([
                v.numero_factura, v.cliente or 'N/A',
                v.fecha_venta.strftime('%Y-%m-%d'),
                f'${float(v.total):,.0f}',
                'Completada' if v.estado == 'completada' else v.estado
            ])

        table = Table(data, colWidths=[1.5*inch, 1.5*inch, 1.2*inch, 1.2*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8A230')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0D0E0F')),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#252A2F')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ]))
        elements.append(table)

    else:
        return api_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False,
            errors=[{'message': f'Tipo de reporte inválido: {tipo}', 'code': 'invalid_report_type'}]
        )

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f'reporte_{tipo}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response


# =============================================================================
# DASHBOARD API
# =============================================================================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_api(request):
    """Obtener datos del dashboard (KPI, resumen, actividad reciente)."""
    from django.core.cache import cache
    cached = cache.get('dashboard_api:v1')
    if cached is not None:
        return api_response(cached)
    total_productos = Producto.objects.count()
    stock_bajo = Producto.objects.filter(cantidad__gt=0, cantidad__lte=F('stock_min')).count()
    sin_stock = Producto.objects.filter(cantidad=0).count()
    total_proveedores = Proveedor.objects.count()
    proveedores_activos = Proveedor.objects.filter(estado='activo').count()
    valor_total = Producto.objects.aggregate(total=Sum(F('cantidad') * F('precio')))['total'] or 0
    total_pedidos = Pedido.objects.count()
    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
    total_ventas = Venta.objects.filter(estado='completada').count()
    ingresos_totales = Venta.objects.filter(estado='completada').aggregate(total=Sum('total'))['total'] or 0

    productos_recientes = ProductoListSerializer(
        Producto.objects.select_related('proveedor').order_by('-fecha_creacion')[:5],
        many=True
    ).data

    pedidos_recientes = PedidoSerializer(
        Pedido.objects.select_related('proveedor').prefetch_related('detalles__producto').order_by('-fecha_pedido')[:5],
        many=True
    ).data

    payload = {
        'kpi': {
            'total_productos': total_productos,
            'stock_bajo': stock_bajo,
            'sin_stock': sin_stock,
            'total_proveedores': total_proveedores,
            'proveedores_activos': proveedores_activos,
            'valor_total': float(valor_total),
            'total_pedidos': total_pedidos,
            'pedidos_pendientes': pedidos_pendientes,
            'total_ventas': total_ventas,
            'ingresos_totales': float(ingresos_totales),
        },
        'productos_recientes': productos_recientes,
        'pedidos_recientes': pedidos_recientes,
    }
    from django.core.cache import cache
    cache.set('dashboard_api:v1', payload, 60)
    return api_response(payload)


# =============================================================================
# FACTURACIÓN (factura + factura electrónica DIAN-ready)
# =============================================================================

class FacturaListView(APIView):
    """GET /api/facturas/ - Listar facturas (filtros + paginación)."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = Factura.objects.select_related('venta').all()
        estado = request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        busqueda = request.query_params.get('q')
        if busqueda:
            queryset = queryset.filter(
                Q(numero__icontains=busqueda)
                | Q(cliente_nombre__icontains=busqueda)
                | Q(cliente_documento__icontains=busqueda)
            )
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        return paginator.get_paginated_response(
            FacturaSerializer(page, many=True).data)


class FacturaDetailView(APIView):
    """GET /api/facturas/:id/ - Detalle de factura."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        factura = get_object_or_404(Factura.objects.select_related('venta'), pk=pk)
        return api_response(FacturaSerializer(factura).data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def facturar_venta(request, venta_id):
    """POST /api/ventas/:id/facturar/ - Crea la factura en borrador."""
    venta = get_object_or_404(Venta, pk=venta_id)
    try:
        factura = crear_factura(
            venta,
            cliente_nombre=request.data.get('cliente_nombre'),
            cliente_documento=request.data.get('cliente_documento'),
            cliente_email=request.data.get('cliente_email'),
            descuento=request.data.get('descuento') or 0,
            creado_por=request.user,
        )
    except ValueError as e:
        return api_response(
            status_code=status.HTTP_400_BAD_REQUEST, success=False,
            errors=[{'message': str(e), 'code': 'factura_invalida'}])
    invalidate_dashboard()
    logger.info("Factura creada: %s (venta %d)", factura.numero, venta.pk)
    return api_response(
        data=FacturaSerializer(factura).data,
        status_code=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def emitir_factura_view(request, pk):
    """POST /api/facturas/:id/emitir/ - Emite FE ante el proveedor."""
    factura = get_object_or_404(Factura, pk=pk)
    try:
        factura = emitir_factura(factura)
    except ValueError as e:
        return api_response(
            status_code=status.HTTP_400_BAD_REQUEST, success=False,
            errors=[{'message': str(e), 'code': 'emision_invalida'}])
    invalidate_dashboard()
    data = FacturaSerializer(factura).data
    code = status.HTTP_200_OK if factura.estado == 'validada_dian' else status.HTTP_502_BAD_GATEWAY
    return api_response(data=data, status_code=code)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def anular_factura_view(request, pk):
    """POST /api/facturas/:id/anular/ - Anula (solo Administradores)."""
    factura = get_object_or_404(Factura.objects.select_related('venta'), pk=pk)
    motivo = (request.data.get('motivo') or '').strip()
    try:
        nc = anular_factura(factura, motivo=motivo, usuario=request.user)
    except PermissionError as e:
        return api_response(
            status_code=status.HTTP_403_FORBIDDEN, success=False,
            errors=[{'message': str(e), 'code': 'forbidden'}])
    except ValueError as e:
        return api_response(
            status_code=status.HTTP_400_BAD_REQUEST, success=False,
            errors=[{'message': str(e), 'code': 'anulacion_invalida'}])
    invalidate_dashboard()
    logger.info("Factura anulada: %s (%s)", factura.numero, motivo)
    return api_response(data=NotaCreditoSerializer(nc).data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def factura_pdf_view(request, pk):
    """GET /api/facturas/:id/pdf/ - Descarga la factura en PDF."""
    factura = get_object_or_404(Factura.objects.select_related('venta'), pk=pk)
    buffer = _generar_factura_pdf(factura)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factura_{factura.numero}.pdf"'
    return response


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def factura_ubl_view(request, pk):
    """GET /api/facturas/:id/ubl/ - Descarga el UBL XML."""
    from productos.fe.ubl import construir_ubl
    factura = get_object_or_404(Factura, pk=pk)
    xml = factura.ubl_xml or construir_ubl(factura)
    response = HttpResponse(xml, content_type='application/xml')
    response['Content-Disposition'] = f'attachment; filename="factura_{factura.numero}.xml"'
    return response


class NotaCreditoListView(APIView):
    """GET /api/notas-credito/ - Listar notas crédito."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = NotaCredito.objects.select_related('factura').all()
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        return paginator.get_paginated_response(
            NotaCreditoSerializer(page, many=True).data)


def _generar_factura_pdf(factura):
    """PDF profesional de factura con totales, CUFE y estado DIAN."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle)
    from io import BytesIO

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            topMargin=15 * mm, bottomMargin=15 * mm)
    styles = getSampleStyleSheet()
    brand = colors.HexColor('#E8A230')
    elements = []

    title_style = ParagraphStyle('FTitle', parent=styles['Title'],
                                 fontSize=20, textColor=brand, spaceAfter=2)
    elements.append(Paragraph(f"InvenXis — Factura {factura.numero}", title_style))
    elements.append(Paragraph(
        f"Fecha: {factura.fecha.strftime('%Y-%m-%d %H:%M')} · "
        f"Estado: {factura.get_estado_display()}",
        styles['Normal']))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph(
        f"<b>Cliente:</b> {factura.cliente_nombre} · "
        f"Doc: {factura.cliente_documento}"
        + (f" · {factura.cliente_email}" if factura.cliente_email else ''),
        styles['Normal']))
    elements.append(Paragraph(
        f"<b>Venta:</b> {factura.venta.numero_factura}", styles['Normal']))
    elements.append(Spacer(1, 8))

    rows = [['Descripción', 'Cant.', 'P. unitario', 'Subtotal']]
    for lin in factura.lineas or []:
        rows.append([lin.get('descripcion', ''), str(lin.get('cantidad', '')),
                     str(lin.get('precio_unitario', '')), str(lin.get('subtotal', ''))])
    rows += [
        ['', '', 'Subtotal', f"{factura.subtotal:.2f}"],
        ['', '', 'Descuento', f"{factura.descuento:.2f}"],
        ['', '', f"IVA ({factura.iva_porcentaje}%)", f"{factura.iva:.2f}"],
        ['', '', 'TOTAL', f"{factura.total:.2f}"],
    ]
    table = Table(rows, colWidths=[80 * mm, 20 * mm, 30 * mm, 30 * mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), brand),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0D0E0F')),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#999999')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7F7F7')]),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 10))
    if factura.cufe:
        elements.append(Paragraph(f"<b>CUFE:</b> {factura.cufe}", styles['Normal']))
    if factura.estado == 'anulada' and factura.motivo_anulacion:
        elements.append(Paragraph(
            f"<b>ANULADA:</b> {factura.motivo_anulacion}", styles['Normal']))
    doc.build(elements)
    buffer.seek(0)
    return buffer
