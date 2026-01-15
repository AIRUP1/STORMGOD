"""
StormBuster Spokeo Web API Integration
Enriches property data with owner contact information using Spokeo's web services

Features:
- Property Owner Lookup
- Contact Information Enrichment
- Address Reverse Lookup
- Phone Number Lookup
- Email Address Search
"""
import pandas as pd
import requests
import time
import json
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import re

print("=" * 70)
print("STORMBUSTER SPOKEO WEB API INTEGRATION")
print("=" * 70)
print("\nAPI Features Available:")
print("  - Property Owner Records")
print("  - Contact Information Lookup")
print("  - Reverse Address Lookup")
print("  - Phone Number Search")
print("  - Email Address Search")
print("  - Property Details")

class SpokeoAPI:
    def __init__(self, username: str, password: str):
        self.username = bolison10@gmail.com
        self.password = Bbusta10
        self.session = requests.Session()
        self.base_url = "https://www.spokeo.com"
        self.logged_in = False
        
        # Set headers to mimic browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def login(self) -> bool:
        """
        Login to Spokeo account
        """
        try:
            print("Logging into Spokeo...")
            
            # Get login page
            login_url = f"{self.base_url}/user/account/login"
            response = self.session.get(login_url)
            response.raise_for_status()
            
            # Parse login form
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find CSRF token if present
            csrf_token = ""
            csrf_input = soup.find('input', {'name': '_token'})
            if csrf_input:
                csrf_token = csrf_input.get('value', '')
            
            # Prepare login data
            login_data = {
                'email': self.username,
                'password': self.password,
                '_token': csrf_token
            }
            
            # Submit login
            response = self.session.post(login_url, data=login_data, allow_redirects=True)
            response.raise_for_status()
            
            # Check if login was successful by looking for account indicators
            if ("account" in response.url.lower() or 
                "dashboard" in response.url.lower() or 
                "profile" in response.url.lower() or
                "logout" in response.text.lower()):
                self.logged_in = True
                print("✓ Successfully logged into Spokeo")
                return True
            else:
                print("❌ Login failed - check credentials")
                print(f"   Response URL: {response.url}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def search_property_by_address(self, address: str, city: str, state: str = "TX", zipcode: str = None) -> Dict:
        """
        Search for property information by address
        """
        if not self.logged_in:
            if not self.login():
                return {}
        
        try:
            # Construct search URL
            search_url = f"{self.base_url}/search"
            
            # Prepare search parameters
            search_params = {
                'q': f"{address}, {city}, {state} {zipcode}".strip(),
                'category': 'address'
            }
            
            response = self.session.get(search_url, params=search_params)
            response.raise_for_status()
            
            # Parse search results
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract property information
            property_info = self._extract_property_info(soup)
            
            return property_info
            
        except Exception as e:
            print(f"Error searching property: {e}")
            return {}
    
    def search_person_by_name(self, name: str, city: str = None, state: str = None) -> Dict:
        """
        Search for person by name
        """
        if not self.logged_in:
            if not self.login():
                return {}
        
        try:
            search_url = f"{self.base_url}/search"
            
            search_params = {
                'q': name,
                'category': 'people'
            }
            
            if city:
                search_params['city'] = city
            if state:
                search_params['state'] = state
            
            response = self.session.get(search_url, params=search_params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            person_info = self._extract_person_info(soup)
            
            return person_info
            
        except Exception as e:
            print(f"Error searching person: {e}")
            return {}
    
    def reverse_phone_lookup(self, phone: str) -> Dict:
        """
        Reverse phone number lookup
        """
        if not self.logged_in:
            if not self.login():
                return {}
        
        try:
            search_url = f"{self.base_url}/search"
            
            search_params = {
                'q': phone,
                'category': 'phone'
            }
            
            response = self.session.get(search_url, params=search_params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            phone_info = self._extract_phone_info(soup)
            
            return phone_info
            
        except Exception as e:
            print(f"Error in phone lookup: {e}")
            return {}
    
    def _extract_property_info(self, soup: BeautifulSoup) -> Dict:
        """
        Extract property information from search results
        """
        property_info = {
            'property_owner_name': '',
            'property_owner_phone': '',
            'property_owner_email': '',
            'property_owner_address': '',
            'property_type': '',
            'property_value': '',
            'property_year_built': '',
            'property_sqft': '',
            'spokeo_confidence': '',
            'spokeo_match_type': '',
            'spokeo_data_source': 'spokeo_web'
        }
        
        try:
            # Look for property details in the page
            property_sections = soup.find_all('div', class_=re.compile(r'property|address|owner'))
            
            for section in property_sections:
                text = section.get_text().lower()
                
                # Extract owner name
                if 'owner' in text or 'resident' in text:
                    name_pattern = r'(?:owner|resident)[:\s]+([a-zA-Z\s]+)'
                    name_match = re.search(name_pattern, text)
                    if name_match and not property_info['property_owner_name']:
                        property_info['property_owner_name'] = name_match.group(1).strip()
                
                # Extract phone number
                phone_pattern = r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})'
                phone_match = re.search(phone_pattern, text)
                if phone_match and not property_info['property_owner_phone']:
                    property_info['property_owner_phone'] = phone_match.group(1)
                
                # Extract email
                email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
                email_match = re.search(email_pattern, text)
                if email_match and not property_info['property_owner_email']:
                    property_info['property_owner_email'] = email_match.group(1)
            
            # Look for property value information
            value_sections = soup.find_all(text=re.compile(r'\$[\d,]+'))
            for value_text in value_sections:
                if 'value' in value_text.lower() or 'worth' in value_text.lower():
                    value_match = re.search(r'\$[\d,]+', value_text)
                    if value_match:
                        property_info['property_value'] = value_match.group(0)
                        break
            
        except Exception as e:
            print(f"Error extracting property info: {e}")
            property_info['spokeo_data_source'] = 'error'
        
        return property_info
    
    def _extract_person_info(self, soup: BeautifulSoup) -> Dict:
        """
        Extract person information from search results
        """
        person_info = {
            'name': '',
            'phone': '',
            'email': '',
            'address': '',
            'age': '',
            'spokeo_data_source': 'spokeo_web'
        }
        
        try:
            # Look for person details
            person_sections = soup.find_all('div', class_=re.compile(r'person|profile|contact'))
            
            for section in person_sections:
                text = section.get_text()
                
                # Extract phone
                phone_pattern = r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})'
                phone_match = re.search(phone_pattern, text)
                if phone_match:
                    person_info['phone'] = phone_match.group(1)
                
                # Extract email
                email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
                email_match = re.search(email_pattern, text)
                if email_match:
                    person_info['email'] = email_match.group(1)
                
                # Extract address
                address_pattern = r'(\d+\s+[a-zA-Z\s]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|boulevard|blvd))'
                address_match = re.search(address_pattern, text, re.IGNORECASE)
                if address_match:
                    person_info['address'] = address_match.group(1)
        
        except Exception as e:
            print(f"Error extracting person info: {e}")
            person_info['spokeo_data_source'] = 'error'
        
        return person_info
    
    def _extract_phone_info(self, soup: BeautifulSoup) -> Dict:
        """
        Extract phone number information from search results
        """
        phone_info = {
            'phone_number': '',
            'owner_name': '',
            'address': '',
            'carrier': '',
            'location': '',
            'spokeo_data_source': 'spokeo_web'
        }
        
        try:
            # Look for phone details
            phone_sections = soup.find_all('div', class_=re.compile(r'phone|contact|owner'))
            
            for section in phone_sections:
                text = section.get_text()
                
                # Extract owner name
                name_pattern = r'(?:owner|belongs to|associated with)[:\s]+([a-zA-Z\s]+)'
                name_match = re.search(name_pattern, text, re.IGNORECASE)
                if name_match:
                    phone_info['owner_name'] = name_match.group(1).strip()
                
                # Extract address
                address_pattern = r'(\d+\s+[a-zA-Z\s]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|boulevard|blvd))'
                address_match = re.search(address_pattern, text, re.IGNORECASE)
                if address_match:
                    phone_info['address'] = address_match.group(1)
        
        except Exception as e:
            print(f"Error extracting phone info: {e}")
            phone_info['spokeo_data_source'] = 'error'
        
        return phone_info

def enrich_storm_events_with_spokeo(username: str, password: str, max_events: int = 50):
    """
    Enrich storm events with property owner data from Spokeo
    """
    print(f"\n" + "=" * 70)
    print(f"ENRICHING STORM EVENTS WITH SPOKEO DATA")
    print("=" * 70)
    
    # Initialize API
    spokeo = SpokeoAPI(username, password)
    
    # Load storm events
    try:
        df = pd.read_csv('storm_events_dfw_2024_2025_neighborhoods.csv')
        df = df[(df['LAT'].notna()) & (df['LON'].notna())].copy()
    except FileNotFoundError:
        print("❌ Storm events file not found. Creating sample data...")
        # Create sample data for testing
        df = pd.DataFrame({
            'LAT': [32.7767, 32.7831, 32.7505],
            'LON': [-96.7970, -96.8067, -96.7970],
            'city': ['Dallas', 'Dallas', 'Dallas'],
            'neighborhood': ['Downtown', 'Uptown', 'Deep Ellum'],
            'postcode': [75201, 75204, 75226],
            'STORM_SIZE_IN': [1.5, 2.0, 1.2]
        })
    
    # Filter to events with address data
    df_address = df[df['city'].notna()].copy()
    
    print(f"Total events with city data: {len(df_address)}")
    print(f"Processing first {min(max_events, len(df_address))} events...")
    
    # Process events
    enriched_data = []
    
    for idx, row in df_address.head(max_events).iterrows():
        print(f"\nProcessing {idx+1}/{min(max_events, len(df_address))}: {row['city']}")
        
        # Prepare address for lookup
        address = f"{row.get('neighborhood', '')} {row.get('city', '')}".strip()
        city = row['city']
        zipcode = str(int(row['postcode'])) if pd.notna(row.get('postcode')) else None
        
        print(f"  Looking up: {address}, {city}, TX {zipcode}")
        
        # Property lookup
        property_data = spokeo.search_property_by_address(
            address=address,
            city=city,
            state="TX",
            zipcode=zipcode
        )
        
        # Add to enriched data
        enriched_row = row.to_dict()
        enriched_row.update(property_data)
        enriched_data.append(enriched_row)
        
        # Rate limiting
        time.sleep(2)  # 2 seconds between requests to be respectful
    
    # Create enriched DataFrame
    enriched_df = pd.DataFrame(enriched_data)
    
    # Save results
    output_file = 'storm_events_enriched_spokeo.csv'
    enriched_df.to_csv(output_file, index=False)
    
    print(f"\n✓ Enriched data saved to: {output_file}")
    print(f"✓ Processed {len(enriched_data)} events")
    
    return enriched_df

def create_stormbuster_marketing_reports(enriched_df: pd.DataFrame):
    """
    Create marketing reports from StormBuster enriched data
    """
    print(f"\n" + "=" * 70)
    print("CREATING STORMBUSTER MARKETING REPORTS")
    print("=" * 70)
    
    # Filter to events with owner data
    has_owner = enriched_df['property_owner_name'].notna() & (enriched_df['property_owner_name'] != '')
    owner_data = enriched_df[has_owner].copy()
    
    print(f"Events with property owner data: {len(owner_data)}")
    
    if len(owner_data) == 0:
        print("No property owner data found. Check your credentials and try again.")
        return
    
    # Report 1: Property Owners by City
    city_owners = owner_data.groupby('city').agg({
        'property_owner_name': 'count',
        'STORM_SIZE_IN': ['mean', 'max'],
        'property_owner_phone': lambda x: sum(x.notna() & (x != '')),
        'property_owner_email': lambda x: sum(x.notna() & (x != ''))
    }).round(2)
    
    city_owners.columns = ['Owner_Count', 'Avg_Storm_Size', 'Max_Storm_Size', 'Phone_Count', 'Email_Count']
    city_owners = city_owners.sort_values('Owner_Count', ascending=False)
    
    print("\nTop Cities with Property Owner Data:")
    print("-" * 50)
    for city, row in city_owners.head(10).iterrows():
        print(f"{city:20} | {int(row['Owner_Count']):3} owners | "
              f"Phones: {int(row['Phone_Count']):2} | Emails: {int(row['Email_Count']):2}")
    
    # Save reports
    city_owners.to_csv('stormbuster_owners_by_city.csv')
    
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
    with open('stormbuster_contact_summary.txt', 'w') as f:
        for key, value in contact_summary.items():
            f.write(f"{key}: {value}\n")
    
    # Report 3: High-Value Properties
    high_value = owner_data[owner_data['property_value'].notna() & (owner_data['property_value'] != '')].copy()
    if len(high_value) > 0:
        # Extract numeric values from property_value
        high_value['property_value_num'] = high_value['property_value'].str.replace('$', '').str.replace(',', '').astype(float, errors='coerce')
        high_value = high_value[high_value['property_value_num'].notna()]
        
        if len(high_value) > 0:
            print(f"\nHigh-Value Properties (with values):")
            print("-" * 50)
            print(f"Average Property Value: ${high_value['property_value_num'].mean():,.0f}")
            print(f"Highest Property Value: ${high_value['property_value_num'].max():,.0f}")
            print(f"Properties over $500K: {len(high_value[high_value['property_value_num'] > 500000])}")
            
            # Save high-value properties
            high_value_export = high_value[['city', 'property_owner_name', 'property_owner_phone', 
                                          'property_owner_email', 'property_value', 'STORM_SIZE_IN']].copy()
            high_value_export.to_csv('stormbuster_high_value_properties.csv', index=False)
    
    print(f"\n✓ Reports saved:")
    print(f"  - stormbuster_owners_by_city.csv")
    print(f"  - stormbuster_contact_summary.txt")
    if len(high_value) > 0:
        print(f"  - stormbuster_high_value_properties.csv")

def main():
    """
    Main function to run Spokeo integration
    """
    print("STORMBUSTER SPOKEO WEB API INTEGRATION")
    print("=" * 50)
    print("\nTo use this integration:")
    print("1. Enter your Spokeo account credentials below")
    print("2. Run the script")
    
    # TODO: Replace with your actual Spokeo credentials
    USERNAME = "bolison10@gmail.com"
    PASSWORD = "Bbusta10"
    
    if PASSWORD == "YOUR_SPOKEO_PASSWORD_HERE":
        print(f"\n⚠️  Please update the PASSWORD variable with your Spokeo account password")
        print(f"   Sign up at: https://www.spokeo.com/myspokeo")
        return
    
    # Test API connection
    spokeo = SpokeoAPI(USERNAME, PASSWORD)
    print(f"\nTesting API connection...")
    
    # Enrich data (start with small batch for testing)
    enriched_df = enrich_storm_events_with_spokeo(USERNAME, PASSWORD, max_events=20)
    
    # Create marketing reports
    create_stormbuster_marketing_reports(enriched_df)
    
    print(f"\n✓ StormBuster integration complete!")
    print(f"✓ Check the generated CSV files for enriched data")

if __name__ == "__main__":
    main()
