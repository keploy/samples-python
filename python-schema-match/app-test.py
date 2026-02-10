#!/usr/bin/env python3
"""
TEST VERSION of the HTTP server with MODIFIED responses.
Use this for TESTING mode.

EXPECTED RESULTS (Total 10):
PASS: 7
FAIL: 3 (Missing Field, Type Mismatch, Hierarchy Mismatch)
"""
import socket
import json
import random
import string
import time

PORT = 5000

RESPONSES = {
    # 1. PASS: Different values, same types
    '/user/profile': {
        "id": 999,
        "username": "different_user",
        "active": False,
        "profile": {
            "age": 99,
            "city": "New York",
            "preferences": {"theme": "light", "notifications": False}
        },
        "roles": ["viewer"]
    },
    
    # 2. PASS: Array length diff (Standard schema matching allows this)
    '/user/history': {
        "user_id": 999,
        "login_history": [
            {"ip": "1.1.1.1", "timestamp": 9999999999}
        ]
    },
    
    # 3. PASS: Extra fields (Superset is allowed)
    '/product/search': {
        "query": "laptop",
        "total_results": 1500,
        "page": 1,
        "items": [
            {"id": "p1", "name": "Laptop Pro", "price": 1299.99, "stock": 50},
            {"id": "p2", "name": "Laptop Air", "price": 999.99, "stock": 0}
        ],
        "extra_field": "This field was not in original",
        "metadata": {"source": "api", "cache": True}
    },
    
    # 4. FAIL: FIELD DELETION (Missing 'feature_flags')
    '/admin/config': {
        "maintenance_mode": False,
        # "feature_flags": MISSING! -> Should Fail
        "deprecated_since": None,
        "retry_limit": 3,
        "added_config": "extra"
    },
    
    # 5. FAIL: TYPE MISMATCH (Int -> String)
    '/data/matrix': {
        "matrix": [["1", "0", "0"], ["0", "1", "0"], ["0", "0", "1"]],
        "dimension": "3x3"
    },
    
    # 6. FAIL: HIERARCHY/TUPLE MISMATCH
    # Original: [int, string, bool...]
    # Here: [string, int, bool...] (Swapped first two)
    '/data/mixed_array': {
        "mixed": ["string", 1, True, {"obj": "val"}, None, [1, 2]]
    },
    
    # 7. PASS: Exact match
    '/edge/empty_response': {},
    
    # 8. PASS: Exact match
    '/edge/null_root': None,
    
    # 9. PASS: Exact match
    '/edge/special_chars': {
        "text": "Hello Hello",
        "emoji": "🚀 🔥 🐛",
        "symbols": "!@#$%^&*()_+-=[]{}|;':\",./<>?",
        "path": "C:\\Program Files\\Keploy"
    },

    # 10. PASS: Exact match
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
        path = parts[1]
        
        print(f"Test Request: {path}")
        
        if path == '/edge/large_payload':
            body_data = get_large_payload()
        elif path in RESPONSES:
            body_data = RESPONSES[path]
        else:
            response = "HTTP/1.0 404 Not Found\r\n\r\n"
            client_socket.sendall(response.encode('utf-8'))
            return
        
        if body_data is None:
            body = "null"
        else:
            body = json.dumps(body_data)
        
        response = f"HTTP/1.0 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(body)}\r\n\r\n{body}"
        client_socket.sendall(response.encode('utf-8'))
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', PORT))
    server_socket.listen(10)
    print(f"Starting TEST Server on port {PORT}...")
    
    while True:
        try:
            client_socket, addr = server_socket.accept()
            handle_request(client_socket)
        except KeyboardInterrupt:
            break
    server_socket.close()

if __name__ == "__main__":
    main()