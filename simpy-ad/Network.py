from Units import Units
from abc import ABC

class Network(ABC):
    def getTransferDuration(data: int):
        """ implemented by child classes """

class LTE(Network):
    DOWNLOAD = 20 * Units.mega
    UPLOAD = 10 * Units.mega

    def getTransferDuration(data: int):
        return data/ (LTE.UPLOAD/8)

class LTE_PLUS(Network):
    DOWNLOAD = 50 * Units.mega
    UPLOAD = 15 * Units.mega

    def getTransferDuration(data: int):
        return data/ (LTE_PLUS.UPLOAD/8)


