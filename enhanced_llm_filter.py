#!/usr/bin/env python3
"""
Enhanced LLM Metadata Filter with OpenAI GPT Integration
Uses GPT to interpret natural language queries and generate proper ZeroEntropy metadata filters
"""

import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dotenv import load_dotenv
from zeroentropy import ZeroEntropy, ConflictError, APIStatusError

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
    
    def __init__(self, client=None, openai_api_key=None):
        self.client = client
        if not self.client:
            self.initialize_client()
        
        # OpenAI setup
        self.openai_client = None
        if OPENAI_AVAILABLE and openai_api_key:
            self.openai_client = OpenAI(api_key=openai_api_key)
        
        # Fallback patterns for when OpenAI is not available
        self.fallback_patterns = {
            'teams': {
                'patterns': [
                    r'(manchester united|man utd|united)',
                    r'(liverpool|reds)',
                    r'(arsenal|gunners)',
                    r'(chelsea|blues)',
                    r'(manchester city|city)',
                    r'(tottenham|spurs)',
                    r'(newcastle|magpies)',
                    r'(aston villa|villa)',
                    r'(west ham|hammers)',
                    r'(brighton|seagulls)',
                    r'(crystal palace|palace)',
                    r'(brentford|bees)',
                    r'(fulham|cottagers)',
                    r'(wolves)',
                    r'(nottingham forest|forest)',
                    r'(burnley|clarets)',
                    r'(sheffield united|blades)',
                    r'(everton|toffees)',
                    r'(luton town|luton)',
                    r'(bournemouth|cherries)'
                ],
                'metadata_field': 'home_team',
                'filter_type': 'team_match'
            },
            'venues': {
                'patterns': [
                    r'(old trafford)',
                    r'(anfield)',
                    r'(emirates stadium|emirates)',
                    r'(stamford bridge)',
                    r'(etihad stadium|etihad)',
                    r'(tottenham hotspur stadium)',
                    r'(st james park)',
                    r'(villa park)',
                    r'(london stadium)',
                    r'(amex stadium|amex)',
                    r'(selhurst park)',
                    r'(gtech community stadium)',
                    r'(craven cottage)',
                    r'(molineux stadium|molineux)',
                    r'(city ground)',
                    r'(turf moor)',
                    r'(bramall lane)',
                    r'(goodison park)',
                    r'(kenilworth road)',
                    r'(vitality stadium)'
                ],
                'metadata_field': 'venue',
                'filter_type': 'venue_match'
            },
            'dates': {
                'patterns': [
                    r'(today|tonight)',
                    r'(yesterday)',
                    r'(tomorrow)',
                    r'(this week|this weekend)',
                    r'(last week|last weekend)',
                    r'(next week|next weekend)',
                    r'(august|aug)',
                    r'(september|sep)',
                    r'(\d{1,2}(st|nd|rd|th)?\s+(august|aug|september|sep))',
                    r'(\d{4}-\d{2}-\d{2})'
                ],
                'metadata_field': 'date',
                'filter_type': 'date_range'
            }
        }
    
    def initialize_client(self):
        """Initialize ZeroEntropy client"""
        try:
            load_dotenv()
            api_key = os.getenv("ZEROENTROPY_API_KEY")
            if not api_key:
                print("❌ ZEROENTROPY_API_KEY not found in environment")
                return False
            
            self.client = ZeroEntropy()
            return True
        except Exception as e:
            print(f"❌ Failed to initialize ZeroEntropy client: {e}")
            return False
    
    def interpret_query_with_gpt(self, query: str) -> Dict[str, Any]:
        """
        Use OpenAI GPT to interpret the natural language query and generate metadata filters
        """
        if not self.openai_client:
            return {"error": "OpenAI client not available"}
        
        try:
            # Get today's date for context
            from datetime import datetime, timedelta
            today = datetime.now()
            
            # Calculate various date references
            current_week_start = today - timedelta(days=today.weekday())
            current_week_end = current_week_start + timedelta(days=6)
            next_week_start = current_week_start + timedelta(days=7)
            next_week_end = next_week_start + timedelta(days=6)
            last_week_start = current_week_start - timedelta(days=7)
            last_week_end = last_week_start + timedelta(days=6)
            
            # Current month calculations
            current_month_start = today.replace(day=1)
            if today.month == 12:
                next_month_start = today.replace(year=today.year + 1, month=1, day=1)
            else:
                next_month_start = today.replace(month=today.month + 1, day=1)
            last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
            
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
            
            last_weekend_start = this_weekend_start - timedelta(days=7)
            last_weekend_end = last_weekend_start + timedelta(days=1)
            next_weekend_start = this_weekend_start + timedelta(days=7)
            next_weekend_end = next_weekend_start + timedelta(days=1)
            
            # Create a system prompt that explains ZeroEntropy metadata filtering
            system_prompt = """You are an expert at interpreting natural language queries and converting them to ZeroEntropy metadata filters using GPT-5 intelligence.

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

IMPORTANT: For win/loss analysis, use this approach:
- Filter by team first (home_team or away_team = "Team Name")
- Then manually analyze scores in the response to determine wins/losses
- This avoids issues with string score comparisons in metadata filters

IMPORTANT: For date ranges, ensure chronological order:
- Start date should be earlier than end date
- If user specifies dates in reverse order, automatically correct them
- Example: "between September 15 and August 3rd" should become "between August 3rd and September 15th"

CRITICAL FILTER RULES:
- Each metadata field can only have ONE operator
- For date ranges, use separate filter conditions with $and
- Example: For "next weekend", use: {{"$and": [{{"date": {{"$gte": "2024-08-23"}}}}, {{"date": {{"$lte": "2024-08-24"}}}}]}}
- NEVER combine multiple operators for the same field like: {{"date": {{"$gte": "2024-08-23", "$lte": "2024-08-24"}}}}

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
            print(f"🔍 Raw GPT-5 Response: {gpt_response}")
            
            # Try to extract JSON from the response
            try:
                # Look for JSON content in the response
                import json
                import re
                
                # Try to find JSON content
                json_match = re.search(r'\{.*\}', gpt_response, re.DOTALL)
                if json_match:
                    parsed_response = json.loads(json_match.group())
                    print(f"✅ Successfully parsed GPT-5 JSON: {parsed_response}")
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
            print(f"❌ Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            return {"error": f"OpenAI API error: {e}"}
    
    def execute_enhanced_query(self, collection_name: str, query: str, k: int = 10) -> Dict[str, Any]:
        """
        Execute an enhanced query using GPT interpretation and metadata filtering
        """
        if not self.client:
            return {"error": "ZeroEntropy client not initialized"}
        
        try:
            # Step 1: Use GPT to interpret the query
            gpt_interpretation = self.interpret_query_with_gpt(query)
            
            if "error" in gpt_interpretation:
                # Fallback to pattern-based filtering
                print(f"GPT interpretation failed: {gpt_interpretation['error']}, using fallback patterns")
                extracted_filters, llm_context = self._analyze_query_intent_fallback(query)
                metadata_filter = self._build_metadata_filter_fallback(extracted_filters)
                query_type = "fallback"
            else:
                # Use GPT interpretation
                metadata_filter = gpt_interpretation.get("metadata_filter", {})
                query_type = gpt_interpretation.get("query_type", "semantic")
                llm_context = {
                    "intent": gpt_interpretation.get("intent", ""),
                    "explanation": gpt_interpretation.get("explanation", "")
                }
            
            # Step 2: Execute ZeroEntropy query
            query_params = {
                "collection_name": collection_name,
                "query": query,
                "k": k,
                "include_metadata": True
            }
            
            if metadata_filter and query_type == "filtered":
                query_params["filter"] = metadata_filter
            
            results = self.client.queries.top_documents(**query_params)
            
            # Step 3: Generate response
            if query_type == "filtered":
                response = self._generate_filtered_response(query, results, llm_context, metadata_filter)
            else:
                response = self._generate_semantic_response(query, results, llm_context)
            
            result_dict = {
                "query": query,
                "query_type": query_type,
                "metadata_filter": metadata_filter,
                "llm_context": llm_context,
                "zeroentropy_results": results,
                "response": response,
                "total_results": len(results.results),
                "gpt_interpretation": gpt_interpretation if "error" not in gpt_interpretation else None
            }
            
            print(f"🔍 Debug - Query Type: {query_type}")
            print(f"🔍 Debug - Metadata Filter: {metadata_filter}")
            print(f"🔍 Debug - Results Count: {len(results.results)}")
            
            return result_dict
            
        except Exception as e:
            import traceback
            print(f"❌ Enhanced query execution failed: {e}")
            print(f"❌ Traceback: {traceback.format_exc()}")
            return {"error": f"Enhanced query execution failed: {e}"}
    
    def _analyze_query_intent_fallback(self, query: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Fallback pattern-based query analysis"""
        extracted_filters = {}
        llm_context = {"reasoning": []}
        
        query_lower = query.lower()
        
        # Team detection
        for team_pattern in self.fallback_patterns['teams']['patterns']:
            if re.search(team_pattern, query_lower):
                team_name = re.search(team_pattern, query_lower).group(1)
                if 'teams' not in extracted_filters:
                    extracted_filters['teams'] = []
                extracted_filters['teams'].append(team_name)
                llm_context["reasoning"].append(f"Detected teams: '{team_name}' -> maps to home_team")
        
        # Venue detection
        for venue_pattern in self.fallback_patterns['venues']['patterns']:
            if re.search(venue_pattern, query_lower):
                venue_name = re.search(venue_pattern, query_lower).group(1)
                if 'venues' not in extracted_filters:
                    extracted_filters['venues'] = []
                extracted_filters['venues'].append(venue_name)
                llm_context["reasoning"].append(f"Detected venues: '{venue_name}' -> maps to venue")
        
        return extracted_filters, llm_context
    
    def _build_metadata_filter_fallback(self, extracted_filters: Dict[str, Any]) -> Dict[str, Any]:
        """Build metadata filter from fallback patterns"""
        filter_conditions = []
        
        # Team filters
        if 'teams' in extracted_filters:
            teams = extracted_filters['teams']
            if len(teams) == 1:
                team_name = teams[0].title()
                filter_conditions.append({
                    "$or": [
                        {"home_team": {"$eq": team_name}},
                        {"away_team": {"$eq": team_name}}
                    ]
                })
        
        # Venue filters
        if 'venues' in extracted_filters:
            venues = extracted_filters['venues']
            if len(venues) == 1:
                venue_name = venues[0]
                # Create case variations for better matching
                venue_variations = [
                    venue_name.title(),  # "Etihad Stadium"
                    venue_name.lower(),   # "etihad stadium"
                    venue_name.upper(),   # "ETIHAD STADIUM"
                    venue_name.capitalize()  # "Etihad stadium"
                ]
                
                # Add intelligent case variations for the full venue name
                venue_variations.extend([
                    venue_name.title(),      # "etihad stadium" -> "Etihad Stadium"
                    venue_name.lower(),      # "Etihad Stadium" -> "etihad stadium"
                    venue_name.upper(),      # "etihad stadium" -> "ETIHAD STADIUM"
                    venue_name.capitalize()  # "etihad stadium" -> "Etihad stadium"
                ])
                
                # Add case variations for individual words (but only as part of the full name)
                words = venue_name.split()
                if len(words) > 1:
                    # Only add the full venue name with different word capitalizations
                    # This prevents matching partial names that could be too broad
                    for i in range(len(words)):
                        # Create variations where we capitalize different words
                        word_variations = words.copy()
                        word_variations[i] = word_variations[i].title()
                        partial_variation = ' '.join(word_variations)
                        venue_variations.append(partial_variation)
                
                # Remove duplicates while preserving order
                venue_variations = list(dict.fromkeys(venue_variations))
                filter_conditions.append({"venue": {"$in": venue_variations}})
        
        # Combine conditions
        if len(filter_conditions) == 1:
            return filter_conditions[0]
        elif len(filter_conditions) > 1:
            return {"$and": filter_conditions}
        else:
            return {}
    
    def _generate_filtered_response(self, query: str, results, llm_context: Dict, metadata_filter: Dict) -> str:
        """Generate response for filtered queries"""
        if not results.results:
            response_parts = []
            response_parts.append(f"🎯 **Query Analysis**: {query}")
            response_parts.append(f"📊 **No games found**")
            
            if metadata_filter:
                response_parts.append(f"🔍 **Applied Filters**: {self._explain_filters(metadata_filter)}")
                
                # Check if this is a date-related query with no results
                if any("date" in str(f) for f in [metadata_filter]):
                    response_parts.append(f"\n⚠️ **Data Availability Notice**:")
                    response_parts.append(f"   • Your query requested data for specific dates")
                    response_parts.append(f"   • The sports collection contains data from 2024")
                    response_parts.append(f"   • No games were found for the requested time period")
                    response_parts.append(f"   • Try searching without date constraints to see all available games")
                
                response_parts.append(f"❌ **No games match these criteria**")
            
            response_parts.append(f"\n💡 **Suggestions**:")
            response_parts.append(f"   • Try broadening your search criteria")
            response_parts.append(f"   • Remove date filters to search all available data")
            response_parts.append(f"   • Search for specific teams or venues instead")
            
            return "\n\n".join(response_parts)
        
        # Check if this is a win/loss query for a specific team
        query_lower = query.lower()
        team_name = None
        
        # Extract team name from query
        for word in query_lower.split():
            if word in ['liverpool', 'manchester', 'united', 'chelsea', 'arsenal', 'city', 'tottenham', 'spurs']:
                if word == 'manchester' and 'united' in query_lower:
                    team_name = 'Manchester United'
                elif word == 'manchester' and 'city' in query_lower:
                    team_name = 'Manchester City'
                elif word == 'tottenham' or word == 'spurs':
                    team_name = 'Tottenham Hotspur'
                else:
                    team_name = word.title()
                break
        
        # If it's a date range query, do detailed date analysis
        if any(word in query_lower for word in ['between', 'from', 'to', 'date']) and any(word in query_lower for word in ['august', 'september', 'october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june', 'july']):
            return self._analyze_date_range_query(query, results, metadata_filter)
        
        # If it's a win/loss query and we have a team, do detailed analysis
        if team_name and any(word in query_lower for word in ['win', 'loss', 'lost', 'won', 'beat', 'defeat']):
            analysis = self._analyze_win_loss_results(results, team_name)
            
            response_parts = []
            response_parts.append(f"🎯 **Query Analysis**: {query}")
            response_parts.append(f"📊 **Found {analysis['total_games']} {team_name} games**")
            
            if metadata_filter:
                response_parts.append(f"🔍 **Applied Filters**: {self._explain_filters(metadata_filter)}")
            
            # Show win/loss summary
            response_parts.append(f"\n📈 **{team_name} Performance Summary**:")
            response_parts.append(f"   🏆 Wins: {analysis['win_count']}")
            response_parts.append(f"   ❌ Losses: {analysis['loss_count']}")
            response_parts.append(f"   🤝 Draws: {analysis['draw_count']}")
            
            # Show specific results based on query intent
            if 'loss' in query_lower or 'lost' in query_lower:
                if analysis['loss_count'] > 0:
                    response_parts.append(f"\n💔 **{team_name} Losses ({analysis['loss_count']}):**")
                    for i, result in enumerate(analysis['losses'], 1):
                        metadata = result.metadata or {}
                        home_team = metadata.get('home_team', 'Unknown')
                        away_team = metadata.get('away_team', 'Unknown')
                        date = metadata.get('date', 'Unknown')
                        venue = metadata.get('venue', 'Unknown')
                        home_score = metadata.get('home_score', '?')
                        away_score = metadata.get('away_score', '?')
                        
                        game_result = f"{i}. **{home_team} vs {away_team}**"
                        game_result += f"\n   📅 {date} | 🏟️ {venue} | 📊 {home_score}-{away_score}"
                        game_result += f"\n   🎯 Relevance Score: {result.score:.4f}"
                        response_parts.append(game_result)
                else:
                    response_parts.append(f"\n🎉 **Great news! {team_name} has no losses in the selected criteria.**")
            
            elif 'win' in query_lower or 'won' in query_lower or 'beat' in query_lower:
                if analysis['win_count'] > 0:
                    response_parts.append(f"\n🏆 **{team_name} Wins ({analysis['win_count']}):**")
                    for i, result in enumerate(analysis['wins'], 1):
                        metadata = result.metadata or {}
                        home_team = metadata.get('home_team', 'Unknown')
                        away_team = metadata.get('away_team', 'Unknown')
                        date = metadata.get('date', 'Unknown')
                        venue = metadata.get('venue', 'Unknown')
                        home_score = metadata.get('home_score', '?')
                        away_score = metadata.get('away_score', '?')
                        
                        game_result = f"{i}. **{home_team} vs {away_team}**"
                        game_result += f"\n   📅 {date} | 🏟️ {venue} | 📊 {home_score}-{away_score}"
                        game_result += f"\n   🎯 Relevance Score: {result.score:.4f}"
                        response_parts.append(game_result)
                else:
                    response_parts.append(f"\n😔 **{team_name} has no wins in the selected criteria.**")
            
            else:
                # Show all games with win/loss indicators
                response_parts.append(f"\n🏆 **All {team_name} Games:**")
                for i, result in enumerate(results.results, 1):
                    metadata = result.metadata or {}
                    home_team = metadata.get('home_team', 'Unknown')
                    away_team = metadata.get('away_team', 'Unknown')
                    date = metadata.get('date', 'Unknown')
                    venue = metadata.get('venue', 'Unknown')
                    home_score = metadata.get('home_score', '?')
                    away_score = metadata.get('away_score', '?')
                    status = metadata.get('status', 'Unknown')
                    notes = metadata.get('notes', '')
                    
                    # Determine result for the team
                    if home_team == team_name:
                        if int(home_score) > int(away_score):
                            result_indicator = "🏆 WIN"
                        elif int(home_score) < int(away_score):
                            result_indicator = "💔 LOSS"
                        else:
                            result_indicator = "🤝 DRAW"
                    elif away_team == team_name:
                        if int(away_score) > int(home_score):
                            result_indicator = "🏆 WIN"
                        elif int(away_score) < int(home_score):
                            result_indicator = "💔 LOSS"
                        else:
                            result_indicator = "🤝 DRAW"
                    else:
                        result_indicator = ""
                    
                    game_result = f"{i}. **{home_team} vs {away_team}** {result_indicator}"
                    game_result += f"\n   📅 {date} | 🏟️ {venue} | 📊 {home_score}-{away_score}"
                    game_result += f"\n   📝 {status} | 💬 {notes}"
                    game_result += f"\n   🎯 Relevance Score: {result.score:.4f}"
                    
                    response_parts.append(game_result)
            
            return "\n\n".join(response_parts)
        
        # Standard response for non-win/loss queries
        response_parts = []
        response_parts.append(f"🎯 **Query Analysis**: {query}")
        response_parts.append(f"📊 **Found {len(results.results)} matching games**")
        
        if metadata_filter:
            response_parts.append(f"🔍 **Applied Filters**: {self._explain_filters(metadata_filter)}")
        
        response_parts.append("\n🏆 **Game Results**:")
        
        for i, result in enumerate(results.results, 1):
            metadata = result.metadata or {}
            
            home_team = metadata.get('home_team', 'Unknown')
            away_team = metadata.get('away_team', 'Unknown')
            date = metadata.get('date', 'Unknown')
            venue = metadata.get('venue', 'Unknown')
            home_score = metadata.get('home_score', '?')
            away_score = metadata.get('away_score', '?')
            status = metadata.get('status', 'Unknown')
            notes = metadata.get('notes', '')
            
            game_result = f"{i}. **{home_team} vs {away_team}**"
            game_result += f"\n   📅 {date} | 🏟️ {venue} | 📊 {home_score}-{away_score}"
            game_result += f"\n   📝 {status} | 💬 {notes}"
            game_result += f"\n   🎯 Relevance Score: {result.score:.4f}"
            
            response_parts.append(game_result)
        
        return "\n\n".join(response_parts)
    
    def _generate_semantic_response(self, query: str, results, llm_context: Dict) -> str:
        """Generate response for semantic queries"""
        if not results.results:
            return f"🎯 **Query Analysis**: {query}\n📊 **No games found**\n❌ **No games match your query**"
        
        response_parts = []
        response_parts.append(f"🎯 **Query Analysis**: {query}")
        response_parts.append(f"📊 **Found {len(results.results)} relevant games**")
        response_parts.append(f"💡 **Note**: Using semantic search (no specific filters applied)")
        
        response_parts.append("\n🏆 **Game Results**:")
        
        for i, result in enumerate(results.results, 1):
            metadata = result.metadata or {}
            
            home_team = metadata.get('home_team', 'Unknown')
            away_team = metadata.get('away_team', 'Unknown')
            date = metadata.get('date', 'Unknown')
            venue = metadata.get('venue', 'Unknown')
            home_score = metadata.get('home_score', '?')
            away_score = metadata.get('away_score', '?')
            status = metadata.get('status', 'Unknown')
            notes = metadata.get('notes', '')
            
            game_result = f"{i}. **{home_team} vs {away_team}**"
            game_result += f"\n   📅 {date} | 🏟️ {venue} | 📊 {home_score}-{away_score}"
            game_result += f"\n   📝 {status} | 💬 {notes}"
            game_result += f"\n   🎯 Relevance Score: {result.score:.4f}"
            
            response_parts.append(game_result)
        
        return "\n\n".join(response_parts)
    
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
    
    def _analyze_win_loss_results(self, results, team_name: str) -> Dict[str, Any]:
        """Analyze results to determine wins, losses, and draws for a specific team"""
        wins = []
        losses = []
        draws = []
        
        for result in results.results:
            metadata = result.metadata or {}
            home_team = metadata.get('home_team', '')
            away_team = metadata.get('away_team', '')
            home_score = metadata.get('home_score', '0')
            away_score = metadata.get('away_score', '0')
            
            # Skip if scores are not available
            if not home_score or not away_score:
                continue
                
            try:
                home_score_int = int(home_score)
                away_score_int = int(away_score)
            except ValueError:
                continue
            
            if home_team == team_name:
                # Team is home team
                if home_score_int > away_score_int:
                    wins.append(result)
                elif home_score_int < away_score_int:
                    losses.append(result)
                else:
                    draws.append(result)
            elif away_team == team_name:
                # Team is away team
                if away_score_int > home_score_int:
                    wins.append(result)
                elif away_score_int < home_score_int:
                    losses.append(result)
                else:
                    draws.append(result)
        
        return {
            'wins': wins,
            'losses': losses,
            'draws': draws,
            'total_games': len(results.results),
            'win_count': len(wins),
            'loss_count': len(losses),
            'draw_count': len(draws)
        }
    
    def _correct_date_range(self, start_date: str, end_date: str) -> tuple:
        """Correct date range to ensure chronological order"""
        try:
            from datetime import datetime
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            if start_dt > end_dt:
                # Dates are in reverse order, swap them
                return end_date, start_date, True
            else:
                return start_date, end_date, False
        except ValueError:
            # If date parsing fails, return as-is
            return start_date, end_date, False
    
    def _analyze_date_range_query(self, query: str, results, metadata_filter: Dict) -> str:
        """Generate enhanced response for date range queries"""
        response_parts = []
        response_parts.append(f"🎯 **Query Analysis**: {query}")
        response_parts.append(f"📊 **Found {len(results.results)} matching games**")
        
        if metadata_filter:
            response_parts.append(f"🔍 **Applied Filters**: {self._explain_filters(metadata_filter)}")
        
        # Check if dates were corrected
        date_correction_note = ""
        if "date" in query.lower() and "between" in query.lower():
            # Try to extract date information from the filter
            if metadata_filter and "$and" in metadata_filter:
                date_filters = [f for f in metadata_filter["$and"] if "date" in f]
                if len(date_filters) >= 2:
                    start_date = None
                    end_date = None
                    for date_filter in date_filters:
                        if "$gte" in date_filter.get("date", {}):
                            start_date = date_filter["date"]["$gte"]
                        elif "$lt" in date_filter.get("date", {}):
                            end_date = date_filter["date"]["$lt"]
                    
                    if start_date and end_date:
                        corrected_start, corrected_end, was_corrected = self._correct_date_range(start_date, end_date)
                        if was_corrected:
                            date_correction_note = f"\n💡 **Note**: Date range automatically corrected from '{start_date} to {end_date}' to '{corrected_start} to {corrected_end}' for chronological order."
        
        if date_correction_note:
            response_parts.append(date_correction_note)
        
        # Add date range summary
        if len(results.results) > 0:
            dates = [r.metadata.get('date', '') for r in results.results if r.metadata and r.metadata.get('date')]
            if dates:
                dates.sort()
                response_parts.append(f"\n📅 **Date Range**: {dates[0]} to {dates[-1]}")
                response_parts.append(f"📊 **Games per month**:")
                
                # Count games by month
                month_counts = {}
                for date in dates:
                    month = date[:7]  # YYYY-MM
                    month_counts[month] = month_counts.get(month, 0) + 1
                
                for month in sorted(month_counts.keys()):
                    month_name = datetime.strptime(month, '%Y-%m').strftime('%B %Y')
                    response_parts.append(f"   📍 {month_name}: {month_counts[month]} games")
        
        response_parts.append("\n🏆 **Game Results**:")
        
        for i, result in enumerate(results.results, 1):
            metadata = result.metadata or {}
            
            home_team = metadata.get('home_team', 'Unknown')
            away_team = metadata.get('away_team', 'Unknown')
            date = metadata.get('date', 'Unknown')
            venue = metadata.get('venue', 'Unknown')
            home_score = metadata.get('home_score', '?')
            away_score = metadata.get('away_score', '?')
            status = metadata.get('status', 'Unknown')
            notes = metadata.get('notes', '')
            
            game_result = f"{i}. **{home_team} vs {away_team}**"
            game_result += f"\n   📅 {date} | 🏟️ {venue} | 📊 {home_score}-{away_score}"
            game_result += f"\n   📝 {status} | 💬 {notes}"
            game_result += f"\n   🎯 Relevance Score: {result.score:.4f}"
            
            response_parts.append(game_result)
        
        return "\n\n".join(response_parts)

def main():
    """Demo the enhanced LLM filter"""
    print("🧠 Enhanced LLM Metadata Filter with OpenAI Integration")
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
    
    if not llm_filter.client:
        print("❌ Failed to initialize ZeroEntropy client")
        return
    
    # Test queries
    test_queries = [
        "Show me Manchester United home games from August",
        "Liverpool games at Anfield",
        "High scoring matches",
        "Games from last week"
    ]
    
    collection_name = "Mo-schedules-test-csv"
    
    for query in test_queries:
        print(f"\n🔍 Testing: {query}")
        print("-" * 50)
        
        result = llm_filter.execute_enhanced_query(collection_name, query, 5)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Query type: {result['query_type']}")
            print(f"📊 Results: {result['total_results']}")
            if result.get('gpt_interpretation'):
                print(f"🤖 GPT Intent: {result['gpt_interpretation'].get('intent', 'N/A')}")
                print(f"🔍 GPT Filter: {json.dumps(result['gpt_interpretation'].get('metadata_filter', {}), indent=2)}")
            print(f"📝 Response preview: {result['response'][:200]}...")

if __name__ == "__main__":
    main()
