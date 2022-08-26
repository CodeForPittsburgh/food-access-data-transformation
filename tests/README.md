# Unit Tests

This section of the repository contains the unit tests for the scripts and modules being used in the data transformation. The unit tests leverage the following base modules.

* [PyTest](https://docs.pytest.org/en/7.1.x/)
* [AssertPy](https://assertpy.github.io/docs.html)

PyTest provides the framework for test execution while AssertPy provides a fluent interface for performing common assertions within the tests.

## Adding Tests

These tests were constructed with a Test Driven Development (TDD) mindset. Additional tests can be added to each of the existing Testing Modules or additional modules can be added. All Unit Test files should follow the existing naming convention: `<module_name>_test.py`.

## Executing Tests

Tests can be executed simply by invoking pytest at the command line:

```bash
pytest
```

This will execute the PyTest module and execute all of the tests located in the __tests__ directory.