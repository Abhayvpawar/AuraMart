from django.urls import path
from .views import ProductSearchView
from . import views

urlpatterns=[
    path('',views.welcome,name='welcome'),
    path('join_aura/',views.join_aura,name='join_aura'),
    path('home_page/',views.home_page,name='home_page'),
    path('about/',views.about,name='About'),
    path('regester/',views.regester,name='regester'),
    path('login/',views.userlogin,name='userlogin'),
    path('auraexit/',views.auraexit,name='auraexit'),
    # path('product_page/<int:product_id>/',views.product_page,name='product_page'),
    path('product_page/<int:product_id>/', views.product_page, name='product_page'),
    path('profile/',views.profile,name='profile'),
    path('profile_form/',views.profile_form,name='profile_form'),
    path('add_to_cart/<int:product_id>/',views.add_to_cart,name='add_to_cart'),
    path('aurabag/',views.aura_bag,name='aura_bag'),
    path('reset_password/',views.reset_password,name='reset_password'),
    path('update_cart/', views.update_cart, name='update_cart'),
    path('security_check/', views.security_check, name='Security_check'),
    path('security_que/', views.security_que, name='Security_que'),
    path('api/search/', ProductSearchView.as_view(), name='product-search'),
    path('order/', views.order, name='order'),
    path('order_page/', views.order_page, name='order_page'),
    path('get_ai_response/<int:product_id>/', views.get_ai_response, name='get_ai_response'),
    # path('demo/',views.demo,name='demo'),
]   