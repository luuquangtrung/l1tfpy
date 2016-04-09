"""
    Solve the L1TF problem ADMM and only numpy
"""

import numpy as np
from matplotlib import pylab as plt
from numpy.linalg import inv


def soft_threshold(k, a):
    """
    Soft threshold function, proximal operator for l1 norm
    vectorized version
    :param k: number
    :param a: number
    :return: number
    """
    n = len(a)
    result = np.zeros(n)
    mask = a > k
    result[mask] = a[mask] - k
    mask = a < -k
    result[mask] = a[mask] + k
    return result


def memo(f):
    """ Memoization decorator for a function taking a single argument """
    class memodict(dict):
        def __missing__(self, key):
            ret = self[key] = f(key)
            return ret
    return memodict().__getitem__


@memo
def get_second_derivative_matrix(n):
    """
    :param n: The size of the input dimension
    :return: A matrix D such that D * x is the second derivative of x
    """
    m = n - 2
    D = np.zeros((m, n))
    v = np.array([1.0, -2.0, 1.0])
    for row_num in xrange(m):
        D[row_num, row_num:row_num+3] = v
    return D


def test_l1tf(n=50, seed=None, iter_max=1000, rho=1, lam=1.0,
              prompt=False, tol=1e-8, verbose=True, do_plot=True):
    """
    :param n: dimension of vector
    :param seed: random seed
    :param iter_max: maximum number of iterations
    :param rho: the ADMM step parameter
    :param lam: the problem's l1 regularization parameter
    :param prompt: show plots and print stuff at each step
                (default False)
    :param tol: Stop if max change between steps is lower than this
                times the max value of y
    :param verbose: Print stuff (default False)
    :param do_plot: Make a plot (default True)
    :return:
    """
    if seed is not None:
        np.random.seed(seed)
    y = np.cumsum(np.random.randn(n))
    x = l1tf(y, iter_max=iter_max, rho=rho, lam=lam, tol=tol,
             prompt=prompt, verbose=verbose)
    if do_plot:
        plt.clf()
        plt.plot(x, 'ro-')
        plt.plot(y, 'bo-')
        plt.show()


def l1tf(y, iter_max=1000, rho=1.0, lam=1.0, prompt=False,
         tol=1e-8, verbose=False):
    """
    Find the bets fit L1TF solution
    :param y: the data vector
    :param iter_max: maximum number of iterations
    :param rho: the ADMM step parameter
    :param lam: the problem's l1 regularization parameter
    :param prompt: show plots and print stuff at each step
                (default False)
    :param tol: Stop if max change between steps is lower than this
                times the max value of y
    :param verbose: Print stuff (default False)
    :return: the best fit regularized trend vector
    """
    tol_max = tol*y.max()
    rho = float(rho)
    lam = float(lam)
    n = len(y)
    m = n - 2

    D = get_second_derivative_matrix(n)
    M = np.eye(n) + rho * D.T.dot(D)
    M_inv = inv(M)

    # initialize
    x = y.copy()
    z = np.zeros(m)
    u = np.zeros(m)
    ratio = lam/rho

    for iter in xrange(iter_max):
        x_last = x
        x = M_inv.dot(y + rho*D.T.dot(z-u))
        q = D.dot(x) + u
        z = soft_threshold(ratio, q)
        u += D.dot(x) - z
        if prompt:
            print 'iter: %s' % iter
            print x-x_last
            if iter == 0:
                plt.clf()
                plt.plot(y)

            plt.plot(x, alpha=0.3)
            plt.show()
            ok = raw_input('ok?')
            if ok == 'q':
                return
            if ok == 'n':
                prompt = False

        max_delta = abs(x - x_last).max()
        if max_delta < tol_max:
            break

    if verbose:
        print "Max change: %s" % max_delta
        print "niter: %s" % iter

    return x