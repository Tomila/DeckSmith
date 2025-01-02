import os
import secrets
import stripe
from flask import Flask, render_template, url_for, request, redirect, flash, session, jsonify
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Initialize Flask app
main = Flask(__name__)

# Generate and set a secure secret key
main.secret_key = secrets.token_hex(16)

# Stripe API keys
# Secret Key
stripe.api_key = "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"
STRIPE_PUBLIC_KEY = "pk_live_8QntnuNdOpEeAJOI1GGXIBCo"

# SQLAlchemy setup
DATABASE_URL = "sqlite:///decksmith.db"  # Use SQLite; update for production
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Customer model
class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zip_code = Column(String, nullable=False)
    country = Column(String, nullable=False)
    total_price = Column(Float, nullable=False)

    def __repr__(self):
        return f"<Customer(id={self.id}, name={self.name}, email={self.email}, phone={self.phone})>"

# Create tables
Base.metadata.create_all(engine)

# Session maker
Session = sessionmaker(bind=engine)
db_session = Session()

# Dummy data for catalog
product_catalog = [
    {"id": 1, "name": "Hugo Boss Bottled EDT 50ml", "price": 9999, "image": "hugo_boss_bottled_50ml.jpg", "sale_price": 9999, "description": "A timeless, elegant fragrance for men with fresh and woody notes."},
    {"id": 2, "name": "Hugo Boss Bottled Infinite EDP 100ml", "price": 9999, "image": "hugo_boss_infinite_edp_100ml.jpg", "sale_price": 9999, "description": "A vibrant and invigorating scent with citrus and spicy undertones."},
    {"id": 3, "name": "Armani Acqua di Gio EDP 125ml", "price": 9999, "image": "armani_acqua_di_gio_125ml.jpg", "sale_price": 9999, "description": "A fresh aquatic fragrance with a mix of marine and earthy tones."},
    {"id": 4, "name": "Hugo Boss Bottled EDP 200ml", "price": 999, "image": "hugo_boss_bottled_50ml.jpg", "sale_price": 9999, "description": "An intense and sophisticated version of the classic Bottled fragrance."},
    {"id": 5, "name": "Montblanc_legend_EDT_50ml", "price": 9999, "image": "montblanc_legend_EDT_50ml.jpg", "sale_price": 9999, "description": "A daring and adventurous scent with woody and leather notes."},
    {"id": 6, "name": "Giorgio Armani EDT 30ml", "price": 9999, "image": "armani_acqua_di_gio_125ml.jpg", "sale_price": 9999, "description": "A classic fragrance with an elegant balance of citrus and spices."},
    {"id": 7, "name": "1 Million Paco Rabanne EDT 100ml", "price": 9999, "image": "paco_rabanne_1million_100ml.jpg", "sale_price": 9999, "description": "A bold and luxurious scent with warm and spicy notes."},
    {"id": 8, "name": "Burberry EDT 50ml", "price": 9999, "image": "Burberry_EDT_100ml.png", "sale_price": 9999, "description": "A classic and sophisticated fragrance with floral and woody undertones."},
    {"id": 9, "name": "Hugo Boss The Scent EDT 100ml", "price": 9999, "image": "hugo_boss_thescent.jpg", "sale_price": 9999, "description": "An irresistible scent with spicy, fruity, and leathery accords."},
    {"id": 10, "name": "Giorgio Armani Acqua di Gio EDP 200ml", "price": 9999, "image": "armani_acqua_di_gio_125ml.jpg", "sale_price": 9999, "description": "A refreshing and masculine fragrance inspired by the Mediterranean."},
    {"id": 11, "name": "Burberry EDT 100ml", "price": 9999, "image": "Burberry_EDT_100ml.png", "sale_price": 9999, "description": "A smaller-sized classic Burberry fragrance, perfect for everyday wear."},
    {"id": 12, "name": "Kenzo L'Eau EDT 30ml", "price": 9999, "image": "kenzo_pour_homme_edp2.jpg", "sale_price": 9999, "description": "A light and aquatic fragrance with fresh and floral notes."},
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

@main.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        # Capture customer details from form
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        zip_code = request.form['zip']
        country = request.form['country']

        # Calculate total price
        cart = session.get('cart', [])
        total_price = sum(item['price'] * item['quantity'] for item in cart)

        # Save customer to the database
        new_customer = Customer(
            name=name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            country=country,
            total_price=total_price
        )
        db_session.add(new_customer)
        db_session.commit()

        flash("Customer details saved! Proceeding to payment...", "success")
        return redirect(url_for('create_checkout_session'))

    # Render checkout page
    cart = session.get('cart', [])
    total_price = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('checkout.html', cart=cart, total_price=total_price, STRIPE_PUBLIC_KEY=STRIPE_PUBLIC_KEY)

@main.route('/create_checkout_session', methods=['POST'])
def create_checkout_session():
    try:
        cart = session.get('cart', [])
        if not cart:
            raise Exception('No items in cart')

        line_items = [
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': item['name']},
                    'unit_amount': int(item['price'] * 100),
                },
                'quantity': item['quantity'],
            } for item in cart
        ]

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=f'https://www.decksmith.eu/success',
            cancel_url=f'https://www.decksmith.eu/cancel',
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











