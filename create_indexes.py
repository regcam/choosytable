#!/usr/bin/env python3
"""
MongoDB Index Creation Script for ChoosyTable

This script creates the necessary indexes to optimize database performance.
Run this script after setting up your MongoDB database.

Usage: python3 create_indexes.py
"""

import os
from pymongo import MongoClient, ASCENDING, DESCENDING
import sys

def create_indexes():
    """Create all necessary indexes for optimal query performance."""
    
    # MongoDB connection
    try:
        mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/choosytable')
        client = MongoClient(mongo_uri)
        db = client.choosytable
        collection = db.choosytable
        
        print("🔗 Connected to MongoDB")
        print(f"📊 Database: {db.name}")
        print(f"📋 Collection: {collection.name}")
        print()
        
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        sys.exit(1)
    
    indexes_to_create = [
        {
            'name': 'email_index',
            'keys': [('email', ASCENDING)],
            'description': 'Fast user lookup by email for authentication'
        },
        {
            'name': 'reviews_user_index', 
            'keys': [('reviews.user', ASCENDING)],
            'description': 'Fast lookup of reviews by user ID'
        },
        {
            'name': 'last_modified_index',
            'keys': [('last_modified', DESCENDING)],
            'description': 'Efficient sorting by modification date'
        },
        {
            'name': 'reviews_exists_last_modified',
            'keys': [('reviews', ASCENDING), ('last_modified', DESCENDING)],
            'description': 'Compound index for companies with reviews, sorted by date'
        },
        {
            'name': 'company_name_index',
            'keys': [('company', ASCENDING)],
            'description': 'Fast company lookup by name'
        },
        {
            'name': 'reviews_id_index',
            'keys': [('reviews._id', ASCENDING)],
            'description': 'Fast review lookup by review ID'
        },
        {
            'name': 'user_id_index',
            'keys': [('_id', ASCENDING)],
            'description': 'Ensure _id index exists (usually automatic)'
        }
    ]
    
    print("🚀 Creating indexes...")
    print("=" * 60)
    
    created_count = 0
    skipped_count = 0
    
    for index_info in indexes_to_create:
        try:
            # Check if index already exists
            existing_indexes = collection.list_indexes()
            index_exists = any(
                idx.get('name') == index_info['name'] 
                for idx in existing_indexes
            )
            
            if index_exists:
                print(f"⏭️  {index_info['name']}: Already exists - skipped")
                skipped_count += 1
                continue
            
            # Create the index
            collection.create_index(
                index_info['keys'], 
                name=index_info['name'],
                background=True  # Create in background to avoid blocking
            )
            
            print(f"✅ {index_info['name']}: Created successfully")
            print(f"   📝 {index_info['description']}")
            created_count += 1
            
        except Exception as e:
            print(f"❌ {index_info['name']}: Failed to create - {e}")
    
    print("=" * 60)
    print(f"📊 Summary:")
    print(f"   ✅ Created: {created_count} indexes")
    print(f"   ⏭️  Skipped: {skipped_count} indexes (already existed)")
    
    # Display all current indexes
    print(f"\n📋 Current indexes in {collection.name}:")
    for idx in collection.list_indexes():
        index_name = idx.get('name', 'unnamed')
        key_info = idx.get('key', {})
        print(f"   • {index_name}: {dict(key_info)}")
    
    print("\n🎉 Index creation completed!")
    client.close()

def check_index_usage():
    """Check if indexes are being used effectively (optional diagnostic)."""
    
    try:
        mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/choosytable')
        client = MongoClient(mongo_uri)
        db = client.choosytable
        collection = db.choosytable
        
        print("\n🔍 Checking index usage statistics...")
        
        # Get index stats
        stats = db.command("collStats", "choosytable", indexDetails=True)
        
        if 'indexSizes' in stats:
            print("\n📊 Index sizes:")
            for index_name, size in stats['indexSizes'].items():
                print(f"   • {index_name}: {size} bytes")
        
        client.close()
        
    except Exception as e:
        print(f"⚠️  Could not retrieve index statistics: {e}")

if __name__ == "__main__":
    print("🗄️  MongoDB Index Creation Script")
    print("=" * 60)
    
    create_indexes()
    
    # Optionally check usage stats
    check_index_usage()
    
    print("\n💡 Next steps:")
    print("   1. Monitor query performance in your application")
    print("   2. Use db.collection.explain() to verify index usage")
    print("   3. Consider adding more specific indexes based on query patterns")