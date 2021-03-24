import enum

class ItemType(enum.Enum):
    BOOK=1
    BAG=2
    SHOES=3
    CLOTHES=4

class ExpenditureType(enum.Enum):
    FEES=1
    BUYING=2

class DonationPlan(enum.Enum):
    ANUALLY=1
    SEMI_ANUALLY =2