#!/usr/bin/env python

from sklearn import svm
from sklearn.model_selection import GridSearchCV
import matplotlib.pyplot as plt
import numpy as np

# straight
left1  = [[0, 0], [0, 1], [0, 2], [0, 3]]
right1 = [[1, 0], [1, 1], [1, 2], [1, 3]]

# left curve
left2  = [[0, 0], [0, 1], [0, 2], [0, 3], [-0.5, 4], [-1, 5], [-2, 6], [-3, 6], [.4, 0]] * 5
right2 = [[1, 0], [1, 1], [1, 2], [1, 3], [1, 4], [0.5, 5], [0, 6], [-1, 7], [-2, 7], [.6, 0]] * 5

# immediate left curve
left3  = [[0, 2], [0, 3], [-0.5, 4], [-1, 5]] * 5
right3 = [[1, 2], [1, 3], [1, 4], [0.5, 5], [0, 6]] * 5

left  = left2
right = right2
X = np.asarray(left + right)
y = [0] * len(left) + [1] * len(right)

def weight(x):
    return (x[0] - 0.5)**2 + x[1]**2

weights = [weight(x) for x in X]
max_weight = max(weights)
weights = [100 * (max_weight - w) for w in weights]
print(weights)

parameters = [{'kernel': ['rbf'], 'gamma': [1e-3, 1e-4],
                    'C': [1, 10, 100, 1000]},
                {'kernel': ['linear'], 'degree': [1, 2, 3, 4, 5],
                    'C': [1, 10, 100, 1000]}]
#svr = svm.SVC()
#clf = GridSearchCV(svr, parameters)
clf = svm.SVC(kernel='rbf', degree=3, gamma=0.1, C=50.)
clf.fit(X, y, sample_weight=weights)
#print(clf.best_params_)

plt.plot([x[0] for x in left], [x[1] for x in left], 'b^')
plt.plot([x[0] for x in right], [x[1] for x in right], 'r^')

h = .02
x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                    np.arange(y_min, y_max, h))

Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)
plt.contour(xx, yy, Z, cmap=plt.cm.Paired)

plt.axis([-4, 3, -1, 8])
plt.show()
