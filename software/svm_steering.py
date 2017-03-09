#!/usr/bin/env python

from sklearn import svm
from sklearn.model_selection import GridSearchCV
import matplotlib.pyplot as plt
import numpy as np
import time

from filter_data import *
from parse_data import *
from greedy import *

# straight
left1  = [[0, 0], [0, 1], [0, 2], [0, 3]]
right1 = [[1, 0], [1, 1], [1, 2], [1, 3]]

# left curve
left2  = [[0, 0], [0, 1], [0, 2], [0, 3], [-0.5, 4], [-1, 5], [-2, 6], [-3, 6], [.4, 0]] * 5
right2 = [[1, 0], [1, 1], [1, 2], [1, 3], [1, 4], [0.5, 5], [0, 6], [-1, 7], [-2, 7], [.6, 0]] * 5

# immediate left curve
left3  = [[0, 2], [0, 3], [-0.5, 4], [-1, 5]] * 5
right3 = [[1, 2], [1, 3], [1, 4], [0.5, 5], [0, 6]] * 5

# choose data
#left  = left2
#right = right2
frames = parse_csv_data('data/2017_02_19_19_51_09_729_sharp_right.csv')
frame = filter_data(frames[0])
cones = get_cones(frame)
left, right = create_boundary_lines(cones)
plt.scatter([cone[0] for cone in left], [cone[1] for cone in left], color='y', marker='^')
plt.scatter([cone[0] for cone in right], [cone[1] for cone in right], color='r', marker='^')
plt.scatter(0, 0, color='g')

X = np.asarray(left + right)
y = [0] * len(left) + [1] * len(right)

# add weights
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

#print('starting')
#start = time.time()
#svr = svm.SVC()
#clf = GridSearchCV(svr, parameters)
#clf.fit(X, y)
#print('SVM took %f seconds' % (time.time() - start))
#print(clf.best_params_)

print('starting')
start = time.time()
clf = svm.SVC(kernel='poly', degree=2, max_iter=3, gamma=0.1, C=50.)
clf.fit(X, y)
print('SVM took %f seconds' % (time.time() - start))
clf.fit(X, y, sample_weight=weights)

#plt.plot([x[0] for x in left], [x[1] for x in left], 'b^')
#plt.plot([x[0] for x in right], [x[1] for x in right], 'r^')

h = .02 * 1000
x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
print(x_min, x_max)
print(y_min, y_max)
xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                    np.arange(y_min, y_max, h))

Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)
plt.contour(xx, yy, Z, cmap=plt.cm.Paired)

#plt.axis([-4, 3, -1, 8])
plt.show()
