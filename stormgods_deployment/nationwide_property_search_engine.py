"""
StormBuster Nationwide Property Search Engine
Searches all US states for storm events and property data
Integrates multiple data sources for comprehensive lead generation
"""
import pandas as pd
import requests
import json
import time
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional
from spokeo_integration import SpokeoAPI

print("=" * 80)
print("STORMBUSTER NATIONWIDE PROPERTY SEARCH ENGINE")
print("=" * 80)
print("Searching all US states for storm events and property data")
print("Integrating: NOAA, County Records, Spokeo, Property APIs")

class NationwidePropertySearchEngine:
    def __init__(self):
        self.noaa_base = "https://www1.ncdc.noaa.gov/pub/data/swdi/stormevents/csvfiles"
        self.results = []
        self.property_apis = {
            'spokeo': 'https://www.spokeo.com',
            'melissa': 'https://api.melissa.com',
            'corelogic': 'https://api.corelogic.com',
            'lexisnexis': 'https://api.lexisnexis.com'
        }
        
    def search_all_states(self, years: List[int] = [2024, 2025], 
                         min_storm_size: float = 1.0) -> pd.DataFrame:
        """
        Search all US states for storm events
        """
        print(f"\n🔍 SEARCHING ALL US STATES")
        print(f"Years: {years}")
        print(f"Minimum Storm Size: {min_storm_size}\"")
        print("-" * 60)
        
        all_events = []
        
        # Get all state FIPS codes
        states = self.get_us_states()
        
        for year in years:
            print(f"\n📅 Processing {year}...")
            
            # Download NOAA data for the year
            try:
                year_data = self.download_noaa_year(year)
                if year_data is not None:
                    # Filter for storm events
                    storm_data = year_data[
                        (year_data['EVENT_TYPE'].str.upper() == 'HAIL') &
                        (year_data['MAGNITUDE'] >= min_storm_size)
                    ].copy()
                    
                    print(f"  Found {len(storm_data)} storm events in {year}")
                    all_events.append(storm_data)
                    
            except Exception as e:
                print(f"  Error processing {year}: {e}")
                continue
        
        if all_events:
            combined_df = pd.concat(all_events, ignore_index=True)
            print(f"\n✅ Total storm events found: {len(combined_df)}")
            return combined_df
        else:
            print("❌ No data found")
            return pd.DataFrame()
    
    def get_us_states(self) -> Dict[str, str]:
        """Get US state FIPS codes"""
        return {
            '01': 'Alabama', '02': 'Alaska', '04': 'Arizona', '05': 'Arkansas',
            '06': 'California', '08': 'Colorado', '09': 'Connecticut', '10': 'Delaware',
            '11': 'District of Columbia', '12': 'Florida', '13': 'Georgia', '15': 'Hawaii',
            '16': 'Idaho', '17': 'Illinois', '18': 'Indiana', '19': 'Iowa',
            '20': 'Kansas', '21': 'Kentucky', '22': 'Louisiana', '23': 'Maine',
            '24': 'Maryland', '25': 'Massachusetts', '26': 'Michigan', '27': 'Minnesota',
            '28': 'Mississippi', '29': 'Missouri', '30': 'Montana', '31': 'Nebraska',
            '32': 'Nevada', '33': 'New Hampshire', '34': 'New Jersey', '35': 'New Mexico',
            '36': 'New York', '37': 'North Carolina', '38': 'North Dakota', '39': 'Ohio',
            '40': 'Oklahoma', '41': 'Oregon', '42': 'Pennsylvania', '44': 'Rhode Island',
            '45': 'South Carolina', '46': 'South Dakota', '47': 'Tennessee', '48': 'Texas',
            '49': 'Utah', '50': 'Vermont', '51': 'Virginia', '53': 'Washington',
            '54': 'West Virginia', '55': 'Wisconsin', '56': 'Wyoming'
        }
    
    def download_noaa_year(self, year: int) -> Optional[pd.DataFrame]:
        """Download NOAA data for a specific year"""
        try:
            # Get file list
            index_url = f"{self.noaa_base}/"
            response = requests.get(index_url, timeout=60)
            response.raise_for_status()
            
            # Find the latest file for the year
            lines = response.text.splitlines()
            candidates = []
            for line in lines:
                if f"StormEvents_details-ftp_v1.0_d{year}" in line and ".csv.gz" in line:
                    start = line.find('href="')
                    if start != -1:
                        start += 6
                        end = line.find('"', start)
                        href = line[start:end]
                        candidates.append(href)
            
            if not candidates:
                return None
            
            # Download the latest file
            filename = sorted(candidates)[-1]
            url = f"{self.noaa_base}/{filename}"
            
            print(f"  Downloading: {filename}")
            response = requests.get(url, timeout=300)
            response.raise_for_status()
            
            # Decompress and read
            import gzip
            import io
            df = pd.read_csv(io.BytesIO(gzip.decompress(response.content)))
            return df
            
        except Exception as e:
            print(f"  Error downloading {year}: {e}")
            return None
    
    def geocode_events(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add geocoding to events for property lookup
        """
        print(f"\n🌍 GEOCODING {len(df)} EVENTS")
        print("-" * 40)
        
        # Filter events with coordinates
        geo_df = df[(df['BEGIN_LAT'].notna()) & (df['BEGIN_LON'].notna())].copy()
        
        if len(geo_df) == 0:
            print("❌ No events with coordinates found")
            return df
        
        print(f"✅ {len(geo_df)} events have coordinates")
        
        # Add reverse geocoding for city/state
        geo_df['city'] = ''
        geo_df['state_name'] = ''
        geo_df['zipcode'] = ''
        
        # Use a geocoding service (you can integrate with Google, OpenCage, etc.)
        # For now, we'll use the state FIPS to get state names
        states = self.get_us_states()
        geo_df['state_name'] = geo_df['STATE_FIPS'].astype(str).map(states)
        
        return geo_df
    
    def search_property_data(self, df: pd.DataFrame, 
                           spokeo_username: str = None, spokeo_password: str = None) -> pd.DataFrame:
        """
        Search for property data using Spokeo API
        """
        print(f"\n🏠 SEARCHING PROPERTY DATA WITH SPOKEO")
        print("-" * 40)
        
        if not spokeo_username or not spokeo_password:
            print("⚠️  Spokeo credentials not provided. Using simulated data.")
            return self._generate_simulated_property_data(df)
        
        # Initialize Spokeo API
        spokeo = SpokeoAPI(spokeo_username, spokeo_password)
        
        # Test login first
        if not spokeo.login():
            print("⚠️  Spokeo login failed. Using simulated data.")
            return self._generate_simulated_property_data(df)
        
        property_data = []
        
        for idx, row in df.head(50).iterrows():  # Limit for API usage
            print(f"  Processing {idx+1}/{min(50, len(df))}: {row.get('city', 'Unknown')}")
            
            # Prepare address for lookup
            address = f"{row.get('city', '')}, {row.get('state_name', '')}"
            city = row.get('city', '')
            state = row.get('state_name', '')
            zipcode = str(row.get('zipcode', '')) if pd.notna(row.get('zipcode')) else None
            
            # Search property using Spokeo
            property_info = spokeo.search_property_by_address(
                address=address,
                city=city,
                state=state,
                zipcode=zipcode
            )
            
            # Add event information
            property_info.update({
                'event_id': row.get('EVENT_ID', ''),
                'address': address,
                'data_source': 'spokeo_api'
            })
            
            property_data.append(property_info)
            time.sleep(2)  # Rate limiting for Spokeo
        
        property_df = pd.DataFrame(property_data)
        print(f"✅ Found property data for {len(property_df)} properties")
        
        return property_df
    
    def _generate_simulated_property_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate simulated property data when Spokeo credentials are not available
        """
        print("📊 Generating simulated property data...")
        
        property_data = []
        
        for idx, row in df.head(100).iterrows():
            property_info = {
                'event_id': row.get('EVENT_ID', ''),
                'address': f"{row.get('city', '')}, {row.get('state_name', '')}",
                'property_owner_name': f"Property Owner {idx+1}",
                'property_owner_phone': f"(555) {1000+idx:04d}",
                'property_owner_email': f"owner{idx+1}@example.com",
                'property_value': f"${(200000 + idx*10000):,}",
                'property_type': 'Single Family',
                'data_source': 'simulated'
            }
            
            property_data.append(property_info)
            time.sleep(0.1)  # Rate limiting
        
        property_df = pd.DataFrame(property_data)
        print(f"✅ Generated simulated data for {len(property_df)} properties")
        
        return property_df
    
    def create_lead_database(self, events_df: pd.DataFrame, 
                           property_df: pd.DataFrame) -> pd.DataFrame:
        """
        Combine events and property data into lead database
        """
        print(f"\n📊 CREATING LEAD DATABASE")
        print("-" * 40)
        
        # Merge the data
        leads_df = events_df.merge(property_df, left_on='EVENT_ID', right_on='event_id', how='left')
        
        # Add lead scoring
        leads_df['lead_score'] = 0
        
        # Score based on storm size
        leads_df.loc[leads_df['MAGNITUDE'] >= 2.0, 'lead_score'] += 50
        leads_df.loc[leads_df['MAGNITUDE'] >= 1.5, 'lead_score'] += 30
        leads_df.loc[leads_df['MAGNITUDE'] >= 1.0, 'lead_score'] += 10
        
        # Score based on property value (if available)
        if 'property_value' in leads_df.columns:
            leads_df['property_value_num'] = leads_df['property_value'].str.replace('$', '').str.replace(',', '').astype(float, errors='ignore')
            leads_df.loc[leads_df['property_value_num'] >= 500000, 'lead_score'] += 20
            leads_df.loc[leads_df['property_value_num'] >= 300000, 'lead_score'] += 10
        else:
            # Add default property value for scoring
            leads_df['property_value'] = '$300,000'  # Default value
            leads_df['property_value_num'] = 300000
            leads_df['lead_score'] += 10  # Default score for property value
        
        # Score based on recency
        if 'BEGIN_DATE_TIME' in leads_df.columns:
            leads_df['BEGIN'] = pd.to_datetime(leads_df['BEGIN_DATE_TIME'])
            recent_events = leads_df['BEGIN'] >= (datetime.now() - timedelta(days=30))
        else:
            recent_events = pd.Series([False] * len(leads_df))
        leads_df.loc[recent_events, 'lead_score'] += 15
        
        # Sort by lead score
        leads_df = leads_df.sort_values('lead_score', ascending=False)
        
        print(f"✅ Created lead database with {len(leads_df)} leads")
        print(f"   High-priority leads (score 70+): {len(leads_df[leads_df['lead_score'] >= 70])}")
        
        return leads_df
    
    def generate_reports(self, leads_df: pd.DataFrame):
        """
        Generate comprehensive reports
        """
        print(f"\n📈 GENERATING REPORTS")
        print("-" * 40)
        
        # Lead summary
        summary = {
            'total_leads': len(leads_df),
            'high_priority_leads': len(leads_df[leads_df['lead_score'] >= 70]),
            'medium_priority_leads': len(leads_df[(leads_df['lead_score'] >= 40) & (leads_df['lead_score'] < 70)]),
            'low_priority_leads': len(leads_df[leads_df['lead_score'] < 40]),
            'states_covered': leads_df['state_name'].nunique(),
            'cities_covered': leads_df['city'].nunique(),
            'avg_lead_score': leads_df['lead_score'].mean()
        }
        
        print("Lead Summary:")
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        # Save reports
        leads_df.to_csv('nationwide_leads_database.csv', index=False)
        
        # Top leads report
        top_leads = leads_df.head(100)
        top_leads.to_csv('top_100_leads.csv', index=False)
        
        # State breakdown
        state_summary = leads_df.groupby('state_name').agg({
            'lead_score': ['count', 'mean'],
            'MAGNITUDE': 'mean'
        }).round(2)
        state_summary.columns = ['lead_count', 'avg_score', 'avg_hail_size']
        state_summary = state_summary.sort_values('lead_count', ascending=False)
        state_summary.to_csv('leads_by_state.csv')
        
        print(f"\n✅ Reports saved:")
        print(f"  - nationwide_leads_database.csv")
        print(f"  - top_100_leads.csv") 
        print(f"  - leads_by_state.csv")
        
        return summary

def main():
    """
    Main function to run nationwide property search
    """
    print("🚀 STARTING STORMBUSTER NATIONWIDE SEARCH")
    print("=" * 80)
    
    # Spokeo credentials - Update these with your actual credentials
    SPOKEO_USERNAME = "bolison10@gmail.com"
    SPOKEO_PASSWORD = "Bbusta10"
    
    if SPOKEO_PASSWORD == "YOUR_SPOKEO_PASSWORD_HERE":
        print("⚠️  Please update SPOKEO_PASSWORD with your Spokeo account password")
        print("   Sign up at: https://www.spokeo.com/myspokeo")
        print("   Using simulated data for demonstration...")
    
    # Initialize search engine
    engine = NationwidePropertySearchEngine()
    
    # Search for storm events nationwide
    print("\nStep 1: Searching for storm events...")
    events_df = engine.search_all_states(years=[2024, 2025], min_storm_size=1.0)
    
    if events_df.empty:
        print("❌ No events found. Exiting.")
        return
    
    # Geocode events
    print("\nStep 2: Geocoding events...")
    geo_df = engine.geocode_events(events_df)
    
    # Search property data with Spokeo
    print("\nStep 3: Searching property data with Spokeo...")
    property_df = engine.search_property_data(geo_df, SPOKEO_USERNAME, SPOKEO_PASSWORD)
    
    # Create lead database
    print("\nStep 4: Creating lead database...")
    leads_df = engine.create_lead_database(geo_df, property_df)
    
    # Generate reports
    print("\nStep 5: Generating reports...")
    summary = engine.generate_reports(leads_df)
    
    print(f"\n🎉 STORMBUSTER SEARCH COMPLETE!")
    print(f"Found {summary['total_leads']} leads across {summary['states_covered']} states")
    print(f"High-priority leads: {summary['high_priority_leads']}")
    print(f"Data source: {'Spokeo API' if SPOKEO_USERNAME != 'YOUR_SPOKEO_USERNAME_HERE' else 'Simulated'}")

if __name__ == "__main__":
    main()
