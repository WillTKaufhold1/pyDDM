#!/home/wtk23/anaconda3/bin/python
import numpy as np
import matplotlib.pyplot as plt
%matplotlib inline

import image_structure_maker
from reader import MovieObject

import os

fnames = os.listdir("../Data/")

for fname in fnames:
    print (fname)
    m = MovieObject(f"../Data/{fname}")
    N_frames = 400
    move = image_structure_maker.Movie(m,N_frames)
    move.get_iqtau()
    move.save_raw(f"../Data_structures/{fname}.pkl")
