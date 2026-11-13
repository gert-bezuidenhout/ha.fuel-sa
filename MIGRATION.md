# Updating Fuel SA

## From 1.0.0 to 1.0.1

The integration domain remains `fuelsa`. Keep existing integration entries; do not delete and recreate them to update. Entity identities and polling behaviour are unchanged.

Download through HACS, or replace `/config/custom_components/fuelsa/` with the folder from the release ZIP, then restart Home Assistant.

The API key stays in your existing configuration entry. If rejected or expired, use the reauthentication prompt to supply a valid key. Copy `examples/www/fuelsa/` into `/config/www/fuelsa/` and use the dashboard YAML in `examples/` if desired. The notification example depends on your own `script.notification_all`; review its fields before enabling it.

## Moving a manual install to HACS

Back up Home Assistant, add this repository to HACS as an Integration, then download it and restart. Keep the same integration domain and configuration entry. Verify your sensors and dashboards afterwards. HACS manages only the integration folder; dashboard files are updated separately.
