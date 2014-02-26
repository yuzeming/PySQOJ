import hashlib
# MD5File(open("a.zip","rb"))
def MD5File(fobj,bs=2**20):
    m = hashlib.md5()
    while True:
        d = fobj.read(bs)
        if not d:
            break
        m.update(d)
    return m.hexdigest()

