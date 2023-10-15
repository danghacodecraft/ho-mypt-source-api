def mapping(data: dict, pattern: dict) -> dict:
    _data = data.copy()
    if dict.__subclasscheck__(_data.__class__) and dict.__subclasscheck__(pattern.__class__):
        for key, value in pattern.items():
            if key in _data:
                _data[value] = _data[key]
        return _data
    else:
        raise TypeError('data and pattern must be dict')

def data_mapping(data: dict, pattern: dict) -> dict:
    _data = data.copy()
    if dict.__subclasscheck__(_data.__class__) and dict.__subclasscheck__(pattern.__class__):
        for key, func in pattern.items():
            if key in _data:
                _data[key] = func(_data[key])
        return _data
    else:
        raise TypeError('data and pattern must be dict')