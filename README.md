# ha-glinet4-integration

A HomeAssistant custom component for GL-iNet routers that uses [their API version 4](https://dev.gl-inet.com/api/).

Disclaimer: GL-iNet no longer publicly documents their API, so the longevity of this integration is unknown and may well break in future firmware versions.

Contributions are welcome, for ideas see the TODO list below or the various `#TODO`s in the code.

## Features

- Device tracker for devices connected directly or indirectly to a Gl-inet router.
  - Note, modern phones use MAC address randomisation when they connect to WiFi, you will need to disable this for your home wifi only on [android](https://www.howtogeek.com/722653/how-to-disable-random-wi-fi-mac-address-on-android/) and [iphone](https://www.linksys.com/support-article?articleNum=317709)
- Control all configured wireguard and tailscale clients with a switch.
- Reboot your router
- System device sensors including CPU temperature (if supported by your device), CPU load and Uptime
- Coming soon:
  - On/off control of WiFi Networks

## Installation

1. [Install HACS](https://www.youtube.com/watch?v=a4lSlN6EI04)
2. Open the HACS page in home assistant
3. Search for GL-iNet and download the latest release

## Development

See **[DEVELOPMENT.md](DEVELOPMENT.md)** for the full setup.

In short: open the repo in a VS Code **Dev Container** (or Codespace) and run
`scripts/develop` to launch Home Assistant with this integration loaded, then add
it from the UI. A no-devcontainer path (`uv sync && scripts/develop`) is also
documented.

## TODO

- [ ] Handle all the errors gracefully, including empty client lists that happen after a glinet device restart.
- [ ] Auto detect router IP for config flow - assume it is the default gateway, test an endpoint that doesn't require auth (/model or /hello), fallback to default `192.168.8.1`
- [ ] Add switches for wireguard and open vpn (client and server), done for wireguard client, but we can probably do all programmatically rather than repeating boilerplate
  - worth considering you can have multiple clients, most of the API endpoints act on the last used client config. Can we get a list from the API and create switches for all? Maybe (router/vpn/status?)
- [ ] Allow deletion of unhelpful device tracker devices/entities, [docs](https://developers.home-assistant.io/docs/device_registry_index/#removing-devices), [example](https://github.com/home-assistant/core/pull/73293/commits/9c253c6072cf60f92228051d918fd550d38b6ac3)
- [ ] Enable strict type checking with mypy and a github action
- [ ] Add tests - will need to mock the API
- [ ] Detect and create a re-configure entry if the password changes
- [ ] Enable support for `https` as well as `http` and consider enabling it by default.
- [ ] Static type gli4py and then enable static typing on this repo
- [ ] Add features:
  - Upload/Download sensors
  - Internet reachable sensors (remember that API timesout when internet not reachable)
  - Public IP sensor
- [ ] Features under consideration
  - Making changes to the VPN client policies would be cool to automate switching on/off VPN use per device in automations. Useful for bypassing geofilters for example
  - Firmware upgrades https://dev.gl-inet.com/api/#api-firmware (should have warnings)
  - Switch for LED control https://dev.gl-inet.com/api/#api-cloud-PostLedEnable
  - Tethering controls:https://dev.gl-inet.com/api/#api-tethering
  - Modem control (useful for failover internet automations)
  - ?SMS control - maybe a notify platform [see example](https://github.com/home-assistant/core/blob/dev/homeassistant/components/sms/notify.py)
  - Explore using the smarthome BLE endpoints: https://dev.gl-inet.com/api/#api-SmartHome

## Tested on

- Beryl MT3000
- Convexa B1300

## Depends on

https://github.com/HarvsG/gli4py
