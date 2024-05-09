from keploy import run, RunOptions

def test_keploy():
    try:
        options = RunOptions(delay=15, debug=False, port=0)
    except ValueError as e:
        print(e)
    run("python3 -m coverage run -p --data-file=.coverage.keploy app.py", options)