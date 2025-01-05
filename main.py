import os
import secrets
import stripe
from flask import Flask, render_template, url_for, request, redirect, flash, session, jsonify
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

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
    {"id": 1, "name": "Hugo Boss Bottled EDT 50ml", "price": 44.99, "image": "hugo_boss_bottled_50ml.jpg", "sale_price": 44.99, "description": "A timeless, elegant fragrance for men with fresh and woody notes."},
    {"id": 2, "name": "Versace Eros EDT 100 ml", "price": 67.99, "image": "versace_eros_EDT_100ml.jpg", "sale_price": 67.99, "description": "A vibrant and invigorating scent with citrus and spicy undertones."},
    {"id": 3, "name": "Acqua di Gio EDP 50ml", "price": 67, "image": "armani_acqua_di_gio_125ml.jpg", "sale_price": 67, "description": "A fresh aquatic fragrance with a mix of marine and earthy tones."},
    {"id": 4, "name": "Hugo Boss Bottled EDT 100ml", "price": 66.99, "image": "hugo_boss_bottled_50ml.jpg", "sale_price": 66.99, "description": "A timeless, elegant fragrance for men with fresh and woody notes."},
    {"id": 5, "name": "Montblanc_legend_EDT_30ml", "price": 32.1, "image": "montblanc_legend_EDT_50ml.jpg", "sale_price": 32.1, "description": "A daring and adventurous scent with woody and leather notes."},
    {"id": 6, "name": "Acqua di Gio EDP 75ml", "price": 80.19, "image": "armani_acqua_di_gio_125ml.jpg", "sale_price": 80.19, "description": "A fresh aquatic fragrance with a mix of marine and earthy tones."},
    {"id": 7, "name": "1 Million Paco Rabanne EDT 100ml", "price": 74.99, "image": "paco_rabanne_1million_100ml.jpg", "sale_price": 74.99, "description": "A bold and luxurious scent with warm and spicy notes."},
    {"id": 8, "name": "Burberry EDT 50ml", "price": 39.69, "image": "Burberry_EDT_100ml.png", "sale_price": 39.69, "description": "A classic and sophisticated fragrance with floral and woody undertones."},
    {"id": 9, "name": "Hugo Boss The Scent EDT 100ml", "price": 64.99, "image": "hugo_boss_thescent.jpg", "sale_price": 64.99, "description": "An irresistible scent with spicy, fruity, and leathery accords."},
    {"id": 10, "name": "Giorgio Armani Acqua di Gio EDP 200ml", "price": 100.15, "image": "armani_acqua_di_gio_125ml.jpg", "sale_price": 100.15, "description": "A fresh aquatic fragrance with a mix of marine and earthy tones."},
    {"id": 11, "name": "Burberry EDT 100ml", "price": 44.33, "image": "Burberry_EDT_100ml.png", "sale_price": 44.33, "description": "A smaller-sized classic Burberry fragrance, perfect for everyday wear."},
    {"id": 12, "name": "Kenzo L'Eau EDT 100ml", "price": 58.74, "image": "kenzo_pour_homme_edp2.jpg", "sale_price": 58.74, "description": "A light and aquatic fragrance with fresh and floral notes."},
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
        
        try:
            # Get form data
            data = request.form.to_dict()

            # Validate required fields
            required_fields = ['name', 'email', 'phone', 'address', 'city', 'state', 'zip', 'country']
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                flash(f'Missing fields: {", ".join(missing_fields)}', 'danger')
                return redirect(url_for('checkout'))

            # Retrieve cart from session
            cart = session.get('cart', [])
            if not cart:
                flash('Cart is empty. Please add items to proceed.', 'danger')
                return redirect(url_for('cart'))

            # Calculate total price
            total_price = sum(item['price'] * item['quantity'] for item in cart)

            # Save or update customer details
            existing_customer = db_session.query(Customer).filter_by(email=data['email']).first()
            if existing_customer:
                # Update details
                for field in ['name', 'phone', 'address', 'city', 'state', 'zip', 'country']:
                    setattr(existing_customer, field, data[field])
                existing_customer.total_price = total_price
            else:
                # Create new customer
                new_customer = Customer(
                    name=data['name'],
                    email=data['email'],
                    phone=data['phone'],
                    address=data['address'],
                    city=data['city'],
                    state=data['state'],
                    zip_code=data['zip'],
                    country=data['country'],
                    total_price=total_price

                )
                db_session.add(new_customer)

            db_session.commit()

            # Create Stripe Checkout session
            line_items = [
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': item['name'],
                        },
                        'unit_amount': int(item['price'] * 100),  # Convert to cents
                    },
                    'quantity': item['quantity'],
                }
                for item in cart
            ]

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=url_for('success', _external=True),
                cancel_url=url_for('cancel', _external=True),
            )

            # Redirect to Stripe Checkout
            return jsonify({'sessionId': checkout_session.id})

        except Exception as e:
            db_session.rollback()
            flash(f'An error occurred: {e}', 'danger')
            return redirect(url_for('checkout'))

    # Render checkout page
    cart = session.get('cart', [])
    total_price = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('checkout.html', cart=cart, total_price=total_price, STRIPE_PUBLIC_KEY=STRIPE_PUBLIC_KEY)


@main.route('/create_checkout_session', methods=['POST'])
def create_checkout_session():
    try:
        cart = session.get('cart', [])
        if not cart:
            return jsonify({'error': 'No items in cart'}), 400

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

        if not line_items:
            return jsonify({'error': 'No valid items to process in cart'}), 400

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url='https://www.decksmith.eu/success',
            cancel_url='https://www.decksmith.eu/cancel',
            customer_email=request.form.get('email'),  # Use form email if provided
            shipping_address_collection={
                'allowed_countries': ['US', 'CA', 'GB', 'AU', 'FR', 'FI'],  # Add relevant countries
            },
            billing_address_collection='required',  # Force billing address collection
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












