# Fuel SA for Home Assistant

<img src="custom_components/fuelsa/brand/logo.png" alt="Fuel SA" width="220">

Bring South African petrol and diesel prices into Home Assistant, with Reef and Coast sensors, a dashboard and a price-change notification example.

[Home Assistant](https://www.home-assistant.io/) brings devices, services, dashboards and automations together. [Fuel SA](https://www.fuelsa.co.za/) supplies the fuel-price API.

This is an independent community integration maintained by Gert Bezuidenhout, not an official Fuel SA or Home Assistant product.

## Features

- Sensors for regions and grades returned by Fuel SA.
- ZAR/L prices, effective dates and retail/wholesale attributes.
- One shared request every six hours.
- API-key setup and reauthentication.
- A full-width price table, logo assets and notification example.

## Before installing

Obtain a valid API key from Fuel SA; provider account and subscription terms apply. Enter it only in Home Assistant's setup or reauthentication form. Do not post it to GitHub or Issues.

This package requires Home Assistant 2026.3 or newer, including local branding support.

## Install with HACS

Default catalogue submission remains deferred. Install as a custom repository:

1. Install and configure [HACS](https://www.hacs.xyz/docs/use/).
2. Open HACS > menu > **Custom repositories**.
3. Add `https://github.com/gert-bezuidenhout/ha.fuel-sa` with type **Integration**.
4. Download **Fuel SA** and restart Home Assistant.
5. Open **Settings > Devices & services > Add integration > Fuel SA** and enter your API key.

If your Marketplace offers **Add from a GitHub link**, use the same URL. Downloading and configuration are separate steps. No configuration.yaml changes are required.

For manual installation, download the complete ZIP from [Releases](https://github.com/gert-bezuidenhout/ha.fuel-sa/releases/latest), copy `custom_components/fuelsa/` to `/config/custom_components/fuelsa/`, restart and complete step 5.

## Sensors

The documented feed contains ten prices: five grades for each of Reef (inland) and Coast. New grades are discovered from successful updates.

| Fuel | Grades | Price basis |
| --- | --- | --- |
| Petrol | Unleaded 93, Unleaded 95, LRP 95 | Retail |
| Diesel | 50 ppm, 500 ppm | Wholesale; filling-station prices may differ |

Attributes include `location`, `fuel`, `grade`, `effective_at` and `price_basis`. Entity IDs normally start with `sensor.fuel_sa_`.

Six-hour polling uses approximately 120 scheduled requests per 30 days, plus setup, restarts, retries and manual refreshes. Updates may take six hours to appear. Use `homeassistant.update_entity` for a manual refresh.

## Dashboard and notifications

Download the installation ZIP from the [latest release](https://github.com/gert-bezuidenhout/ha.fuel-sa/releases/latest). HACS installs only the integration, not the examples.

1. Copy `examples/www/fuelsa/` into `/config/www/fuelsa/`. Restart if creating `/config/www/` for the first time.
2. Add a **Manual** card using `examples/fuel_prices_card.yaml`.
3. Review `examples/fuel_price_notification.yaml` before adding it as an automation.

The card uses Home Assistant's built-in Markdown card with no frontend add-ons. It preserves the full-width logo header and table, with right-aligned prices.

The notification example calls the author's custom `script.notification_all`, which is **not included**. Adapt it to your notification action or supply a compatible script before enabling it. Existing defaults are TTS off and WhatsApp to Gert enabled. It sends one message per changed sensor and ignores startup/unavailable transitions. See [examples/README.md](examples/README.md).

## Troubleshooting and privacy

- **Invalid key:** verify the key and provider access. Rejected credentials trigger reauthentication.
- **Unavailable prices:** check connectivity and provider availability; failed updates are retried.
- **Missing grade:** grades absent from a successful feed become unavailable.
- **Dashboard mismatch:** match example entity IDs to your actual entities.
- **Logo missing:** copy dashboard assets separately and refresh the browser.

The key is stored in the configuration entry, not entity attributes or explicit integration log messages. Redact credentials from shared logs, backups and screenshots.

## Updates and removal

Update through HACS and restart. Keep your existing entry and key. Update dashboard/example files separately from the ZIP. See [MIGRATION.md](MIGRATION.md).

To uninstall, remove the entry, uninstall in HACS and restart. Review dashboards and automations using its sensors.

## Support and files

Use [GitHub Issues](https://github.com/gert-bezuidenhout/ha.fuel-sa/issues) with versions, reproduction steps and redacted logs.

See [repository files](docs/FILES.md), [API and validation details](docs/DETAILS.md), [release notes](docs/releases/) and [Marketplace preparation](docs/HACS_SUBMISSION.md).

## Licence

Original code is under the [MIT licence](LICENSE), copyright Gert Bezuidenhout. Fuel SA branding and third-party content retain their respective rights; this project does not imply endorsement.
