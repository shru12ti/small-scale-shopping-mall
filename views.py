from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import ProductForm
from .models import Product, Customer
from .serializers import ProductSerializer, CustomerSerializer
from math import ceil

# Your views and API endpoints follow...

def homePage(request):
    products = Product.objects.all()
    print(products)
    n = len(products)
    nSlides = n//4 + ceil((n/4)-(n//4))
    params = {'no_of_slides':nSlides, 'range': range(nSlides), 'product': products}
    data={
        'title':'Home Page'
        }
    return render(request,"index.html",data)


# Define the bill_customer function for handling cash payment
def bill_customer(request):
    if request.method == 'POST':
        # Assuming you have form data or other parameters required for billing
        # Extract the necessary information from the request
        # Generate the bill content based on the information

        # For demonstration purposes, let's say the bill includes product names and prices
        products = request.POST.getlist('products')  # Assuming you have a list of product IDs in the form
        total_price = 0
        bill_content = "Bill for customer:\n"

        for product_id in products:
            product = Product.objects.get(id=product_id)
            bill_content += f"{product.name}: ${product.price}\n"
            total_price += product.price

        bill_content += f"Total: ${total_price}"

        # Assuming you want to render the bill as a plain text response
        return HttpResponse(bill_content, content_type='text/plain')
    else:
        # If the request method is GET, render the bill form
        # You may need to create a form for selecting products or providing other billing information
        products = Product.objects.all()
        return render(request, 'billing/bill_form.html', {'products': products})

class BillingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Retrieve customer information from request data
        customer_id = request.data.get('customer_id')
        products_data = request.data.get('products')  # Assuming products data is sent as a list of dictionaries

        # Check if customer exists
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

        # Calculate bill amount based on products purchased
        total_amount = 0
        for product_data in products_data:
            product_id = product_data.get('product_id')
            quantity = product_data.get('quantity')
            # Retrieve product from database
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
            # Calculate subtotal for this product
            subtotal = product.price * quantity
            total_amount += subtotal

        # Create bill record in the database
        # Assuming you have a Bill model defined with appropriate fields
        bill = bill_customer.objects.create(customer=customer, total_amount=total_amount)

        # Accept cash payment
        # Assuming cash amount is sent in the request data
        cash_amount = request.data.get('cash_amount')
        if cash_amount is None or cash_amount < total_amount:
            return Response({'error': 'Invalid cash amount'}, status=status.HTTP_400_BAD_REQUEST)

        # Here you can add more validation or business logic related to payment processing

        # Return response indicating successful bill generation
        return Response({'message': 'Bill generated successfully'})

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

class CustomerListCreateView(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

class CustomerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error_message': 'Invalid username or password'})
    else:
        return render(request, 'login.html')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'billing/product_list.html', {'products': products})

from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProductForm
from .models import Product

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'billing/add_product.html', {'form': form})

@login_required
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'billing/update_product.html', {'form': form, 'product': product})


@login_required
def manage_product(request, product_id=None):
    product = None
    if product_id:
        product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)

    template_name = 'billing/update_product.html' if product_id else 'billing/add_product.html'
    return render(request, template_name, {'form': form, 'product': product})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'billing/delete_product.html', {'product': product})

