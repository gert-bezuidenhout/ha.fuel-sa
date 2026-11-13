# API and validation

Requests use GET https://api.fuelsa.co.za/exapi/fuel/current with the key header. Values convert from cents to rand by dividing by 100. Identity uses region, fuel and grade, not database IDs or dates. Newest duplicate records win independent of order.

References: [API documentation](https://api.fuelsa.co.za/apidocs/), [examples](https://api.fuelsa.co.za/apidocs/api_data.json), [provider client](https://github.com/naileddigital/fuelsa-php-client).

Install requirements-dev.txt, then run:

```sh
python -m unittest discover -s tests -v
python tests/validate_examples.py
python -m compileall -q custom_components tests
```

Tests use mocked responses and the provider example fixture. They cover parsing, stable identities, dates, authentication and service failures. Example checks cover YAML, notification transitions, table rows, unavailable values and transparency. No tests send notifications or make live requests.

GitHub Actions also runs HACS and Hassfest. These do not replace Home Assistant setup/reauthentication/lifecycle testing. The user confirmed ten sensors and the dashboard working in the previous build; runtime code is preserved.
