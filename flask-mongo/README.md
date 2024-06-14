# Sample Flask+Mongo app to demo Keploy

## Clone the sample flask-mongo application

```bash
git clone https://github.com/keploy/samples-python.git && cd samples-python/flask-mongo-local
```

## Install all dependencies

```bash
pip install -r requirements.txt
```

## Start the MongoDB server

```bash
sudo service mongod start
```

## Setup Keploy

Let's get started by setting up the Keploy alias with this command:


```bash
curl --silent -O -L https://keploy.io/install.sh && source install.sh
```

You should see something like this:

```bash
       ▓██▓▄
    ▓▓▓▓██▓█▓▄
     ████████▓▒
          ▀▓▓███▄      ▄▄   ▄               ▌
         ▄▌▌▓▓████▄    ██ ▓█▀  ▄▌▀▄  ▓▓▌▄   ▓█  ▄▌▓▓▌▄ ▌▌   ▓
       ▓█████████▌▓▓   ██▓█▄  ▓█▄▓▓ ▐█▌  ██ ▓█  █▌  ██  █▌ █▓
      ▓▓▓▓▀▀▀▀▓▓▓▓▓▓▌  ██  █▓  ▓▌▄▄ ▐█▓▄▓█▀ █▓█ ▀█▄▄█▀   █▓█
       ▓▌                           ▐█▌                   █▌
        ▓

Keploy CLI

Available Commands:
  example         Example to record and test via keploy
  generate-config generate the keploy configuration file
  record          record the keploy testcases from the API calls
  test            run the recorded testcases and execute assertions
  update          Update Keploy

Flags:
      --debug     Run in debug mode
  -h, --help      help for keploy
  -v, --version   version for keploy

Use "keploy [command] --help" for more information about a command.
```

## Lights, Camera, Record! 🎥

To initiate the recording of API calls, execute this command in your terminal:

```bash
keploy record -c "python3 app.py"
```

Now, your app will start running, and you have to make some API calls!!

And once you are done, you can stop the recording and give yourself a pat on the back! With that simple spell, you've conjured up a test case with a mock! Explore the **keploy** directory and you'll discover your handiwork in `tests` directory and `mocks.yml`.

## Check Test Coverage

We have a `test-app.py` where all the unit test cases has been written. Now using Keploy, we can check it's code coverage!!
Now to run your unit tests with Keploy, you can run the command given below:

```bash
python3 -m coverage run -p --data-file=.coverage.unit -m pytest -s test_keploy.py test_app.py
```

To combine the coverage from the unit tests, and Keploy's API tests we can use the command below:

```bash
python3 -m coverage combine
```

Finally, to generate the coverage report for the test run, you can run:

```bash
python3 -m coverage report
```

and if you want the coverage in an html file, you can run:

```bash
python3 -m coverage html
```

## Wrapping it up 🎉

Congrats on the journey so far! You've seen Keploy's power, flexed your coding muscles, and had a bit of fun too! Now, go out there and keep exploring, innovating, and creating! Remember, with the right tools and a sprinkle of fun, anything's possible.😊🚀

Happy coding! ✨👩‍💻👨‍💻✨
