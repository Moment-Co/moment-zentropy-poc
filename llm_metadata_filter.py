#!/usr/bin/env python3
"""
LLM-Enhanced Metadata Filtering for ZeroEntropy
Combines ZeroEntropy's powerful metadata filtering with LLM reasoning
for intelligent sports game queries and analysis
"""

import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dotenv import load_dotenv
from zeroentropy import ZeroEntropy, ConflictError, APIStatusError

# Load environment variables
load_dotenv()

class LLMMetadataFilter:
    """
    Advanced metadata filtering system that combines ZeroEntropy queries
    with LLM reasoning for intelligent sports game analysis
    """
    
    def __init__(self, client=None):
        self.client = client
        if not self.client:
            self.initialize_client()
        
        # Define metadata filter patterns and mappings
        self.filter_patterns = {
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
            },
            'scores': {
                'patterns': [
                    r'(high scoring|high score|lots of goals)',
                    r'(low scoring|low score|few goals)',
                    r'(goalless|no goals|0-0)',
                    r'(draw|tie)',
                    r'(win|victory|defeat|loss)',
                    r'(\d+-\d+)'
                ],
                'metadata_field': 'score_analysis',
                'filter_type': 'score_pattern'
            },
            'status': {
                'patterns': [
                    r'(completed|finished|played)',
                    r'(scheduled|upcoming|future)',
                    r'(cancelled|postponed)'
                ],
                'metadata_field': 'status',
                'filter_type': 'status_match'
            },
            'leagues': {
                'patterns': [
                    r'(premier league|epl|english premier league)',
                    r'(championship)',
                    r'(fa cup)',
                    r'(carabao cup)'
                ],
                'metadata_field': 'league',
                'filter_type': 'league_match'
            }
        }
    
    def initialize_client(self):
        """Initialize the ZeroEntropy client"""
        try:
            api_key = os.getenv("ZEROENTROPY_API_KEY")
            if not api_key:
                raise ValueError("ZEROENTROPY_API_KEY not found in environment variables")
            
            self.client = ZeroEntropy()
            print("✅ ZeroEntropy client initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize ZeroEntropy client: {e}")
            self.client = None
    
    def analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Analyze natural language query to extract filtering intent
        Returns structured filter criteria and LLM context
        """
        query_lower = query.lower()
        extracted_filters = {}
        llm_context = {
            "query": query,
            "extracted_filters": {},
            "reasoning": [],
            "suggested_filters": []
        }
        
        # Analyze each filter pattern
        for filter_type, config in self.filter_patterns.items():
            for pattern in config['patterns']:
                matches = re.findall(pattern, query_lower)
                if matches:
                    if filter_type not in extracted_filters:
                        extracted_filters[filter_type] = []
                    
                    for match in matches:
                        if match:  # Skip empty matches
                            extracted_filters[filter_type].append(match)
                            
                            # Add reasoning
                            llm_context["reasoning"].append(
                                f"Detected {filter_type}: '{match}' -> maps to {config['metadata_field']}"
                            )
        
        # Special handling for complex queries
        self._analyze_complex_patterns(query_lower, extracted_filters, llm_context)
        
        llm_context["extracted_filters"] = extracted_filters
        return extracted_filters, llm_context
    
    def _analyze_complex_patterns(self, query: str, filters: Dict, context: Dict):
        """Analyze complex query patterns and relationships"""
        
        # Time-based queries
        if any(word in query for word in ['recent', 'latest', 'newest']):
            filters['time_recency'] = ['recent']
            context["reasoning"].append("Detected time recency: looking for recent games")
        
        if any(word in query for word in ['classic', 'historic', 'memorable']):
            filters['game_quality'] = ['classic']
            context["reasoning"].append("Detected game quality: looking for classic/memorable matches")
        
        # Performance-based queries
        if any(word in query for word in ['dominant', 'strong', 'weak']):
            filters['performance'] = ['performance_analysis']
            context["reasoning"].append("Detected performance analysis: looking for team performance patterns")
        
        # Rivalry queries
        if any(word in query for word in ['rivalry', 'derby', 'classic']):
            filters['rivalry'] = ['rivalry_match']
            context["reasoning"].append("Detected rivalry: looking for classic rivalry matches")
    
    def build_metadata_filter(self, extracted_filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert extracted filters into ZeroEntropy metadata filter
        """
        filter_conditions = []
        
        # Team filters
        if 'teams' in extracted_filters:
            teams = extracted_filters['teams']
            if len(teams) == 1:
                # Single team - check both home and away
                # Handle case sensitivity by using proper case
                team_name = teams[0].title()  # Convert to title case
                filter_conditions.append({
                    "$or": [
                        {"home_team": {"$eq": team_name}},
                        {"away_team": {"$eq": team_name}}
                    ]
                })
            else:
                # Multiple teams
                team_filters = []
                for team in teams:
                    team_name = team.title()  # Convert to title case
                    team_filters.extend([
                        {"home_team": {"$eq": team_name}},
                        {"away_team": {"$eq": team_name}}
                    ])
                filter_conditions.append({"$or": team_filters})
        
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
            else:
                # Handle case sensitivity for multiple venues
                venue_variations_list = []
                for venue in venues:
                    venue_variations = [
                        venue.title(),  # "Etihad Stadium"
                        venue.lower(),   # "etihad stadium"
                        venue.upper(),   # "ETIHAD STADIUM"
                        venue.capitalize()  # "Etihad stadium"
                    ]
                    venue_variations_list.extend(venue_variations)
                
                # Remove duplicates while preserving order
                venue_variations_list = list(dict.fromkeys(venue_variations_list))
                filter_conditions.append({"venue": {"$in": venue_variations_list}})
        
        # Date filters
        if 'dates' in extracted_filters:
            date_filter = self._build_date_filter(extracted_filters['dates'])
            if date_filter:
                filter_conditions.append(date_filter)
        
        # Score filters
        if 'scores' in extracted_filters:
            score_filter = self._build_score_filter(extracted_filters['scores'])
            if score_filter:
                filter_conditions.append(score_filter)
        
        # Status filters
        if 'status' in extracted_filters:
            statuses = extracted_filters['status']
            if len(statuses) == 1:
                # Handle case sensitivity
                status_name = statuses[0].title()  # Convert to title case
                filter_conditions.append({"status": {"$eq": status_name}})
            else:
                # Handle case sensitivity for multiple statuses
                status_names = [status.title() for status in statuses]
                filter_conditions.append({"status": {"$in": status_names}})
        
        # League filters
        if 'leagues' in extracted_filters:
            leagues = extracted_filters['leagues']
            if len(leagues) == 1:
                # Handle case sensitivity
                league_name = leagues[0].title()  # Convert to title case
                filter_conditions.append({"league": {"$eq": league_name}})
            else:
                # Handle case sensitivity for multiple leagues
                league_names = [league.title() for league in leagues]
                filter_conditions.append({"league": {"$in": league_names}})
        
        # Combine all conditions
        if len(filter_conditions) == 1:
            return filter_conditions[0]
        elif len(filter_conditions) > 1:
            return {"$and": filter_conditions}
        else:
            return {}  # Return empty dict, not empty list
    
    def _build_date_filter(self, date_patterns: List[str]) -> Optional[Dict]:
        """Build date-based filter from extracted patterns"""
        today = datetime.now()
        
        for pattern in date_patterns:
            if 'today' in pattern or 'tonight' in pattern:
                return {"date": {"$eq": today.strftime("%Y-%m-%d")}}
            elif 'yesterday' in pattern:
                yesterday = today - timedelta(days=1)
                return {"date": {"$eq": yesterday.strftime("%Y-%m-%d")}}
            elif 'tomorrow' in pattern:
                tomorrow = today + timedelta(days=1)
                return {"date": {"$eq": tomorrow.strftime("%Y-%m-%d")}}
            elif 'this week' in pattern or 'this weekend' in pattern:
                week_start = today - timedelta(days=today.weekday())
                return {"date": {"$gte": week_start.strftime("%Y-%m-%d")}}
            elif 'last week' in pattern or 'last weekend' in pattern:
                week_start = today - timedelta(days=today.weekday() + 7)
                week_end = week_start + timedelta(days=6)
                return {
                    "$and": [
                        {"date": {"$gte": week_start.strftime("%Y-%m-%d")}},
                        {"date": {"$lte": week_end.strftime("%Y-%m-%d")}}
                    ]
                }
            elif 'august' in pattern or 'aug' in pattern:
                return {"date": {"$gte": "2024-08-01", "$lt": "2024-09-01"}}
            elif 'september' in pattern or 'sep' in pattern:
                return {"date": {"$gte": "2024-09-01", "$lt": "2024-10-01"}}
        
        return None
    
    def _build_score_filter(self, score_patterns: List[str]) -> Optional[Dict]:
        """Build score-based filter from extracted patterns"""
        for pattern in score_patterns:
            if 'high scoring' in pattern or 'lots of goals' in pattern:
                return {
                    "$or": [
                        {"home_score": {"$gte": "3"}},
                        {"away_score": {"$gte": "3"}}
                    ]
                }
            elif 'low scoring' in pattern or 'few goals' in pattern:
                return {
                    "$and": [
                        {"home_score": {"$lte": "1"}},
                        {"away_score": {"$lte": "1"}}
                    ]
                }
            elif 'goalless' in pattern or 'no goals' in pattern or '0-0' in pattern:
                return {
                    "$and": [
                        {"home_score": {"$eq": "0"}},
                        {"away_score": {"$eq": "0"}}
                    ]
                }
            elif 'draw' in pattern or 'tie' in pattern:
                return {"home_score": {"$eq": "away_score"}}
        
        return None
    
    def execute_intelligent_query(self, collection_name: str, query: str, k: int = 10) -> Dict[str, Any]:
        """
        Execute intelligent query combining metadata filtering with LLM reasoning
        
        Args:
            collection_name: Name of the collection to query
            query: Natural language query
            k: Number of results to return
        """
        if not self.client:
            return {"error": "ZeroEntropy client not initialized"}
        
        # Debug: Check client status
        print(f"🔍 LLM Filter - Client status: {self.client is not None}")
        print(f"🔍 LLM Filter - Collection name: '{collection_name}'")
        print(f"🔍 LLM Filter - Query: '{query}'")
        
        try:
            # Step 1: Analyze query intent
            extracted_filters, llm_context = self.analyze_query_intent(query)
            
            # Step 2: Build metadata filter
            metadata_filter = self.build_metadata_filter(extracted_filters)
            
            # Debug: Check filter validity
            print(f"🔍 Extracted filters: {extracted_filters}")
            print(f"🔍 Built metadata filter: {json.dumps(metadata_filter, indent=2)}")
            
            # Step 3: Execute ZeroEntropy query
            
            # Only pass filter if it's not empty
            query_params = {
                "collection_name": collection_name,
                "query": query,
                "k": k,
                "include_metadata": True
            }
            
            if metadata_filter:
                query_params["filter"] = metadata_filter
            
            print(f"🔍 Query params: {query_params}")
            results = self.client.queries.top_documents(**query_params)
            
            # Step 4: Generate LLM-style response
            llm_response = self._generate_llm_response(query, results, llm_context, metadata_filter)
            
            return {
                "query": query,
                "extracted_filters": extracted_filters,
                "metadata_filter": metadata_filter,
                "llm_context": llm_context,
                "zeroentropy_results": results,
                "llm_response": llm_response,
                "total_results": len(results.results)
            }
            
        except Exception as e:
            return {"error": f"Query execution failed: {e}"}
    
    def _generate_llm_response(self, query: str, results, llm_context: Dict, metadata_filter: Dict) -> str:
        """Generate LLM-style response based on query and results"""
        
        if not results.results:
            # Provide a more helpful response when no games are found
            response_parts = []
            response_parts.append(f"🎯 **Query Analysis**: {query}")
            response_parts.append(f"📊 **No games found**")
            
            # Add context about what was searched
            if metadata_filter:
                response_parts.append(f"🔍 **Applied Filters**: {self._explain_filters(metadata_filter)}")
                response_parts.append(f"❌ **No games match these criteria**")
            else:
                response_parts.append(f"❌ **No games found for your query**")
            
            # Provide helpful suggestions based on query content
            response_parts.append(f"\n💡 **Suggestions**:")
            
            query_lower = query.lower()
            if any(word in query_lower for word in ['team', 'teams', 'united', 'liverpool', 'arsenal', 'chelsea']):
                response_parts.append(f"   • Try specific team names: 'Manchester United games', 'Liverpool home games'")
                response_parts.append(f"   • Check team spelling and variations")
            elif any(word in query_lower for word in ['venue', 'stadium', 'old trafford', 'anfield', 'emirates']):
                response_parts.append(f"   • Try venue names: 'games at Old Trafford', 'matches at Anfield'")
                response_parts.append(f"   • Check venue spelling and variations")
            elif any(word in query_lower for word in ['date', 'time', 'today', 'tomorrow', 'week', 'month']):
                response_parts.append(f"   • Try specific dates: 'August games', 'games this week'")
                response_parts.append(f"   • Check if the date range exists in the data")
            elif any(word in query_lower for word in ['score', 'goals', 'high', 'low', 'draw']):
                response_parts.append(f"   • Try score patterns: 'high scoring games', 'draws', 'wins'")
                response_parts.append(f"   • Check if score data is available")
            else:
                response_parts.append(f"   • Try broadening your search criteria")
                response_parts.append(f"   • Use simpler queries like 'all games' or 'Manchester United games'")
            
            response_parts.append(f"   • Check if the collection has data for your criteria")
            
            return "\n\n".join(response_parts)
        
        # Build comprehensive response for when games are found
        response_parts = []
        
        # Header
        response_parts.append(f"🎯 **Query Analysis**: {query}")
        response_parts.append(f"📊 **Found {len(results.results)} matching games**")
        
        # Filter explanation
        if metadata_filter:
            response_parts.append(f"🔍 **Applied Filters**: {self._explain_filters(metadata_filter)}")
        
        # Results summary
        response_parts.append("\n🏆 **Game Results**:")
        
        for i, result in enumerate(results.results, 1):
            metadata = result.metadata or {}
            
            # Extract game details
            home_team = metadata.get('home_team', 'Unknown')
            away_team = metadata.get('away_team', 'Unknown')
            date = metadata.get('date', 'Unknown')
            venue = metadata.get('venue', 'Unknown')
            home_score = metadata.get('home_score', '?')
            away_score = metadata.get('away_score', '?')
            status = metadata.get('status', 'Unknown')
            notes = metadata.get('notes', '')
            
            # Format game result
            game_result = f"{i}. **{home_team} vs {away_team}**"
            game_result += f"\n   📅 {date} | 🏟️ {venue} | 📊 {home_score}-{away_score}"
            game_result += f"\n   📝 {status} | 💬 {notes}"
            game_result += f"\n   🎯 Relevance Score: {result.score:.4f}"
            
            response_parts.append(game_result)
        
        # Insights and analysis
        insights = self._generate_insights(results.results, llm_context)
        if insights:
            response_parts.append(f"\n💡 **Insights**: {insights}")
        
        # Suggestions
        suggestions = self._generate_suggestions(query, results.results)
        if suggestions:
            response_parts.append(f"\n💭 **Suggestions**: {suggestions}")
        
        return "\n\n".join(response_parts)
    
    def _explain_filters(self, metadata_filter: Dict) -> str:
        """Explain metadata filters in human-readable format"""
        if not metadata_filter:
            return "No specific filters applied"
        
        explanations = []
        
        if "$and" in metadata_filter:
            for condition in metadata_filter["$and"]:
                explanations.append(self._explain_single_filter(condition))
        elif "$or" in metadata_filter:
            for condition in metadata_filter["$or"]:
                explanations.append(self._explain_single_filter(condition))
        else:
            explanations.append(self._explain_single_filter(metadata_filter))
        
        return "; ".join(explanations)
    
    def _explain_single_filter(self, filter_condition: Dict) -> str:
        """Explain a single filter condition"""
        for field, condition in filter_condition.items():
            if isinstance(condition, dict):
                for operator, value in condition.items():
                    if operator == "$eq":
                        return f"{field} equals '{value}'"
                    elif operator == "$in":
                        return f"{field} is one of {value}"
                    elif operator == "$gte":
                        return f"{field} is greater than or equal to '{value}'"
                    elif operator == "$lte":
                        return f"{field} is less than or equal to '{value}'"
        
        return str(filter_condition)
    
    def _generate_insights(self, results, llm_context: Dict) -> str:
        """Generate insights based on query results"""
        if not results:
            return ""
        
        insights = []
        
        # Team performance insights
        team_stats = {}
        for result in results:
            metadata = result.metadata or {}
            home_team = metadata.get('home_team')
            away_team = metadata.get('away_team')
            home_score = int(metadata.get('home_score', 0))
            away_score = int(metadata.get('away_score', 0))
            
            if home_team:
                if home_team not in team_stats:
                    team_stats[home_team] = {'games': 0, 'wins': 0, 'goals_for': 0, 'goals_against': 0}
                team_stats[home_team]['games'] += 1
                team_stats[home_team]['goals_for'] += home_score
                team_stats[home_team]['goals_against'] += away_score
                if home_score > away_score:
                    team_stats[home_team]['wins'] += 1
            
            if away_team:
                if away_team not in team_stats:
                    team_stats[away_team] = {'games': 0, 'wins': 0, 'goals_for': 0, 'goals_against': 0}
                team_stats[away_team]['games'] += 1
                team_stats[away_team]['goals_for'] += away_score
                team_stats[away_team]['goals_against'] += home_score
                if away_score > home_score:
                    team_stats[away_team]['wins'] += 1
        
        # Find top performers
        if team_stats:
            top_scorer = max(team_stats.items(), key=lambda x: x[1]['goals_for'])
            top_winner = max(team_stats.items(), key=lambda x: x[1]['wins'])
            
            insights.append(f"Top scorer: {top_scorer[0]} with {top_scorer[1]['goals_for']} goals")
            insights.append(f"Most wins: {top_winner[0]} with {top_winner[1]['wins']} wins")
        
        # Venue insights
        venues = {}
        for result in results:
            metadata = result.metadata or {}
            venue = metadata.get('venue')
            if venue:
                venues[venue] = venues.get(venue, 0) + 1
        
        if venues:
            most_used_venue = max(venues.items(), key=lambda x: x[1])
            insights.append(f"Most games at: {most_used_venue[0]} ({most_used_venue[1]} games)")
        
        return " | ".join(insights)
    
    def _generate_suggestions(self, query: str, results) -> str:
        """Generate suggestions for follow-up queries"""
        suggestions = []
        
        if 'team' in query.lower() or 'teams' in query.lower():
            suggestions.append("Try filtering by specific teams like 'Manchester United games'")
        
        if 'venue' in query.lower() or 'stadium' in query.lower():
            suggestions.append("Try filtering by specific venues like 'games at Old Trafford'")
        
        if 'date' in query.lower() or 'time' in query.lower():
            suggestions.append("Try filtering by dates like 'games this week' or 'August games'")
        
        if 'score' in query.lower() or 'goals' in query.lower():
            suggestions.append("Try filtering by score patterns like 'high scoring games' or 'draws'")
        
        if len(results) > 5:
            suggestions.append("Try narrowing your search with more specific criteria")
        
        return " | ".join(suggestions)

def main():
    """Demo the LLM-enhanced metadata filtering system"""
    
    print("🧠 LLM-Enhanced Metadata Filtering Demo")
    print("=" * 60)
    
    # Initialize the system
    llm_filter = LLMMetadataFilter()
    
    if not llm_filter.client:
        print("❌ Failed to initialize ZeroEntropy client")
        return
    
    # Collection name
    collection_name = "Mo-schedules-test-csv"
    
    # Test queries
    test_queries = [
        "Show me all Manchester United games",
        "What games were played at Old Trafford?",
        "Find high scoring matches",
        "Show me all completed games from August",
        "Liverpool vs Arsenal games",
        "Games with lots of goals",
        "Recent matches this week",
        "Classic rivalry games"
    ]
    
    print(f"\n🎯 Testing queries on collection: {collection_name}")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: {query}")
        print("-" * 40)
        
        try:
            result = llm_filter.execute_intelligent_query(collection_name, query, k=5)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ Found {result['total_results']} results")
                print(f"🔍 Applied filter: {json.dumps(result['metadata_filter'], indent=2)}")
                print(f"🧠 LLM Response Preview:")
                
                # Show first part of LLM response
                llm_response = result['llm_response']
                preview = llm_response[:300] + "..." if len(llm_response) > 300 else llm_response
                print(f"   {preview}")
                
        except Exception as e:
            print(f"❌ Query failed: {e}")
    
    print(f"\n🎉 Demo completed!")
    print(f"\n🚀 You can now use this system in your Streamlit app!")
    print(f"   - Launch: ./launch_streamlit.sh")
    print(f"   - Go to Chat Interface")
    print(f"   - Select collection: {collection_name}")
    print(f"   - Ask natural language questions about your sports data!")

if __name__ == "__main__":
    main()
