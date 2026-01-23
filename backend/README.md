# Tests
```
# Run all tests
pytest src/tests/ -v

# Run only auth tests
pytest src/tests/test_auth.py -v

# Run a specific test class
pytest src/tests/test_auth.py::TestLogin -v

# Run a specific test
pytest src/tests/test_auth.py::TestLogin::test_login_success -v

# Run with print statements visible
pytest src/tests/test_auth.py -v -s

# Run and stop on first failure
pytest src/tests/test_auth.py -v -x

# Run with coverage report
pytest src/tests/ -v --cov=src --cov-report=html
```
