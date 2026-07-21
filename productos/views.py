from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto
from .forms import ProductoForm

ITEMS_PER_PAGE = 10


@login_required
def lista_productos(request):
    productos = Producto.objects.all()
    paginator = Paginator(productos, ITEMS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'productos/lista_productos.html', {
        'page_obj': page_obj,
    })


@login_required
def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'productos/detalle_producto.html', {
        'producto': producto,
    })


@login_required
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado correctamente.')
            return redirect('productos:lista')
    else:
        form = ProductoForm()
    return render(request, 'productos/formulario_producto.html', {
        'form': form,
        'titulo': 'Registrar Producto',
    })


@login_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado correctamente.')
            return redirect('productos:lista')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/formulario_producto.html', {
        'form': form,
        'titulo': 'Editar Producto',
        'producto': producto,
    })


@login_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, f'Producto "{producto.nombre}" eliminado correctamente.')
        return redirect('productos:lista')
    return render(request, 'productos/confirmar_eliminar.html', {
        'producto': producto,
    })
