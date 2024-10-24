"""provide data that cross entire package"""

from dataclasses import dataclass
from sanity.agent.ssh import SSHInfo
from sanity.agent.pdu import PDUInfo


@dataclass
class DevData:
    """The data would be used cross package"""

    project: str = "ubuntu"
    hostname: str = "ubuntu"
    uname: str = "ubuntu"
    passwd: str = "ubuntu"
    netif: str = "eth0"
    ssh: SSHInfo = SSHInfo("127.0.0.1", 22)
    pdu: PDUInfo = PDUInfo("127.0.0.1", 0)
