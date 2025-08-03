from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import hmac, base64, random
from django.views.decorators.csrf import csrf_exempt

def order_form_view(request):
    return render(request, "form.html")


def generate_shopier_form(data):
    buyer_account_age = 1
    currency = 0
    product_type = 1
    modul_version = '1.0.4'
    random_nr = str(random.randint(1000000, 9999999))
    api_key = data['apikey']
    api_secret = data['apisecret']

    args = {
        "API_key": api_key,
        "website_index": 1,
        "platform_order_id": data['order_id'],
        "product_name": data['item_name'],
        "product_type": product_type,
        "buyer_name": data['buyer_name'],
        "buyer_surname": data['buyer_surname'],
        "buyer_email": data['buyer_email'],
        "buyer_account_age": buyer_account_age,
        "buyer_id_nr": 0,
        "buyer_phone": data['buyer_phone'],
        "billing_address": data['billing_address'],
        "billing_city": data['city'],
        "billing_country": "TR",
        "billing_postcode": "",
        "shipping_address": data['billing_address'],
        "shipping_city": data['city'],
        "shipping_country": "TR",
        "shipping_postcode": "",
        "total_order_value": data['ucret'],
        "currency": currency,
        "platform": 0,
        "is_in_frame": 1,
        "current_language": 0,
        "modul_version": modul_version,
        "random_nr": random_nr
    }

    sign_data = f"{random_nr}{args['platform_order_id']}{args['total_order_value']}{args['currency']}"
    signature = base64.b64encode(
        hmac.new(api_secret.encode(), sign_data.encode(), digestmod='sha256').digest()
    ).decode()

    args['signature'] = signature

    input_fields = "".join(
        [f"<input type='hidden' name='{k}' value='{v}'/>" for k, v in args.items()]
    )

    return f"""
    <html><head><meta charset='UTF-8'></head>
    <body>
    <form action='https://www.shopier.com/ShowProduct/api_pay4.php' method='post' id='shopier_form'>
    {input_fields}
    </form>
    <script>document.getElementById('shopier_form').submit();</script>
    </body></html>
    """

@csrf_exempt
def shopier_payment_post(request):
    if request.method == "POST":
        data = {
            "apikey": settings.SHOPIER_API_KEY,
            "apisecret": settings.SHOPIER_API_SECRET,
            "item_name": request.POST.get("package_name"),
            "order_id": str(random.randint(1000000, 9999999)),
            "buyer_name": request.POST.get("name"),
            "buyer_surname": request.POST.get("surname"),
            "buyer_email": request.POST.get("email"),
            "buyer_phone": request.POST.get("phone"),
            "city": request.POST.get("city"),
            "billing_address": request.POST.get("address"),
            "ucret": request.POST.get("price")
        }

        html = generate_shopier_form(data)
        return HttpResponse(html)

    return HttpResponse("Sadece POST destekleniyor.", status=405)

@csrf_exempt
def shopier_callback(request):
    if request.method == "POST":
        try:
            # Shopier POST verilerini alır
            platform_order_id = request.POST.get("platform_order_id")
            status = request.POST.get("status")  # 1: başarılı, 0: başarısız
            signature = request.POST.get("signature")

            # İmza doğrulama için gerekli alanlar
            random_nr = request.POST.get("random_nr")
            total_order_value = request.POST.get("total_order_value")
            currency = request.POST.get("currency")

            sign_data = f"{random_nr}{platform_order_id}{total_order_value}{currency}"
            expected_signature = base64.b64encode(
                hmac.new(
                    settings.SHOPIER_API_SECRET.encode(),
                    sign_data.encode(),
                    digestmod='sha256'
                ).digest()
            ).decode()

            if signature != expected_signature:
                return HttpResponse("Geçersiz imza", status=400)

            # Burada işlem başarılıysa veri tabanına kaydedebilir ya da başka işlem yapabilirsin
            if status == "1":
                # ödeme başarılı
                print(f"Ödeme başarılı: Sipariş No: {platform_order_id}")
            else:
                print(f"Ödeme başarısız: Sipariş No: {platform_order_id}")

            return HttpResponse("OK")

        except Exception as e:
            return HttpResponse(f"Hata: {str(e)}", status=500)


    return HttpResponse("Sadece POST destekleniyor", status=405)
