import sys
import math
import json
import re
from datetime import datetime

from typing import Dict, List, Union, Any
from types import FunctionType


__all__ = ['CSRF_TOKEN_REGEX', 'dict_updater', 'remove_illegal_name_characters', 'NULL', 'load_json', 'metric_size_formatter', 'make_progress_bar', 'get_date_from_string', 'inquire_params', 'remove_duplicate_in_list', 'PrettyPrinter']

CSRF_TOKEN_REGEX = re.compile(r".*?csrf-token.*?content=\"(.*?)\">", re.DOTALL)

remove_illegal_name_characters = lambda name: re.sub(r"[/\\:*?<>|\"]", '', name)
dict_updater = lambda base,updater:(lambda dbase,dupdt:[dbase.update(dupdt), dbase][-1])(base.copy(), updater)

NULL_TYPE = type('NULL')
NULL = NULL_TYPE()


def load_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)


def metric_size_formatter(value: int, suffix: str = 'B', decimal_places: int = 2, divisor: Union[int, float] = 1024.0):
    formattable_str = "{%s:.%sf} {unit}{suffix}" % ('value', decimal_places)
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(value) < divisor:
            return formattable_str.format(value=value, unit=unit, suffix=suffix)
        value /= divisor
    return formattable_str.format(value=value, unit='Y', suffix=suffix)


def make_progress_bar(value: int, length: int = 40, title: str = " ", vmin: Union[int,float] = 0.0, vmax: Union[int,float] = 1.0, prefix: str = "", suffix: str = ""):
    # Block progression is 1/8
    blocks = ["", "▏","▎","▍","▌","▋","▊","▉","█"]
    vmin = vmin or 0.0
    vmax = vmax or 1.0
    lsep, rsep = "▏", "▕"

    # Normalize value
    value = min(max(value, vmin), vmax)
    value = (value-vmin)/float(vmax-vmin)

    v = value*length
    x = math.floor(v) # integer part
    y = v - x         # fractional part
    base = 0.125      # 0.125 = 1/8
    prec = 3
    i = int(round(base*math.floor(float(y)/base),prec)/base)
    bar = "█"*x + blocks[i]
    n = length-len(bar)
    bar = lsep + bar + " "*n + rsep
    return "\r{title}{prefix}{bar}{value:.1f}%{suffix}".format(title=title, prefix=prefix, suffix=suffix, bar=bar, value=value*100)


def get_date_from_string(_s: str):
    formats = ['%y-%m-%d', '%Y-%m-%d', '%y/%m/%d', '%Y/%m/%d', '%y.%m.%d', '%Y.%m.%d', '%y %m %d', '%Y %m %d',
               '%d-%m-%y', '%d-%m-%Y', '%d/%m/%y', '%d/%m/%Y', '%d.%m.%y', '%d.%m.%Y', '%d %m %y', '%d %m %Y', '%d%m%y', '%d%m%Y']
    
    for fmt in formats:
        try:
            return datetime.strptime(_s, fmt)
        except ValueError:
            pass
    return None


def inquire_params(keyPromptPair: Dict[str,str]):
    """
    Usage: inquire_params({'parameter_name':'parameter_prompt'})
    Note that the return value type would not be converted.
    """
    params = {}
    for key, prompt in keyPromptPair.items():
        val = input(prompt)
        params.update({key:val}) if val else None
    return params


def remove_duplicate_in_list(_lst:List[Dict], grouper_key: str, eliminator_callable: FunctionType):
    grouped_data = {}
    for entry in _lst:
        try:
            grouped_data[entry[grouper_key]] = grouped_data.get(entry[grouper_key], []) + [entry]
        except KeyError:
            continue
    
    return [max(entries, key=eliminator_callable) for entries in grouped_data.values()]


class PrettyPrinter:
    _PRINTERS = []
    _DEFAULT_PRINTER = None
    
    def __new__(cls):
        instance = super().__new__(cls)
        cls._PRINTERS.append(instance)
        return instance
    
    @classmethod
    def _get_default(cls):
        if cls._DEFAULT_PRINTER is None:
            cls._DEFAULT_PRINTER = cls()
        return cls._DEFAULT_PRINTER
    
    def __init__(self, debug: bool = False, target_pipe = sys.stdout, defaults: Dict = {}, **kw):
        self.pipe = target_pipe
        self.debug = debug
        self.defaults = {'header_prefix':'|+|', 'converter':str}
        self.defaults = dict_updater(self.defaults, dict_updater(defaults, kw))
    
    def set_defaults(self, new_defaults: Dict):
        self.defaults = new_defaults
    
    def update_defaults(self, updater: Dict):
        self.defaults.update(updater)
    
    def make_info(self, header_text: str, header_prefix: str, info_entries: Dict[str,Any], *, with_header: bool = True, converter = str, **kw):
        head = "{header_prefix}{header_text}".format(header_prefix=header_prefix, header_text=header_text)
        max_name_length = len(max(info_entries.keys(), key=len))
        entries = ["{prefix}{entry}".format(prefix=" "*len(header_prefix), entry="{} : {}".format(name.ljust(max_name_length), converter(value))) for name, value in info_entries.items()]
        if with_header:
            return [head]+entries
        return entries
    
    def print_info(self, header_text: str, info_entries: Dict[str,Any], **kw):
        kwargs = dict_updater(self.defaults, dict_updater({'header_text':header_text, 'info_entries':info_entries}, kw))
        lines = self.make_info(**kwargs)
        self.pipe.write("\n".join(lines)+"\n")
        self.pipe.flush()
    
    def print(self, header_text: str, info_entries: Dict[str,Any], *args, **kw):
        return self.print_info(header_text, info_entries, *args, **kw)
    
    def print_debug(self, header_text: str, info_entries: Dict[str,Any], *args, **kw):
        if self.debug:
            self.print_info(header_text, info_entries, *args, **kw)
