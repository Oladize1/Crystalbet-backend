import asyncio
from db.mongodb import MongoDBConnection

async def main():
    """Main function to test MongoDB connection and operations."""
    try:
        await MongoDBConnection.connect()
        
        # Fetch and display quick links and A-Z menu items
        quick_links = await MongoDBConnection.fetch_quick_links()
        az_menu = await MongoDBConnection.fetch_az_menu()
        
        print("Quick Links:", quick_links)
        print("A-Z Menu:", az_menu)
    
    finally:
        await MongoDBConnection.close_connection()

if __name__ == "__main__":
    asyncio.run(main())
