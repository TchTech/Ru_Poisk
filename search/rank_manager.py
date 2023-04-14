from inspect import getfullargspec
class RankManager():
    def __init__(self):
        self.methods=list()
    def add_method(self, method):
        if "texts" in getfullargspec(method)[0] and "query" in getfullargspec(method)[0] and method.__annotations__["return"]==dict:
            self.methods.append(method)
        else:
            raise ValueError("Rank-method must contain 'texts', 'query' parameters and return-type 'dict'!")
    def rank(self, query : str, texts : dict):
        ranks = dict()
        for method in self.methods:
            r=method(query=query, texts=texts)
            for link in r.keys():
                ranks[link] = (0 and ranks.get(link)) + float(r[link])
        return ranks