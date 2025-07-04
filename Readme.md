# pycusbi

A python library for managed USB hubs that are usually operated by a tool called cusbi, e.g., hubs
from the company EXSYS and StarTech.

## Usage

```python
from cusbi import CUsbI
import time

# Example:
path_to_device = "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_B0036Y2H-if00-port0"
port = 1

with CUsbI(path_to_device) as hub:
    hub.port_power_on(port, False)
    time.sleep(1)
    hub.port_power_on(port, True)
```
