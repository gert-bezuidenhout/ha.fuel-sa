# Fuel notifications and dashboard

## Notification automation

Open **Settings → Automations & scenes → Create automation → Create new automation**. Open the menu, choose **Edit in YAML**, and paste `fuel_price_notification.yaml`. Save and enable it.

It calls your existing `script.notification_all` once for each sensor whose numeric price changes. A full national price update may produce ten notifications. The message contains the fuel/region, old and new price, difference in cents per litre, and effective date.

Defaults: TTS off, WhatsApp to Gert enabled even while home, WhatsApp to Letitia off. Your script still respects its `input_boolean.notifications_whatsapp_gert` switch. Discord, Gmail and desktop delivery continue to follow the switches in your script. Change the action's fields to suit your preferences.

Startup, unavailable/unknown transitions, numeric formatting changes, and attribute-only changes are ignored. Consequently, a price that changes while Home Assistant is offline or the sensor is unavailable will not produce a notification upon recovery. This version compares consecutive valid readings and does not keep a persistent last-known-price helper.

The **Run actions** button does not supply the state trigger required by this automation. To test it, use Developer Tools → States to change a Fuel SA sensor from its numeric value to a different numeric value. This sends a real notification through your script. Restore the original value afterward (which sends another notification), or wait for the next integration refresh.

## Dashboard card

The prices table uses native HTML with `width="100%"` so it fills the card's content width. Columns use 44% for fuel and 28% for each region, with right-aligned prices.

1. Copy the contents of `www/fuelsa/` into `/config/www/fuelsa/` on Home Assistant, including `logo-header.svg`. Create those folders if needed. If this is the first time creating `/config/www`, restart Home Assistant.
2. Open `/local/fuelsa/logo-header.svg?v=2` on your Home Assistant address to verify the image loads.
3. Edit your dashboard, choose **Add card → Manual**, and paste `fuel_prices_card.yaml`.

The built-in Markdown card displays all ten prices in a compact comparison table, formats values to two decimal places, and shows unavailable data explicitly. No HACS frontend dependencies are needed. The logo spans the available card width while preserving its proportions. The SVG header embeds the clean transparent PNG over a light rounded panel for contrast on dark dashboards. The transparent PNG is also included separately. The experimental light logo variants were discarded because of edge artifacts. When all ten effective dates match, only one date is displayed. If dates differ or some are missing, each grade's effective date is shown in compact lines.

Offline validation: `python tests/validate_examples.py` checks YAML parsing, numeric transition guards, notification message amounts/directions, rendered table rows, unavailable values, and the PNG alpha channel. These checks do not execute Home Assistant or send messages.

References: [state triggers](https://www.home-assistant.io/docs/automation/trigger/), [Markdown card](https://www.home-assistant.io/dashboards/markdown/), [local image paths](https://www.home-assistant.io/dashboards/picture/).

## Logo production

Generated with the built-in imagegen tool using the existing Fuel SA logo as the edit target. Prompt: “Remove only the outer white background to actual alpha transparency. Preserve the complete exact existing pump and South African flag artwork, dark navy FUEL SA lettering, layout, proportions, and colors. Preserve the intentional white details inside the pump and flag. No redesign, no extra text, no shadows. Produce a tightly framed wide PNG logo suitable for a Home Assistant dashboard. Text verbatim: FUEL SA.”

Dark-theme variant also uses the built-in imagegen tool. Prompt: “Change only the FUEL SA lettering from navy to solid near-white #F5F5F5 and the outer navy pump silhouette and hose to light slate #CAD5DF so they are visible on a #1C1C1C dashboard background. Keep the droplet dark navy within its white panel. Preserve flag colors, all shapes, layout, proportions, exact text FUEL SA, and existing white details. Preserve genuine alpha transparency everywhere in the background. No background rectangle, no shadows, no extra elements. Wide horizontal logo, tightly framed.”

Final cleanup prompt: “Create a pristine flat digital Fuel SA logo for use on a dark dashboard, based exactly on the supplied original. Keep original composition: fuel pump and South African flag on left, bold text FUEL SA to right. ALL lettering solid clean near-white, outer pump and hose solid light slate, dark droplet within white pump panel, original flag colors. Transparent alpha background including holes in lettering and empty areas. Extremely clean smooth geometric outlines, solid uniform fills, no texture, no noise, no distressing, no scattered pixels or speckles, no gradients, no glow. Preserve exact spelling FUEL SA. Keep entire logo inside frame with small transparent margin.”
