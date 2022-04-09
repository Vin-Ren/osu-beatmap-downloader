
from datetime import datetime
from collections import namedtuple
from msilib.schema import Property
from types import NoneType


ForeignKey = namedtuple('ForeignKey', ('key', 'referenced_table', 'referenced_key'))
BLOB = blob = type('BLOB')
INT = Int = int
STR = Str = str
FLOAT = Float = float
DATETIME = DateTime = datetime
BOOLEAN = Boolean = bool


class Field:
    """SQLITE3 Based Field Syntax"""
    # datetime: ISO8601 strings ("YYYY-MM-DD HH:MM:SS.SSS")
    TYPE_MAPPING = {int:'INTEGER', str:'TEXT', blob:'BLOB', float:'REAL', datetime:'TEXT', bool:'INTEGER', NoneType:'NULL'}
    VALUE_CONVERTER = {int: int, str: lambda _s: '"{}"'.format(_s), float:float, 
                               datetime: lambda dt:'"{}"'.format(dt.isoformat()), 
                               bool: lambda _bool:1 if _bool else 0, -1: str} # -1 is default converter
    
    def __init__(self, name, _type, default=None, *, not_null: bool = False, primary_key: bool = False, auto_increment: bool = False, unique: bool = False, foreign_key: ForeignKey = None):
        self.name = name
        self.type = _type
        self.settings = {'NOT NULL':not_null, 'PRIMARY KEY':primary_key, 'AUTO INCREMENT':auto_increment, 'UNIQUE':unique}
        self.default = default
        self.foreign_key = foreign_key
    
    @property
    def value_converter(self):
        return self.VALUE_CONVERTER.get(self.type, self.VALUE_CONVERTER[-1])
    
    def get_type_str(self):
        return self.TYPE_MAPPING.get(self.type)
    
    def get_default_value(self):
        return self.value_converter(self.default) if self.default is not None else None
    
    def make_query(self):
        type_str = self.get_type_str()
        settings_str = " ".join([phrase for phrase, checked in self.settings.items() if checked])
        default_str = "Default {}".format(self.get_default_value()) if self.default is not None else ''
        # self.foreign_key = ('KEY_IN_THIS_TABLE', 'OTHER_TABLE', 'KEY_IN_OTHER_TABLE')
        foreign_key_str = (""",\nFOREIGN KEY({0.key}) REFERENCES "{0.referenced_table}"("{0.referenced_key}")""".format(self.foreign_key)) if self.foreign_key is not None and len(self.foreign_key) >= 3 else ""
        
        # Similiar to => _s = "{name} {type} {settings} {default} {foreign_key}"
        # but dumps extra unnecessary spaces.
        entries = [self.name, type_str, settings_str, default_str]
        sub_strings = [phrase for phrase in entries if phrase.strip()]
        return (" ".join(sub_strings), foreign_key_str)



class ModelMeta(type):
    @property
    def table_name(cls):
        return cls.__TABLE_NAME__ if cls.__TABLE_NAME__ is not None else cls.__name__

    def make_query(cls):
        _s = """CREATE TABLE IF NOT EXISTS "{table_name}"({queries})"""
        fields_queries = [field.make_query() for field in cls.FIELDS]
        field_queries = ", ".join([field_query[0] for field_query in fields_queries])
        modifier_queries = ", ".join([field_query[1] for field_query in fields_queries if len(field_query[1].strip())])
        queries = " ".join([field_queries, modifier_queries])
        return _s.format(table_name=cls.table_name, queries=queries)

    def make_insert_query(cls, replace=False, ignore=False):
        command = "INSERT " +("INTO OR IGNORE" if ignore else "OR REPLACE INTO" if replace else "INTO")
        _s = "{command} {table_name} VALUES ({values_placeholder})".format(command=command, table_name=cls.table_name, 
                                                                           values_placeholder=','.join([':{}'.format(field.name) for field in cls.FIELDS]))
        return _s


class Model(metaclass=ModelMeta):
    __TABLE_NAME__ = None
    FIELDS=[]
    
    def __init__(self, data: dict):
        self.data = data

    def __getattribute__(self, __name: str):
        try:
            return super().__getattribute__(__name)
        except AttributeError:
            return self.data.get(__name)
    
    @property
    def valid(self):
        return all(map(lambda key:self.data.__contains__(key), self.FIELDS))
    
    def __repr__(self):
        return "<{0} Model with {1} field(s) and data_size={2} is_valid={3}>".format(self.__class__.__name__, self.FIELDS.__len__(), self.data.__len__(), self.valid)
    
    def make_insert_values(self):
        entry_data = {}
        for field in self.FIELDS:
            try:
                entry_data[field.name] = self.data[field.name]
            except KeyError:
                if not field.settings['NOT NULL']:
                    entry_data[field.name] = None
                    continue
                if field.default is None:
                    raise KeyError("'{}' is required but not found in data.".format(field.name))
                entry_data[field.name] = field.get_default_value()
        return entry_data
        
    def make_insert_args(self, replace=False, ignore=False):
        query = self.make_insert_query()
        values = self.make_insert_values()
        return (query, values)

    def make_selector_query(self):
        _s = "SELECT * FROM {table_name} WHERE {conditions}"
        conditions = []
        for field in self.FIELDS:
            try:
                conditions.append("{0}={1}".format(field.name, field.value_converter(self.data[field.name])))
            except KeyError:
                pass
        return _s.format(table_name=self.__class__.table_name, conditions=" AND ".join(conditions))


class Beatmap(Model):
    __TABLE_NAME__ = 'beatmaps'
    FIELDS = [Field('beatmap_id', int, not_null=True, primary_key=True, unique=True), 
              Field('beatmapset_id', int, not_null=True), 
              Field('approved', int, not_null=True),
              Field('total_length', int, not_null=True),
              Field('hit_length', int, not_null=True),
              Field('version', str, not_null=True),
              Field('file_md5', str, not_null=True),
              Field('diff_size', int, not_null=True),
              Field('diff_overall', int, not_null=True),
              Field('diff_approach', int, not_null=True),
              Field('diff_drain', int, not_null=True),
              Field('mode', int, not_null=True),
              Field('count_normal', int, not_null=True),
              Field('count_slider', int, not_null=True),
              Field('count_spinner', int, not_null=True),
              Field('submit_date', datetime, not_null=True),
              Field('approved_date', datetime),
              Field('last_update', datetime),
              Field('artist', str, not_null=True),
              Field('artist_unicode', str, not_null=True),
              Field('title', str, not_null=True),
              Field('title_unicode', str, not_null=True),
              Field('creator', str, not_null=True),
              Field('creator_id', int, not_null=True),
              Field('bpm', float, not_null=True),
              Field('source', str),
              Field('tags', str, not_null=True),
              Field('genre_id', int, not_null=True),
              Field('language_id', int, not_null=True),
              Field('favourite_count', int, not_null=True),
              Field('rating', int, not_null=True),
              Field('storyboard', bool, not_null=True),
              Field('video', bool, not_null=True),
              Field('download_unavailable', bool, not_null=True),
              Field('audio_unavailable', bool, not_null=True),
              Field('playcount', int, not_null=True),
              Field('passcount', int, not_null=True),
              Field('packs', str),
              Field('max_combo', int),
              Field('diff_aim', float),
              Field('diff_speed', float),
              Field('difficultyrating', float)
              ]
    
    def __repr__(self) -> str:
        return "<{0} object beatmap_id={1[beatmap_id]} beatmapset_id={1[beatmapset_id]} approved={1[approved]} is_valid={2}>".format(self.__class__.__name__, self.data, self.valid)


class DownloadedBeatmapset(Model):
    __TABLE_NAME__ = 'downloaded_beatmapsets'
    FIELDS = [Field('beatmapset_id', int, not_null=True, primary_key=True, unique=True, 
                    foreign_key=ForeignKey(key='beatmapset_id', referenced_table=Beatmap.__TABLE_NAME__, referenced_key='beatmapset_id')),
              Field('downloaded', bool, default=False)
              ]
