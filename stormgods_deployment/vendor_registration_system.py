#!/usr/bin/env python3
"""
Vendor Registration System for StormBuster
Allows businesses to register as vendors for storm damage services
"""

import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Optional
import os

class VendorRegistrationSystem:
    def __init__(self):
        self.vendor_types = [
            "Roofing Contractors",
            "Construction Workers", 
            "General Contractors",
            "Insurance Adjusters",
            "Emergency Services",
            "Tree Removal Services",
            "Window Replacement",
            "Siding Contractors",
            "Gutter Services",
            "Fence Contractors",
            "Landscaping Services",
            "HVAC Services",
            "Electrical Services",
            "Plumbing Services",
            "Water Damage Restoration",
            "Mold Remediation",
            "Carpet Cleaning",
            "Painting Services",
            "Flooring Services",
            "Other"
        ]
        
        self.service_areas = [
            "Dallas-Fort Worth Metroplex",
            "North Texas",
            "East Texas",
            "Central Texas", 
            "Houston Area",
            "Austin Area",
            "San Antonio Area",
            "West Texas",
            "South Texas",
            "Panhandle",
            "Nationwide",
            "Multi-State"
        ]
        
        self.licensing_requirements = {
            "Roofing Contractors": ["State Roofing License", "General Liability Insurance", "Workers Compensation"],
            "Construction Workers": ["General Contractor License", "General Liability Insurance", "Bonding"],
            "General Contractors": ["State Contractor License", "General Liability Insurance", "Workers Compensation"],
            "Insurance Adjusters": ["State Adjuster License", "E&O Insurance"],
            "Emergency Services": ["Emergency Response Certification", "General Liability Insurance"],
            "Tree Removal Services": ["Arborist License", "General Liability Insurance", "Tree Service Bond"],
            "Window Replacement": ["Window Installation Certification", "General Liability Insurance"],
            "Siding Contractors": ["Siding Installation License", "General Liability Insurance"],
            "Gutter Services": ["Gutter Installation License", "General Liability Insurance"],
            "Fence Contractors": ["Fence Installation License", "General Liability Insurance"],
            "Landscaping Services": ["Landscaping License", "General Liability Insurance"],
            "HVAC Services": ["HVAC License", "General Liability Insurance", "EPA Certification"],
            "Electrical Services": ["Electrical License", "General Liability Insurance", "Bonding"],
            "Plumbing Services": ["Plumbing License", "General Liability Insurance", "Bonding"],
            "Water Damage Restoration": ["IICRC Certification", "General Liability Insurance"],
            "Mold Remediation": ["Mold Remediation License", "General Liability Insurance"],
            "Carpet Cleaning": ["Carpet Cleaning License", "General Liability Insurance"],
            "Painting Services": ["Painting License", "General Liability Insurance"],
            "Flooring Services": ["Flooring Installation License", "General Liability Insurance"],
            "Other": ["Business License", "General Liability Insurance"]
        }
    
    def register_vendor(self, vendor_data: Dict) -> Dict:
        """
        Register a new vendor
        """
        try:
            # Validate required fields
            required_fields = ['business_name', 'vendor_type', 'contact_name', 'phone', 'email', 'service_areas']
            for field in required_fields:
                if field not in vendor_data or not vendor_data[field]:
                    return {
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }
            
            # Generate vendor ID
            vendor_id = f"VENDOR_{int(datetime.now().timestamp())}"
            
            # Create vendor record
            vendor_record = {
                'vendor_id': vendor_id,
                'business_name': vendor_data['business_name'],
                'vendor_type': vendor_data['vendor_type'],
                'contact_name': vendor_data['contact_name'],
                'phone': vendor_data['phone'],
                'email': vendor_data['email'],
                'website': vendor_data.get('website', ''),
                'address': vendor_data.get('address', ''),
                'city': vendor_data.get('city', ''),
                'state': vendor_data.get('state', ''),
                'zip_code': vendor_data.get('zip_code', ''),
                'service_areas': vendor_data['service_areas'],
                'services_offered': vendor_data.get('services_offered', []),
                'years_experience': vendor_data.get('years_experience', 0),
                'crew_size': vendor_data.get('crew_size', 0),
                'equipment_available': vendor_data.get('equipment_available', []),
                'licenses': vendor_data.get('licenses', []),
                'insurance_info': vendor_data.get('insurance_info', {}),
                'certifications': vendor_data.get('certifications', []),
                'references': vendor_data.get('references', []),
                'emergency_availability': vendor_data.get('emergency_availability', False),
                'response_time': vendor_data.get('response_time', '24-48 hours'),
                'pricing_model': vendor_data.get('pricing_model', 'Hourly'),
                'minimum_job_size': vendor_data.get('minimum_job_size', '$500'),
                'payment_methods': vendor_data.get('payment_methods', ['Cash', 'Check', 'Credit Card']),
                'warranty_offered': vendor_data.get('warranty_offered', '1 year'),
                'rating': 0.0,
                'total_jobs': 0,
                'status': 'Pending Review',
                'registration_date': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'notes': vendor_data.get('notes', ''),
                'specializations': vendor_data.get('specializations', []),
                'languages_spoken': vendor_data.get('languages_spoken', ['English']),
                'availability_schedule': vendor_data.get('availability_schedule', 'Monday-Friday 8AM-6PM')
            }
            
            # Save to CSV
            self._save_vendor_record(vendor_record)
            
            return {
                'success': True,
                'vendor_id': vendor_id,
                'message': 'Vendor registration submitted successfully',
                'next_steps': [
                    'Your application is under review',
                    'We will contact you within 24-48 hours',
                    'Please ensure all licenses and insurance are current',
                    'Keep your contact information updated'
                ]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Registration failed: {str(e)}'
            }
    
    def _save_vendor_record(self, vendor_record: Dict):
        """Save vendor record to CSV file"""
        vendor_file = 'vendor_registrations.csv'
        
        if os.path.exists(vendor_file):
            df = pd.read_csv(vendor_file)
            new_df = pd.DataFrame([vendor_record])
            df = pd.concat([df, new_df], ignore_index=True)
        else:
            df = pd.DataFrame([vendor_record])
        
        df.to_csv(vendor_file, index=False)
    
    def get_vendor_types(self) -> List[str]:
        """Get list of available vendor types"""
        return self.vendor_types
    
    def get_service_areas(self) -> List[str]:
        """Get list of service areas"""
        return self.service_areas
    
    def get_licensing_requirements(self, vendor_type: str) -> List[str]:
        """Get licensing requirements for specific vendor type"""
        return self.licensing_requirements.get(vendor_type, ["Business License", "General Liability Insurance"])
    
    def get_vendor_list(self) -> List[Dict]:
        """Get list of all registered vendors"""
        try:
            vendor_file = 'vendor_registrations.csv'
            if os.path.exists(vendor_file):
                df = pd.read_csv(vendor_file)
                return df.to_dict('records')
            else:
                return []
        except Exception as e:
            print(f"Error loading vendor list: {e}")
            return []
    
    def update_vendor_status(self, vendor_id: str, status: str, notes: str = '') -> Dict:
        """Update vendor status (Approved, Rejected, Suspended, etc.)"""
        try:
            vendor_file = 'vendor_registrations.csv'
            if not os.path.exists(vendor_file):
                return {'success': False, 'error': 'No vendor records found'}
            
            df = pd.read_csv(vendor_file)
            vendor_index = df[df['vendor_id'] == vendor_id].index
            
            if len(vendor_index) == 0:
                return {'success': False, 'error': 'Vendor not found'}
            
            df.loc[vendor_index[0], 'status'] = status
            df.loc[vendor_index[0], 'last_updated'] = datetime.now().isoformat()
            if notes:
                df.loc[vendor_index[0], 'notes'] = notes
            
            df.to_csv(vendor_file, index=False)
            
            return {
                'success': True,
                'message': f'Vendor status updated to {status}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Status update failed: {str(e)}'
            }
    
    def search_vendors(self, criteria: Dict) -> List[Dict]:
        """Search vendors by criteria"""
        try:
            vendors = self.get_vendor_list()
            filtered_vendors = []
            
            for vendor in vendors:
                match = True
                
                if 'vendor_type' in criteria and criteria['vendor_type']:
                    if vendor['vendor_type'] != criteria['vendor_type']:
                        match = False
                
                if 'service_area' in criteria and criteria['service_area']:
                    if criteria['service_area'] not in str(vendor['service_areas']):
                        match = False
                
                if 'status' in criteria and criteria['status']:
                    if vendor['status'] != criteria['status']:
                        match = False
                
                if 'emergency_availability' in criteria and criteria['emergency_availability']:
                    if not vendor['emergency_availability']:
                        match = False
                
                if match:
                    filtered_vendors.append(vendor)
            
            return filtered_vendors
            
        except Exception as e:
            print(f"Error searching vendors: {e}")
            return []
    
    def generate_vendor_report(self) -> Dict:
        """Generate vendor statistics report"""
        try:
            vendors = self.get_vendor_list()
            
            if not vendors:
                return {
                    'total_vendors': 0,
                    'by_type': {},
                    'by_status': {},
                    'by_service_area': {},
                    'emergency_available': 0
                }
            
            df = pd.DataFrame(vendors)
            
            report = {
                'total_vendors': len(vendors),
                'by_type': df['vendor_type'].value_counts().to_dict(),
                'by_status': df['status'].value_counts().to_dict(),
                'emergency_available': len(df[df['emergency_availability'] == True]),
                'average_rating': df['rating'].mean() if 'rating' in df.columns else 0,
                'total_jobs': df['total_jobs'].sum() if 'total_jobs' in df.columns else 0,
                'registration_trend': self._get_registration_trend(df)
            }
            
            return report
            
        except Exception as e:
            print(f"Error generating vendor report: {e}")
            return {'error': str(e)}
    
    def _get_registration_trend(self, df: pd.DataFrame) -> Dict:
        """Get registration trend over time"""
        try:
            df['registration_date'] = pd.to_datetime(df['registration_date'])
            df['month'] = df['registration_date'].dt.to_period('M')
            trend = df['month'].value_counts().sort_index()
            return trend.to_dict()
        except:
            return {}

# Initialize the vendor registration system
vendor_system = VendorRegistrationSystem()
