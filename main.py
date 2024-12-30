import os
import secrets
import stripe
from flask import Flask, render_template, url_for, request, redirect, flash, session, jsonify
from datetime import datetime, timedelta

# Initialize Flask app
main = Flask(__name__)

# Generate and set a secure secret key
main.secret_key = secrets.token_hex(16)

# Stripe API keys
# Secret Key
stripe.api_key = "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"
STRIPE_PUBLIC_KEY = "pk_live_8QntnuNdOpEeAJOI1GGXIBCo"

# Dummy data for catalog
product_catalog = [
    {"id": 1, "name": "DJI Mini 3 Pro", "price": 749, "image": "dji_mini_3_pro.jpg", "sale_price": 699},
    {"id": 2, "name": "DJI Air 2S", "price": 999, "image": "dji_air_2s.jpg", "sale_price": 899},
    {"id": 3, "name": "Autel Robotics EVO II", "price": 1299, "image": "autel_evo_ii.jpg", "sale_price": 1199},
    {"id": 4, "name": "Parrot Anafi USA", "price": 7000, "image": "parrot_anafi_usa.jpg", "sale_price": 6800},
    {"id": 5, "name": "Ruko F11 Pro", "price": 250, "image": "ruko_f11_pro.jpg", "sale_price": 199},
    {"id": 6, "name": "DJI Mavic Mini", "price": 399, "image": "dji_mavic_mini.jpg", "sale_price": 359},
    {"id": 7, "name": "Hubsan Zino Pro", "price": 499, "image": "hubsan_zino_pro.jpg", "sale_price": 449},
    {"id": 8, "name": "BetaFPV Beta95X V3", "price": 150, "image": "betafpv_beta95x_v3.jpg", "sale_price": 130},
    {"id": 9, "name": "DJI FPV Drone", "price": 1299, "image": "dji_fpv_drone.jpg", "sale_price": 1199},
    {"id": 10, "name": "Sky Viper Streaming Drone", "price": 100, "image": "sky_viper_streaming.jpg", "sale_price": 80},
    {"id": 11, "name": "Mavic Air 2 Fly More Combo", "price": 998, "image": "mavic_air_2_combo.jpg", "sale_price": 899},
    {"id": 12, "name": "GoPro Karma Drone", "price": 799, "image": "gopro_karma.jpg", "sale_price": 699},
    {"id": 13, "name": "FPV Racing Drone Kit", "price": 200, "image": "fpv_racing_drone_kit.jpg", "sale_price": 170},
    {"id": 14, "name": "DJI Phantom 4 Pro V2.0", "price": 1799, "image": "dji_phantom_4_pro.jpg", "sale_price": 1599},
    {"id": 15, "name": "Fimi X8 SE", "price": 450, "image": "fimi_x8_se.jpg", "sale_price": 399},
    {"id": 16, "name": "Holy Stone HS720E", "price": 320, "image": "holy_stone_hs720e.jpg", "sale_price": 280},
    {"id": 17, "name": "Autel Robotics EVO Nano", "price": 799, "image": "autel_evo_nano.jpg", "sale_price": 749},
    {"id": 18, "name": "SwellPro SplashDrone 4", "price": 1300, "image": "swellpro_splashdrone4.jpg", "sale_price": 1200},
    {"id": 19, "name": "Tello Drone by DJI", "price": 99, "image": "tello_drone.jpg", "sale_price": 79},
    {"id": 20, "name": "Xiaomi Mi Drone 4K", "price": 450, "image": "xiaomi_mi_drone.jpg", "sale_price": 399},
]



# Flash sale configuration
flash_sale_duration = timedelta(hours=4)
flash_sale_end = datetime.now() + flash_sale_duration

# News items
news_items = [
    {"title": "New Winter Collection Released!", "date": "2024-09-01"},
    {"title": "Free Shipping for Orders Over $100", "date": "2024-09-03"},
]

@main.after_request
def add_ngrok_header(response):
    # Add the ngrok-skip-browser-warning header to all responses
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

@main.route('/')
def index():
    return render_template('index.html', products=product_catalog, flash_sale_end=flash_sale_end, news_items=news_items)

@main.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Add your authentication logic here (e.g., check username and password)
        if username == 'admin' and password == 'password':  # Dummy check
            flash('Successfully signed in!', 'success')
            return redirect(url_for('index'))  # Redirect to the index or another page after successful sign-in
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('signin.html')

@main.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    total_price = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@main.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = next((item for item in product_catalog if item["id"] == product_id), None)
    if product:
        cart = session.get('cart', [])
        # Check if the product already exists in the cart, and increment quantity if so
        for item in cart:
            if item['id'] == product['id']:
                item['quantity'] += 1
                break
        else:
            product['quantity'] = 1
            cart.append(product)
        session['cart'] = cart
        flash(f'{product["name"]} added to your cart.')

    # Get updated cart count and total price for the AJAX response
    cart_count = len(session.get('cart', []))
    total_price = sum(item['price'] * item['quantity'] for item in cart)

    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'cart_count': cart_count, 'total_price': total_price})

    return redirect(url_for('cart'))  # Redirect to the cart page for non-AJAX requests

@main.route('/remove_from_cart/<int:product_id>', methods=['GET'])
def remove_from_cart(product_id):
    cart = session.get('cart', [])
    cart = [item for item in cart if item['id'] != product_id]
    session['cart'] = cart
    flash('Item removed from cart.')
    return redirect(url_for('cart'))

@main.route('/checkout')
def checkout():
    cart = session.get('cart', [])
    total_price = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('checkout.html', cart=cart, total_price=total_price, STRIPE_PUBLIC_KEY=STRIPE_PUBLIC_KEY)

@main.route('/create_checkout_session', methods=['POST'])
def create_checkout_session():
    try:
        cart = session.get('cart', [])
        if not cart:
            raise Exception('No items in cart')

        line_items = []
        for item in cart:
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': item['name']},
                    'unit_amount': int(item['price'] * 100),
                },
                'quantity': item['quantity'],
            })

        # Rename session to checkout_session to avoid conflict
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            #success_url=url_for('success', _external=True),
            #cancel_url=url_for('cancel', _external=True),
            success_url=f'https://322a-2001-14bb-675-4f13-2590-2557-6f3a-e018.ngrok-free.app/success',  # Update with ngrok HTTPS URL
            cancel_url=f'https://322a-2001-14bb-675-4f13-2590-2557-6f3a-e018.ngrok-free.app/cancel',    # Update with ngrok HTTPS URL
        )
        return jsonify({'sessionId': checkout_session.id})
    except Exception as e:
        print(f"Error creating checkout session: {e}")
        return jsonify({'error': str(e)}), 400

@main.route('/success')
def success():
    return render_template('success.html')

@main.route('/cancel')
def cancel():
    return render_template('cancel.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    main.run(host="0.0.0.0", port=port)











