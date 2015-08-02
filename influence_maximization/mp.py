from multiprocessing import Pool, Manager

def sub(wseq, i):
    wseq[i] = -i


def test():
    m    = Manager()
    wseq = m.list(range(30))
    p    = Pool()
    for i in xrange(30):
        p.apply_async(sub, args=(wseq,i))
    p.close()
    p.join()
    print wseq


if __name__ == '__main__':
    test()
