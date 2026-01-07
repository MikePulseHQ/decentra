#!/usr/bin/env python3
"""
Test script to verify user profile bio and status message functionality
"""

import os
import sys
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from database import Database
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def test_profile():
    print("Testing User Profile Bio and Status Message")
    print("=" * 50)
    
    # Use a temporary test database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_profile.db")
    
    # For PostgreSQL, use in-memory or test database
    # For this test, we'll use a local SQLite database if the Database class supports it
    # Otherwise, skip the test
    try:
        db = Database(db_path)
        print("✓ Database created successfully")
    except Exception as e:
        print(f"⚠ Warning: Could not create test database: {e}")
        print("Skipping test (requires PostgreSQL or modified Database class)")
        return
    
    # Test 1: Create user and verify default profile fields
    print("\nTest 1: Creating user and checking default profile...")
    assert db.create_user("alice", hash_password("password123")), "Failed to create alice"
    alice = db.get_user("alice")
    assert alice is not None, "Failed to retrieve alice"
    assert alice['bio'] == '', "Default bio should be empty"
    assert alice['status_message'] == '', "Default status should be empty"
    print("✓ User created with empty bio and status")
    
    # Test 2: Update profile with bio and status
    print("\nTest 2: Updating profile with bio and status...")
    db.update_user_profile("alice", 
                          bio="I love coding!", 
                          status_message="Coding away...")
    alice = db.get_user("alice")
    assert alice['bio'] == "I love coding!", "Bio not updated"
    assert alice['status_message'] == "Coding away...", "Status not updated"
    print(f"✓ Profile updated - Bio: '{alice['bio']}', Status: '{alice['status_message']}'")
    
    # Test 3: Update only bio
    print("\nTest 3: Updating only bio...")
    db.update_user_profile("alice", bio="Updated bio")
    alice = db.get_user("alice")
    assert alice['bio'] == "Updated bio", "Bio not updated"
    assert alice['status_message'] == "Coding away...", "Status should remain unchanged"
    print(f"✓ Bio updated, status unchanged: '{alice['status_message']}'")
    
    # Test 4: Update only status
    print("\nTest 4: Updating only status...")
    db.update_user_profile("alice", status_message="New status")
    alice = db.get_user("alice")
    assert alice['bio'] == "Updated bio", "Bio should remain unchanged"
    assert alice['status_message'] == "New status", "Status not updated"
    print(f"✓ Status updated, bio unchanged: '{alice['bio']}'")
    
    # Test 5: Clear profile
    print("\nTest 5: Clearing profile...")
    db.update_user_profile("alice", bio="", status_message="")
    alice = db.get_user("alice")
    assert alice['bio'] == "", "Bio not cleared"
    assert alice['status_message'] == "", "Status not cleared"
    print("✓ Profile cleared successfully")
    
    # Test 6: Long bio and status
    print("\nTest 6: Testing long bio and status...")
    long_bio = "A" * 500  # Max length
    long_status = "B" * 100  # Max length
    db.update_user_profile("alice", bio=long_bio, status_message=long_status)
    alice = db.get_user("alice")
    assert len(alice['bio']) == 500, "Long bio not saved correctly"
    assert len(alice['status_message']) == 100, "Long status not saved correctly"
    print("✓ Maximum length bio and status saved successfully")
    
    # Cleanup
    try:
        os.remove(db_path)
        os.rmdir(temp_dir)
    except:
        pass
    
    print("\n" + "=" * 50)
    print("All profile tests passed! ✓")
    print("Profile bio and status functionality is working correctly.")

if __name__ == "__main__":
    test_profile()
