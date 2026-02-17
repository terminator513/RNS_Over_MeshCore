# RNS_Over_MeshCore
Interface for RNS using MeshCore as the underlying networking layer to utilize existing meshtastic hardware.

- NOT TESTED

## Usage
- Install MeshCore Python Library
- Add the file [Meshcore_Interface.py](Interface%2FMeshcore_Interface.py) to your interfaces folder for reticulum
- Modify the node config file and add the following
```
[[MeshCore]]
    type = Meshcore_Interface
    interface_enabled = true
    #port = /dev/ttyUSB0
    #baudrate = 115200
    transport = ble #serial|tcp|ble
    #tcp_port = 25565
    ble_name = MeshCore-Obdolbus
    mtu = 256
    #bitrate = 2000
```
