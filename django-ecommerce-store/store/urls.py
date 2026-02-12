from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
	path('', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),

	path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),
	path('profile/', views.profile, name="profile"),
	path('product_view/<str:pk>/', views.productView, name="product_view"),

    # NEW LOGIN/REGISTER URLS
	path('login/', views.loginPage, name="login"),
	path('register/', views.registerPage, name="register"),
    path('logout/', auth_views.LogoutView.as_view(next_page='store'), name='logout'),
]