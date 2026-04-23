[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)

[![license_badge](https://img.shields.io/github/license/shaiu/technicolor)](https://img.shields.io/github/license/shaiu/technicolor)

# technicolor

The Technicolor integration can connect Home Assistant to a Technicolor router that runs on Technicolor firmware.

There is currently support for the following device types within Home Assistant:

Presence Detection - The Technicolor platform offers presence detection by looking at connected devices to a Technicolor based router.

It uses the https://pypi.org/project/pytechnicolor/ to retrieve devices

# configuration

Install as usual and then follow UI configuration to input your router IP address and credentials.

## Multiple routers

This integration supports configuring **more than one router**:

- **UI**: Add the integration multiple times (one config entry per router).
- **YAML import**: You can configure a single router (dictionary) or multiple routers (list). On startup, each router will be imported as a separate config entry.

### YAML examples

Single router:

```yaml
technicolor:
  host: 192.168.0.1
  port: 80
  use_ssl: false
  verify_ssl: true
  username: admin
  password: your_password
```

Multiple routers:

```yaml
technicolor:
  - host: 192.168.1.1
    port: 80
    use_ssl: false
    verify_ssl: true
    username: admin
    password: your_password
  - host: 192.168.2.1
    port: 80
    use_ssl: false
    verify_ssl: true
    username: admin
    password: your_password
```
