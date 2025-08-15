#!bin/bash

curl -X POST "http://localhost:8000/send-sms/" \
     -H 'Content-Type: application/json' \
     -d '{"Body": "Keploy test!", "To": "+919999999999"}'