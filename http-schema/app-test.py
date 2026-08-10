#!/usr/bin/env python3
"""
TEST VERSION of the HTTP server with MODIFIED responses.
Use this with: sudo ../../keploy-bin test -c "python3 app-test.py" --schema-match --delay 5

MODIFICATIONS FOR SCHEMA-MATCH TESTING:
- Tests 1-2: Different VALUES but same TYPES → Should PASS
- Tests 3-4: EXTRA FIELDS (superset) → Should PASS  
- Tests 5-6: TYPE MISMATCHES → Should FAIL
- Tests 7-10: Same as original (control tests) → Should PASS
"""
import socket
import json
import random
import string

PORT = 5000

RESPONSES = {
    # TEST 1: Different values, same types → PASS
    '/user/profile': {
        "id": 999,  # Changed from 101
        "username": "different_user",  # Changed
        "active": False,  # Changed from True
        "profile": {
            "age": 99,  # Changed from 25
            "city": "New York",  # Changed
            "preferences": {"theme": "light", "notifications": False}  # Changed
        },
        "roles": ["viewer"]  # Changed from ["admin", "editor"]
    },
    
    # TEST 2: Different values, same types → PASS
    '/user/history': {
        "user_id": 999,  # Changed
        "login_history": [
            {"ip": "1.1.1.1", "timestamp": 9999999999}  # Different values, fewer items
        ]
    },
    
    # TEST 3: EXTRA FIELDS (superset) → PASS
    '/product/search': {
        "query": "laptop",
        "total_results": 1500,
        "page": 1,
        "items": [
            {"id": "p1", "name": "Laptop Pro", "price": 1299.99, "stock": 50},
            {"id": "p2", "name": "Laptop Air", "price": 999.99, "stock": 0}
        ],
        "extra_field": "This field was not in original",  # EXTRA
        "metadata": {"source": "api", "cache": True}  # EXTRA nested
    },
    
    # TEST 4: EXTRA FIELDS in nested object → PASS
    '/admin/config': {
        "maintenance_mode": False,
        "feature_flags": {
            "beta_access": True, 
            "legacy_support": False,
            "new_feature": True  # EXTRA field in nested object
        },
        "deprecated_since": None,
        "retry_limit": 3,
        "added_config": "extra"  # EXTRA field at root
    },
    
    # TEST 5: TYPE MISMATCH (int → string) → FAIL
    '/data/matrix': {
        "matrix": [["1", "0", "0"], ["0", "1", "0"], ["0", "0", "1"]],  # strings instead of ints!
        "dimension": "3x3"
    },
    
    # TEST 6: TYPE MISMATCH (mixed types changed) → FAIL
    '/data/mixed_array': {
        "mixed": ["1", 2, "true", {"obj": "val"}, "null", [1, 2]]  # int->str, bool->str, null->str
    },
    
    # TEST 7-10: Same as original (control tests) → PASS
    '/edge/empty_response': {},
    '/edge/null_root': None,
    '/edge/special_chars': {
        "text": "Hello Hello",
        "emoji": "🚀 🔥 🐛",
        "symbols": "!@#$%^&*()_+-=[]{}|;':\",./<>?",
        "path": "C:\\Program Files\\Keploy"
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
        
        if not request:
            return
        
        lines = request.split('\r\n')
        if not lines:
            return
            
        request_line = lines[0]
        parts = request_line.split(' ')
        if len(parts) < 2:
            return
            
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
        
        response = f"HTTP/1.0 200 OK\r\n"
        response += f"Content-Type: application/json\r\n"
        response += f"Content-Length: {len(body)}\r\n"
        response += f"Connection: close\r\n"
        response += f"\r\n"
        response += body
        
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
    server_socket.bind(('0.0.0.0', PORT))
    server_socket.listen(10)
    
    print(f"Starting TEST Server on port {PORT}...")
    print("⚠️  This server has MODIFIED responses for schema-match testing!")
    print("Expected: 8 PASS (tests 1-4, 7-10), 2 FAIL (tests 5-6)")
    
    while True:
        try:
            client_socket, addr = server_socket.accept()
            handle_request(client_socket)
        except KeyboardInterrupt:
            print("\nShutting down...")
            break
        except Exception as e:
            print(f"Accept error: {e}")
    
    server_socket.close()

if __name__ == "__main__":
    main()
