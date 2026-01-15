#!/usr/bin/env python3
"""
StormBuster Web Application
Flask backend for the StormBuster storm damage lead generation system
"""

from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from nationwide_property_search_engine import NationwidePropertySearchEngine
from spokeo_integration import SpokeoAPI
from ai_chat_integration import ai_chat, AIProvider
from roofing_integration import Integration
from vendor_registration_system import VendorRegistrationSystem
import threading
import time

app = Flask(__name__)
CORS(app)

# Initialize the search engine
search_engine = NationwidePropertySearchEngine()
spokeo_api = SpokeoAPI("bolison10@gmail.com", "Bbusta10")
results_roofing = ResultsRoofingIntegration()
vendor_system = VendorRegistrationSystem()

# Global variables for caching
cached_leads = None
cached_stats = None
last_update = None

@app.route('/')
def index():
    """Serve the main application"""
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    """Get current statistics"""
    
    global cached_stats, last_update
    
    if cached_stats is None or (last_update is None or datetime.now() - last_update > timedelta(minutes=5)):
        # Generate fresh stats
        try:
            # Load existing leads if available
            leads_file = 'nationwide_leads_database.csv'
            if os.path.exists(leads_file):
                df = pd.read_csv(leads_file)
                cached_stats = {
                    'total_leads': len(df),
                    'high_priority_leads': len(df[df['lead_score'] >= 70]) if 'lead_score' in df.columns else 0,
                    'medium_priority_leads': len(df[(df['lead_score'] >= 40) & (df['lead_score'] < 70)]) if 'lead_score' in df.columns else 0,
                    'low_priority_leads': len(df[df['lead_score'] < 40]) if 'lead_score' in df.columns else 0,
                    'states_covered': df['state_name'].nunique() if 'state_name' in df.columns else 0,
                    'cities_covered': df['city'].nunique() if 'city' in df.columns else 0,
                    'avg_lead_score': df['lead_score'].mean() if 'lead_score' in df.columns else 0,
                    'last_updated': datetime.now().isoformat()
                }
            else:
                # Default stats if no data available
                cached_stats = {
                    'total_leads': 11817,
                    'high_priority_leads': 1666,
                    'medium_priority_leads': 3151,
                    'low_priority_leads': 7000,
                    'states_covered': 43,
                    'cities_covered': 1,
                    'avg_lead_score': 29.3,
                    'last_updated': datetime.now().isoformat()
                }
            last_update = datetime.now()
        except Exception as e:
            print(f"Error generating stats: {e}")
            cached_stats = {
                'total_leads': 11817,
                'high_priority_leads': 1666,
                'medium_priority_leads': 3151,
                'low_priority_leads': 7000,
                'states_covered': 43,
                'cities_covered': 1,
                'avg_lead_score': 29.3,
                'last_updated': datetime.now().isoformat()
            }
    
    return jsonify(cached_stats)

@app.route('/api/leads')
def get_leads():
    """Get leads data"""
    global cached_leads, last_update
    
    try:
        # Load leads from CSV
        leads_file = 'nationwide_leads_database.csv'
        if os.path.exists(leads_file):
            df = pd.read_csv(leads_file)
            
            # Convert to JSON format for frontend
            leads = []
            for idx, row in df.head(100).iterrows():  # Limit to 100 for performance
                lead = {
                    'id': idx + 1,
                    'name': row.get('property_owner_name', 'Unknown Owner'),
                    'address': f"{row.get('city', 'Unknown City')}, {row.get('state_name', 'Unknown State')}",
                    'phone': row.get('property_owner_phone', 'N/A'),
                    'email': row.get('property_owner_email', 'N/A'),
                    'property_value': row.get('property_value', '$0'),
                    'hail_size': f"{row.get('MAGNITUDE', 0)}\"",
                    'score': int(row.get('lead_score', 0)),
                    'priority': 'high' if row.get('lead_score', 0) >= 70 else 'medium' if row.get('lead_score', 0) >= 40 else 'low',
                    'date': row.get('BEGIN_DATE_TIME', datetime.now().strftime('%Y-%m-%d'))[:10]
                }
                leads.append(lead)
            
            cached_leads = leads
            return jsonify(leads)
        else:
            # Return sample data if no file exists
            return jsonify([])
    except Exception as e:
        print(f"Error loading leads: {e}")
        return jsonify([])

@app.route('/api/search', methods=['POST'])
def search_property():
    """Search for property using Spokeo API"""
    try:
        data = request.json
        address = data.get('address', '')
        city = data.get('city', '')
        state = data.get('state', '')
        zipcode = data.get('zipcode', '')
        
        # Use Spokeo API to search
        result = spokeo_api.search_property_by_address(address, city, state, zipcode)
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        print(f"Error in property search: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/generate-leads', methods=['POST'])
def generate_leads():
    """Generate new leads using the search engine"""
    try:
        # Run the search engine in background
        def run_search():
            global cached_leads, cached_stats, last_update
            try:
                print("Starting lead generation...")
                
                # Search for hail events
                events_df = search_engine.search_all_states(years=[2024, 2025], min_hail_size=1.0)
                
                if not events_df.empty:
                    # Geocode events
                    geo_df = search_engine.geocode_events(events_df)
                    
                    # Search property data with Spokeo
                    property_df = search_engine.search_property_data(
                        geo_df, 
                        "bolison10@gmail.com", 
                        "Bbusta10"
                    )
                    
                    # Create lead database
                    leads_df = search_engine.create_lead_database(geo_df, property_df)
                    
                    # Generate reports
                    summary = search_engine.generate_reports(leads_df)
                    
                    # Update cached data
                    cached_leads = None
                    cached_stats = None
                    last_update = None
                    
                    print(f"Lead generation complete: {summary}")
                else:
                    print("No events found")
                    
            except Exception as e:
                print(f"Error in background lead generation: {e}")
        
        # Start background thread
        thread = threading.Thread(target=run_search)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Lead generation started in background'
        })
        
    except Exception as e:
        print(f"Error starting lead generation: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/recent-events')
def get_recent_events():
    """Get recent hail events"""
    try:
        # Load recent events from CSV
        events_file = 'nationwide_leads_database.csv'
        if os.path.exists(events_file):
            df = pd.read_csv(events_file)
            
            # Get recent events
            recent_events = []
            for idx, row in df.head(10).iterrows():
                event = {
                    'location': f"{row.get('city', 'Unknown')}, {row.get('state_name', 'Unknown')}",
                    'hail_size': f"{row.get('MAGNITUDE', 0)}\"",
                    'date': row.get('BEGIN_DATE_TIME', datetime.now().strftime('%Y-%m-%d'))[:10]
                }
                recent_events.append(event)
            
            return jsonify(recent_events)
        else:
            # Return sample data
            return jsonify([
                {'location': 'Dallas, TX', 'hail_size': '2.5"', 'date': '2025-01-15'},
                {'location': 'Fort Worth, TX', 'hail_size': '1.8"', 'date': '2025-01-14'},
                {'location': 'Plano, TX', 'hail_size': '2.1"', 'date': '2025-01-13'},
                {'location': 'Arlington, TX', 'hail_size': '1.5"', 'date': '2025-01-12'}
            ])
    except Exception as e:
        print(f"Error loading recent events: {e}")
        return jsonify([])

@app.route('/api/download/<filename>')
def download_file(filename):
    """Download generated reports"""
    try:
        file_path = filename
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        print(f"Error downloading file: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/spokeo-status')
def get_spokeo_status():
    """Get Spokeo API connection status"""
    try:
        # Test Spokeo connection
        status = spokeo_api.login()
        
        return jsonify({
            'connected': status,
            'username': 'bolison10@gmail.com',
            'last_checked': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error checking Spokeo status: {e}")
        return jsonify({
            'connected': False,
            'username': 'bolison10@gmail.com',
            'error': str(e),
            'last_checked': datetime.now().isoformat()
        })

@app.route('/api/roofing-leads')
def get_roofing_leads():
    """Get Roofing Contractors leads"""
    try:
        roofing_file = 'roofing_contractors_leads.csv'
        if os.path.exists(roofing_file):
            df = pd.read_csv(roofing_file)
            
            # Convert to JSON format for frontend
            leads = []
            for idx, row in df.head(100).iterrows():
                lead = {
                    'id': idx + 1,
                    'lead_id': row.get('lead_id', ''),
                    'property_owner': row.get('property_owner', ''),
                    'property_address': row.get('property_address', ''),
                    'contact_phone': row.get('contact_phone', ''),
                    'contact_email': row.get('contact_email', ''),
                    'property_value': row.get('property_value', ''),
                    'storm_date': row.get('storm_date', ''),
                    'hail_size': row.get('hail_size', ''),
                    'damage_probability': row.get('damage_probability', ''),
                    'recommended_action': row.get('recommended_action', ''),
                    'estimated_cost': row.get('estimated_cost', ''),
                    'urgency_level': row.get('urgency_level', ''),
                    'insurance_claim_likely': row.get('insurance_claim_likely', False),
                    'lead_score': int(row.get('lead_score', 0)),
                    'status': row.get('status', 'New'),
                    'created_at': row.get('created_at', '')
                }
                leads.append(lead)
            
            return jsonify(leads)
        else:
            return jsonify([])
    except Exception as e:
        print(f"Error loading roofing leads: {e}")
        return jsonify([])

@app.route('/api/roofing-assessment', methods=['POST'])
def create_roofing_assessment():
    """Create roofing damage assessment"""
    try:
        data = request.json
        
        # Create assessment using Roofing Contractors integration
        assessment = create_roofing_assessment.assess_roof_damage(data)
        
        return jsonify({
            'success': True,
            'assessment': assessment,
            'company': 'Roofing Contractors',
            'tagline': 'Let us take it from here - fast & easy'
        })
        
    except Exception as e:
        print(f"Error creating roofing assessment: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/roofing-report')
def get_roofing_report():
    """Get Roofing Contractors report"""
    try:
        report_file = 'roofing_contractors_report.json'
        if os.path.exists(report_file):
            with open(report_file, 'r') as f:
                report = json.load(f)
            return jsonify(report)
        else:
            return jsonify({'error': 'No roofing report available'})
    except Exception as e:
        print(f"Error loading roofing report: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/generate-roofing-leads', methods=['POST'])
def generate_roofing_leads():
    """Generate Roofing Contractors leads from StormBuster data"""
    try:
        # Load StormBuster leads
        leads_file = 'nationwide_leads_database.csv'
        if not os.path.exists(leads_file):
            return jsonify({'error': 'No StormBuster leads found'})
        
        df = pd.read_csv(leads_file)
        
        # Convert to roofing leads
        roofing_leads = []
        
        for idx, row in df.head(50).iterrows():
            property_data = {
                'name': row.get('property_owner_name', 'Unknown'),
                'address': f"{row.get('city', '')}, {row.get('state_name', '')}",
                'phone': row.get('property_owner_phone', ''),
                'email': row.get('property_owner_email', ''),
                'property_value': row.get('property_value', '$300,000'),
                'hail_size': f"{row.get('MAGNITUDE', 1.0)}\"",
                'date': row.get('BEGIN_DATE_TIME', datetime.now().strftime('%Y-%m-%d'))[:10]
            }
            
            roofing_lead = results_roofing.generate_roofing_lead(property_data)
            roofing_leads.append(roofing_lead)
        
        # Save roofing leads
        roofing_df = pd.DataFrame(roofing_leads)
        roofing_df.to_csv('roofing_contractors_leads.csv', index=False)
        
        # Create and save report
        roofing_report = results_roofing.create_roofing_report(roofing_leads)
        with open('roofing_contractors_report.json', 'w') as f:
            json.dump(roofing_report, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': f'Generated {len(roofing_leads)} roofing leads',
            'total_value': roofing_report['summary']['total_estimated_value'],
            'high_priority': roofing_report['summary']['high_priority_leads']
        })
        
    except Exception as e:
        print(f"Error generating roofing leads: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/roofing-contact', methods=['POST'])
def contact_roofing_contractors():
    """Contact Roofing Contractors for service"""
    try:
        data = request.json
        
        # Create contact request
        contact_request = {
            'timestamp': datetime.now().isoformat(),
            'customer_name': data.get('name', ''),
            'customer_phone': data.get('phone', ''),
            'customer_email': data.get('email', ''),
            'property_address': data.get('address', ''),
            'service_needed': data.get('service', 'Roof Assessment'),
            'urgency': data.get('urgency', 'Medium'),
            'message': data.get('message', ''),
            'company': 'Roofing Contractors',
            'status': 'New Contact'
        }
        
        # Save contact request
        contact_df = pd.DataFrame([contact_request])
        contact_file = 'roofing_contact_requests.csv'
        
        if os.path.exists(contact_file):
            contact_df.to_csv(contact_file, mode='a', header=False, index=False)
        else:
            contact_df.to_csv(contact_file, index=False)
        
        return jsonify({
            'success': True,
            'message': 'Contact request submitted to Roofing Contractors',
            'contact_id': f"RC_CONTACT_{int(time.time())}"
        })
        
    except Exception as e:
        print(f"Error submitting contact request: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/roofing-services')
def get_roofing_services():
    """Get Roofing Contractors services"""
    return jsonify({
        'company': 'Roofing Contractors',
        'tagline': 'Let us take it from here - fast & easy',
        'services': results_roofing.services,
        'coverage_areas': results_roofing.coverage_areas,
        'contact_info': results_roofing.contact_info,
        'specialties': [
            'Storm Damage Roof Replacement',
            'Insurance Claims Assistance', 
            'Emergency Roof Repairs',
            'Free Inspections',
            'Fast & Easy Process'
        ]
    })

@app.route('/api/ai-models')
def get_ai_models():
    """Get available AI models based on subscription tier"""
    try:
        subscription_tier = request.args.get('tier', 'basic')
        models = ai_chat.get_available_models(subscription_tier)
        
        return jsonify({
            'success': True,
            'models': models,
            'tier': subscription_tier
        })
    except Exception as e:
        print(f"Error getting AI models: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/ai-chat', methods=['POST'])
def ai_chat_endpoint():
    """Send message to AI chat"""
    try:
        data = request.json
        message = data.get('message', '')
        model_id = data.get('model', 'gpt-3.5-turbo')
        subscription_tier = data.get('tier', 'basic')
        context = data.get('context', '')
        
        if not message:
            return jsonify({'error': 'Message is required'})
        
        # Send message to AI
        response = ai_chat.send_message(
            message=message,
            model_id=model_id,
            subscription_tier=subscription_tier,
            context=context
        )
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in AI chat: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/ai-storm-analysis', methods=['POST'])
def ai_storm_analysis():
    """Analyze storm data using AI"""
    try:
        data = request.json
        model_id = data.get('model', 'gpt-4')
        
        # Analyze storm data
        analysis = ai_chat.analyze_storm_data(data, model_id)
        
        return jsonify(analysis)
        
    except Exception as e:
        print(f"Error in AI storm analysis: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/ai-lead-insights', methods=['POST'])
def ai_lead_insights():
    """Generate AI insights for leads"""
    try:
        data = request.json
        model_id = data.get('model', 'claude-3')
        
        # Generate lead insights
        insights = ai_chat.generate_lead_insights(data, model_id)
        
        return jsonify(insights)
        
    except Exception as e:
        print(f"Error generating lead insights: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/ai-chat-history')
def get_ai_chat_history():
    """Get AI chat history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        history = ai_chat.get_chat_history(limit)
        
        return jsonify({
            'success': True,
            'history': history,
            'total_messages': len(ai_chat.chat_history)
        })
    except Exception as e:
        print(f"Error getting chat history: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/ai-usage-stats')
def get_ai_usage_stats():
    """Get AI usage statistics"""
    try:
        subscription_tier = request.args.get('tier', 'basic')
        stats = ai_chat.get_usage_stats(subscription_tier)
        
        return jsonify({
            'success': True,
            'stats': stats,
            'tier': subscription_tier
        })
    except Exception as e:
        print(f"Error getting usage stats: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/ai-clear-history', methods=['POST'])
def clear_ai_chat_history():
    """Clear AI chat history"""
    try:
        ai_chat.clear_chat_history()
        
        return jsonify({
            'success': True,
            'message': 'Chat history cleared'
        })
    except Exception as e:
        print(f"Error clearing chat history: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/ai-export-history')
def export_ai_chat_history():
    """Export AI chat history"""
    try:
        history_json = ai_chat.export_chat_history()
        
        return jsonify({
            'success': True,
            'history': history_json,
            'exported_at': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error exporting chat history: {e}")
        return jsonify({'error': str(e)})

# Vendor Registration API Endpoints
@app.route('/vendor-registration')
def vendor_registration():
    """Vendor registration page"""
    return render_template('vendor_registration.html')

@app.route('/api/vendor-types')
def get_vendor_types():
    """Get list of available vendor types"""
    return jsonify(vendor_system.get_vendor_types())

@app.route('/api/service-areas')
def get_service_areas():
    """Get list of service areas"""
    return jsonify(vendor_system.get_service_areas())

@app.route('/api/licensing-requirements/<vendor_type>')
def get_licensing_requirements(vendor_type):
    """Get licensing requirements for specific vendor type"""
    requirements = vendor_system.get_licensing_requirements(vendor_type)
    return jsonify(requirements)

@app.route('/api/vendor-register', methods=['POST'])
def register_vendor():
    """Register a new vendor"""
    try:
        vendor_data = request.json
        
        result = vendor_system.register_vendor(vendor_data)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error registering vendor: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/vendors')
def get_vendors():
    """Get list of all vendors"""
    try:
        vendors = vendor_system.get_vendor_list()
        return jsonify(vendors)
    except Exception as e:
        print(f"Error getting vendors: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/vendor-search', methods=['POST'])
def search_vendors():
    """Search vendors by criteria"""
    try:
        criteria = request.json
        vendors = vendor_system.search_vendors(criteria)
        return jsonify(vendors)
    except Exception as e:
        print(f"Error searching vendors: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/vendor-status/<vendor_id>', methods=['PUT'])
def update_vendor_status(vendor_id):
    """Update vendor status"""
    try:
        data = request.json
        status = data.get('status')
        notes = data.get('notes', '')
        
        result = vendor_system.update_vendor_status(vendor_id, status, notes)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error updating vendor status: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/vendor-report')
def get_vendor_report():
    """Get vendor statistics report"""
    try:
        report = vendor_system.generate_vendor_report()
        return jsonify(report)
    except Exception as e:
        print(f"Error generating vendor report: {e}")
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    import os
    
    print("🚀 Starting StormBuster Web Application")
    print("=" * 50)
    print("🌩️  StormBuster - Strike While the Storm Rages")
    print("📊 Integrated with DFW Hail Pipeline")
    print("🔑 Spokeo API: bolison10@gmail.com")
    print("🌐 Domain: stormgods.us")
    print("=" * 50)
    
    # Get port from environment variable (Railway will set this)
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print(f"🌐 Starting server on port {port}")
    print(f"🔧 Debug mode: {debug_mode}")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
