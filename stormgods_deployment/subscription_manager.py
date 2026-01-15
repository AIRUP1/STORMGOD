#!/usr/bin/env python3
"""
StormBuster Subscription Management
Stripe payment processing and subscription tiers
"""

import stripe
import os
from datetime import datetime, timedelta
from flask   `  import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'stormbuster-secret-key-2025')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///stormbuster.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_your_stripe_secret_key')

# Subscription Plans
SUBSCRIPTION_PLANS = {
    'starter': {
        'name': 'Starter',
        'price': 29.99,
        'price_id': 'price_starter_monthly',
        'features': [
            'Up to 1,000 leads per month',
            'Basic storm data access',
            'Email support',
            'Standard lead scoring'
        ],
        'limits': {
            'monthly_leads': 1000,
            'api_calls': 5000,
            'export_downloads': 10
        }
    },
    'professional': {
        'name': 'Professional',
        'price': 79.99,
        'price_id': 'price_professional_monthly',
        'features': [
            'Up to 10,000 leads per month',
            'Advanced storm data access',
            'Priority support',
            'Enhanced lead scoring',
            'API access',
            'Custom reports'
        ],
        'limits': {
            'monthly_leads': 10000,
            'api_calls': 50000,
            'export_downloads': 100
        }
    },
    'enterprise': {
        'name': 'Enterprise',
        'price': 199.99,
        'price_id': 'price_enterprise_monthly',
        'features': [
            'Unlimited leads',
            'Real-time storm data',
            '24/7 phone support',
            'AI-powered lead scoring',
            'Full API access',
            'Custom integrations',
            'White-label options'
        ],
        'limits': {
            'monthly_leads': -1,  # Unlimited
            'api_calls': -1,      # Unlimited
            'export_downloads': -1  # Unlimited
        }
    },
    # AI Chat Plans
    'ai_free': {
        'name': 'Free Basic',
        'price': 0.00,
        'price_id': 'price_ai_free',
        'features': [
            'ChatGPT-3.5 Access',
            '100 AI Messages/Month',
            'Basic Storm Analysis',
            'Email Support',
            'Standard Response Time',
            'Basic Lead Generation'
        ],
        'limits': {
            'ai_messages': 100,
            'ai_models': ['gpt-3.5-turbo'],
            'custom_prompts': False,
            'api_access': False
        }
    },
    'ai_basic': {
        'name': 'Basic AI',
        'price': 40.00,
        'price_id': 'price_ai_basic_monthly',
        'features': [
            'ChatGPT-3.5 Access',
            '1,000 AI Messages/Month',
            'Basic Storm Analysis',
            'Email Support',
            'Standard Response Time',
            'Enhanced Lead Generation'
        ],
        'limits': {
            'ai_messages': 1000,
            'ai_models': ['gpt-3.5-turbo'],
            'custom_prompts': False,
            'api_access': False
        }
    },
    'ai_professional': {
        'name': 'Professional AI',
        'price': 70.00,
        'price_id': 'price_ai_professional_monthly',
        'features': [
            'ChatGPT-4 Access',
            'Claude-3 Access',
            '5,000 AI Messages/Month',
            'Advanced Storm Analysis',
            'Lead Scoring AI',
            'Priority Support',
            'Custom Prompts',
            'API Access'
        ],
        'limits': {
            'ai_messages': 5000,
            'ai_models': ['gpt-4', 'claude-3'],
            'custom_prompts': True,
            'api_access': True
        }
    },
    'ai_unlimited': {
        'name': 'Unlimited Access',
        'price': 100.00,
        'price_id': 'price_ai_unlimited_monthly',
        'features': [
            'Unlimited AI Messages',
            'All Premium Models',
            'GPT-4 Turbo',
            'Claude-3 Opus',
            'Gemini Pro',
            'AI-Powered Reports',
            'Custom AI Training',
            '24/7 Support',
            'White-label AI',
            'Dedicated Support'
        ],
        'limits': {
            'ai_messages': -1,  # Unlimited
            'ai_models': ['gpt-4-turbo', 'claude-3-opus', 'gemini-pro'],
            'custom_prompts': True,
            'api_access': True,
            'white_label': True
        }
    }
}

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    company = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Subscription relationship
    subscription = db.relationship('Subscription', backref='user', uselist=False)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan = db.Column(db.String(50), nullable=False)
    stripe_subscription_id = db.Column(db.String(100), unique=True)
    stripe_customer_id = db.Column(db.String(100))
    status = db.Column(db.String(20), default='active')  # active, canceled, past_due
    current_period_start = db.Column(db.DateTime)
    current_period_end = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Usage tracking
    monthly_leads_used = db.Column(db.Integer, default=0)
    api_calls_used = db.Column(db.Integer, default=0)
    export_downloads_used = db.Column(db.Integer, default=0)
    last_reset = db.Column(db.DateTime, default=datetime.utcnow)

class PaymentHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stripe_payment_intent_id = db.Column(db.String(100), unique=True)
    amount = db.Column(db.Integer)  # Amount in cents
    currency = db.Column(db.String(3), default='usd')
    status = db.Column(db.String(20))  # succeeded, failed, pending
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    """Home page with subscription plans"""
    return render_template('subscription_plans.html', plans=SUBSCRIPTION_PLANS)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        data = request.json
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        user = User(
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            company=data.get('company', ''),
            phone=data.get('phone', '')
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Log user in
        login_user(user)
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user_id': user.id
        })
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        data = request.json
        user = User.query.filter_by(email=data['email']).first()
        
        if user and check_password_hash(user.password_hash, data['password']):
            login_user(user)
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user_id': user.id
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    subscription = current_user.subscription
    plan_info = SUBSCRIPTION_PLANS.get(subscription.plan, {}) if subscription else {}
    
    return render_template('dashboard.html', 
                         user=current_user, 
                         subscription=subscription,
                         plan_info=plan_info)

@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    """Create Stripe checkout session"""
    try:
        data = request.json
        plan_id = data['plan_id']
        
        if plan_id not in SUBSCRIPTION_PLANS:
            return jsonify({'error': 'Invalid plan'}), 400
        
        plan = SUBSCRIPTION_PLANS[plan_id]
        
        # Create or get Stripe customer
        if current_user.subscription and current_user.subscription.stripe_customer_id:
            customer_id = current_user.subscription.stripe_customer_id
        else:
            customer = stripe.Customer.create(
                email=current_user.email,
                name=f"{current_user.first_name} {current_user.last_name}",
                metadata={
                    'user_id': current_user.id,
                    'company': current_user.company or ''
                }
            )
            customer_id = customer.id
        
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': plan['price_id'],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.url_root + 'success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.url_root + 'cancel',
            metadata={
                'user_id': current_user.id,
                'plan': plan_id
            }
        )
        
        return jsonify({'checkout_url': checkout_session.url})
        
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'An error occurred'}), 500

@app.route('/success')
@login_required
def success():
    """Payment success page"""
    session_id = request.args.get('session_id')
    
    if session_id:
        try:
            # Retrieve the checkout session
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status == 'paid':
                # Create or update subscription
                subscription = Subscription.query.filter_by(user_id=current_user.id).first()
                
                if not subscription:
                    subscription = Subscription(user_id=current_user.id)
                    db.session.add(subscription)
                
                # Update subscription details
                subscription.plan = session.metadata.get('plan')
                subscription.stripe_subscription_id = session.subscription
                subscription.stripe_customer_id = session.customer
                subscription.status = 'active'
                subscription.current_period_start = datetime.fromtimestamp(session.subscription_details.current_period_start)
                subscription.current_period_end = datetime.fromtimestamp(session.subscription_details.current_period_end)
                
                db.session.commit()
                
                flash('Subscription activated successfully!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Payment not completed', 'error')
                return redirect(url_for('index'))
                
        except stripe.error.StripeError as e:
            flash(f'Error retrieving payment: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    return redirect(url_for('dashboard'))

@app.route('/cancel')
def cancel():
    """Payment cancellation page"""
    flash('Payment was cancelled', 'info')
    return redirect(url_for('index'))

@app.route('/cancel-subscription', methods=['POST'])
@login_required
def cancel_subscription():
    """Cancel user subscription"""
    try:
        subscription = current_user.subscription
        
        if not subscription:
            return jsonify({'error': 'No active subscription'}), 400
        
        # Cancel subscription in Stripe
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True
        )
        
        # Update local subscription status
        subscription.status = 'canceled'
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Subscription will be canceled at the end of the current period'})
        
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'An error occurred'}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """Stripe webhook handler"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'invoice.payment_succeeded':
        # Handle successful payment
        invoice = event['data']['object']
        subscription_id = invoice['subscription']
        
        subscription = Subscription.query.filter_by(stripe_subscription_id=subscription_id).first()
        if subscription:
            subscription.status = 'active'
            db.session.commit()
    
    elif event['type'] == 'invoice.payment_failed':
        # Handle failed payment
        invoice = event['data']['object']
        subscription_id = invoice['subscription']
        
        subscription = Subscription.query.filter_by(stripe_subscription_id=subscription_id).first()
        if subscription:
            subscription.status = 'past_due'
            db.session.commit()
    
    elif event['type'] == 'customer.subscription.deleted':
        # Handle subscription cancellation
        subscription_data = event['data']['object']
        subscription_id = subscription_data['id']
        
        subscription = Subscription.query.filter_by(stripe_subscription_id=subscription_id).first()
        if subscription:
            subscription.status = 'canceled'
            db.session.commit()
    
    return jsonify({'status': 'success'})

@app.route('/api/usage')
@login_required
def get_usage():
    """Get current usage statistics"""
    subscription = current_user.subscription
    
    if not subscription:
        return jsonify({'error': 'No active subscription'}), 400
    
    plan_info = SUBSCRIPTION_PLANS[subscription.plan]
    
    # Reset monthly counters if needed
    if subscription.last_reset < datetime.utcnow().replace(day=1):
        subscription.monthly_leads_used = 0
        subscription.api_calls_used = 0
        subscription.export_downloads_used = 0
        subscription.last_reset = datetime.utcnow()
        db.session.commit()
    
    usage = {
        'leads': {
            'used': subscription.monthly_leads_used,
            'limit': plan_info['limits']['monthly_leads'],
            'unlimited': plan_info['limits']['monthly_leads'] == -1
        },
        'api_calls': {
            'used': subscription.api_calls_used,
            'limit': plan_info['limits']['api_calls'],
            'unlimited': plan_info['limits']['api_calls'] == -1
        },
        'exports': {
            'used': subscription.export_downloads_used,
            'limit': plan_info['limits']['export_downloads'],
            'unlimited': plan_info['limits']['export_downloads'] == -1
        }
    }
    
    return jsonify(usage)

def check_subscription_limit(user, limit_type):
    """Check if user has exceeded subscription limits"""
    subscription = user.subscription
    
    if not subscription:
        return False, 'No active subscription'
    
    plan_info = SUBSCRIPTION_PLANS[subscription.plan]
    limits = plan_info['limits']
    
    if limits[limit_type] == -1:  # Unlimited
        return True, None
    
    current_usage = getattr(subscription, f'{limit_type}_used', 0)
    
    if current_usage >= limits[limit_type]:
        return False, f'{limit_type} limit exceeded'
    
    return True, None

def increment_usage(user, limit_type):
    """Increment usage counter for user"""
    subscription = user.subscription
    
    if subscription:
        current_usage = getattr(subscription, f'{limit_type}_used', 0)
        setattr(subscription, f'{limit_type}_used', current_usage + 1)
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    print("🚀 Starting StormBuster Subscription System")
    print("=" * 50)
    print("💳 Stripe Integration: Enabled")
    print("🔐 User Authentication: Enabled")
    print("📊 Subscription Management: Enabled")
    print("🌐 Web Interface: http://localhost:5000")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
