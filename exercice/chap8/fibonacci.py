import sys

def gen_fibo(n):
    if n > 1:
        fino = gen_fibo(n-1) + gen_fibo(n-2)
        return fino
    else:
        return n


def gen_fibo_recur(n):
    for i in xrange(n+1):
        yield gen_fibo(i)


if __name__ == '__main__':
    n = int(sys.argv[1])
    for i,fi in enumerate(gen_fibo_recur(n)):
        print i,fi
