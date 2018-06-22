from difflib import SequenceMatcher as seq
from heapq import nlargest

from Cryptodome.Cipher import AES
from Cryptodome.Util import Padding

from constants.variables import ENCRYPT_KEY

def find_closest_records(a: "Search str", b: "List of records", limit=10) -> list:
    scores_set = set()
    for entry in b:
        aes = AES.new(ENCRYPT_KEY, AES.MODE_ECB)
        content = aes.decrypt(entry["content"])
        content = Padding.unpad(content, 16).decode("utf-8")

        score = seq(a=a.lower(), b=content.lower()).ratio()
        if score > 0.3:
            scores_set.add((score, entry))

    if limit > len(scores_set):
        limit = len(scores_set)

    return nlargest(limit, scores_set, key=lambda tup: tup[0])
