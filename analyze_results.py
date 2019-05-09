#!/usr/bin/python

import sys
import json
import numpy as np
import os

subdir1 = "1"
subdir2 = "2"
ind_keys = {"1.png": 0, "2.png": 1, "3.png": 2}

def subdir_and_inds(key, value):
    
    if key[:len(subdir1)] == subdir1:
        subdir = subdir1
    elif key[:len(subdir2)] == subdir2:
        subdir = subdir2
    else:
        print "Did not find matching dir!"
        sys.exit(-1)

    inds = (ind_keys[value[0]], ind_keys[value[1]])
    return subdir, inds

def analyze_file(filename):

    with open(filename) as f:
        data = json.load(f)

    name = data.pop("name")
    affiliation = data.pop("affiliation")
    sidescan_familiarity = data.pop("sidescan_familiarity")
    time = data.pop("time")

    print name, affiliation, sidescan_familiarity, time

    print data

    preferences1 = np.zeros((3, 3))
    preferences2 = np.zeros((3, 3))

    for key, value in data.items():

        if value == "None":
            continue

        subdir, inds = subdir_and_inds(key, value)
        if subdir == subdir1:
            preferences1[inds[0], inds[1]] = preferences1[inds[0], inds[1]] + 1
        elif subdir == subdir2:
            preferences2[inds[0], inds[1]] = preferences2[inds[0], inds[1]] + 1

    return preferences1, preferences2

def to_percentages(preferences):

    percent_preferences = preferences.copy()

    N = preferences.shape[0]
    for i in range(0, N):
        for j in range(i+1, N):
            number = preferences[i, j]+preferences[j, i]
            percent_preferences[i, j] = 100.*preferences[i, j]/number
            percent_preferences[j, i] = 100.*preferences[j, i]/number

    return percent_preferences

preferences1 = np.zeros((3, 3))
preferences2 = np.zeros((3, 3))

files = [os.path.join(sys.argv[1], o) for o in os.listdir(sys.argv[1]) if not os.path.isdir(os.path.join(sys.argv[1], o))]

for filename in files:
    file_preferences1, file_preferences2 = analyze_file(filename)
    preferences1 += file_preferences1
    preferences2 += file_preferences2

preferences = preferences1 + preferences2

print "Preferences 1:"
print preferences1
print to_percentages(preferences1)

print "Preferences 2:"
print preferences2
print to_percentages(preferences2)

print "Preferences:"
print preferences

print to_percentages(preferences)
