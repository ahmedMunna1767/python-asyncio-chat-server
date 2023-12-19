import random
import string


def generate_random_code(length=5):
    letters = string.ascii_letters
    return "".join(random.choice(letters) for i in range(length))
