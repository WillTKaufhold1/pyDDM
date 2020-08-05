import numpy as np
import struct

def fread(fid,my_type):
    N_bytes = {"uint":2,"uint32":4, "uint64":8,"int32":4,"int64":8}[my_type]
    dtype = {"uint":"H","uint32":"I","uint64":"Q","int32":"i","int64":"q"}[my_type]
    data = fid.read(N_bytes)
    if len(data) == 0:
        raise Exception("reached the end of the file...")
    return struct.unpack(dtype,data)[0]

class MovieObject():
    def __init__(self,fname):

        self.fname = fname
        
        f =  open(self.fname,"rb")

        magic = int('496d6554',16)

        self.offset = 0

        struct.unpack("i", f.read(4))[0]

        word = None
        while (word != magic):
            f.seek(self.offset,0)
            word = struct.unpack("i",f.read(4))[0]
            self.offset += 1
            if word == magic:
                print ("found word")
                self.offset = self.offset - 1 
                f.seek(self.offset,0) #i.e. from beginning 
                break

        self.common_info = [struct.unpack("i",f.read(4))[0] for _ in range(6)]

        self.version, self.camera_type,self.endian,self.length_header,self.length_data = self.common_info[1:]

        CAMERA_TYPE_IIDC = 1;
        CAMERA_TYPE_ANDOR= 2;
        CAMERA_TYPE_XIMEA= 3;

        if self.camera_type == CAMERA_TYPE_IIDC:
            f.seek(24, 1) #but from current, i.e. 1

        self.first_frame_timestamp_sec = struct.unpack("q",f.read(8))[0] / 1e6# read as a uint64

        self.data_shape = [struct.unpack("i",f.read(4)) for _ in range(10)]
        self.data_shape.append(struct.unpack("q",f.read(8)))
        self.timestamp_pos = 48
        f.seek(self.offset + self.length_header + self.length_data + self.timestamp_pos,0) 
        framerate = 1/(struct.unpack("q",f.read(8))[0] / 10**6 - self.first_frame_timestamp_sec)
        self.width = self.data_shape[2][0]
        self.height = self.data_shape[3][0]
        self.data_depth = self.data_shape[8]
        self.image_bytes = self.data_shape[9]
        self.total_bytes = self.data_shape[10]

        if self.data_depth == 16:
            length_in_words = int(self.image_bytes / 2)
        elif self.data_depth == 8:
            length_in_words = self.image_bytes 
        elif self.data_depth == 12:
            length_in_words = int(self.image_bytes / 1.5) #what the fuck.

        f.seek(0,2)
        self.file_size = f.tell()

        f.seek(self.offset, 0)

        self.nn = (self.file_size - self.offset) / (self.length_header + self.length_data )

        self.NumberOfFrames = int(self.nn)

        f.close()
         
    def load_frames(self,frames_to_read):
        #ah shit, range is an array.
        offset = self.offset + self.length_header + self.length_data
        #if self.data_depth == 16: #only bother doing the 16 one...          
        
        template =  [       ('uint32' , 'magic'),
                            ('uint32' , 'version'),
                            ('uint32' , 'type'),
                            ('uint32' , 'pixelmode'),
                            ('uint32' , 'length_header'),
                            ('uint32' , 'length_data'),
                            ('uint64' , 'i_guid'),
                            ('uint32' , 'i_vendor_id'),
                            ('uint32' , 'i_model_id'),
                            ('uint32' , 'i_video_mode'),
                            ('uint32' , 'i_color_coding'),
                            ('uint64' , 'i_timestamp_us'),# %in microseconds
                            ('uint32' , 'i_size_x_max'),
                            ('uint32' , 'i_size_y_max'),
                            ('uint32' , 'i_size_x'),
                            ('uint32' , 'i_size_y'),
                            ('uint32' , 'i_pos_x'),
                            ('uint32' , 'i_pos_y'),
                            ('uint32' , 'i_pixnum'),
                            ('uint32' , 'i_stride'),
                            ('uint32' , 'i_data_depth'),
                            ('uint32' , 'i_image_bytes'),
                            ('uint64' , 'i_total_bytes'),
                            ('uint32' , 'i_brightness_mode'),
                            ('uint32' , 'i_brightness'), # %this could be a 'float' (in movie2tiff a 'union' was used, but I don't know how to handle that in MatLab).
                            ('uint32' , 'i_exposure_mode'),
                            ('uint32' , 'i_exposure'), # %this could be a 'float' (in movie2tiff a 'union' was used, but I don't know how to handle that in MatLab).
                            ('uint32' , 'i_gamma_mode'),
                            ('uint32' , 'i_gamma'),#  %this could be a 'float' (in movie2tiff a 'union' was used, but I don't know how to handle that in MatLab).
                            ('uint32' , 'i_shutter_mode'),
                            ('uint32' , 'i_shutter'),#  %this could be a 'float' (in movie2tiff a 'union' was used, but I don't know how to handle that in MatLab).
                            ('uint32' , 'i_gain_mode'),
                            ('uint32' , 'i_gain'),#  %this could be a 'float' (in movie2tiff a 'union' was used, but I don't know how to handle that in MatLab).
                            ('uint32' , 'i_temperature_mode'),
                            ('uint32' , 'i_temperature'),#  %this could be a 'float' (in movie2tiff a 'union' was used, but I don't know how to handle that in MatLab).
                            ('uint32' , 'i_trigger_delay_mode'),
                            ('uint32' , 'i_trigger_delay'),#  %this could be a 'float' (in movie2tiff a 'union' was used, but I don't know how to handle that in MatLab).
                            ('int32'  , 'i_trigger_mode'),
                            ('uint32' , 'i_avt_channel_balance_mode'),
                            ('int32'  , 'i_avt_channel_balance')]
                           
        f = open(self.fname,"rb")
        data = {}
        f.seek(offset,0)
        for i in range(frames_to_read):
            data[i] = template_file(f,template)
                     
            N_to_load = self.data_depth
                     
            N_words = self.width * self.height     
            
            image = np.fromfile(f,dtype = np.int16,
                               count = N_words, sep = "").reshape(self.width,self.height)
            
            #image = np.array([fread(f,"uint") for word in range(N_words)]).reshape(self.width, self.height,order = "C")
            data[i]["IM"] = image.byteswap()
        f.close()
        return data

def template_file(f,template):
    my_object = {}
    for i in template:
        my_object[i[1]] = fread(f,i[0])
    return my_object
