# FastAPI-Twilio Application

A sample FastAPI-Twilio app to test Keploy integration capabilities using [FastAPI](https://fastapi.tiangolo.com/) and [Twilio](https://www.twilio.com/en-us). <br>

## Installation Setup

```bash
git clone https://github.com/keploy/samples-python.git && cd samples-python/fastapi-twilio
pip3 install -r requirements.txt
```

## Installation Keploy

Keploy can be installed on Linux directly and on Windows with the help of WSL. Based on your system architecture, install the keploy latest binary release

```bash
 curl -O https://raw.githubusercontent.com/keploy/keploy/main/keploy.sh && source keploy.sh
 keploy
```

### Get your Twilio Credentials

You can get your Twilio credentials by signing in to [Twilio Console](https://console.twilio.com/).
Once you get the Twilio Account SID, Auth Token, and Phone Number, modify the `.env` file with your credentials.

### Capture the Testcases

This command will start the recording of API calls:-

```shell
keploy record -c "uvicorn main:app --reload"
```

Make API Calls using Hoppscotch, Postman or cURL command. Keploy with capture those calls to generate the test-suites containing testcases and data mocks.

### Make the POST requests

1. Replace the place holder below i.e. `YOUR_REGISTERED_PERSONAL_PHONE_NUMBER` with your registered personal phone number that you linked with Twilio.

    ```bash
    curl --location 'http://127.0.0.1:8000/send-sms/' \
    --header 'Content-Type: application/json' \
    --data '{
        "Body": "Test, testtt, testttttttssss :)",
        "To": "YOUR_REGISTERED_PERSONAL_PHONE_NUMBER",
    }'
    ```

2. Replace the place holder below i.e. `SOME_WRONG_PHONE_NUMBER` with any wrong phone number and make the request.

    ```bash
    curl --location 'http://127.0.0.1:8000/send-sms/' \
    --header 'Content-Type: application/json' \
    --data '{
        "Body": "Test, testtt, testttttttssss :)",
        "To": "SOME_WRONG_PHONE_NUMBER",
    }'
    ```

Now all these API calls were captured as **editable** testcases and written to `keploy/tests` folder. The keploy directory would also have `mocks` file that contains all the outputs of Twilio operations.

## Run the Testcases

Now let's run the application in test mode.

```shell
keploy test -c "uvicorn main:app --reload" --delay 10
```

So, no need to setup fake apis like Twilio or write mocks for them. Keploy automatically mocks them and, **The application thinks it's talking to Twilio 😄**
