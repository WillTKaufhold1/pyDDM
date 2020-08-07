import numpy as np
import numpy_groupies as npg

class Fitter():
    def __init__(self,fname):
        import pickle as pkl
        self.fname = fname
        database = pkl.load(open(fname,'rb'))
        self.iqtau = database['iqtau']
        self.freq_array = database['freqs']
        self.framerate = database['framerate']
        self.max_tau = database["max_tau"]


    def get_image(self,q_quantization_levels):
        self.q_quantization_levels = q_quantization_levels

        self.q_tau_structure = np.zeros((self.max_tau,
                                         q_quantization_levels)) 

        increment = max(self.freq_array) / q_quantization_levels
    
        self.mid_bin_vals = np.array([increment*i for i in range(q_quantization_levels)]) + increment/2

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

