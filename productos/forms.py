from django import forms
from .models import Producto, Proveedor

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'precio', 'cantidad', 'stock_min', 'descripcion', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej. Resma Papel A4 75gr'}),
            'categoria': forms.Select(attrs={'class': 'form-input'}),
            'precio': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0.00', 'step': '0.01'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0'}),
            'stock_min': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '10'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Descripción breve del producto...'}),
            'estado': forms.Select(attrs={'class': 'form-input'}),
        }
        labels = {
            'nombre': 'Nombre del Producto',
            'categoria': 'Categoría',
            'precio': 'Precio Unitario ($)',
            'cantidad': 'Stock Actual',
            'stock_min': 'Stock Mínimo',
            'descripcion': 'Descripción',
            'estado': 'Estado',
        }

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is not None and precio < 0:
            raise forms.ValidationError('El precio no puede ser negativo.')
        return precio

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is not None and cantidad < 0:
            raise forms.ValidationError('La cantidad no puede ser negativa.')
        return cantidad

    def clean_stock_min(self):
        stock_min = self.cleaned_data.get('stock_min')
        if stock_min is not None and stock_min < 0:
            raise forms.ValidationError('El stock mínimo no puede ser negativo.')
        return stock_min


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['razon_social', 'nit', 'categoria', 'contacto', 'telefono', 'email', 'estado']
        widgets = {
            'razon_social': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Empresa S.A.S.'}),
            'nit': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '900.000.000-0'}),
            'categoria': forms.Select(attrs={'class': 'form-input'}),
            'contacto': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre del contacto'}),
            'telefono': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '(57) 300 000 0000'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'contacto@empresa.com'}),
            'estado': forms.Select(attrs={'class': 'form-input'}),
        }
        labels = {
            'razon_social': 'Razón Social',
            'nit': 'NIT',
            'categoria': 'Categoría',
            'contacto': 'Contacto Principal',
            'telefono': 'Teléfono',
            'email': 'Correo Electrónico',
            'estado': 'Estado',
        }
