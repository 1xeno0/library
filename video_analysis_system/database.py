from pymongo import MongoClient
from pymongo.errors import ConfigurationError, ServerSelectionTimeoutError
from datetime import datetime
import config
import logging
import re

class DatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.videos_collection = None
        self.connected = False
        
        try:
            self.client = MongoClient(config.MONGODB_URI, serverSelectionTimeoutMS=5000)
            # Test the connection
            self.client.admin.command('ping')
            self.db = self.client.patchwork_library
            self.videos_collection = self.db.videos
            self.connected = True
            print("✅ MongoDB connected successfully")
        except (ConfigurationError, ServerSelectionTimeoutError, Exception) as e:
            print(f"⚠️  MongoDB connection failed: {e}")
            print("📝 Running in offline mode - video analysis will work but search won't persist")
            self.connected = False
        
    def save_video_analysis(self, video_url, analysis_data):
        """Save video analysis to MongoDB"""
        if not self.connected:
            print("⚠️  Database not connected - analysis not saved")
            return None
            
        try:
            document = {
                "video_url": video_url,
                "title": analysis_data.get("title", ""),
                "description": analysis_data.get("description", ""),
                "tags": analysis_data.get("tags", []),
                "upload_date": analysis_data.get("upload_date", ""),
                "analyzed_at": datetime.utcnow(),
                "frames_analyzed": analysis_data.get("frames_analyzed", [])
            }
            
            # Check if video already exists
            existing = self.videos_collection.find_one({"video_url": video_url})
            if existing:
                # Update existing document
                self.videos_collection.update_one(
                    {"video_url": video_url},
                    {"$set": document}
                )
                return existing["_id"]
            else:
                # Insert new document
                result = self.videos_collection.insert_one(document)
                return result.inserted_id
        except Exception as e:
            print(f"⚠️  Failed to save to database: {e}")
            return None
    
    def search_videos(self, search_query="", tags=None):
        """
        Search videos by text query and/or tags
        Simplified approach for reliable searching
        """
        try:
            if not self.connected:
                print("⚠️  Database not connected, returning empty results")
                return []
            
            # Build search criteria
            search_conditions = []
            
            # Text search
            if search_query:
                query_words = search_query.lower().split()
                
                # Create OR conditions for each word in title, description, or tags
                word_conditions = []
                for word in query_words:
                    escaped_word = re.escape(word)
                    word_conditions.append({
                        "$or": [
                            {"title": {"$regex": escaped_word, "$options": "i"}},
                            {"description": {"$regex": escaped_word, "$options": "i"}},
                            {"tags": {"$regex": escaped_word, "$options": "i"}}
                        ]
                    })
                
                # All words must match (AND)
                if word_conditions:
                    search_conditions.append({"$and": word_conditions})
            
            # Tag search
            if tags and len(tags) > 0:
                valid_tags = [tag.strip() for tag in tags if tag.strip()]
                if valid_tags:
                    # Search for exact tag matches or partial matches
                    tag_conditions = []
                    for tag in valid_tags:
                        escaped_tag = re.escape(tag)
                        tag_conditions.append({"tags": {"$regex": escaped_tag, "$options": "i"}})
                    
                    if tag_conditions:
                        search_conditions.append({"$or": tag_conditions})
            
            # Combine all conditions
            if search_conditions:
                if len(search_conditions) == 1:
                    query = search_conditions[0]
                else:
                    query = {"$and": search_conditions}
            else:
                # No search criteria, return all videos
                query = {}
            
            # Execute search
            cursor = self.videos_collection.find(query).sort("analyzed_at", -1).limit(50)
            results = list(cursor)
            
            # Convert ObjectId to string for JSON serialization
            for result in results:
                if "_id" in result:
                    result["_id"] = str(result["_id"])
            
            print(f"🔍 Search query: '{search_query}', tags: {tags}")
            print(f"📊 Found {len(results)} results")
            
            return results
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []
    
    def get_video_by_url(self, video_url):
        """Get video analysis by URL"""
        if not self.connected:
            return None
            
        try:
            result = self.videos_collection.find_one({"video_url": video_url})
            if result:
                result["_id"] = str(result["_id"])
                if "analyzed_at" in result:
                    result["analyzed_at"] = result["analyzed_at"].isoformat()
            return result
        except Exception as e:
            print(f"⚠️  Failed to get video from database: {e}")
            return None
    
    def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close() 