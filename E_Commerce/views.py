from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from .models import Product,userinfo,Category,Cart,CartItem,security_question,Order,OrderItem
import random,json
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password
import bcrypt
from django.contrib.auth import update_session_auth_hash
from rest_framework import generics, permissions
from rest_framework.authentication import TokenAuthentication
from .models import Product
from .serializers import ProductSerializer
from django.views.decorators.csrf import csrf_exempt
import openai,ollama
from dotenv import load_dotenv
import os
import requests

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

# Create your views here.

def welcome(request):
    # if request.user.is_authenticated:
    #     context={'login':'true'}
    #     return render(request,'index.html',context)
    return render(request, 'index.html')

def home_page(request):
    context={}
    if request.user.is_authenticated:
        context['login']='True'
    products = list(Product.objects.all())  # Fetch all products
    random.shuffle(products)  # Shuffle the list to randomize the order
    context['products']=products[:9]
    return render(request,'home_page.html',context)

def join_aura(request):
    return render(request,'join_aura.html')

def about(request):
    if request.user.is_authenticated:
        context={'login':'true'}
        return render(request,'about.html',context)
    return render(request, 'about.html')

def regester(request):
    if request.method=='POST':
        name=request.POST.get('name')
        password=request.POST.get('password1')
        email=request.POST.get('regester-email')
        if User.objects.filter(email=email).exists():
            context={'error_message_regester':'Email already regestered'}
            return render(request,'join_aura.html',context)
        user=User.objects.create_user(first_name=name,email=email,password=password,username=email)
        login(request,user)
        return redirect('home_page')   

def userlogin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            return redirect('home_page')
        else:
            context={'error_message_login':'Invalid username or password'}
            return render(request,'join_aura.html',context)

    return render(request, 'index.html')

def auraexit(request):
    logout(request)
    return redirect('home_page')

def product_page(request, product_id):
    context = {}

    if request.user.is_authenticated:
        context['login'] = 'true'

    product = get_object_or_404(Product, id=product_id)
    category_name = product.category.name

    sug = Product.objects.filter(category_id=product.category_id).exclude(id=product_id)
    sug = list(sug)
    random.shuffle(sug)
    sug = sug[:4]

    context.update({'product': product, 'category': category_name, 'sug': sug})
    return render(request, 'p1.html', context)

def profile(request):
    user_info=userinfo.objects.filter(email=request.user.email).first()
    if user_info:
        return render(request,'profile.html',context={'user_info':user_info})
    else:
        return redirect('profile_form')

def profile_form(request):
    if request.method == 'POST':
        
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        phonenumber = request.POST.get('phone')
        Country = request.POST.get('country')
        gender = request.POST.get('gender')
        address1 = request.POST.get('address1')
        address2 = request.POST.get('address2')

        user_info=userinfo.objects.filter(email=request.user.email).first()

        if user_info:
            # If user info exists, update it
            user_info.first_name = firstname
            user_info.last_name = lastname
            user_info.phone_number = phonenumber
            user_info.country = Country
            user_info.gender = gender
            user_info.address_1 = address1
            user_info.address_2 = address2
            user_info.save()
        else:
            # If no user info exists, create a new one
            user_info = userinfo.objects.create(
                first_name=firstname,
                last_name=lastname,
                phone_number=phonenumber,
                country=Country,
                gender=gender,
                address_1=address1,
                address_2=address2,
                email=request.user.email
            )

        user = request.user
        user.first_name = firstname
        user.last_name = lastname
        user.save()

        return redirect('profile')

    return render(request, 'profile_form.html')

def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if user is not authenticated

    cart, created = Cart.objects.get_or_create(user=request.user)
    
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': 1})

    if not created:
        cart_item.quantity += 1  
        cart_item.save()

    return redirect('aura_bag')  # Redirect to cart page (Update this with your actual cart view name)


def aura_bag(request):
    if not request.user.is_authenticated:
        return redirect('join_aura')
    
    cart=Cart.objects.filter(user=request.user).first()

    if not cart:
        Cart.objects.create(user=request.user)
        cart=Cart.objects.filter(user=request.user).first()

    cart_items=CartItem.objects.filter(cart_id=cart.id)

    if not cart_items:
        return render(request, 'cart.html', {'products': [], 'total_price': 0, 'cart_price': 0})

    product_details=[]
    for item in cart_items:
        product_details.append(
            {
                'product':item.product,
                'total_price':item.total_price,
                'quantity':item.quantity,
            }
        )
    total_price=0
    for item in cart_items:
        base_price=item.quantity*item.product.price
        total_price+=base_price

    cart_price = round((float(total_price + 100)) * 0.80, 2)
    cart.cart_price=cart_price
    cart.save(update_fields=['cart_price'])

    print(Cart.cart_price)

    return render(request,'cart.html',context={'products':product_details,'total_price':total_price,'cart_price':cart_price})

def update_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        change = int(data.get('change'))  # +1 for increase, -1 for decrease

        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            return JsonResponse({'error': 'Cart not found'}, status=400)

        cart_item = CartItem.objects.filter(cart=cart, product_id=product_id).first()
        if not cart_item:
            return JsonResponse({'error': 'Item not found in cart'}, status=400)

        # Update quantity
        cart_item.quantity = max(cart_item.quantity + change, 0)

        if cart_item.quantity == 0:
            cart_item.delete()
        else:
            cart_item.total_price = cart_item.quantity * cart_item.product.price
            cart_item.save()

        # Recalculate total cart price
        total_price = sum(item.total_price for item in CartItem.objects.filter(cart=cart))
        cart.cart_price = round(float((total_price + 100)) * 0.80, 2)  # Example calculation
        cart.save()

        return JsonResponse({
            'quantity': cart_item.quantity if cart_item.quantity > 0 else 0,
            'item_total': cart_item.total_price if cart_item.quantity > 0 else 0,
            'total_price': total_price,
            'cart_price': cart.cart_price
        })

def reset_password(request):
    user = security_question.objects.filter(user=request.user).values('question','answer').first()
    context={'question': user['question']}

    if request.method == 'POST':
        answer=request.POST.get('answer')
        new_password=request.POST.get('new_password')
        repeat_password=request.POST.get('repeat_password')

        if bcrypt.checkpw(answer.encode(), user['answer'].encode()):
            if (new_password == repeat_password):
                user=User.objects.get(username=request.user)
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                return redirect(home_page)
            else:
                context['error_password_match'] = "Passwords didn't matched."
        else:
            context['error_security_answer']='invalid security answer.'

    return render(request,'password_reset.html',context)

def security_check(request):
    context = {'successful': False}

    if request.method == 'POST':
        password = request.POST.get('password')

        if check_password(password, request.user.password):
            context['successful'] = True
        else:
            context['error_message_check'] = "Invalid password"

    return render(request, 'Security_que.html', context)

def security_que(request):
    if request.method == 'POST':
        question=request.POST.get('question')
        answer=request.POST.get('answer')

        answer = bcrypt.hashpw(answer.encode(), bcrypt.gensalt()).decode()

        user =security_question.objects.filter(user=request.user).first()
        if user:
            security_question.objects.filter(user=request.user).delete()

        security_question.objects.create(user=request.user, question=question, answer=answer)
    
    return redirect('home_page')

class ProductSearchView(generics.ListAPIView):
    serializer_class = ProductSerializer
    authentication_classes = [TokenAuthentication]  # Secure API
    permission_classes = [permissions.IsAuthenticated]  # Only logged-in users

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        return Product.objects.filter(name__icontains=query)  # Case-insensitive search
    
def search_products(request):
    query = request.GET.get("q", "").strip()
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    print(f"Query: {query}, Is AJAX: {is_ajax}")  # Debugging Output

    if is_ajax:  # AJAX request handling
        products = Product.objects.filter(name__icontains=query) if query else Product.objects.all()
        results = list(products.values("id", "name", "description", "price"))
        return JsonResponse(results, safe=False)

    # Regular page rendering
    products = Product.objects.all()
    return render(request, "search.html", {"products": products})

def order(request):
    user = request.user
    cart=Cart.objects.filter(user=user).first()
    cart_items=CartItem.objects.filter(cart=cart)

    if cart_items:
        order, created = Order.objects.get_or_create(user=user, total_price=cart.cart_price)

        for i in cart_items:
            OrderItem.objects.create(quantity=i.quantity, price_at_purchase=i.total_price, product=i.product, order=order)
        
        Cart.objects.filter(user=user).delete()

    else:
        return redirect("home_page")

    return HttpResponse("Order succestsful")

from django.shortcuts import render
from .models import Order

def order_page(request):
    orders = list(Order.objects.filter(user=request.user).values('order_id', 'created_at', 'total_price'))
    
    return render(request, 'Order.html', {'orders': orders})

client = openai.OpenAI(api_key=api_key)
import requests
import json
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import Product  

@csrf_exempt
def get_ai_response(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_name = product.name
    print("\n✅ Product Name:", product_name)

    prompt = f"Give me details about this product: {product.name}."

    # Call TinyLlama API
    url = "http://localhost:11434/api/generate"
    data = {"model": "tinyllama", "prompt": prompt}

    try:
        response = requests.post(url, json=data, stream=True, timeout=10)  # Add timeout
        print("🔄 Status Code:", response.status_code)

        answer = ""  # Empty answer by default

        if response.status_code == 200:
            print("✅ API Call Successful. Processing response...")
            
            # Read response line by line
            for line in response.iter_lines():
                if line:
                    try:
                        json_data = json.loads(line.decode("utf-8"))  # Convert bytes to JSON
                        print("🔹 Raw JSON:", json_data)  # Print raw JSON data
                        answer += json_data.get("response", "").replace("\n", "<br>").replace("•", "<br>•")
                    except json.JSONDecodeError as e:
                        print("❌ JSON Decode Error:", e)
            
            print("\n✅ Final Answer:", answer)  # Debugging output

        else:
            print("❌ API returned an error:", response.text)
            answer = "Error: AI response failed."

    except requests.exceptions.RequestException as e:
        print("❌ Request Exception:", e)
        answer = "Error: Could not connect to AI server."

    return render(request, "AiAns.html", {"response": answer})
