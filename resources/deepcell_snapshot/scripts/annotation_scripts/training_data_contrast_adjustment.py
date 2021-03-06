"""
training_data_contrast_adjustment.py

Code for adjusting the contrast of images to aid image annotaters

@author: David Van Valen
"""

"""
Import python packages
"""

from deepcell import get_image, get_images_from_directory
import numpy as np
import skimage as sk
import os
import tifffile as tiff
from scipy import ndimage
import scipy


"""
Load images
"""

directory = "/home/vanvalen/Data/HeLa/set5/RawImages"
save_directory = os.path.join("/home/vanvalen/Data/HeLa/set5/", "Processed")
channel_names = ["Phase_000", "Far-red"]

images = get_images_from_directory(directory, channel_names)

print images[0].shape

number_of_images = len(images)

"""
Adjust contrast
"""

for j in xrange(number_of_images):
	print "Processing image " + str(j+1) + " of " + str(number_of_images)
	image = np.array(images[j], dtype = 'float')
	phase_image = image[0,0,:,:]
	nuclear_image = image[0,1,:,:]


	"""
	Do stuff to enhance contrast
	"""

	nuclear = sk.util.invert(nuclear_image)

	win = 30
	avg_kernel = np.ones((2*win + 1, 2*win + 1))

	phase_image -= ndimage.convolve(phase_image, avg_kernel)/avg_kernel.size
	nuclear_image -= ndimage.filters.median_filter(nuclear_image, footprint = avg_kernel) #ndimage.convolve(nuclear_image, avg_kernel)/avg_kernel.size

	nuclear_image += 100*sk.filters.sobel(nuclear_image)
	nuclear_image = sk.util.invert(nuclear_image)

	phase_image = sk.exposure.rescale_intensity(phase_image, in_range = 'image', out_range = 'float')
	nuclear_image = sk.exposure.rescale_intensity(nuclear_image, in_range = 'image', out_range = 'float')

	phase_image = sk.exposure.equalize_hist(phase_image)
	nuclear_image = sk.exposure.equalize_adapthist(nuclear_image, kernel_size = [100,100], clip_limit = 0.03)

	phase_image = ndimage.filters.gaussian_filter(phase_image, 1)
	phase_image = sk.img_as_uint(phase_image)
	nuclear_image = sk.img_as_uint(nuclear_image)

	"""
	Save images
	"""
	image_size_x = nuclear_image.shape[0]
	image_size_y = nuclear_image.shape[1]

	x_lower_lim = [0, image_size_x/2-30]
	x_upper_lim = [image_size_x/2+30, image_size_x]

	y_lower_lim = [0, image_size_y/2-30]
	y_upper_lim = [image_size_y/2+30, image_size_y]

	for i in xrange(2):
		for k in xrange(2):
			phase_temp = phase_image[x_lower_lim[i]:x_upper_lim[i],y_lower_lim[k]:y_upper_lim[k]]
			nuclear_temp = nuclear_image[x_lower_lim[i]:x_upper_lim[i],y_lower_lim[k]:y_upper_lim[k]]

			phase_temp_2 = np.repeat(phase_temp[:,:,np.newaxis], 3, axis = 2)
			nuclear_temp_2 = np.repeat(nuclear_temp[:,:,np.newaxis], 3, axis = 2)
	
			# phase_temp_2[:,:,0] = 255-nuclear_temp

			phase_name = os.path.join(save_directory,"phase_" + str(j) + "_quad_" + str(i) + "_" + str(k) + ".png")
			nuclear_name = os.path.join(save_directory,"nuclear_" + str(j) + "_quad_" + str(i) + "_" + str(k) + ".png")

			scipy.misc.imsave(phase_name, phase_temp_2)
			scipy.misc.imsave(nuclear_name, nuclear_temp_2)




