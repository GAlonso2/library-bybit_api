from datetime import datetime


class AbstractModel:
    created: datetime

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, dict):
                self.__dict__[key] = AbstractModel(**value)
            else:
                setattr(self, key, value)
