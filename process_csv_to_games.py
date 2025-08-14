#!/usr/bin/env python3
"""
Process CSV to Individual Game Documents
Converts the uploaded sports schedule CSV into individual game documents
"""

import os
import csv
from dotenv import load_dotenv
from zeroentropy import ZeroEntropy, ConflictError, APIStatusError

def process_csv_to_games():
    """Process the CSV file and create individual game documents"""
    
    print("⚽ Processing CSV to Individual Game Documents")
    print("=" * 60)
    
    # Load environment
    load_dotenv()
    api_key = os.getenv("ZEROENTROPY_API_KEY")
    
    if not api_key:
        print("❌ ZEROENTROPY_API_KEY not found in .env file")
        return
    
    try:
        # Initialize client
        print("📡 Initializing ZeroEntropy client...")
        client = ZeroEntropy()
        print("✅ Client initialized successfully")
        
        collection_name = "Mo-schedules-test-csv"
        
        # First, let's check what's in the CSV document
        print(f"\n📄 Checking existing CSV document...")
        
        try:
            csv_doc = client.documents.get_info(
                collection_name=collection_name,
                path="/tmp/sports_schedule.csv"
            )
            print(f"✅ Found CSV document: {csv_doc.document.path}")
            print(f"   Status: {csv_doc.document.index_status}")
            
            # Get the content if available
            if hasattr(csv_doc.document, 'content') and csv_doc.document.content:
                print(f"   Content preview: {csv_doc.document.content[:200]}...")
            else:
                print("   Content not available")
                
        except Exception as e:
            print(f"❌ Error getting CSV document: {e}")
            return
        
        # Now let's create individual game documents
        print(f"\n📝 Creating individual game documents...")
        
        # Read the CSV file from test_documents
        csv_file = "test_documents/sports_schedule.csv"
        
        if not os.path.exists(csv_file):
            print(f"❌ CSV file not found: {csv_file}")
            return
        
        games_created = 0
        games_skipped = 0
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                # Create a unique path for each game
                game_date = row['Date']
                home_team = row['Home_Team']
                away_team = row['Away_Team']
                
                # Create document path
                doc_path = f"games/{game_date}_{home_team}_vs_{away_team}.txt"
                
                # Create content from the row
                content = {
                    "type": "text",
                    "text": f"Game: {home_team} vs {away_team}\nDate: {game_date}\nTime: {row['Game_Time']}\nVenue: {row['Venue']}\nLeague: {row['League']}\nSeason: {row['Season']}\nScore: {row['Home_Score']} - {row['Away_Score']}\nStatus: {row['Status']}\nNotes: {row['Notes']}"
                }
                
                # Create metadata
                metadata = {
                    "type": "game",
                    "date": game_date,
                    "home_team": home_team,
                    "away_team": away_team,
                    "venue": row['Venue'],
                    "game_time": row['Game_Time'],
                    "league": row['League'],
                    "season": row['Season'],
                    "home_score": row['Home_Score'],
                    "away_score": row['Away_Score'],
                    "status": row['Status'],
                    "notes": row['Notes'],
                    "source": "sports_schedule.csv"
                }
                
                try:
                    client.documents.add(
                        collection_name=collection_name,
                        path=doc_path,
                        content=content,
                        metadata=metadata
                    )
                    print(f"   ✅ Created: {home_team} vs {away_team} ({game_date})")
                    games_created += 1
                except ConflictError:
                    print(f"   ℹ️  Game already exists: {home_team} vs {away_team} ({game_date})")
                    games_skipped += 1
                except Exception as e:
                    print(f"   ❌ Failed to create {home_team} vs {away_team}: {e}")
        
        print(f"\n🎉 Processing completed!")
        print(f"   Games created: {games_created}")
        print(f"   Games skipped: {games_skipped}")
        print(f"   Total: {games_created + games_skipped}")
        
        # Show collection status
        print(f"\n📊 Collection Status:")
        try:
            status = client.status.get_status()
            print(f"   Total Documents: {status.num_documents}")
            print(f"   Indexed: {status.num_indexed_documents}")
            print(f"   Failed: {status.num_failed_documents}")
            print(f"   Processing: {status.num_parsing_documents + status.num_indexing_documents}")
        except Exception as e:
            print(f"   Could not get status: {e}")
        
        print(f"\n⚽ Now you can test the Moment sports search!")
        print(f"   Try queries like:")
        print(f"   - 'Show me all Manchester United games'")
        print(f"   - 'What games were played at Old Trafford?'")
        print(f"   - 'Find high scoring matches'")
        
    except APIStatusError as e:
        print(f"❌ API Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    process_csv_to_games()
