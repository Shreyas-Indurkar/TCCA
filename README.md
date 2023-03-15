# TCCA
Atlases, input NIFTI images and the extent of Overlap between them.

# Preprocessing in FSL
* 1mm3 NIFTI formatted atlas files in MNI reference space. Using fsl tools (FSL commands in shell) to prepare the data for processing.
* fslinfo - To get the information regarding resolution and dimensions
* fsleyes - To Visualize the atlases
* fslroi - To extract the left and right hemispheres into individual nifti files
  Can also be done in FSLeyes -- *FSLeyes -> Tools -> Crop
  
* fslstats - To determine the range of intensities in the given nifti image
* fslmaths - To extract each region corresponding to an intensity into an individual file

# Computation of Dice Similarity Coefficient and analysis in Python
