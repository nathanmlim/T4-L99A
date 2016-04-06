import numpy as np
from scipy.stats import linregress

def rmse(predictions, targets):
    return np.sqrt(np.mean((predictions - targets) ** 2))

def rsquared(x, y):
    """ Return R^2 where x and y are array-like."""
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    return r_value**2

def remove_outliers(arr, k):
    mu, sigma = np.mean(arr, axis=0), np.std(arr, axis=0, ddof=1)
    return arr[np.all(np.abs((arr - mu) / sigma) < k, axis=1)]

def zscore(predicted,expected,err):
   return (predicted - expected)/err
