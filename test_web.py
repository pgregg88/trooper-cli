#!/usr/bin/env python3
"""Test script for web server functionality."""

import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

import socketio
from loguru import logger

# Initialize Socket.IO client
sio = socketio.Client()

@sio.event
def connect():
    logger.info("Connected to server")

@sio.event
def disconnect():
    logger.info("Disconnected from server")

@sio.on('status')
def on_status(data):
    logger.info(f"Status: {data['message']}")

@sio.on('response')
def on_response(data):
    logger.info(f"Response: {data['message']}")
    logger.info(f"Audio received: {len(data['audio'])} bytes")
    logger.info(f"Cliff mode: {data['cliff_mode']}")

@sio.on('error')
def on_error(data):
    logger.error(f"Error: {data['message']}")

def main():
    """Run the tests."""
    try:
        # Connect to server
        sio.connect('http://localhost:5001')
        
        # Test 1: Basic message
        logger.info("\nTest 1: Basic message")
        sio.emit('message', {'message': 'What is your designation?'})
        time.sleep(5)  # Wait for response
        
        # Test 2: Cliff mode
        logger.info("\nTest 2: Cliff mode")
        sio.emit('toggle_cliff_mode')
        time.sleep(2)
        sio.emit('message', {'message': 'Tell me about TIE Fighters'})
        time.sleep(5)
        
        # Test 3: History
        logger.info("\nTest 3: History")
        sio.emit('message', {'message': 'What was my last question?'})
        time.sleep(5)
        
        # Cleanup
        sio.emit('clear_history')
        time.sleep(1)
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
    finally:
        sio.disconnect()

if __name__ == '__main__':
    main() 