"""
Abstract Class for Networking

You can extend Network interface to implement different type of network like 5G
"""
from Units import Units
from abc import ABC, abstractmethod

class Network(ABC):
    @abstractmethod
    def getTransferDuration(data: int):
        """ implemented by child classes """

    @abstractmethod
    def getUploadSpeed() -> int:
        """ implemented by child classes """
        
    @abstractmethod
    def getDownloadSpeed() -> int:
        """ implemented by child classes """

class LTE(Network):
    DOWNLOAD = 20 * Units.mega
    UPLOAD = 10 * Units.mega

    def getTransferDuration(data: int) -> float:
        return data/ (LTE.UPLOAD/8)
    
    def getUploadSpeed() -> int:
        return LTE.UPLOAD
    
    def getDownloadSpeed() -> int:
        return LTE.DOWNLOAD

class LTE_PLUS(Network):
    DOWNLOAD = 50 * Units.mega
    UPLOAD = 15 * Units.mega

    def getTransferDuration(data: int) -> float:
        return data/ (LTE_PLUS.UPLOAD/8)
    
    def getUploadSpeed() -> int:
        return LTE_PLUS.UPLOAD
    
    def getDownloadSpeed() -> int:
        return LTE_PLUS.DOWNLOAD

class FIFTH_GEN(Network):
    """
    ToDo
    """

UI_OPTIONS = [
    LTE, LTE_PLUS
]

if __name__ == "__main__":
    lte_speed = LTE.getDownloadSpeed()
    lte_plus_speed = LTE_PLUS.getDownloadSpeed()
    print("speed", lte_speed, lte_plus_speed)