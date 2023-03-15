# TCCA
Brain Atlases, input NIFTI images and the extent of Overlap between them.

# Preprocessing in FSL
* 1mm3 NIFTI formatted atlas files in MNI reference space. Using fsl tools (FSL commands in shell) to prepare the data for processing.
* fslinfo - To get the information regarding resolution and dimensions
* fsleyes - To Visualize the atlases
* fslroi - To extract the left and right hemispheres into individual nifti files
  Can also be done in FSLeyes -- *FSLeyes -> Tools -> Crop*
  
* fslstats - To determine the range of intensities in the given nifti image
* fslmaths - To extract each region corresponding to an intensity into an individual file

# Computation of Dice Similarity Coefficient and analysis in Python
def tcca(input_img, hemi, res_check = True, dim_check = True):
    
    """
    The Tübingen Cortical Concordance Atlas (TCCA) toolbox function takes a 1mm3 NIFTI image in MNI reference space
    as an input. The user is prompted for the paths to the input image and atlas folder. The program is written
    in a way to loop through the given atlases and compute the dice overlap between the input image and each region
    of the given atlases. The shape of the input image is reshaped to match that of the atlas.
    """
    
    Input Variables:
    input_img : .nii.gz format file with a resolution of 1mm3 in MNI reference space
    hemi      : 'left' or 'right'. Brain hemisphere of the data to be compared
    res_check : True. Checks for the resolution of the input image with respect to the resolution of the atlases
    dim_check : True. Checks for the dimensions of the input image with respect to the dimensions of the atlases
    
    Output:
    Dice_dict : A python dictionary data structure. It contains the data regarding the maximum overlapping region for the input image in each atlas and                     their corresponding dice coefficient.
    
# Volume-to-surface mapping
All the human brain atlases used in the study were available in 3D NIFTI data format. They had to be converted into 2D GIFTI data format for further analysis of DSC between the atlases. This was achieved using Human Connectome Project based ribbon mapping method with workbench commands. The mapping was performed by projecting the individual volumetric areas on to a midthickness brain surface with a Conte69_32k_fs_LR mesh with trilinear interpolation.
* Syntax:
          wb_command -volume-to-surface-mapping <Volume> <Surface mesh> <Out> [-trilinear]
