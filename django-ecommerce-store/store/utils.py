import json
from .models import *

def cookieCart(request):
    # Create empty cart for now
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}

    print('Cart:', cart)
    items = []
    order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
    cartItems = order['get_cart_items']

    for i in cart:
        # We use try block to prevent items in cart that may have been removed from causing error
        try:    
            cartItems += cart[i]['quantity']

            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])

            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']

            item = {
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price, 
                    'imageURL':product.imageURL,
                    },
                'quantity':cart[i]['quantity'],
                'get_total':total,
                }
            items.append(item)

            if product.digital == False:
                order['shipping'] = True
        except:
            pass
            
    return {'cartItems':cartItems ,'order':order, 'items':items}

def cartData(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(user=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    return {'cartItems':cartItems ,'order':order, 'items':items}

def guestOrder(request, data):
    print('User is not logged in')
    
    print('COOKIES:', request.COOKIES)
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    # Create a user for the guest (or find existing email)
    # Note: We are using the User model, but usually you might want a separate Customer model
    # For now, let's just create the Order directly attached to a "Guest" concept or leave User null.
    
    # Create the Order
    order = Order.objects.create(
        complete=False,
    )
    
    # Connect the items to that order
    for item in items:
        product = Product.objects.get(id=item['product']['id'])
        orderItem = OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity'],
        )
    return customer, order # This line might need adjustment based on your exact Customer model setup
def guestOrder(request, data):
    print('User is not logged in')
    
    print('COOKIES:', request.COOKIES)
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    # Create a user (or customer) for the guest
    # Note: Since your model links Order to User, we might need to attach it to a temporary user or handle nulls.
    # For this specific project structure where Order.user is nullable:
    
    # We create the order first
    order = Order.objects.create(
        complete=False,
    )
    
    # We attach the items from the cookie to this new database order
    for item in items:
        product = Product.objects.get(id=item['product']['id'])
        orderItem = OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity'],
        )
    
    # Note: We return customer as None here because your model expects a User instance
    # But for guest checkout, we just want the order to exist.
    return None, order