"""
Abstract Class for Network

You can extend Network interface to implement different type of network like 5G
"""
from simulation.utils.units import Units

class Network:
    DOWNLOAD = None
    UPLOAD = None

    @classmethod
    def getTransferDuration(cls, data: int):
        return data/ (cls.UPLOAD/8)

    @classmethod
    def getUploadSpeed(cls) -> int:
        return cls.UPLOAD
        
    @classmethod
    def getDownloadSpeed(cls) -> int:
        return cls.DOWNLOAD

class LTE(Network):
    DOWNLOAD = 20 * Units.mega
    UPLOAD = 10 * Units.mega

class LTE_PLUS(Network):
    DOWNLOAD = 50 * Units.mega
    UPLOAD = 15 * Units.mega

class FIFTH_GEN(Network):
    DOWNLOAD = 777 * Units.mega
    UPLOAD = 77 * Units.mega

UI_OPTIONS = [
    LTE, LTE_PLUS, FIFTH_GEN
]

def getNetworkClass(name: str) -> Network:
    for option in UI_OPTIONS:
        if option.__name__ == name:
            return option

if __name__ == "__main__":
    print("LTE", LTE.getUploadSpeed(), LTE.getDownloadSpeed())
    print("LTE_PLUS", LTE_PLUS.getUploadSpeed(), LTE_PLUS.getDownloadSpeed())
    print("FIFTH_GEN", FIFTH_GEN.getUploadSpeed(), FIFTH_GEN.getDownloadSpeed())