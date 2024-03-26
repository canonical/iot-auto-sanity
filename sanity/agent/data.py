"""provide data that cross entire package"""

import dataclasses


@dataclasses.dataclass
class DevData:
    """The data would be used cross package"""

    project = None
    IF = "eth0"
    device_uname = None
    device_pwd = None
    hostname = "ubuntu"
