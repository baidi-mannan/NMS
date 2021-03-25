from SupportModules import ItemType
class Item:
    def __init__(self, itemType, class_ =1):
        self.itemType = itemType
        self.class_ = itemType.value

        