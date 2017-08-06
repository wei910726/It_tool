from pyDes import des, PAD_PKCS5
import random
import rsa


class EnsafeDes(object):
    def __init__(self):
        self.rankey = str(random.randrange(1000, 8000))
        self.p1 = "AN"
        self.p2 = "MS"
        self.key = des(self.rankey, "\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)

    def ensec(self, pre):
        ensec_data = self.key.encrypt(pre)
        return ensec_data

    def desec(self, ensec):
        desec_data = self.key.decrypt(ensec)
        return desec_data


class EnsafeRsa(object):
    def __init__(self):
        with open("d://code//private.pem", "rb") as f:
            self.pridata = f.read()
        with open("d://code//public.pem", "rb") as f:
            self.pubdata = f.read()

    def ensec(self, pre):
        prikey = rsa.PrivateKey.load_pkcs1(self.pridata, "PEM")
        ensec_data = rsa.encrypt(pre.encode("utf-8"), prikey)
        return ensec_data

    def desec(self, ensec):
        pubkey = rsa.PublicKey.load_pkcs1(self.pubdata, "PEM")
        desec_data = rsa.decrypt(ensec, pubkey)
        return desec_data.decode("utf-8")
