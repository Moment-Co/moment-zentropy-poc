#!/usr/bin/env python3
"""
Enhanced LLM Metadata Filter for Streamlit App
Uses GPT-5 to interpret natural language queries and generate proper ZeroEntropy metadata filters
"""

import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dotenv import load_dotenv

# OpenAI integration
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class EnhancedLLMMetadataFilter:
    """
    Advanced metadata filtering system that uses OpenAI GPT to interpret queries
    and generate precise ZeroEntropy metadata filters
    """
    
    def __init__(self, openai_api_key=None):
        # OpenAI setup
        self.openai_client = None
        if OPENAI_AVAILABLE and openai_api_key:
            self.openai_client = OpenAI(api_key=openai_api_key)
        elif not openai_api_key:
            # Try to get from environment
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
    
    def interpret_query_with_gpt(self, query: str) -> Dict[str, Any]:
        """
        Use OpenAI GPT to interpret the natural language query and generate metadata filters
        """
        if not self.openai_client:
            return {"error": "OpenAI client not available"}
        
        try:
            # Get today's date for context
            today = datetime.now()
            
            # Calculate various date references
            current_week_start = today - timedelta(days=today.weekday())
            current_week_end = current_week_start + timedelta(days=6)
            next_week_start = current_week_start + timedelta(days=7)
            next_week_end = next_week_start + timedelta(days=6)
            
            # Current month calculations
            current_month_start = today.replace(day=1)
            if today.month == 12:
                next_month_start = today.replace(year=today.year + 1, month=1, day=1)
            else:
                next_month_start = today.replace(month=today.month + 1, day=1)
            
            # Calculate next month end for display
            if next_month_start.month == 12:
                next_month_end = next_month_start.replace(year=next_month_start.year + 1, month=1, day=1)
            else:
                next_month_end = next_month_start.replace(month=next_month_start.month + 1, day=1)
            
            # Weekend calculations (assuming weekend is Saturday-Sunday)
            days_until_saturday = (5 - today.weekday()) % 7
            if days_until_saturday == 0:  # Today is Saturday
                this_weekend_start = today
                this_weekend_end = today + timedelta(days=1)
            else:
                this_weekend_start = today + timedelta(days=days_until_saturday)
                this_weekend_end = this_weekend_start + timedelta(days=1)
            
            next_weekend_start = this_weekend_start + timedelta(days=7)
            next_weekend_end = next_weekend_start + timedelta(days=1)
            
            # Create a system prompt that explains ZeroEntropy metadata filtering
            system_prompt = """You are an expert at interpreting natural language queries and converting them to ZeroEntropy metadata filters.

IMPORTANT: The sports data in this collection is from 2024, but use CURRENT REAL DATES for relative time references.

TODAY'S DATE CONTEXT: {today}

KEY DATE REFERENCES (use these EXACT current dates):
- Next Weekend: {next_weekend} to {next_weekend_end}
- This Week: {current_week} to {current_week_end}
- Next Week: {next_week} to {next_week_end}
- This Month: {current_month} to {next_month}
- Next Month: {next_month} to {next_month_end}

IMPORTANT RULES:
1. When users say "next weekend", "this week", "next month", etc., use the EXACT dates above (these are real current dates)
2. If the query does NOT specify a time period (e.g., "show me Liverpool games", "find Arsenal matches"), do NOT apply date filters - search the entire datastore
3. Only apply date filters when the user explicitly mentions time-related terms like "next weekend", "this month", "in August", etc.
4. For queries without time constraints, return "query_type": "semantic" and no metadata_filter
5. Be honest about data availability - if searching for 2025 dates but data is from 2024, the filter will find no results

ZeroEntropy supports these metadata operators:
- $eq: equals
- $ne: not equals  
- $gt: greater than
- $gte: greater than or equal to
- $lt: less than
- $lte: less than or equal to
- $in: in list
- $nin: not in list
- $and: logical AND
- $or: logical OR

Available metadata fields for sports games:
- home_team: string (team name)
- away_team: string (team name)
- venue: string (stadium name)
- date: string (YYYY-MM-DD format)
- league: string (e.g., "Premier League")
- status: string (e.g., "Completed", "Scheduled")
- home_score: string (score as string)
- away_score: string (score as string)

CRITICAL FILTER RULES:
- Each metadata field can only have ONE operator
- For date ranges, use separate filter conditions with $and
- Example: For "September 2024", use: {{"$and": [{{"date": {{"$gte": "2024-09-01"}}}}, {{"date": {{"$lte": "2024-09-30"}}}}]}}
- NEVER combine multiple operators for the same field like: {{"date": {{"$gte": "2024-09-01", "$lte": "2024-09-30"}}}}

Generate a JSON response with:
1. "intent": What the user is looking for
2. "metadata_filter": The ZeroEntropy filter object
3. "explanation": Human-readable explanation of the filter
4. "query_type": "filtered" if using metadata, "semantic" if just text search

Return ONLY a valid JSON object with this structure:
{{
  "intent": "brief description of what the query is looking for",
  "metadata_filter": {{ "filter_object_here" }},
  "explanation": "brief explanation of the filter logic",
  "query_type": "filtered"
}}"""

            # Format the system prompt with actual date values
            system_prompt = system_prompt.format(
                today=today.strftime('%A, %B %d, %Y'),
                current_week=current_week_start.strftime('%Y-%m-%d'),
                current_week_end=current_week_end.strftime('%Y-%m-%d'),
                next_week=next_week_start.strftime('%Y-%m-%d'),
                next_week_end=next_week_end.strftime('%Y-%m-%d'),
                current_month=current_month_start.strftime('%Y-%m-%d'),
                next_month=next_month_start.strftime('%Y-%m-%d'),
                next_month_end=next_month_end.strftime('%Y-%m-%d'),
                next_weekend=next_weekend_start.strftime('%Y-%m-%d'),
                next_weekend_end=next_weekend_end.strftime('%Y-%m-%d')
            )

            # User message with the query
            user_message = f"Interpret this query and generate a ZeroEntropy metadata filter: '{query}'"
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",  # Using GPT-4 for better compatibility
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500
            )
            
            # Parse the response
            gpt_response = response.choices[0].message.content
            print(f"🔍 Raw GPT Response: {gpt_response}")
            
            # Try to extract JSON from the response
            try:
                # Look for JSON content in the response
                json_match = re.search(r'\{.*\}', gpt_response, re.DOTALL)
                if json_match:
                    parsed_response = json.loads(json_match.group())
                    print(f"✅ Successfully parsed GPT JSON: {parsed_response}")
                    return parsed_response
                else:
                    print(f"⚠️ No JSON pattern found in response")
                    return {"error": "No valid JSON found in GPT response"}
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                print(f"Raw response: {gpt_response}")
                return {"error": f"Invalid JSON from GPT: {gpt_response}"}
                
        except Exception as e:
            print(f"❌ OpenAI API error in interpret_query_with_gpt: {e}")
            return {"error": f"OpenAI API error: {e}"}
    
    def create_date_filter_for_month(self, month: int, year: str = "2024") -> Dict[str, Any]:
        """
        Create a date filter for a specific month
        """
        # Get the last day of the month
        if month in [4, 6, 9, 11]:  # April, June, September, November
            last_day = 30
        elif month == 2:  # February
            if (int(year) % 4 == 0 and int(year) % 100 != 0) or (int(year) % 400 == 0):
                last_day = 29  # Leap year
            else:
                last_day = 28
        else:  # January, March, May, July, August, October, December
            last_day = 31
        
        start_date = f"{year}-{month:02d}-01"
        end_date = f"{year}-{month:02d}-{last_day}"
        
        return {
            "$and": [
                {"date": {"$gte": start_date}},
                {"date": {"$lte": end_date}}
            ]
        }
    
    def create_team_filter(self, team_name: str) -> Dict[str, Any]:
        """
        Create a filter for a specific team (home or away)
        """
        return {
            "$or": [
                {"home_team": {"$eq": team_name}},
                {"away_team": {"$eq": team_name}}
            ]
        }
    
    def create_venue_filter(self, venue_name: str) -> Dict[str, Any]:
        """
        Create a filter for a specific venue
        """
        return {"venue": {"$eq": venue_name}}
    
    def combine_filters(self, filters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Combine multiple filters with AND logic
        """
        if not filters:
            return {}
        elif len(filters) == 1:
            return filters[0]
        else:
            return {"$and": filters}
    
    def analyze_query_and_create_filter(self, query: str) -> Dict[str, Any]:
        """
        Analyze the query and create appropriate metadata filters
        """
        query_lower = query.lower()
        
        # Initialize filters list
        filters = []
        
        # Check for month-specific queries
        month_patterns = {
            'january': 1, 'jan': 1,
            'february': 2, 'feb': 2,
            'march': 3, 'mar': 3,
            'april': 4, 'apr': 4,
            'may': 5,
            'june': 6, 'jun': 6,
            'july': 7, 'jul': 7,
            'august': 8, 'aug': 8,
            'september': 9, 'sep': 9,
            'october': 10, 'oct': 10,
            'november': 11, 'nov': 11,
            'december': 12, 'dec': 12
        }
        
        detected_month = None
        for month_name, month_num in month_patterns.items():
            if month_name in query_lower:
                detected_month = month_num
                break
        
        # If month detected, create date filter
        if detected_month:
            date_filter = self.create_date_filter_for_month(detected_month, "2024")
            filters.append(date_filter)
        
        # Check for team queries
        team_patterns = [
            'manchester united', 'man utd', 'united',
            'liverpool', 'reds',
            'arsenal', 'gunners',
            'chelsea', 'blues',
            'manchester city', 'city',
            'tottenham', 'spurs',
            'newcastle', 'magpies',
            'aston villa', 'villa',
            'west ham', 'hammers',
            'brighton', 'seagulls',
            'crystal palace', 'palace',
            'brentford', 'bees',
            'fulham', 'cottagers',
            'wolves',
            'nottingham forest', 'forest',
            'burnley', 'clarets',
            'sheffield united', 'blades',
            'everton', 'toffees',
            'luton town', 'luton',
            'bournemouth', 'cherries'
        ]
        
        detected_team = None
        for team_pattern in team_patterns:
            if team_pattern in query_lower:
                detected_team = team_pattern
                break
        
        # If team detected, create team filter
        if detected_team:
            team_filter = self.create_team_filter(detected_team.title())
            filters.append(team_filter)
        
        # Check for venue queries
        venue_patterns = [
            'old trafford',
            'anfield',
            'emirates stadium', 'emirates',
            'stamford bridge',
            'etihad stadium', 'etihad',
            'tottenham hotspur stadium',
            'st james park',
            'villa park',
            'london stadium',
            'amex stadium', 'amex',
            'selhurst park',
            'gtech community stadium',
            'craven cottage',
            'molineux stadium', 'molineux',
            'city ground',
            'turf moor',
            'bramall lane',
            'goodison park',
            'kenilworth road',
            'vitality stadium'
        ]
        
        detected_venue = None
        for venue_pattern in venue_patterns:
            if venue_pattern in query_lower:
                detected_venue = venue_pattern
                break
        
        # If venue detected, create venue filter
        if detected_venue:
            venue_filter = self.create_venue_filter(detected_venue.title())
            filters.append(venue_filter)
        
        # Combine all filters
        final_filter = self.combine_filters(filters)
        
        return {
            "intent": f"Search for games matching: {', '.join([f for f in ['month', 'team', 'venue'] if locals().get(f'detected_{f}')])}",
            "metadata_filter": final_filter,
            "explanation": f"Applied filters: {self._explain_filters(final_filter)}",
            "query_type": "filtered" if final_filter else "semantic"
        }
    
    def _explain_filters(self, metadata_filter: Dict) -> str:
        """Explain metadata filters in human-readable format"""
        if not metadata_filter:
            return "No filters applied"
        
        explanations = []
        
        for key, value in metadata_filter.items():
            if key.startswith('$'):
                if key == '$and':
                    explanations.append(f"AND condition: {self._explain_single_filter(value)}")
                elif key == '$or':
                    explanations.append(f"OR condition: {self._explain_single_filter(value)}")
            else:
                explanations.append(f"{key}: {self._explain_single_filter(value)}")
        
        return "; ".join(explanations)
    
    def _explain_single_filter(self, filter_condition: Dict) -> str:
        """Explain a single filter condition"""
        if isinstance(filter_condition, dict):
            for operator, value in filter_condition.items():
                if operator.startswith('$'):
                    return f"{operator} '{value}'"
                else:
                    return f"equals '{value}'"
        return str(filter_condition)

def main():
    """Demo the enhanced LLM filter"""
    print("🧠 Enhanced LLM Metadata Filter for Streamlit App")
    print("=" * 70)
    
    # Check OpenAI availability
    if not OPENAI_AVAILABLE:
        print("⚠️  OpenAI package not available. Install with: pip install openai")
        return
    
    # Initialize filter
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return
    
    llm_filter = EnhancedLLMMetadataFilter(openai_api_key=openai_api_key)
    
    # Test queries
    test_queries = [
        "Games in September 2024",
        "Liverpool games at Anfield",
        "Manchester United home games",
        "High scoring matches"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: {query}")
        print("-" * 50)
        
        # Try GPT interpretation first
        gpt_result = llm_filter.interpret_query_with_gpt(query)
        
        if "error" not in gpt_result:
            print(f"✅ GPT Interpretation:")
            print(f"   Intent: {gpt_result.get('intent', 'N/A')}")
            print(f"   Filter: {json.dumps(gpt_result.get('metadata_filter', {}), indent=2)}")
            print(f"   Type: {gpt_result.get('query_type', 'N/A')}")
        else:
            print(f"❌ GPT Error: {gpt_result['error']}")
            print(f"🔄 Using fallback pattern matching...")
            
            # Fallback to pattern matching
            fallback_result = llm_filter.analyze_query_and_create_filter(query)
            print(f"✅ Fallback Result:")
            print(f"   Intent: {fallback_result.get('intent', 'N/A')}")
            print(f"   Filter: {json.dumps(fallback_result.get('metadata_filter', {}), indent=2)}")
            print(f"   Type: {fallback_result.get('query_type', 'N/A')}")

if __name__ == "__main__":
    main()
