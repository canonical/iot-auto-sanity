"""provide data that cross entire package"""

from dataclasses import dataclass


@dataclass
class DevData:
    """The data would be used cross package"""

    project: str = "ubuntu"
    hostname: str = "ubuntu"
    uname: str = "ubuntu"
    passwd: str = "ubuntu"
    netif: str = "eth0"
