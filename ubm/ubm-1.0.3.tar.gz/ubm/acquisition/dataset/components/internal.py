class Temperatures:

    EXCHANGER_1 = "TScamb1"
    EXCHANGER_2 = "TScamb2"
    COOLER_1 = "TCool1"
    COOLER_2 = "TCool2"
    COOLER_3 = "TCool3"

    def __init__(self, dataset):
        self.dataset = dataset

    def get_exchanger_1(self):
        return self.dataset.get_data()[self.EXCHANGER_1]

    def get_exchanger_2(self):
        return self.dataset.get_data()[self.EXCHANGER_2]

    def get_cooler_1(self):
        return self.dataset.get_data()[self.COOLER_1]

    def get_cooler_2(self):
        return self.dataset.get_data()[self.COOLER_2]

    def get_cooler_3(self):
        return self.dataset.get_data()[self.COOLER_3]