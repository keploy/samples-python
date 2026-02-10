#!/usr/bin/env python3
"""
Simple socket-based HTTP server for Keploy compatibility.
ORIGINAL STATE - Use this for RECORDING.
"""
import socket
import json
import random
import string
import time
import sys

PORT = 5000

# Pre-compute responses for each endpoint
RESPONSES = {
    '/user/profile': {
        "id": 101,
        "username": "keploy_user",
        "active": True,
        "profile": {
            "age": 25,
            "city": "San Francisco",
            "preferences": {"theme": "dark", "notifications": True}
        },
        "roles": ["admin", "editor"]
    },
    '/user/history': {
        "user_id": 101,
        "login_history": [
            {"ip": "192.168.1.1", "timestamp": 1700000001},
            {"ip": "10.0.0.1", "timestamp": 1700000050}
        ]
    },
    '/product/search': {
        "query": "laptop",
        "total_results": 1500,
        "page": 1,
        "items": [
            {"id": "p1", "name": "Laptop Pro", "price": 1299.99, "stock": 50},
            {"id": "p2", "name": "Laptop Air", "price": 999.99, "stock": 0}
        ]
    },
    '/admin/config': {
        "maintenance_mode": False,
        "feature_flags": {"beta_access": True, "legacy_support": False},
        "deprecated_since": None,
        "retry_limit": 3
    },
    '/data/matrix': {
        "matrix": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        "dimension": "3x3"
    },
    '/data/mixed_array': {
        "mixed": [1, "string", True, {"obj": "val"}, None, [1, 2]]
    },
    '/edge/empty_response': {},
    '/edge/null_root': None,
    '/edge/special_chars': {
        "text": "Hello Hello",
        "emoji": "🚀 🔥 🐛",
        "symbols": "!@#$%^&*()_+-=[]{}|;':\",./<>?",
        "path": "C:\\Program Files\\Keploy"
    },
    # Added 10th endpoint for clean 7/3 split
    '/edge/nested_null': {
        "data": {"value": None}
    }
}

def get_large_payload():
    return {
        "payload_size": "5KB",
        "content": "".join(random.choices(string.ascii_letters, k=5000))
    }

def handle_request(client_socket):
    try:
        client_socket.settimeout(5.0)
        request = client_socket.recv(4096).decode('utf-8', errors='ignore')
        
        if not request: return
        
        lines = request.split('\r\n')
        if not lines: return
            
        request_line = lines[0]
        parts = request_line.split(' ')
        if len(parts) < 2: return
            
        method = parts[0]
        path = parts[1]
        
        print(f"Request: {method} {path}")
        
        if path == '/edge/large_payload':
            body_data = get_large_payload()
        elif path in RESPONSES:
            body_data = RESPONSES[path]
        else:
            response = "HTTP/1.0 404 Not Found\r\nConnection: close\r\n\r\nNot Found"
            client_socket.sendall(response.encode('utf-8'))
            return
        
        if body_data is None:
            body = "null"
        else:
            body = json.dumps(body_data)
        
        response = f"HTTP/1.0 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n{body}"
        client_socket.sendall(response.encode('utf-8'))
        
    except socket.timeout:
        pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind(('0.0.0.0', PORT))
    except OSError:
        print("Port in use, waiting...")
        time.sleep(2)
        server_socket.bind(('0.0.0.0', PORT))
        
    server_socket.listen(10)
    print(f"Starting ORIGINAL Server on port {PORT}...")
    
    while True:
        try:
            client_socket, addr = server_socket.accept()
            handle_request(client_socket)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Accept error: {e}")
    
    server_socket.close()

if __name__ == "__main__":
    main()