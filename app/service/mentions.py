class Mention:
    def __init__(self, obj: dict, keyword: str):
        self.arr = []
        self.sub_arr = []
        self.obj = obj
        self.keyword = keyword

    def extract(self, obj, sub_arr, val):
        if isinstance(obj, dict):
            for k, v in obj.items():
                found_arr = [*sub_arr, k]
                if isinstance(v, (dict, list)):
                    self.extract(v, found_arr, val)
                elif v == val:
                    self.arr.append(found_arr)
        elif isinstance(obj, list):
            for item in obj:
                found_arr = [*sub_arr, obj.index(item)]
                if isinstance(item, (dict, list)):
                    self.extract(item, found_arr, val)
                elif item == val:
                    self.arr.append(found_arr)
        return self.arr

    def traverse_dict_by_path(self, dictionary, paths):
        self.extract(self.obj, [], self.keyword)

        res = []

        for path in paths:
            _dictionary = dictionary.copy()
            for item in path[:-1]:
                _dictionary = _dictionary[item]
            res.append(_dictionary)
        return res

    def process(self):
        mention_uuids = []
        mentions = self.traverse_dict_by_path(self.obj, self.arr)

        for mention in mentions:
            mention_uuids.append(mention["attrs"]["id"])
        return mention_uuids


# g = Mention(json_object, "groupMention").process()
# print("groups",g)

# u = Mention(json_object, "userMention").process()
# print("users", u)
