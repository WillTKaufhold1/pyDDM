import numpy as np
from matplotlib import pyplot as plt
from reader import MovieObject
from sexy_gpu_fft import fft2_gpu as fft2
import numpy_groupies as npg
from scipy.optimize import curve_fit

def get_power_distribution(FT,goto):
    FTflat = FT.flatten()
    #also propagate the sigma here.
    #uncertainty is sqrt(A^2 + B^2 + ...)
    #or I could maybe more effectively just take the var?
    return npg.aggregate(goto, FTflat, func = "mean") 

class Movie():
    def __init__(self,m,N_frames):
        
        self.m = m
        self.N_frames = N_frames
               
        self.framerate = self.m.framerate

        self.tmp = m.load_frames(N_frames)

        self.X = len(self.tmp[0]['IM'][0])
        self.Y = len(self.tmp[0]['IM'][1])

        if self.X != self.Y:
            raise Exception("image must be square")

        self.max_tau = int(self.N_frames / 2)
        self.max_q = int(self.X / 2) #wait, this is obviously wrong.

        freqs = np.fft.fftfreq(self.X)
        freq_matrix = np.zeros((self.X,self.X))
        for f_i,f in enumerate(freqs):
            for q_i,q in enumerate(freqs):
                freq_matrix[f_i,q_i] = np.sqrt(f**2 + q**2)

        self.freq_array = np.sort(np.unique(freq_matrix))
        inverse_freq_dict = {self.freq_array[key] : key for key in range(len(self.freq_array))}
        goto_matrix = np.zeros((self.X,self.X))

        for f_i,f in enumerate(freqs):
            for q_i,q in enumerate(freqs):
                goto_matrix[f_i,q_i] = inverse_freq_dict[freq_matrix[f_i,q_i]]

        self.goto_matrix_flat = goto_matrix.flatten().astype(dtype=int)
        
    def get_iqtau(self):
        self.iqtau = {}

        fft2_norm_factor = 1/self.X**2
        fft2_norm_factor2 = fft2_norm_factor**2

        for tau in range(self.max_tau): #only go up to tau / 2 for some reason...

            FT = np.zeros((self.X,self.X)).astype(dtype = "float64")

            N_iter_max = 10

            tau_0_vals = range(N_iter_max)
            
            for tau_iter in tau_0_vals:
                diff_image = self.tmp[tau_iter]['IM'] - self.tmp[tau_iter+tau]['IM'] 
                FT += np.abs(fft2(diff_image))**2 * fft2_norm_factor2    
                #hmm... we'll also want the power?

            FT = FT / len(tau_0_vals) 
            self.iqtau[tau] = get_power_distribution(FT,self.goto_matrix_flat) 
            
            if tau % 10 == 0:
                print ("We are %.2f done" %(tau / self.max_tau*100,) )
                

    def save_raw(self,fname): 
        import pickle as pkl
        #need to somehow also save the scale, and frame rate

        data_file = {"iqtau" : self.iqtau, 
                     "freqs" : self.freq_array,
                     "framerate" : self.framerate,
        	     "max_tau" : self.max_tau,}
        pkl.dump(data_file, open(fname,'wb+'))




