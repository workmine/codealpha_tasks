from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime
from .models import *
from .utils import cookieCart, cartData, guestOrder

# Imports for Login/Register
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def store(request):
    if not request.user.is_authenticated:
        return redirect('login')

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    products = Product.objects.all()
    context = {'products':products, 'cartItems':cartItems}
    return render(request, 'store/store.html', context)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(user=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    elif action == 'delete': 
        orderItem.delete()   # This deletes the item instantly
        return JsonResponse('Item was deleted', safe=False)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(user=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment submitted..', safe=False)

# -------------------------
# NEW LOGIN / REGISTER VIEWS
# -------------------------

def registerPage(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + username)
            login(request, user) # Automatically log the user in
            return redirect('store')

    context = {'form':form}
    return render(request, 'store/register.html', context)

def loginPage(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('store')
            else:
                messages.error(request, "Invalid username or password.")
        else:
             messages.error(request, "Invalid username or password.")

    form = AuthenticationForm()
    context = {'form':form}
    return render(request, 'store/login.html', context)
def profile(request):
    if request.user.is_authenticated:
        customer = request.user
        
        # 1. Handle Form Submission
        if request.method == 'POST':
            # Get data from the form
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')

            # Update the User object
            customer.first_name = first_name
            customer.last_name = last_name
            customer.email = email
            customer.save()
            
            messages.success(request, 'Profile details updated successfully!')
            return redirect('profile') # Reload page to show changes

        # 2. Get Order History
        orders = Order.objects.filter(user=customer, complete=True).order_by('-date_ordered')
        context = {'orders':orders}
        return render(request, 'store/profile.html', context)
    else:
        return redirect('login')
def productView(request, pk):
	product = Product.objects.get(id=pk)
	data = cartData(request)
	cartItems = data['cartItems']
	
	context = {'product':product, 'cartItems':cartItems}
	return render(request, 'store/product_view.html', context)