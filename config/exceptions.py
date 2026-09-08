"""Custom exception handler for InvenXis API."""

import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """Custom exception handler that returns consistent JSON error responses."""
    response = exception_handler(exc, context)

    if response is not None:
        errors = _format_errors(response.data, exc)
        response.data = {
            'success': False,
            'errors': errors,
            'status_code': response.status_code,
        }
        return response

    logger.exception("Unhandled exception: %s", exc)
    return Response(
        {
            'success': False,
            'errors': [{'message': 'Error interno del servidor', 'code': 'internal_error'}],
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _format_errors(data, exc):
    """Recursively format error messages into a consistent structure."""
    if isinstance(data, dict):
        formatted = []
        for key, value in data.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        formatted.extend(_format_errors(item, exc))
                    else:
                        formatted.append({
                            'field': key,
                            'message': str(item),
                            'code': _get_error_code(key, str(item)),
                        })
            elif isinstance(value, dict):
                formatted.extend(_format_errors(value, exc))
            else:
                formatted.append({
                    'field': key,
                    'message': str(value),
                    'code': _get_error_code(key, str(value)),
                })
        return formatted
    elif isinstance(data, list):
        formatted = []
        for item in data:
            formatted.extend(_format_errors(item, exc))
        return formatted
    else:
        return [{'message': str(data), 'code': 'error'}]


def _get_error_code(field, message):
    """Generate a consistent error code from field name and message."""
    field_map = {
        'username': 'invalid_username',
        'password': 'invalid_password',
        'email': 'invalid_email',
        'telefono': 'invalid_phone',
        'precio': 'invalid_price',
        'cantidad': 'invalid_quantity',
        'nombre': 'invalid_name',
        'razon_social': 'invalid_business_name',
        'nit': 'invalid_nit',
        'detalles': 'invalid_details',
        'non_field_errors': 'validation_error',
        'detail': 'not_found',
    }
    return field_map.get(field, 'validation_error')
