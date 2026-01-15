#!/usr/bin/env python3
"""
Roofing Contractors Integration for StormBuster
Professional Roofing Contractors - "Let us take it from here - fast & easy"
"""

import pandas as pd
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
class RoofingIntegration:
    def __init__(self):
        self.company_name = "Roofing Contractors"
        self.tagline = "Let us take it from here - fast & easy"
        self.services = [
            "Roof Replacement",
            "Storm Damage Assessment", 
            "Insurance Claims Assistance",
            "Emergency Roof Repairs",
            "Roof Inspections",
            "Gutter Installation",
            "Siding Replacement",
            "Window Replacement"
        ]
        self.coverage_areas = [
            "Dallas-Fort Worth Metroplex",
            "North Texas",
            "East Texas", 
            "Central Texas",
            "Houston Area",
            "Austin Area",
            "San Antonio Area"
        ]
        self.contact_info = {
            "phone": "(972) 818-2441",
            "email": "busterolison@results-roofing.com",
            "email_alt": "brandonsteward@resultsroofing.com",
            "website": "www.results-roofing.com",
            "address": "2828 E Trinity Mills Rd, Ste. 212, Carrollton, TX 75006"
        }
        
    def assess_roof_damage(self, property_data: Dict) -> Dict:
        """
        Assess roof damage based on storm data
        """
        assessment = {
            "property_address": property_data.get('address', ''),
            "storm_date": property_data.get('date', ''),
            "hail_size": property_data.get('hail_size', ''),
            "damage_probability": self._calculate_damage_probability(property_data),
            "recommended_action": self._get_recommended_action(property_data),
            "estimated_cost": self._estimate_repair_cost(property_data),
            "insurance_claim_likely": self._assess_insurance_claim(property_data),
            "urgency_level": self._determine_urgency(property_data),
            "next_steps": self._get_next_steps(property_data)
        }
        
        return assessment
    
    def _calculate_damage_probability(self, property_data: Dict) -> str:
        """Calculate probability of roof damage"""
        hail_size = float(property_data.get('hail_size', '0').replace('"', ''))
        
        if hail_size >= 2.0:
            return "High (90%+)"
        elif hail_size >= 1.5:
            return "Medium-High (70-90%)"
        elif hail_size >= 1.0:
            return "Medium (50-70%)"
        else:
            return "Low (30-50%)"
    
    def _get_recommended_action(self, property_data: Dict) -> str:
        """Get recommended action based on damage assessment"""
        hail_size = float(property_data.get('hail_size', '0').replace('"', ''))
        
        if hail_size >= 2.0:
            return "Immediate roof replacement recommended"
        elif hail_size >= 1.5:
            return "Professional inspection and likely replacement"
        elif hail_size >= 1.0:
            return "Professional inspection recommended"
        else:
            return "Visual inspection sufficient"
    
    def _estimate_repair_cost(self, property_data: Dict) -> Dict:
        """Estimate repair costs"""
        hail_size = float(property_data.get('hail_size', '0').replace('"', ''))
        property_value = property_data.get('property_value', '$300,000')
        
        # Extract numeric value
        try:
            prop_val_num = float(property_value.replace('$', '').replace(',', ''))
        except:
            prop_val_num = 300000
        
        # Base cost estimates
        if hail_size >= 2.0:
            base_cost = prop_val_num * 0.08  # 8% of property value
            cost_range = f"${base_cost * 0.8:,.0f} - ${base_cost * 1.2:,.0f}"
        elif hail_size >= 1.5:
            base_cost = prop_val_num * 0.06  # 6% of property value
            cost_range = f"${base_cost * 0.8:,.0f} - ${base_cost * 1.2:,.0f}"
        elif hail_size >= 1.0:
            base_cost = prop_val_num * 0.04  # 4% of property value
            cost_range = f"${base_cost * 0.8:,.0f} - ${base_cost * 1.2:,.0f}"
        else:
            base_cost = prop_val_num * 0.02  # 2% of property value
            cost_range = f"${base_cost * 0.8:,.0f} - ${base_cost * 1.2:,.0f}"
        
        return {
            "estimated_range": cost_range,
            "insurance_coverage": "Likely covered with proper documentation",
            "out_of_pocket": f"${base_cost * 0.1:,.0f} - ${base_cost * 0.2:,.0f} (deductible)"
        }
    
    def _assess_insurance_claim(self, property_data: Dict) -> Dict:
        """Assess insurance claim likelihood and process"""
        hail_size = float(property_data.get('hail_size', '0').replace('"', ''))
        
        if hail_size >= 1.0:
            claim_likely = True
            claim_strength = "Strong"
            documentation_needed = [
                "Storm date verification",
                "Hail size documentation", 
                "Property photos",
                "Professional inspection report",
                "Repair estimates"
            ]
        else:
            claim_likely = False
            claim_strength = "Weak"
            documentation_needed = [
                "Professional inspection",
                "Damage photos",
                "Storm verification"
            ]
        
        return {
            "claim_likely": claim_likely,
            "claim_strength": claim_strength,
            "documentation_needed": documentation_needed,
            "timeline": "File within 30 days of storm for best results"
        }
    
    def _determine_urgency(self, property_data: Dict) -> str:
        """Determine urgency of roof work"""
        hail_size = float(property_data.get('hail_size', '0').replace('"', ''))
        days_since_storm = self._days_since_storm(property_data.get('date', ''))
        
        if hail_size >= 2.0 and days_since_storm <= 7:
            return "Critical - Immediate action required"
        elif hail_size >= 1.5 and days_since_storm <= 14:
            return "High - Schedule within 1 week"
        elif hail_size >= 1.0 and days_since_storm <= 30:
            return "Medium - Schedule within 2 weeks"
        else:
            return "Low - Schedule when convenient"
    
    def _days_since_storm(self, storm_date: str) -> int:
        """Calculate days since storm"""
        try:
            storm_dt = datetime.strptime(storm_date, '%Y-%m-%d')
            return (datetime.now() - storm_dt).days
        except:
            return 30  # Default to 30 days if date parsing fails
    
    def _get_next_steps(self, property_data: Dict) -> List[str]:
        """Get recommended next steps"""
        steps = [
            "Contact Results Roofing for free inspection",
            "Document storm damage with photos",
            "Review insurance policy coverage",
            "Schedule professional assessment",
            "Get detailed repair estimate",
            "File insurance claim if applicable",
            "Schedule roof work"
        ]
        
        return steps
    
    def generate_roofing_lead(self, property_data: Dict) -> Dict:
        """Generate a roofing lead for Results Roofing"""
        assessment = self.assess_roof_damage(property_data)
        
        lead = {
            "lead_id": f"RR_{int(time.time())}",
            "company": "Results Roofing",
            "property_owner": property_data.get('name', ''),
            "property_address": property_data.get('address', ''),
            "contact_phone": property_data.get('phone', ''),
            "contact_email": property_data.get('email', ''),
            "property_value": property_data.get('property_value', ''),
            "storm_date": property_data.get('date', ''),
            "hail_size": property_data.get('hail_size', ''),
            "damage_probability": assessment['damage_probability'],
            "recommended_action": assessment['recommended_action'],
            "estimated_cost": assessment['estimated_cost'],
            "urgency_level": assessment['urgency_level'],
            "insurance_claim_likely": assessment['insurance_claim_likely']['claim_likely'],
            "lead_score": self._calculate_lead_score(property_data),
            "created_at": datetime.now().isoformat(),
            "status": "New",
            "assigned_to": "Results Roofing Team"
        }
        
        return lead
    
    def _calculate_lead_score(self, property_data: Dict) -> int:
        """Calculate lead score for roofing services"""
        score = 0
        
        # Hail size scoring
        hail_size = float(property_data.get('hail_size', '0').replace('"', ''))
        if hail_size >= 2.0:
            score += 50
        elif hail_size >= 1.5:
            score += 35
        elif hail_size >= 1.0:
            score += 20
        
        # Property value scoring
        property_value = property_data.get('property_value', '$300,000')
        try:
            prop_val_num = float(property_value.replace('$', '').replace(',', ''))
            if prop_val_num >= 500000:
                score += 30
            elif prop_val_num >= 300000:
                score += 20
            elif prop_val_num >= 200000:
                score += 10
        except:
            score += 10
        
        # Recency scoring
        days_since_storm = self._days_since_storm(property_data.get('date', ''))
        if days_since_storm <= 7:
            score += 20
        elif days_since_storm <= 14:
            score += 15
        elif days_since_storm <= 30:
            score += 10
        
        return min(score, 100)  # Cap at 100
    
    def create_roofing_report(self, leads: List[Dict]) -> Dict:
        """Create comprehensive roofing report"""
        if not leads:
            return {"error": "No leads provided"}
        
        total_leads = len(leads)
        high_priority = len([l for l in leads if l['lead_score'] >= 70])
        medium_priority = len([l for l in leads if 40 <= l['lead_score'] < 70])
        low_priority = len([l for l in leads if l['lead_score'] < 40])
        
        total_estimated_value = 0
        for lead in leads:
            try:
                cost_range = lead['estimated_cost']['estimated_range']
                # Extract average cost
                costs = cost_range.replace('$', '').replace(',', '').split(' - ')
                avg_cost = (float(costs[0]) + float(costs[1])) / 2
                total_estimated_value += avg_cost
            except:
                continue
        
        report = {
            "company": "Results Roofing",
            "report_date": datetime.now().isoformat(),
            "summary": {
                "total_leads": total_leads,
                "high_priority_leads": high_priority,
                "medium_priority_leads": medium_priority,
                "low_priority_leads": low_priority,
                "total_estimated_value": f"${total_estimated_value:,.0f}",
                "average_lead_value": f"${total_estimated_value/total_leads:,.0f}" if total_leads > 0 else "$0"
            },
            "top_leads": sorted(leads, key=lambda x: x['lead_score'], reverse=True)[:10],
            "service_opportunities": {
                "roof_replacements": len([l for l in leads if 'replacement' in l['recommended_action'].lower()]),
                "inspections_needed": len([l for l in leads if 'inspection' in l['recommended_action'].lower()]),
                "insurance_claims": len([l for l in leads if l['insurance_claim_likely']])
            }
        }
        
        return report

def roofing_with_stormbuster():
    """
    Integrate  Roofing with StormBuser lead generation
    """
    print("🏠 INTEGRATING RESULTS ROOFING WITH STORMBUSTER")
    print("=" * 60)
    print("Company: Roofing Contractors")
    print("Tagline: 'Let us take it from here - fast & easy'")
    print("Services: Roof Replacement, Storm Damage Assessment, Claims Assistance")
    print("=" * 60)
    
    # Initialize Results Roofing integration
    roofing_integration = RoofingIntegration()
    
    # Sample property data for demonstration
    sample_properties = [
        {
            "name": "John Smith",
            "address": "123 Main St, Dallas, TX",
            "phone": "(555) 123-4567",
            "email": "john@example.com",
            "property_value": "$350,000",
            "date": "2024-01-15",
            "hail_size": "1.75"
        },
        {
            "name": "Jane Doe",
            "address": "456 Oak Ave, Fort Worth, TX",
            "phone": "(555) 987-6543",
            "email": "jane@example.com",
            "property_value": "$280,000",
            "date": "2024-01-20",
            "hail_size": "2.25"
        }
    ]
    
    # Generate roofing leads
    roofing_leads = []
    for property_data in sample_properties:
        lead = roofing_integration.generate_roofing_lead(property_data)
        roofing_leads.append(lead)
    
    # Create roofing report
    roofing_report = roofing_integration.create_roofing_report(roofing_leads)
    
    # Save leads to CSV
    df = pd.DataFrame(roofing_leads)
    df.to_csv('results_roofing_leads.csv', index=False)
    
    # Save roofing report
    with open('results_roofing_report.json', 'w') as f:
        json.dump(roofing_report, f, indent=2)
    
    print(f"\n✅ Results Roofing Integration Complete!")
    print(f"📊 Generated {len(roofing_leads)} roofing leads")
    print(f"💰 Total estimated project value: {roofing_report['summary']['total_estimated_value']}")
    print(f"🏆 High-priority leads: {roofing_report['summary']['high_priority_leads']}")
    print(f"📁 Files saved:")
    print(f"   - results_roofing_leads.csv")
    print(f"   - results_roofing_report.json")
    
    return roofing_leads, roofing_report

if __name__ == "__main__":
    roofing_with_stormbuster()
