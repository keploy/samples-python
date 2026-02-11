#  Python Schema Match

A sample HTTP server application designed to test and validate JSON schema matching capabilities with Keploy. This application serves multiple diverse endpoints with various response schemas to comprehensively test schema structure validation and compatibility.

## Overview

This application is a simple socket-based HTTP server written in Python that provides 10 endpoints covering different schema patterns including:

- **Nested Objects**: User profile with complex nested data structures
- **Arrays**: Different array formats and mixed-type arrays
- **Edge Cases**: Null values, empty responses, special characters, and large payloads
- **Data Types**: Strings, numbers, booleans, objects, and null values

The application supports schema validation testing to ensure API responses maintain consistent structure across different versions or implementations.

### API Endpoints

1. `GET /user/profile` - Returns user profile with nested preferences
2. `GET /user/history` - Returns user login history with array of objects
3. `GET /product/search` - Returns product search results with items array
4. `GET /admin/config` - Returns admin configuration with feature flags
5. `GET /data/matrix` - Returns a matrix data structure
6. `GET /data/mixed_array` - Returns an array with mixed data types
7. `GET /edge/empty_response` - Returns an empty JSON object
8. `GET /edge/null_root` - Returns a null value at root
9. `GET /edge/special_chars` - Returns special characters and escape sequences
10. `GET /edge/nested_null` - Returns an object with null values

## Installation & Setup

### Prerequisites

- Python 3.7 or higher
- Keploy CLI installed on your system
- Linux or WSL (for Windows users)

### Install Keploy

```bash
curl -O -L https://keploy.io/install.sh && source install.sh
```

### Clone the Repository

```bash
git clone https://github.com/keploy/samples-python.git && cd samples-python/python-schema-match
```

## Running the Application

### Start the Server (Original Version - for Recording)

This server returns standard responses and is used for recording test cases:

```bash
python3 app.py
```

The server will start on `http://localhost:5000`

### Start the Test Server (Modified Version - for Testing)

This server returns modified responses with schema variations to test compatibility:

```bash
python3 app-test.py
```

## Keploy Integration

### Recording Test Cases

Keploy will capture API calls and generate test cases with mocked responses.

**1. Start Recording:**

```bash
keploy record -c "python3 app.py"
```

The server will start and be ready to capture API interactions.

**2. Generate Test Cases by Making API Calls:**

Use curl, Postman, or Hoppscotch to make requests to the endpoints. Here are some examples:

```bash
# Check endpoint 1: User Profile
curl http://localhost:5000/user/profile

# Check endpoint 2: User History
curl http://localhost:5000/user/history

# Check endpoint 3: Product Search
curl http://localhost:5000/product/search

# Check endpoint 4: Admin Config
curl http://localhost:5000/admin/config

# Check endpoint 5: Data Matrix
curl http://localhost:5000/data/matrix

# Check endpoint 6: Mixed Array
curl http://localhost:5000/data/mixed_array

# Check endpoint 7: Empty Response
curl http://localhost:5000/edge/empty_response

# Check endpoint 8: Null Root
curl http://localhost:5000/edge/null_root

# Check endpoint 9: Special Characters
curl http://localhost:5000/edge/special_chars

# Check endpoint 10: Nested Null
curl http://localhost:5000/edge/nested_null
```

Or use the provided endpoint checker script:

```bash
python3 check-endpoints.py
```

This script will automatically test all 10 endpoints and provide a summary.

**3. Keploy Test Artifacts**

After making API calls, Keploy will generate test cases in the `keploy/` directory:

- **Test Files**: `keploy/tests/test-*.yml` - Contains HTTP request/response pairs
- **Mock Files**: `keploy/mocks/mocks.yml` - Contains any external service interactions

Each test file captures:
- **Request**: HTTP method, headers, URL, and body
- **Response**: Status code, headers, and response body
- **Assertions**: Validation rules including noise fields (like timestamps)

Example test output:

```yaml
version: api.keploy.io/v1beta2
kind: Http
name: test-1
spec:
  metadata: {}
  req:
    method: GET
    url: http://localhost:5000/user/profile
    header:
      Accept: "*/*"
      Host: localhost:5000
      User-Agent: curl/7.68.0
  resp:
    status_code: 200
    header:
      Content-Type: application/json
      Content-Length: "245"
    body: |
      {
        "id": 101,
        "username": "keploy_user",
        "active": true,
        "profile": {
          "age": 25,
          "city": "San Francisco",
          "preferences": {"theme": "dark", "notifications": true}
        },
        "roles": ["admin", "editor"]
      }
  assertions:
    noise:
      - header.Date
  created: 1694000000
```

### Running Test Cases

Test your application against the captured test cases using the test server:

```bash
keploy test -c "python3 app-test.py" --delay 5
```

The `--delay` flag gives your application time to start before tests begin (in seconds).

**Expected Results:**

- **Total Endpoints**: 10
- **Expected PASS**: 7 (Same schema structure, different values)
- **Expected FAIL**: 3 (Schema modifications testing)
  - Missing fields
  - Type mismatches
  - Hierarchy mismatches

The application validates that:
1. Extra fields are allowed (superset schema)
2. Array length variations are acceptable
3. Different values with same types pass
4. Type changes are detected
5. Missing required fields are detected
6. Nested structure changes are caught

### Output and Coverage

After running tests, Keploy will display:
- Test summary (passed/failed count)
- Coverage metrics
- Detailed failure reports with diff information

## Project Structure

```
python-schema-match/
├── app.py                      # Original HTTP server (for recording)
├── app-test.py                 # Modified HTTP server (for testing)
├── check-endpoints.py          # Utility script to test all endpoints
├── README.md                   # This file
└── keploy/                     # Keploy artifacts (generated)
    ├── tests/
    │   ├── test-1.yml
    │   ├── test-2.yml
    │   └── ...
    └── mocks/
        └── mocks.yml
```

## Use Cases

This sample application demonstrates:

1. **Schema Validation**: Ensure API responses maintain consistent JSON structure
2. **API Contract Testing**: Validate that responses match expected schemas
3. **Backward Compatibility**: Test if new versions break schema contracts
4. **Data Type Verification**: Ensure fields have correct data types
5. **Response Structure Integrity**: Validate nested objects and arrays

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, modify the `PORT` variable in `app.py` or `app-test.py`.

### Connection Refused
Ensure the server is running before making API calls or running tests.

### Test Failures
Expected failures are intentional to demonstrate schema mismatch detection. Review the diff information in Keploy output to understand the schema differences.

## Additional Resources

- [Keploy Documentation](https://docs.keploy.io)
- [JSON Schema Guide](https://json-schema.org/)
- [Python HTTP Servers](https://docs.python.org/3/library/http.server.html)

## Contributing

Feel free to extend this sample by:
- Adding more diverse schema patterns
- Testing additional data types
- Creating more complex nested structures
- Adding custom validation rules

## License

MIT License - See LICENSE.md for details

---

**Happy Testing! 🚀**
