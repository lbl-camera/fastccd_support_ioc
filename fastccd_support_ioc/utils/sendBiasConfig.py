from fastccd_support_ioc.utils import loadBiasConfigFile


def sendBiasConfig(path):
    print("Loading Bias Config File")
    loadBiasConfigFile.loadBiasConfigFile(path)
    loadBiasConfigFile.loadBiasConfigFile(path)
    loadBiasConfigFile.readBiasConfigFile(path)
