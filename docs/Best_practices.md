# Best Practices

For the engineering practices,

- **Unit test** for testing **prediction** part from **deployment** section. **Model Mock** and **Dv Mock** is used in unit testing.
- **Integration Test** for testing the whole **prediction service** from **deployment** section.
- **Linting Tools and Formatters** like pylint, black and isort for code quality
- **Git pre-commit hooks** to check and enforce certain code quality before allowing a commit to proceed
- **Makefile** for automation of the commands and build process

## CI/CD

- Unit case and Integration test for CI/CD will be implemented via **github actions**.
