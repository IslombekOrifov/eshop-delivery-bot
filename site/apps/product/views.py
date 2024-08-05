from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.http import Http404

from apps.cart.cart import Cart

from .models import Category, Product


class CategoryView(TemplateView):
    template_name = 'product/category.html'
    
    def get(self, request, slug, custom_id, *args, **kwargs):
        category = get_object_or_404(Category, slug=slug, custom_id=custom_id)
        products = Product.objects.filter(category__slug=slug, 
                                          category__custom_id=custom_id, 
                                          is_active=True, is_deleted=False)
        
        context = self.get_context_data(products=products, category=category)
        return self.render_to_response(context)
    
    
class ProductDetailView(TemplateView):
    template_name = 'product/detail.html'
    
    def get(self, request, slug, custom_id, *args, **kwargs):
        product = Product.objects.filter(slug=slug, custom_id=custom_id).select_related('category').prefetch_related('images').first()
        if not product:
            raise Http404()
        context = self.get_context_data(product=product)
        return self.render_to_response(context)
    
