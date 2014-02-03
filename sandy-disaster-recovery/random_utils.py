
import random
import base64
import hashlib


def random_url_safe_code():
    " e.g. 'ejaMxJcjsNIz' "
    return base64.urlsafe_b64encode(
        hashlib.md5(
            str(random.random())
        ).digest()
    )[:12]
