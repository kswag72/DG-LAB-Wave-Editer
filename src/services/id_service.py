import random


class IdService:
    def new_id(self) -> str:
        return hex(random.getrandbits(32))[2:]
