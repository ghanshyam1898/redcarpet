import base64
import hashlib
import secrets

from django.utils.crypto import force_bytes, constant_time_compare


def pbkdf2(password, salt, iterations, dklen=0, digest=None):
    """Return the hash of password using pbkdf2."""
    if digest is None:
        digest = hashlib.sha256
    dklen = dklen or None
    password = force_bytes(password)
    salt = force_bytes(salt)
    return hashlib.pbkdf2_hmac(digest().name, password, salt, iterations, dklen)


class PBKDF2PasswordHasher:
    iterations = 216000
    digest = hashlib.sha256

    def encode(self, password, salt):
        # encoded password as iterations$salt$hash
        hash = pbkdf2(password, salt, self.iterations, digest=self.digest)
        hash = base64.b64encode(hash).decode('ascii').strip()
        return "%d$%s$%s" % (self.iterations, salt, hash)

    def verify(self, password, encoded):
        salt, hash = encoded.split('$', 2)
        encoded_2 = self.encode(password, salt)
        return constant_time_compare(encoded, encoded_2)

    def salt(self):
        return secrets.token_urlsafe(12)


def make_password(password):
    hasher = PBKDF2PasswordHasher()
    return hasher.encode(password, hasher.salt())
