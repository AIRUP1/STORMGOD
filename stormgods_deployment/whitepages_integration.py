"""
Whitepages Pro API Integration for DFW Hail Events
Enriches property data with owner contact information

API Documentation: https://www.whitepages.com/pro-api
Features:
- 350M+ Identity Records
- 673M+ Phone & Address Records  
- 454M+ Email Addresses
- 92M+ Property Owner Records
"""
import pandas as pd
import requests
import time
import json
from typing import Dict, List, Optional

print("=" * 70)
print("WHITEPAGES PRO API INTEGRATION")
print("=" * 70)
print("\nAPI Features Available:")
print("  ✓ 350M+ Identity Records")
print("  ✓ 673M+ Phone & Address Records")
print("  ✓ 454M+ Email Addresses")
print("  ✓ 92M+ Property Owner Records")
print("  ✓ Reverse Address Lookup")
print("  ✓ Property Owner Data")
print("  ✓ Contact Enrichment")

class WhitepagesAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://proapi.whitepages.com/v3"
        self.headers = {
            "Authorization": "Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def reverse_address_lookup(self, address: str, city: str, state: str = "TX", zipcode: str = None) -> Dict:
        """
        Look up property owner information by address
        """
        url = f"{self.base_url}/reverse_address"
        
        params = {
            "address": address,
            "city": city,
            "state": state,
            "zipcode": zipcode
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error in reverse address lookup: {e}")
            return {}
    
    def person_lookup(self, name: str, address: str = None, phone: str = None) -> Dict:
        """
        Look up person by name, address, or phone
        """
        url = f"{self.base_url}/person"
        
        params = {"name": name}
        if address:
            params["address"] = address
        if phone:
            params["phone"] = phone
            
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error in person lookup: {e}")
            return {}
    
    def phone_lookup(self, phone: str) -> Dict:
        """
        Reverse phone number lookup
        """
        url = f"{self.base_url}/phone"
        
        params = {"phone": phone}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error in phone lookup: {e}")
            return {}

def enrich_hail_events_with_whitepages(api_key: str, max_events: int = 50):
    """
    Enrich hail events with property owner data from Whitepages
    """
    print(f"\n" + "=" * 70)
    print(f"ENRICHING HAIL EVENTS WITH WHITEPAGES DATA")
    print("=" * 70)
    
    # Initialize API
    wp = WhitepagesAPI(api_key)
    
    # Load hail events
    df = pd.read_csv('hail_events_dfw_2024_2025_neighborhoods.csv')
    df = df[(df['LAT'].notna()) & (df['LON'].notna())].copy()
    
    # Filter to events with address data
    df_address = df[df['city'].notna()].copy()
    
    print(f"Total events with city data: {len(df_address)}")
    print(f"Processing first {min(max_events, len(df_address))} events...")
    
    # Process events
    enriched_data = []
    
    for idx, row in df_address.head(max_events).iterrows():
        print(f"\nProcessing {idx+1}/{min(max_events, len(df_address))}: {row['city']}")
        
        # Prepare address for lookup
        address = f"{row['neighborhood'] or ''} {row['city']}".strip()
        city = row['city']
        zipcode = str(int(row['postcode'])) if pd.notna(row['postcode']) else None
        
        print(f"  Looking up: {address}, {city}, TX {zipcode}")
        
        # Reverse address lookup
        property_data = wp.reverse_address_lookup(
            address=address,
            city=city,
            state="TX",
            zipcode=zipcode
        )
        
        # Extract property owner information
        owner_info = extract_property_owner_info(property_data)
        
        # Add to enriched data
        enriched_row = row.to_dict()
        enriched_row.update(owner_info)
        enriched_data.append(enriched_row)
        
        # Rate limiting - Whitepages has limits
        time.sleep(1)  # 1 second between requests
    
    # Create enriched DataFrame
    enriched_df = pd.DataFrame(enriched_data)
    
    # Save results
    output_file = 'hail_events_enriched_whitepages.csv'
    enriched_df.to_csv(output_file, index=False)
    
    print(f"\n✓ Enriched data saved to: {output_file}")
    print(f"✓ Processed {len(enriched_data)} events")
    
    return enriched_df

def extract_property_owner_info(property_data: Dict) -> Dict:
    """
    Extract property owner information from Whitepages API response
    """
    owner_info = {
        'property_owner_name': '',
        'property_owner_phone': '',
        'property_owner_email': '',
        'property_owner_address': '',
        'property_type': '',
        'property_value': '',
        'property_year_built': '',
        'property_sqft': '',
        'whitepages_confidence': '',
        'whitepages_match_type': '',
        'whitepages_data_source': 'whitepages_api'
    }
    
    try:
        # Navigate through the API response structure
        if 'results' in property_data and property_data['results']:
            result = property_data['results'][0]
            
            # Extract property information
            if 'property' in result:
                prop = result['property']
                owner_info['property_type'] = prop.get('type', '')
                owner_info['property_value'] = prop.get('value', '')
                owner_info['property_year_built'] = prop.get('year_built', '')
                owner_info['property_sqft'] = prop.get('square_footage', '')
            
            # Extract owner information
            if 'associated_people' in result and result['associated_people']:
                person = result['associated_people'][0]
                
                owner_info['property_owner_name'] = person.get('name', '')
                
                # Extract contact information
                if 'phones' in person and person['phones']:
                    phone = person['phones'][0]
                    owner_info['property_owner_phone'] = phone.get('number', '')
                
                if 'emails' in person and person['emails']:
                    email = person['emails'][0]
                    owner_info['property_owner_email'] = email.get('address', '')
                
                if 'addresses' in person and person['addresses']:
                    addr = person['addresses'][0]
                    owner_info['property_owner_address'] = addr.get('formatted_address', '')
            
            # Extract confidence and match information
            owner_info['whitepages_confidence'] = result.get('confidence', '')
            owner_info['whitepages_match_type'] = result.get('match_type', '')
            
    except Exception as e:
        print(f"    Error extracting owner info: {e}")
        owner_info['whitepages_data_source'] = 'error'
    
    return owner_info

def create_whitepages_marketing_reports(enriched_df: pd.DataFrame):
    """
    Create marketing reports from Whitepages enriched data
    """
    print(f"\n" + "=" * 70)
    print("CREATING WHITEPAGES MARKETING REPORTS")
    print("=" * 70)
    
    # Filter to events with owner data
    has_owner = enriched_df['property_owner_name'].notna() & (enriched_df['property_owner_name'] != '')
    owner_data = enriched_df[has_owner].copy()
    
    print(f"Events with property owner data: {len(owner_data)}")
    
    if len(owner_data) == 0:
        print("No property owner data found. Check your API key and try again.")
        return
    
    # Report 1: Property Owners by City
    city_owners = owner_data.groupby('city').agg({
        'property_owner_name': 'count',
        'HAIL_SIZE_IN': ['mean', 'max'],
        'property_owner_phone': lambda x: sum(x.notna() & (x != '')),
        'property_owner_email': lambda x: sum(x.notna() & (x != ''))
    }).round(2)
    
    city_owners.columns = ['Owner_Count', 'Avg_Hail_Size', 'Max_Hail_Size', 'Phone_Count', 'Email_Count']
    city_owners = city_owners.sort_values('Owner_Count', ascending=False)
    
    print("\nTop Cities with Property Owner Data:")
    print("-" * 50)
    for city, row in city_owners.head(10).iterrows():
        print(f"{city:20} | {int(row['Owner_Count']):3} owners | "
              f"Phones: {int(row['Phone_Count']):2} | Emails: {int(row['Email_Count']):2}")
    
    # Save reports
    city_owners.to_csv('whitepages_owners_by_city.csv')
    
    # Report 2: Contact Information Summary
    contact_summary = {
        'Total_Events_Processed': len(enriched_df),
        'Events_with_Owner_Names': len(owner_data),
        'Events_with_Phone_Numbers': len(owner_data[owner_data['property_owner_phone'].notna() & (owner_data['property_owner_phone'] != '')]),
        'Events_with_Email_Addresses': len(owner_data[owner_data['property_owner_email'].notna() & (owner_data['property_owner_email'] != '')]),
        'Events_with_Property_Values': len(owner_data[owner_data['property_value'].notna() & (owner_data['property_value'] != '')]),
        'Contact_Success_Rate': f"{(len(owner_data) / len(enriched_df) * 100):.1f}%"
    }
    
    print(f"\nContact Information Summary:")
    print("-" * 50)
    for key, value in contact_summary.items():
        print(f"{key:30}: {value}")
    
    # Save contact summary
    with open('whitepages_contact_summary.txt', 'w') as f:
        for key, value in contact_summary.items():
            f.write(f"{key}: {value}\n")
    
    # Report 3: High-Value Properties (for premium targeting)
    high_value = owner_data[owner_data['property_value'].notna() & (owner_data['property_value'] != '')].copy()
    if len(high_value) > 0:
        high_value['property_value_num'] = pd.to_numeric(high_value['property_value'], errors='coerce')
        high_value = high_value[high_value['property_value_num'].notna()]
        
        if len(high_value) > 0:
            print(f"\nHigh-Value Properties (with values):")
            print("-" * 50)
            print(f"Average Property Value: ${high_value['property_value_num'].mean():,.0f}")
            print(f"Highest Property Value: ${high_value['property_value_num'].max():,.0f}")
            print(f"Properties over $500K: {len(high_value[high_value['property_value_num'] > 500000])}")
            
            # Save high-value properties
            high_value_export = high_value[['city', 'property_owner_name', 'property_owner_phone', 
                                          'property_owner_email', 'property_value', 'HAIL_SIZE_IN']].copy()
            high_value_export.to_csv('whitepages_high_value_properties.csv', index=False)
    
    print(f"\n✓ Reports saved:")
    print(f"  - whitepages_owners_by_city.csv")
    print(f"  - whitepages_contact_summary.txt")
    if len(high_value) > 0:
        print(f"  - whitepages_high_value_properties.csv")

def main():
    """
    Main function to run Whitepages integration
    """
    print("WHITEPAGES PRO API INTEGRATION")
    print("=" * 50)
    print("\nTo use this integration:")
    print("1. Get your API key from: https://www.whitepages.com/pro-api")
    print("2. Update the API_KEY variable below")
    print("3. Run the script")
    
    # TODO: Replace with your actual API key
    API_KEY = "YOUR_WHITEPAGES_API_KEY_HERE"
    
    if API_KEY == "YOUR_WHITEPAGES_API_KEY_HERE":
        print(f"\n⚠️  Please update the API_KEY variable with your Whitepages Pro API key")
        print(f"   Get your key at: https://www.whitepages.com/pro-api")
        return
    
    # Test API connection
    wp = WhitepagesAPI(API_KEY)
    print(f"\nTesting API connection...")
    
    # Enrich data (start with small batch for testing)
    enriched_df = enrich_hail_events_with_whitepages(API_KEY, max_events=20)
    
    # Create marketing reports
    create_whitepages_marketing_reports(enriched_df)
    
    print(f"\n✓ Whitepages integration complete!")
    print(f"✓ Check the generated CSV files for enriched data")

if __name__ == "__main__":
    main()
