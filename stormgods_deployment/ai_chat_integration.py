#!/usr/bin/env python3
"""
StormBuster AI Chat Integration
Multi-provider AI chat system with ChatGPT, Claude, Gemini, and more
"""

import os
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

class AIProvider(Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"
    REPLICATE = "replicate"

@dataclass
class AIModel:
    """AI Model configuration"""
    name: str
    provider: AIProvider
    model_id: str
    max_tokens: int
    cost_per_token: float
    capabilities: List[str]

@dataclass
class ChatMessage:
    """Chat message structure"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    cost: Optional[float] = None

class AIProviderClient:
    """Base class for AI provider clients"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def chat_completion(self, messages: List[Dict], model: str, **kwargs) -> Dict:
        """Abstract method for chat completion"""
        raise NotImplementedError

class OpenAIClient(AIProviderClient):
    """OpenAI API client"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://api.openai.com/v1"
    
    def chat_completion(self, messages: List[Dict], model: str, **kwargs) -> Dict:
        """OpenAI chat completion"""
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": kwargs.get('max_tokens', 1000),
            "temperature": kwargs.get('temperature', 0.7),
            "stream": kwargs.get('stream', False)
        }
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}

class AnthropicClient(AIProviderClient):
    """Anthropic Claude API client"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://api.anthropic.com/v1"
        self.session.headers.update({
            'anthropic-version': '2023-06-01'
        })
    
    def chat_completion(self, messages: List[Dict], model: str, **kwargs) -> Dict:
        """Anthropic Claude chat completion"""
        url = f"{self.base_url}/messages"
        
        # Convert OpenAI format to Anthropic format
        system_message = None
        conversation_messages = []
        
        for msg in messages:
            if msg['role'] == 'system':
                system_message = msg['content']
            else:
                conversation_messages.append(msg)
        
        payload = {
            "model": model,
            "messages": conversation_messages,
            "max_tokens": kwargs.get('max_tokens', 1000),
            "temperature": kwargs.get('temperature', 0.7)
        }
        
        if system_message:
            payload["system"] = system_message
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}

class GoogleClient(AIProviderClient):
    """Google Gemini API client"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
    
    def chat_completion(self, messages: List[Dict], model: str, **kwargs) -> Dict:
        """Google Gemini chat completion"""
        url = f"{self.base_url}/models/{model}:generateContent"
        
        # Convert to Gemini format
        contents = []
        for msg in messages:
            if msg['role'] != 'system':
                contents.append({
                    "role": msg['role'],
                    "parts": [{"text": msg['content']}]
                })
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": kwargs.get('max_tokens', 1000),
                "temperature": kwargs.get('temperature', 0.7)
            }
        }
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}

class StormBusterAIChat:
    """Main AI Chat system for StormBuster"""
    
    def __init__(self):
        self.providers = {}
        self.models = {}
        self.chat_history = []
        self.usage_stats = {}
        
        # Initialize AI models
        self._initialize_models()
        
        # Initialize providers
        self._initialize_providers()
    
    def _initialize_models(self):
        """Initialize available AI models"""
        self.models = {
            # OpenAI Models
            'gpt-3.5-turbo': AIModel(
                name='ChatGPT-3.5 Turbo',
                provider=AIProvider.OPENAI,
                model_id='gpt-3.5-turbo',
                max_tokens=4096,
                cost_per_token=0.000002,
                capabilities=['chat', 'storm_analysis', 'basic_reasoning']
            ),
            'gpt-4': AIModel(
                name='ChatGPT-4',
                provider=AIProvider.OPENAI,
                model_id='gpt-4',
                max_tokens=8192,
                cost_per_token=0.00003,
                capabilities=['chat', 'storm_analysis', 'advanced_reasoning', 'code_generation']
            ),
            'gpt-4-turbo': AIModel(
                name='ChatGPT-4 Turbo',
                provider=AIProvider.OPENAI,
                model_id='gpt-4-turbo',
                max_tokens=128000,
                cost_per_token=0.00001,
                capabilities=['chat', 'storm_analysis', 'advanced_reasoning', 'code_generation', 'vision']
            ),
            'gpt-4-vision': AIModel(
                name='ChatGPT-4 Vision',
                provider=AIProvider.OPENAI,
                model_id='gpt-4-vision-preview',
                max_tokens=4096,
                cost_per_token=0.00001,
                capabilities=['chat', 'storm_analysis', 'vision', 'image_analysis']
            ),
            
            # Anthropic Models
            'claude-3': AIModel(
                name='Claude-3 Haiku',
                provider=AIProvider.ANTHROPIC,
                model_id='claude-3-haiku-20240307',
                max_tokens=200000,
                cost_per_token=0.00000025,
                capabilities=['chat', 'storm_analysis', 'reasoning', 'long_context']
            ),
            'claude-3-opus': AIModel(
                name='Claude-3 Opus',
                provider=AIProvider.ANTHROPIC,
                model_id='claude-3-opus-20240229',
                max_tokens=200000,
                cost_per_token=0.000015,
                capabilities=['chat', 'storm_analysis', 'advanced_reasoning', 'long_context', 'analysis']
            ),
            'claude-3-sonnet': AIModel(
                name='Claude-3 Sonnet',
                provider=AIProvider.ANTHROPIC,
                model_id='claude-3-sonnet-20240229',
                max_tokens=200000,
                cost_per_token=0.000003,
                capabilities=['chat', 'storm_analysis', 'reasoning', 'long_context', 'code_generation']
            ),
            
            # Google Models
            'gemini-pro': AIModel(
                name='Gemini Pro',
                provider=AIProvider.GOOGLE,
                model_id='gemini-pro',
                max_tokens=32768,
                cost_per_token=0.0000005,
                capabilities=['chat', 'storm_analysis', 'reasoning', 'multimodal']
            ),
            'gemini-1.5-pro': AIModel(
                name='Gemini 1.5 Pro',
                provider=AIProvider.GOOGLE,
                model_id='gemini-1.5-pro',
                max_tokens=1048576,
                cost_per_token=0.00000125,
                capabilities=['chat', 'storm_analysis', 'advanced_reasoning', 'multimodal', 'long_context']
            ),
            'gemini-3.5-pro': AIModel(
                name='Gemini 3.5 Pro',
                provider=AIProvider.GOOGLE,
                model_id='gemini-3.5-pro',
                max_tokens=2097152,
                cost_per_token=0.00000125,
                capabilities=['chat', 'storm_analysis', 'advanced_reasoning', 'multimodal', 'analysis']
            ),
            'gemini-ultra': AIModel(
                name='Gemini Ultra',
                provider=AIProvider.GOOGLE,
                model_id='gemini-ultra',
                max_tokens=32768,
                cost_per_token=0.00000125,
                capabilities=['chat', 'storm_analysis', 'advanced_reasoning', 'multimodal', 'analysis']
            )
        }
    
    def _initialize_providers(self):
        """Initialize AI provider clients"""
        # OpenAI
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            self.providers[AIProvider.OPENAI] = OpenAIClient(openai_key)
        
        # Anthropic
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key:
            self.providers[AIProvider.ANTHROPIC] = AnthropicClient(anthropic_key)
        
        # Google
        google_key = os.getenv('GOOGLE_API_KEY')
        if google_key:
            self.providers[AIProvider.GOOGLE] = GoogleClient(google_key)
    
    def get_available_models(self, subscription_tier: str = 'basic') -> List[Dict]:
        """Get available models based on subscription tier"""
        tier_models = {
            'basic': ['gpt-3.5-turbo'],
            'professional': ['gpt-3.5-turbo', 'gpt-4', 'claude-3'],
            'enterprise': ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo', 'claude-3', 'claude-3-opus', 'gemini-pro', 'gemini-1.5-pro', 'gemini-3.5-pro'],
            'extreme': list(self.models.keys())
        }
        
        available_models = tier_models.get(subscription_tier, tier_models['basic'])
        
        return [
            {
                'id': model_id,
                'name': self.models[model_id].name,
                'provider': self.models[model_id].provider.value,
                'capabilities': self.models[model_id].capabilities,
                'max_tokens': self.models[model_id].max_tokens
            }
            for model_id in available_models
            if model_id in self.models
        ]
    
    def send_message(self, message: str, model_id: str, subscription_tier: str = 'basic', 
                    context: Optional[str] = None) -> Dict:
        """Send a message to the AI and get response"""
        try:
            # Check if model is available for subscription tier
            available_models = self.get_available_models(subscription_tier)
            if not any(m['id'] == model_id for m in available_models):
                return {
                    'success': False,
                    'error': f'Model {model_id} not available for {subscription_tier} tier'
                }
            
            # Get model configuration
            if model_id not in self.models:
                return {
                    'success': False,
                    'error': f'Model {model_id} not found'
                }
            
            model_config = self.models[model_id]
            provider = model_config.provider
            
            # Check if provider is available
            if provider not in self.providers:
                return {
                    'success': False,
                    'error': f'Provider {provider.value} not configured'
                }
            
            # Prepare messages
            messages = []
            
            # Add system context for storm analysis
            if context or 'storm' in message.lower():
                system_prompt = self._get_storm_analysis_prompt()
                messages.append({'role': 'system', 'content': system_prompt})
            
            # Add user message
            messages.append({'role': 'user', 'content': message})
            
            # Add chat history (last 10 messages)
            recent_history = self.chat_history[-10:] if len(self.chat_history) > 10 else self.chat_history
            for msg in recent_history:
                messages.append({'role': msg.role, 'content': msg.content})
            
            # Send request to AI provider
            client = self.providers[provider]
            response = client.chat_completion(
                messages=messages,
                model=model_config.model_id,
                max_tokens=min(1000, model_config.max_tokens),
                temperature=0.7
            )
            
            if 'error' in response:
                return {
                    'success': False,
                    'error': response['error']
                }
            
            # Extract response
            if provider == AIProvider.OPENAI:
                ai_response = response['choices'][0]['message']['content']
                tokens_used = response['usage']['total_tokens']
            elif provider == AIProvider.ANTHROPIC:
                ai_response = response['content'][0]['text']
                tokens_used = response['usage']['input_tokens'] + response['usage']['output_tokens']
            elif provider == AIProvider.GOOGLE:
                ai_response = response['candidates'][0]['content']['parts'][0]['text']
                tokens_used = response['usageMetadata']['totalTokenCount']
            else:
                ai_response = "Response format not supported"
                tokens_used = 0
            
            # Calculate cost
            cost = tokens_used * model_config.cost_per_token
            
            # Create message objects
            user_msg = ChatMessage(
                role='user',
                content=message,
                timestamp=datetime.now()
            )
            
            ai_msg = ChatMessage(
                role='assistant',
                content=ai_response,
                timestamp=datetime.now(),
                model_used=model_id,
                tokens_used=tokens_used,
                cost=cost
            )
            
            # Store in chat history
            self.chat_history.extend([user_msg, ai_msg])
            
            # Update usage stats
            self._update_usage_stats(subscription_tier, tokens_used, cost)
            
            return {
                'success': True,
                'response': ai_response,
                'model_used': model_id,
                'tokens_used': tokens_used,
                'cost': cost,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_storm_analysis_prompt(self) -> str:
        """Get system prompt for storm damage analysis"""
        return """You are StormBuster AI, an expert in storm damage analysis and lead generation for roofing contractors. 

Your expertise includes:
- Analyzing weather data and storm patterns
- Assessing property damage probability
- Identifying high-value leads for roofing contractors
- Providing insights on insurance claims and damage assessment
- Recommending optimal contact strategies

When analyzing storm data, consider:
- Hail size and intensity
- Property values and demographics
- Historical damage patterns
- Insurance claim likelihood
- Seasonal factors
- Geographic risk factors

Always provide actionable insights for roofing contractors to maximize their lead conversion rates."""
    
    def _update_usage_stats(self, subscription_tier: str, tokens_used: int, cost: float):
        """Update usage statistics"""
        if subscription_tier not in self.usage_stats:
            self.usage_stats[subscription_tier] = {
                'total_tokens': 0,
                'total_cost': 0.0,
                'message_count': 0,
                'last_updated': datetime.now()
            }
        
        self.usage_stats[subscription_tier]['total_tokens'] += tokens_used
        self.usage_stats[subscription_tier]['total_cost'] += cost
        self.usage_stats[subscription_tier]['message_count'] += 1
        self.usage_stats[subscription_tier]['last_updated'] = datetime.now()
    
    def get_usage_stats(self, subscription_tier: str) -> Dict:
        """Get usage statistics for subscription tier"""
        return self.usage_stats.get(subscription_tier, {
            'total_tokens': 0,
            'total_cost': 0.0,
            'message_count': 0,
            'last_updated': None
        })
    
    def analyze_storm_data(self, storm_data: Dict, model_id: str = 'gpt-4') -> Dict:
        """Analyze storm data using AI"""
        analysis_prompt = f"""
        Analyze the following storm data and provide insights for roofing contractors:
        
        Storm Data:
        - Date: {storm_data.get('date', 'Unknown')}
        - Location: {storm_data.get('location', 'Unknown')}
        - Hail Size: {storm_data.get('hail_size', 'Unknown')}
        - Property Count: {storm_data.get('property_count', 'Unknown')}
        - Average Property Value: {storm_data.get('avg_property_value', 'Unknown')}
        
        Please provide:
        1. Damage probability assessment
        2. Lead quality scoring
        3. Recommended contact strategy
        4. Insurance claim likelihood
        5. Optimal timing for outreach
        """
        
        return self.send_message(analysis_prompt, model_id, 'professional')
    
    def generate_lead_insights(self, lead_data: Dict, model_id: str = 'claude-3') -> Dict:
        """Generate insights for individual leads"""
        insight_prompt = f"""
        Analyze this roofing lead and provide contractor recommendations:
        
        Lead Data:
        - Property Owner: {lead_data.get('owner_name', 'Unknown')}
        - Address: {lead_data.get('address', 'Unknown')}
        - Property Value: {lead_data.get('property_value', 'Unknown')}
        - Storm Date: {lead_data.get('storm_date', 'Unknown')}
        - Hail Size: {lead_data.get('hail_size', 'Unknown')}
        - Contact Info: {lead_data.get('phone', 'Unknown')}
        
        Provide:
        1. Lead quality score (1-10)
        2. Contact approach recommendations
        3. Estimated project value
        4. Best contact timing
        5. Potential objections and responses
        """
        
        return self.send_message(insight_prompt, model_id, 'professional')
    
    def get_chat_history(self, limit: int = 50) -> List[Dict]:
        """Get chat history"""
        recent_messages = self.chat_history[-limit:] if len(self.chat_history) > limit else self.chat_history
        
        return [
            {
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
                'model_used': msg.model_used,
                'tokens_used': msg.tokens_used,
                'cost': msg.cost
            }
            for msg in recent_messages
        ]
    
    def clear_chat_history(self):
        """Clear chat history"""
        self.chat_history = []
    
    def export_chat_history(self) -> str:
        """Export chat history as JSON"""
        return json.dumps(self.get_chat_history(), indent=2)

# Global AI Chat instance
ai_chat = StormBusterAIChat()

def main():
    """Test the AI Chat system"""
    print("🤖 StormBuster AI Chat Integration")
    print("=" * 50)
    
    # Test basic functionality
    print("\n📋 Available Models:")
    models = ai_chat.get_available_models('professional')
    for model in models:
        print(f"  • {model['name']} ({model['provider']})")
    
    # Test storm analysis
    print("\n🌩️  Testing Storm Analysis:")
    storm_data = {
        'date': '2024-01-15',
        'location': 'Dallas, TX',
        'hail_size': '2.5 inches',
        'property_count': 150,
        'avg_property_value': '$350,000'
    }
    
    analysis = ai_chat.analyze_storm_data(storm_data)
    if analysis['success']:
        print(f"✅ Analysis completed using {analysis['model_used']}")
        print(f"📊 Tokens used: {analysis['tokens_used']}")
        print(f"💰 Cost: ${analysis['cost']:.4f}")
        print(f"🤖 Response: {analysis['response'][:200]}...")
    else:
        print(f"❌ Analysis failed: {analysis['error']}")
    
    # Test usage stats
    print("\n📈 Usage Statistics:")
    stats = ai_chat.get_usage_stats('professional')
    print(f"  Total tokens: {stats['total_tokens']:,}")
    print(f"  Total cost: ${stats['total_cost']:.4f}")
    print(f"  Messages: {stats['message_count']}")

if __name__ == "__main__":
    main()
