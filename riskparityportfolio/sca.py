import tensorflow as tf
import numpy as np
import quadprog


__all__ = ['SuccessiveConvexOptimizer']


class SuccessiveConvexOptimizerValidator:

    def __init__(self):
        pass

    @property
    def gamma(self):
        return self._gamma

    @gamma.setter
    def gamma(self, value):
        if not (0 < value < 1):
            raise ValueError("gamma has to be a real number in the interval"
                             "(0, 1), got {}.".format(value))
        else:
            try:
                self._gamma = float(value)
            except Exception as e:
                raise e

    @property
    def zeta(self):
        return self._zeta

    @zeta.setter
    def zeta(self, value):
        if value < 0:
            raise ValueError("zeta has to be a positive real number, got {}.".format(value))
        else:
            try:
                self._zeta = float(value)
            except Exception as e:
                raise e

    @property
    def funtol(self):
        return self._funtol

    @funtol.setter
    def funtol(self, value):
        if value < 0:
            raise ValueError("funtol has to be a positive real number, got {}.".format(value))
        else:
            try:
                self._funtol = float(value)
            except Exception as e:
                raise e

    @property
    def wtol(self):
        return self._wtol

    @wtol.setter
    def wtol(self, value):
        if value < 0:
            raise ValueError("wtol has to be a positive real number, got {}.".format(value))
        else:
            try:
                self._wtol = float(value)
            except Exception as e:
                raise e
    @property
    def maxiter(self):
        return self._maxiter

    @maxiter.setter
    def maxiter(self, value):
        if value < 0:
            raise ValueError("maxiter has to be a positive integer, got {}.".format(value))
        else:
            try:
                self._maxiter = int(value)
            except Exception as e:
                raise e


class SuccessiveConvexOptimizer:
    """
    Successive Convex Approximation optimizer taylored for the risk parity problem.
    """
    def __init__(self, portfolio, tau = None, gamma = 0.9, zeta = 1E-7, funtol = 1E-6,
                 wtol = 1E-6, maxiter = 5000):
        self.portfolio = portfolio
        self.tau       = (tau or 0.05 * np.sum(np.diag(self.portfolio.covariance.numpy()))
                                 / (2 * self.portfolio.number_of_assets))
        sca_validator  = SuccessiveConvexOptimizerValidator()
        self.gamma     = sca_validator.gamma     = gamma
        self.zeta      = sca_validator.zeta      = zeta
        self.funtol    = sca_validator.funtol    = funtol
        self.wtol      = sca_validator.wtol      = wtol
        self.maxiter   = sca_validator.maxiter   = maxiter
        self.Cmat      = np.vstack((np.ones(self.portfolio.number_of_assets),
                                    np.eye(self.portfolio.number_of_assets))).T
        self.bvec      = np.concatenate((np.array([1.]), np.zeros(self.portfolio.number_of_assets)))

    def iterate(self):
        wk = self.portfolio.weights
        g = self.portfolio.risk_concentration.risk_concentration_vector()
        A = self.portfolio.risk_concentration.jacobian_risk_concentration_vector()
        At = tf.transpose(A)
        Q = 2 * At @ A + self.tau * tf.eye(self.portfolio.number_of_assets, dtype=tf.float64)
        q = 2 * tf.linalg.matvec(At, g) - tf.linalg.matvec(Q, wk)
        w_hat = quadprog.solve_qp(Q.numpy(), -q.numpy(), C=self.Cmat, b=self.bvec, meq=1)[0]
        self.portfolio.weights = wk + self.gamma * (w_hat - wk)
        has_converged = (tf.abs(self.portfolio.weights - wk) <=
                         .5 * self.wtol * (tf.abs(self.portfolio.weights) + tf.abs(wk))).numpy().all()
        return not has_converged

    def solve(self):
        i = 0
        while(self.iterate() and i < self.maxiter): i += 1


def project_line_and_box(weights, lower_bound, upper_bound):
    def objective_function(variable, weights):
        pass
    pass