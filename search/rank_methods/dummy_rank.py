def dummy_rank(texts : dict, query : str) -> dict:
    result = dict()
    for i in texts.keys():
        text = texts[i].lower()
        query = query.lower()
        text = text.replace(",", " ").replace(".", " ").replace("/", " ").replace("-", " ")
        query = query.replace(",", " ").replace(".", " ").replace("/", " ").replace("-", " ")
        result[i] = text.count(query)
    return result