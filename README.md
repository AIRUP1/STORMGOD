# Hail Property Tracker with AI Zipcode Analysis

A comprehensive property tracking system that monitors hail events and provides AI-powered zipcode risk analysis with advanced reverse geocoding capabilities.

## Features

- **Hail Event Tracking**: Collects and processes hail reports from NOAA SPC
- **AI Zipcode Analysis**: Intelligent risk assessment for zipcodes based on historical hail data
- **Risk Scoring**: Automated risk scoring (0-100) with confidence levels
- **Smart Recommendations**: AI-generated recommendations for property protection
- **Batch Processing**: Analyze single or multiple zipcodes at once
- **Multiple Export Formats**: JSON and CSV export options
- **Enhanced Reverse Geocoding**: Google Maps and Mapbox integration for accurate address data
- **PeekYou Integration**: Reverse address lookup for property and contact information
- **Unified Geocoding**: Automatic fallback between multiple geocoding providers

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Set up API keys for enhanced features:
```bash
# For AI analysis
export OPENAI_API_KEY="your-api-key-here"

# For enhanced reverse geocoding (choose one or both)
export GOOGLE_MAPS_API_KEY="your-google-maps-api-key"
export MAPBOX_ACCESS_TOKEN="your-mapbox-token"

# For PeekYou reverse address lookup
export PEEKYOU_API_KEY="your-peekyou-api-key"
export PEEKYOU_API_SECRET="your-peekyou-api-secret"

# Preferred geocoding provider (google_maps or mapbox)
export GEOCODING_PROVIDER="google_maps"
```

**Note**: The system works without API keys using basic geocoding (pgeocode), but enhanced features require API keys.

## Usage

### Step 1: Collect Hail Data

#### Basic Mode (No API keys required)
```bash
python tx_hail_reports_enhanced.py --basic-only
```

#### Enhanced Mode (With Google Maps/Mapbox)
```bash
python tx_hail_reports_enhanced.py --use-enhanced
```

#### Full Mode (With PeekYou reverse address lookup)
```bash
python tx_hail_reports_enhanced.py --use-enhanced --use-peekyou
```

This will generate `tx_hail_reports.json` and `tx_hail_reports.csv` files with enhanced address data.

### Step 2: Analyze Zipcodes

#### Analyze a Single Zipcode
```bash
python main.py --zipcode 75001
```

#### Analyze Multiple Zipcodes
```bash
python main.py --zipcodes 75001 75002 75003
```

#### Analyze All Zipcodes in Data
```bash
python main.py --all
```

#### Export to CSV
```bash
python main.py --all --export-csv
```

#### Use Custom Hail Data File
```bash
python main.py --zipcode 75001 --hail-data path/to/your/hail_data.json
```

## AI Zipcode Analysis Features

### Risk Assessment
- **Risk Score**: 0-100 scale based on hail frequency and severity
- **Risk Levels**: Low, Medium, High, Very High
- **Confidence Score**: Indicates reliability of the analysis

### Analysis Components
1. **Hail Statistics**: Frequency and average size of hail events
2. **Weather Patterns**: AI-generated insights about weather patterns
3. **Demographics**: (Requires API integration) Demographic information
4. **Recommendations**: Personalized recommendations for property protection

### AI Capabilities

The tool supports two modes:

1. **AI-Powered Mode** (with OpenAI API):
   - Advanced natural language insights
   - Context-aware recommendations
   - Detailed weather pattern analysis

2. **Rule-Based Mode** (default):
   - Works without API keys
   - Fast and reliable
   - Basic risk assessment and recommendations

## Output Format

### JSON Output
```json
{
  "zipcode": "75001",
  "risk_score": 65.5,
  "risk_level": "High",
  "hail_frequency": 8,
  "avg_hail_size": 1.25,
  "recommendations": [
    "Consider installing impact-resistant roofing materials",
    "Review and update property insurance coverage"
  ],
  "weather_patterns": "...",
  "analysis_date": "2025-11-07T10:30:00",
  "confidence_score": 0.9
}
```

### CSV Output
Exports all analyses to a CSV file with columns:
- zipcode
- risk_score
- risk_level
- hail_frequency
- avg_hail_size
- confidence_score
- recommendations
- weather_patterns
- analysis_date

## Integration with Hail Tracker

The AI zipcode analyzer integrates seamlessly with the hail tracker:

1. Run `tx_hail_reports.py` to collect hail data
2. The analyzer automatically loads and processes the data
3. Generate comprehensive risk assessments for any zipcode

## Example Workflow

```bash
# 1. Collect hail reports
python tx_hail_reports.py

# 2. Analyze specific zipcodes of interest
python main.py --zipcodes 75001 75002 75003

# 3. Export results for reporting
python main.py --all --export-csv
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: OpenAI API key for advanced AI features

### Command Line Options
- `--zipcode`: Analyze single zipcode
- `--zipcodes`: Analyze multiple zipcodes (space-separated)
- `--all`: Analyze all zipcodes in hail data
- `--hail-data`: Path to hail reports JSON file
- `--export-csv`: Export results to CSV
- `--openai-key`: OpenAI API key (alternative to env var)

## Requirements

- Python 3.8+
- See `requirements.txt` for full dependency list

## Reverse Geocoding Features

### Supported Services

1. **Google Maps Geocoding API**
   - High accuracy address data
   - Comprehensive address components
   - Place IDs for unique identification

2. **Mapbox Geocoding API**
   - Alternative to Google Maps
   - Good coverage and accuracy
   - Flexible pricing options

3. **PeekYou Reverse Address Lookup**
   - Property information
   - Associated names and contacts
   - Social profiles and additional data

4. **Basic Geocoding (pgeocode)**
   - No API keys required
   - Offline database
   - Basic ZIP code and city data

### Usage Examples

```python
from reverse_geocoding import UnifiedReverseGeocoder

# Initialize with API keys
geocoder = UnifiedReverseGeocoder(
    google_api_key="your-key",
    mapbox_token="your-token",
    peekyou_api_key="your-key",
    peekyou_api_secret="your-secret"
)

# Reverse geocode coordinates
address = geocoder.reverse_geocode(32.7767, -96.7970)
print(f"Address: {address.formatted_address}")

# Enhanced lookup with PeekYou
result = geocoder.enhanced_reverse_geocode(32.7767, -96.7970)
print(f"PeekYou data: {result['peekyou_data']}")
```

## Project Structure

```
.
├── tx_hail_reports.py              # Original hail data collection script
├── tx_hail_reports_enhanced.py     # Enhanced version with reverse geocoding
├── reverse_geocoding.py             # Reverse geocoding module
├── ai_zipcode_analyzer.py          # AI analysis engine
├── main.py                         # Main application
├── example_usage.py                 # Usage examples
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
└── tx_hail_reports.json            # Generated hail data (after running tracker)
```

## Advanced Usage

### Programmatic Usage

```python
from ai_zipcode_analyzer import AIZipcodeAnalyzer

# Initialize analyzer
analyzer = AIZipcodeAnalyzer(openai_api_key="your-key")

# Load hail data
analyzer.load_hail_data("tx_hail_reports.json")

# Analyze zipcode
analysis = analyzer.analyze_zipcode("75001")

# Access results
print(f"Risk Score: {analysis.risk_score}")
print(f"Risk Level: {analysis.risk_level}")
print(f"Recommendations: {analysis.recommendations}")

# Batch analysis
analyses = analyzer.analyze_multiple_zipcodes(["75001", "75002", "75003"])
```

## Troubleshooting

### No Hail Data Found
- Ensure you've run `tx_hail_reports.py` first
- Check that `tx_hail_reports.json` exists in the current directory
- Use `--hail-data` to specify a custom path

### OpenAI API Errors
- Verify your API key is correct
- Check your API quota/credi