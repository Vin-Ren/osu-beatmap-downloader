

from enum import Enum
from typing import Any


__all__ = ['Config', 'Credential', 'Beatmap', 'User']


class ObjectifiedDict(dict):
    def __setattr__(self, name: Any, value: Any):
        return super().__setitem__(name, value)
    
    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getitem__(name)
        except KeyError:
            return super().__getattribute__(name)
    
    def __repr__(self):
        return '<{} object with {} field(s)>'.format(self.__class__.__name__, self.__len__())
    
    def update(self, other):
        for k,v in other.items():
            self.__setitem__(k,v)


class Config(ObjectifiedDict):
    pass


class Credential(ObjectifiedDict):
    pass



###------------------------------ OSU OBJECTS ------------------------------###


class BaseOsuObject(ObjectifiedDict):
    REQUIRED_FIELDS = []
    @property
    def valid(self):
        return all(map(lambda key:self.__contains__(key), self.REQUIRED_FIELDS))


class ApprovedEnum(Enum):
    Loved = 4
    Qualified = 3
    Approved = 2
    Ranked = 1
    Pending = 0
    WIP = -1
    Graveyard = -2


class Beatmap(BaseOsuObject):
    REQUIRED_FIELDS = ['beatmap_id', 'beatmapset_id', 'approved', 'title', 'version']
    def __repr__(self):
        return "<{} object id={} beatmapset_id={} approved={} version={}>".format(self.__class__.__name__, self.beatmap_id, self.beatmapset_id, ApprovedEnum(int(self.approved)).name, self.version)
    def __str__(self):
        return "{0[beatmapset_id]} {0[artist]} - {0[title]} ({0[version]})".format(self)


class User(BaseOsuObject):
    REQUIRED_FIELDS = ['user_id', 'username', 'join_date', 'level', 'pp_raw']
    def __repr__(self):
        return "<{} object id={} username={} level={} pp={}>".format(self.__class__.__name__, self.user_id, self.username, round(float(self.level)), round(float(self.pp_raw)))
    def __str__(self):
        return "User#{0[user_id]} {0[username]}".format(self)