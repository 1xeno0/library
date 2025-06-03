from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from datetime import datetime
import re
from config import Config

class DatabaseManager:
    def __init__(self):
        """Initialize database connection."""
        try:
            self.client = MongoClient(Config.MONGODB_URI)
            self.db = self.client[Config.DATABASE_NAME]
            self.collection = self.db[Config.COLLECTION_NAME]
            
            # Test connection
            self.client.admin.command('ping')
            print("✓ Connected to MongoDB successfully")
            
            # Create indexes for better search performance
            self.collection.create_index("video_url", unique=True)
            self.collection.create_index([("title", "text"), ("description", "text")])
            self.collection.create_index("tags")
            
        except ConnectionFailure as e:
            print(f"✗ Failed to connect to MongoDB: {e}")
            raise
    
    def save_video_analysis(self, video_data):
        """Save video analysis to database."""
        try:
            # Add timestamp
            video_data['created_at'] = datetime.utcnow()
            video_data['updated_at'] = datetime.utcnow()
            
            # Insert or update
            result = self.collection.update_one(
                {'video_url': video_data['video_url']},
                {'$set': video_data},
                upsert=True
            )
            
            if result.upserted_id:
                print(f"✓ New video analysis saved with ID: {result.upserted_id}")
                return str(result.upserted_id)
            else:
                print(f"✓ Video analysis updated for URL: {video_data['video_url']}")
                return str(result.matched_count)
                
        except Exception as e:
            print(f"✗ Error saving video analysis: {e}")
            raise
    
    def find_video_by_url(self, video_url):
        """Find video by URL."""
        try:
            return self.collection.find_one({'video_url': video_url})
        except Exception as e:
            print(f"✗ Error finding video by URL: {e}")
            return None
    
    def search_videos(self, query=None, tags=None, limit=50):
        """Search videos by query and/or tags."""
        try:
            search_filter = {}
            
            # Text search in title and description
            if query:
                search_filter['$or'] = [
                    {'title': {'$regex': re.escape(query), '$options': 'i'}},
                    {'description': {'$regex': re.escape(query), '$options': 'i'}}
                ]
            
            # Tag search
            if tags:
                if isinstance(tags, str):
                    tags = [tags]
                
                tag_filter = {'tags': {'$in': tags}}
                
                if '$or' in search_filter:
                    # Combine text and tag search
                    search_filter = {'$and': [search_filter, tag_filter]}
                else:
                    search_filter = tag_filter
            
            # Execute search
            cursor = self.collection.find(search_filter).limit(limit)
            results = list(cursor)
            
            print(f"✓ Found {len(results)} videos matching search criteria")
            return results
            
        except Exception as e:
            print(f"✗ Error searching videos: {e}")
            return []
    
    def get_all_videos(self, limit=100):
        """Get all videos from database."""
        try:
            cursor = self.collection.find().limit(limit).sort('created_at', -1)
            results = list(cursor)
            print(f"✓ Retrieved {len(results)} videos")
            return results
        except Exception as e:
            print(f"✗ Error retrieving videos: {e}")
            return []
    
    def get_video_count(self):
        """Get total number of videos in database."""
        try:
            count = self.collection.count_documents({})
            return count
        except Exception as e:
            print(f"✗ Error getting video count: {e}")
            return 0
    
    def delete_video(self, video_url):
        """Delete video by URL."""
        try:
            result = self.collection.delete_one({'video_url': video_url})
            if result.deleted_count > 0:
                print(f"✓ Video deleted: {video_url}")
                return True
            else:
                print(f"✗ Video not found: {video_url}")
                return False
        except Exception as e:
            print(f"✗ Error deleting video: {e}")
            return False
    
    def close_connection(self):
        """Close database connection."""
        try:
            self.client.close()
            print("✓ Database connection closed")
        except Exception as e:
            print(f"✗ Error closing database connection: {e}") 