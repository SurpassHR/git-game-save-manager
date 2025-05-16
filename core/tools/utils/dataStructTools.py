from typing import Optional, Any

def getNestedDictDataByKey(nestedDict: dict, key: str, default: Optional[Any] = None) -> Any:
    keys = key.split('.')
    current = nestedDict
    for k in keys:
        if k not in current:
            if isinstance(current, list):
                findFlg = False
                for i, item in enumerate(current):
                    if k in item:
                        findFlg = True
                        current = item[k]
                        break
                if findFlg:
                    return current
            else:
                return default
        current = current[k] # type: ignore
    return current

def getHeadersFromDict(data: dict) -> list:
    header = []
    for key in data.keys():
        header.append(key)
    return header