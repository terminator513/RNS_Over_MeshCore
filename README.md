# RNS Over Meshtastic / MeshCore
Interface implementations for Reticulum (RNS) that use external mesh networks as the underlying transport.

## Included interfaces
- `Interface/Meshtastic_Interface.py` — existing Meshtastic transport (unchanged).
- `Interface/Meshcore_Interface.py` — MeshCore-compatible transport via a TCP bridge.

## Meshtastic usage
- Install Meshtastic Python Library
- Add the file [Meshtastic_Interface.py](Interface%2FMeshtastic_Interface.py) to your interfaces folder for reticulum
- Modify the node config file and add the following
```ini
 [[Meshtastic Interface]]
  type = Meshtastic_Interface
  enabled = true
  mode = gateway
  port = /dev/[path to device]  # Optional: Meshtastic serial device port
  ble_port = short_1234  # Optional: Meshtastic BLE device ID (Replacement for serial port)
  tcp_port = 127.0.0.1:4403  # Optional: Meshtastic TCP IP. [port is optional if using default port]
  data_speed = 8  # Radio speed setting desired for the network (do not use long-fast)
```

- Radio settings and their associated transfer speeds are shown below; time unit is seconds between packets (from [Meshtastic_Interface.py](Interface%2FMeshtastic_Interface.py))
```python
speed_to_delay = {8: .4,  # Short-range Turbo (recommended)
                  6: 1,  # Short Fast (best if short turbo is unavailable)
                  5: 3,  # Short-range Slow (best if short turbo is unavailable)
                  7: 12,  # Long Range - moderate Fast
                  4: 4,  # Medium Range - Fast  (Slowest recommended speed)
                  3: 6,  # Medium Range - Slow
                  1: 15,  # Long Range - Slow
                  0: 8  # Long Range - Fast
                  }
```

## MeshCore usage
`Meshcore_Interface.py` expects a local or remote MeshCore bridge that exposes binary frames over TCP using this format:
- `2 bytes`: big-endian payload length
- `N bytes`: raw RNS payload

Reticulum config example:
```ini
 [[MeshCore Interface]]
  type = Meshcore_Interface
  enabled = true
  mode = gateway
  host = 127.0.0.1
  port = 9000
  connect_timeout = 8
  reconnect_delay = 3
  mtu = 512
```
