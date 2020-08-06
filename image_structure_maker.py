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
                
    def get_image(self,q_quantization_levels):
        self.q_quantization_levels = q_quantization_levels
        #subsample... ARGH.
        self.q_tau_structure = np.zeros((self.max_tau,
                                         q_quantization_levels)) #hmm
        #need to bin appropriately.
        increment = max(self.freq_array) / q_quantization_levels
    
        self.mid_bin_vals = np.array([increment*i for i in range(q_quantization_levels)]) + increment/2
        #we should really also get the uncertainty
        #this will help plotting
        #we'll also want to get the standard deviation?
        #how to do error propagation properly?
        
        self.bin_destimations = []
        for i in self.freq_array:
            #oh no, this isn't right..
            goto_bin = int (i/increment)
            if goto_bin == q_quantization_levels:
                goto_bin -= 1
            self.bin_destimations.append(goto_bin)
        
        for tau in self.iqtau:
            self.q_tau_structure[tau,:] = npg.aggregate(self.bin_destimations,
                                                        self.iqtau[tau],
                                                        func="mean")
        self.tau_vals = np.arange(self.max_tau) #issue with off by 1...
