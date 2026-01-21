#!/usr/bin/env python3
"""
Test script to verify messageKey extraction and passthrough functionality.

This test validates that the messageKey field sent by the client is correctly
extracted from WebSocket messages and included in message broadcasts for file
attachment correlation.
"""

import os
import sys
import json
import asyncio
import random
import string
import websockets
import ssl

# Set test encryption key before importing modules that need it
if 'DECENTRA_ENCRYPTION_KEY' not in os.environ:
    os.environ['DECENTRA_ENCRYPTION_KEY'] = 'test-encryption-key-for-messagekey-tests'

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

from database import Database
import bcrypt

def hash_password(password):
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def generate_unique_suffix():
    """Generate a unique suffix for test data to avoid conflicts."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def cleanup_test_data(db, usernames, server_ids, dm_ids):
    """Clean up test data from the database."""
    print("\nCleaning up test data...")
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Delete messages for test servers
            for server_id in server_ids:
                cursor.execute("DELETE FROM messages WHERE context_id = %s OR context_id LIKE %s", 
                              (server_id, server_id + '/%'))
            
            # Delete DM messages
            for dm_id in dm_ids:
                cursor.execute("DELETE FROM messages WHERE context_id = %s", (dm_id,))
            
            # Delete DMs
            for dm_id in dm_ids:
                cursor.execute('DELETE FROM direct_messages WHERE dm_id = %s', (dm_id,))
            
            # Delete servers (cascades to channels and server_members)
            for server_id in server_ids:
                cursor.execute('DELETE FROM servers WHERE server_id = %s', (server_id,))
            
            # Delete users (cascades to related data)
            for username in usernames:
                cursor.execute('DELETE FROM users WHERE username = %s', (username,))
            
            conn.commit()
        print("✓ Test data cleaned up")
    except Exception as e:
        print(f"⚠ Cleanup warning: {e}")

async def connect_websocket(username, password):
    """Connect to the WebSocket server and authenticate."""
    # Create SSL context that doesn't verify certificates (for testing)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Connect to WebSocket
    uri = "wss://localhost:8765/ws"
    websocket = await websockets.connect(uri, ssl=ssl_context)
    
    # Authenticate
    auth_msg = {
        "type": "auth",
        "username": username,
        "password": password
    }
    await websocket.send(json.dumps(auth_msg))
    
    # Wait for auth response
    response = await websocket.recv()
    response_data = json.loads(response)
    
    if response_data.get('type') != 'auth_success':
        raise Exception(f"Authentication failed: {response_data}")
    
    return websocket

async def test_messagekey_passthrough():
    """Test messageKey extraction and passthrough in all contexts."""
    print("Testing messageKey Extraction and Passthrough")
    print("=" * 60)
    
    # Use PostgreSQL test database
    test_db_url = os.getenv('TEST_DATABASE_URL', 'postgresql://decentra:decentra@localhost:5432/decentra_test')
    
    db = Database(test_db_url)
    print("✓ Database connected successfully")
    
    # Generate unique identifiers for this test run
    suffix = generate_unique_suffix()
    alice_username = f"alice_mk_{suffix}"
    bob_username = f"bob_mk_{suffix}"
    server_id = f"server_mk_{suffix}"
    channel_id = f"channel_mk_{suffix}"
    dm_id = f"dm_mk_{suffix}"
    
    usernames = [alice_username, bob_username]
    server_ids = [server_id]
    dm_ids = [dm_id]
    
    try:
        # Create test users
        print("\nSetup: Creating test users...")
        password = "testpass123"
        assert db.create_user(alice_username, hash_password(password)), "Failed to create alice"
        assert db.create_user(bob_username, hash_password(password)), "Failed to create bob"
        print("✓ Test users created")
        
        # Create server and channel for testing
        print("\nSetup: Creating server and channel...")
        assert db.create_server(server_id, "Test Server", alice_username), "Failed to create server"
        assert db.create_channel(channel_id, server_id, "general", "text"), "Failed to create channel"
        assert db.add_server_member(server_id, bob_username), "Failed to add bob to server"
        print("✓ Server and channel created")
        
        # Create DM for testing
        print("\nSetup: Creating DM...")
        assert db.create_dm(alice_username, bob_username, dm_id), "Failed to create DM"
        print("✓ DM created")
        
        # Test 1: Server channel message with messageKey
        print("\n" + "=" * 60)
        print("Test 1: Server channel message with messageKey")
        print("-" * 60)
        
        alice_ws = await connect_websocket(alice_username, password)
        bob_ws = await connect_websocket(bob_username, password)
        print("✓ WebSocket connections established")
        
        # Alice sends a message with messageKey
        test_message_key_1 = f"1234567890_abc123_Test message {suffix}"
        message_data_1 = {
            "type": "message",
            "content": "Hello from server channel",
            "context": "server",
            "context_id": f"{server_id}/{channel_id}",
            "messageKey": test_message_key_1
        }
        await alice_ws.send(json.dumps(message_data_1))
        print(f"✓ Alice sent message with messageKey: {test_message_key_1[:30]}...")
        
        # Alice should receive her own message with messageKey
        alice_received = await asyncio.wait_for(alice_ws.recv(), timeout=5.0)
        alice_msg = json.loads(alice_received)
        
        assert alice_msg.get('type') == 'message', f"Expected message type, got {alice_msg.get('type')}"
        assert alice_msg.get('username') == alice_username, "Username doesn't match"
        assert alice_msg.get('content') == "Hello from server channel", "Content doesn't match"
        assert 'messageKey' in alice_msg, "messageKey not found in broadcast message"
        assert alice_msg['messageKey'] == test_message_key_1, f"messageKey mismatch: expected {test_message_key_1}, got {alice_msg.get('messageKey')}"
        assert 'id' in alice_msg, "Message ID not found"
        print(f"✓ Alice received her message with correct messageKey")
        
        # Bob should also receive the message with messageKey
        bob_received = await asyncio.wait_for(bob_ws.recv(), timeout=5.0)
        bob_msg = json.loads(bob_received)
        
        assert bob_msg.get('messageKey') == test_message_key_1, "Bob should see same messageKey"
        print(f"✓ Bob received message with correct messageKey")
        
        # Test 2: DM message with messageKey
        print("\n" + "=" * 60)
        print("Test 2: Direct message with messageKey")
        print("-" * 60)
        
        test_message_key_2 = f"9876543210_xyz789_DM test {suffix}"
        message_data_2 = {
            "type": "message",
            "content": "Hello from DM",
            "context": "dm",
            "context_id": dm_id,
            "messageKey": test_message_key_2
        }
        await alice_ws.send(json.dumps(message_data_2))
        print(f"✓ Alice sent DM with messageKey: {test_message_key_2[:30]}...")
        
        # Alice should receive her own DM with messageKey
        alice_dm_received = await asyncio.wait_for(alice_ws.recv(), timeout=5.0)
        alice_dm_msg = json.loads(alice_dm_received)
        
        assert alice_dm_msg.get('type') == 'message', "Expected message type"
        assert alice_dm_msg.get('content') == "Hello from DM", "DM content doesn't match"
        assert 'messageKey' in alice_dm_msg, "messageKey not found in DM broadcast"
        assert alice_dm_msg['messageKey'] == test_message_key_2, f"DM messageKey mismatch"
        assert 'id' in alice_dm_msg, "Message ID not found in DM"
        print(f"✓ Alice received her DM with correct messageKey")
        
        # Bob should also receive the DM with messageKey
        bob_dm_received = await asyncio.wait_for(bob_ws.recv(), timeout=5.0)
        bob_dm_msg = json.loads(bob_dm_received)
        
        assert bob_dm_msg.get('messageKey') == test_message_key_2, "Bob should see same DM messageKey"
        print(f"✓ Bob received DM with correct messageKey")
        
        # Test 3: Message without messageKey (backward compatibility)
        print("\n" + "=" * 60)
        print("Test 3: Message without messageKey (backward compatibility)")
        print("-" * 60)
        
        message_data_3 = {
            "type": "message",
            "content": "Message without key",
            "context": "server",
            "context_id": f"{server_id}/{channel_id}"
            # No messageKey field
        }
        await alice_ws.send(json.dumps(message_data_3))
        print("✓ Alice sent message without messageKey")
        
        # Alice should receive message without messageKey
        alice_no_key = await asyncio.wait_for(alice_ws.recv(), timeout=5.0)
        alice_no_key_msg = json.loads(alice_no_key)
        
        assert alice_no_key_msg.get('type') == 'message', "Expected message type"
        assert alice_no_key_msg.get('content') == "Message without key", "Content doesn't match"
        assert 'messageKey' not in alice_no_key_msg, "messageKey should not be present when not sent"
        assert 'id' in alice_no_key_msg, "Message ID should still be present"
        print(f"✓ Message without messageKey works correctly (backward compatible)")
        
        # Test 4: Verify messageKey is stored in database message
        print("\n" + "=" * 60)
        print("Test 4: Verify messageKey correlation with database")
        print("-" * 60)
        
        # Get the message from database
        msg_from_db = db.get_message(alice_msg['id'])
        assert msg_from_db is not None, "Message not found in database"
        assert msg_from_db['content'] == "Hello from server channel", "DB message content doesn't match"
        print(f"✓ Message correctly stored in database with ID: {alice_msg['id']}")
        
        # Close WebSocket connections
        await alice_ws.close()
        await bob_ws.close()
        print("\n✓ WebSocket connections closed")
        
        print("\n" + "=" * 60)
        print("All messageKey tests passed successfully! ✓")
        print("=" * 60)
        print("\nSummary:")
        print("  ✓ messageKey correctly extracted from incoming messages")
        print("  ✓ messageKey passed through in server channel messages")
        print("  ✓ messageKey passed through in direct messages")
        print("  ✓ Messages without messageKey handled correctly (backward compatible)")
        print("  ✓ messageKey enables file attachment correlation")
        
    finally:
        # Clean up test data
        cleanup_test_data(db, usernames, server_ids, dm_ids)

def main():
    """Main entry point for the test."""
    # Check if server is running
    print("Note: This test requires the server to be running on localhost:8765")
    print("Start the server with: cd server && python3 server.py")
    print()
    
    try:
        asyncio.run(test_messagekey_passthrough())
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except websockets.exceptions.WebSocketException as e:
        print(f"\n✗ WebSocket connection failed: {e}")
        print("Make sure the server is running on localhost:8765")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
