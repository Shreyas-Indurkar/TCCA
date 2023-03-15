#Import necessary Python Packages
import numpy as np
from numpy import savetxt
import os
import re
import sys
import nibabel as nib
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from nipype.interfaces.fsl import ImageStats
from nipype.interfaces.fsl import ImageMaths
from scipy import stats
import glob
import seaborn as sns; sns.set()
import matplotlib.pyplot as plt
from nilearn import plotting
from nilearn import image
from nilearn import surface
import multiprocessing

#Sort the numbers into ascending order of value
numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts

#Sort the numbers into ascending order of value
numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts
def tcca(input_img, hemi, res_check = True, dim_check = True, mni_check = False):
    '''
    The Tübingen Cortical Concordance Atlas (TCCA) toolbox function takes a 1mm3 NIFTI image in MNI reference space
    as an input. The user is prompted for the paths to the input image and atlas folder. The program is written
    in a way to loop through the given atlases and compute the dice overlap between the input image and each region
    of the given atlases. The shape of the input image is reshaped to match that of the atlas.
    '''

    # For left hemisphere
    if hemi == 'left':
        Dice_dict = {}
        output_text = []
        input_dir = input("provide path to the input directory")
        root_dir = input("provide path to the atlas directory")    #Define the directory of the atlases
        for atlas_folder in os.listdir(root_dir):
            if atlas_folder.endswith("Atlas"):
                print(atlas_folder)


                ref_dir = root_dir + atlas_folder +'/Left/'   # Loop through each of the atlases
                print(ref_dir)


                os.chdir(ref_dir)
                ref_files=sorted(glob.glob("*.nii.gz"), key = numericalSort)   #Access the ROI files in the atlases
                #print(ref_files)
                left = open(ref_dir + r"list.txt", 'r').read().split('\n')    #Define the list of names for atlas region files
                labels = open(ref_dir + r"labels.txt", 'r').read().split('\n')   #Define a list with atlas area labels
                Dice_list = []
                
                for fname1 in range(len(ref_files)):
                    #print(fname1)
                    fname=ref_files[fname1]
                    print(fname)
                    ref_file=os.path.join(ref_dir + str(fname))

                    input_image = nib.load(input_img)
                    ref = nib.load(ref_file)

                    #Check for equality of dimensions of the atlases
                    if dim_check == True:   
                        if input_image.shape != ref.shape:
                            #Resample the input image with respect to the atlas dimensions
                            input_resample = image.resample_img(input_image, target_affine = ref.affine, target_shape = ref.shape)
                            nib.save(input_resample, os.path.join(input_dir, 'resample.nii.gz'))
                            input_file=os.path.join(input_dir + 'resample.nii.gz')
                        else:
                            input_file=input_img
                    else:
                        input_file=input_img

                    #Check for equality of resolution of the input image and the atlases
                    if res_check == True:
                        if input_image.header.get_zooms() != ref.header.get_zooms():
                            print("Resolution error: Resolution of the images does not match")
                            print("Input resolution:",input_image.header.get_zooms())
                            print("Reference resolution:",ref.header.get_zooms())
                            sys.exit()
                        else:
                            print("Input resolution:",input_image.header.get_zooms())
                            print("Reference resolution:",ref.header.get_zooms())


                    #Get volume of the input image
                    stats = ImageStats(in_file=input_file, op_string='-V').run()
                    volume_A = stats.outputs.out_stat[1]
                    #mulitply to get intersection
                    ImageMaths(in_file=input_file,in_file2=ref_file, out_file=(input_dir + 'intersect.nii.gz'), op_string=("-mul")).run()
                    #get Volume of the atlas region
                    stats2 = ImageStats(in_file=ref_file, op_string='-V').run()
                    volume_B = stats2.outputs.out_stat[1]
                    # get volume Intersect
                    stats3 = ImageStats(in_file=(input_dir + 'intersect.nii.gz'), op_string='-V').run()
                    volume_I = stats3.outputs.out_stat[1]
                    if (volume_A+volume_B)==0: #in rare case a subject does not have one segment we need to 
                        Dice = float('nan') # code for non existing segment
                    else: 
                        Dice = 2* volume_I /(volume_A+volume_B)
                    Dice_list.append(Dice)
                    #print(Dice)
                    os.remove(input_dir + 'intersect.nii.gz')
                    if input_image.shape != ref.shape:
                        os.remove(input_dir + 'resample.nii.gz')

                #sys.stdout = save_stdout
                np.savetxt(root_dir + "Dice_left" + atlas_folder + ".csv", Dice_list, delimiter = ',')
                max_dice = max(Dice_list)
                max_idx = Dice_list.index(max_dice)
                #print(max_idx)
                
                #Saving the output to a dictionary
                Dice_dict[max_dice] = atlas_folder + ": " + str(labels[max_idx])

                #Analysis
                non_zero_dice = Dice_list[Dice_list!=0]

                #Plot a histogram and print the frequency and the edges of the histogram#
                hist, bin_edges = np.histogram(non_zero_dice)
                #print('histogram: ',hist)
                #print('Edges:', bin_edges)

                #Compute the mean value of dice coefficients with only non-zero values#
                #mean_dice = non_zero_dice.mean()
                #avg_dice = print('Mean: ',mean_dice)

                #Compute the standard deviation of dice coefficients#
                #std_dice = non_zero_dice.std()
                #std_dev_dice = print('Std_dev: ', std_dice)

                #Find the minimum and maximum values of dice coefficient from the array and determine their indices#
                #min_dice = non_zero_dice.min()
                #minimum = print('Min: ',min_dice)
                #max_dice = non_zero_dice.max()
                #print('Max: ',max_dice)
                #max_index = np.where(Dice_list == max_dice)
                #idx_max = print('Max_index: ',max_index)
                #min_index = np.where(Dice_list == min_dice)
                #idx_min = print('Min_index: ',min_index)

                #Plot the histogram#
                plt.hist(non_zero_dice)
                plt.axvline(0.1, color='r')
                plt.xlabel('Dice Coefficient')
                plt.ylabel('Frequency')

                plt.show()

                output_text.append("Maximum Overlap of " + str(max_dice) + " at " + str(labels[max_idx]) + " in " + atlas_folder)
                #print(output)

                #Visualize the input image with the atlas area of Maximum overlap
                fig = plt.figure(figsize=(5, 3), facecolor='w')
                display = plotting.plot_glass_brain(None, plot_abs=False, annotate=True, cmap='YlGnBu', figure=fig, display_mode='lyrz', title='Max overlap')   
                max_file = os.path.join(ref_dir+ left[max_idx])
                display.add_contours(input_img, filled=True, colors='b')
                display.add_contours(max_file, filled=False, colors='r')
                plt.savefig(input_dir+'max_overlap_plot.png')
                c = canvas.Canvas(input_dir+"example.pdf", pagesize=letter)
                c.drawImage(input_dir+'max_overlap_plot.png', 50, 525, width=450, height=200)
                c.drawString(50, 750, str(output_text))
            c.showPage()
        c.save()
        return Dice_dict, output_text

    # For left hemisphere
    if hemi == 'right':
        Dice_dict = {}
        output_text = []
        input_dir = input("provide path to the input directory")
        root_dir = input("provide path to the atlas directory")    #Define the directory of the atlases
        for atlas_folder in os.listdir(root_dir):
            if atlas_folder.endswith("Atlas"):
                print(atlas_folder)


                ref_dir = root_dir + atlas_folder +'/Right/'   # Loop through each of the atlases
                print(ref_dir)


                os.chdir(ref_dir)
                ref_files=sorted(glob.glob("*.nii.gz"), key = numericalSort)   #Access the ROI files in the atlases
                #print(ref_files)
                left = open(ref_dir + r"list.txt", 'r').read().split('\n')    #Define the list of names for atlas region files
                labels = open(ref_dir + r"labels.txt", 'r').read().split('\n')   #Define a list with atlas area labels
                Dice_list = []
                
                for fname1 in range(len(ref_files)):
                    #print(fname1)
                    fname=ref_files[fname1]
                    print(fname)
                    ref_file=os.path.join(ref_dir + str(fname))

                    input_image = nib.load(input_img)
                    ref = nib.load(ref_file)

                    #Check for equality of dimensions of the atlases
                    if dim_check == True:   
                        if input_image.shape != ref.shape:
                            #Resample the input image with respect to the atlas dimensions
                            input_resample = image.resample_img(input_image, target_affine = ref.affine, target_shape = ref.shape)
                            nib.save(input_resample, os.path.join(input_dir, 'resample.nii.gz'))
                            input_file=os.path.join(input_dir + 'resample.nii.gz')
                        else:
                            input_file=input_img
                    else:
                        input_file=input_img

                    #Check for equality of resolution of the input image and the atlases
                    if res_check == True:
                        if input_image.header.get_zooms() != ref.header.get_zooms():
                            print("Resolution error: Resolution of the images does not match")
                            print("Input resolution:",input_image.header.get_zooms())
                            print("Reference resolution:",ref.header.get_zooms())
                            sys.exit()
                        else:
                            print("Input resolution:",input_image.header.get_zooms())
                            print("Reference resolution:",ref.header.get_zooms())


                    #Get volume of the input image
                    stats = ImageStats(in_file=input_file, op_string='-V').run()
                    volume_A = stats.outputs.out_stat[1]
                    #mulitply to get inter section
                    ImageMaths(in_file=input_file,in_file2=ref_file, out_file=(input_dir + 'intersect.nii.gz'), op_string=("-mul")).run()
                    #get Volume of the atlas region
                    stats2 = ImageStats(in_file=ref_file, op_string='-V').run()
                    volume_B = stats2.outputs.out_stat[1]
                    # get volume Intersect
                    stats3 = ImageStats(in_file=(input_dir + 'intersect.nii.gz'), op_string='-V').run()
                    volume_I = stats3.outputs.out_stat[1]
                    if (volume_A+volume_B)==0: #in rare case a subject does not have one segment we need to 
                        Dice = float('nan') # code for non existing segment
                    else: 
                        Dice = 2* volume_I /(volume_A+volume_B)
                    Dice_list.append(Dice)
                    #print(Dice)
                    os.remove(input_dir + 'intersect.nii.gz')
                    if input_image.shape != ref.shape:
                        os.remove(input_dir + 'resample.nii.gz')

                #sys.stdout = save_stdout
                np.savetxt(root_dir + "Dice_left" + atlas_folder + ".csv", Dice_list, delimiter = ',')
                max_dice = max(Dice_list)
                max_idx = Dice_list.index(max_dice)
                #print(max_idx)
                
                #Saving the output to a dictionary
                Dice_dict[max_dice] = atlas_folder + ": " + str(labels[max_idx])

                #Analysis
                non_zero_dice = Dice_list[Dice_list!=0]

                #Plot a histogram and print the frequency and the edges of the histogram#
                hist, bin_edges = np.histogram(non_zero_dice)
                #print('histogram: ',hist)
                #print('Edges:', bin_edges)

                #Compute the mean value of dice coefficients with only non-zero values#
                #mean_dice = non_zero_dice.mean()
                #avg_dice = print('Mean: ',mean_dice)

                #Compute the standard deviation of dice coefficients#
                #std_dice = non_zero_dice.std()
                #std_dev_dice = print('Std_dev: ', std_dice)

                #Find the minimum and maximum values of dice coefficient from the array and determine their indices#
                #min_dice = non_zero_dice.min()
                #minimum = print('Min: ',min_dice)
                #max_dice = non_zero_dice.max()
                #print('Max: ',max_dice)
                #max_index = np.where(Dice_list == max_dice)
                #idx_max = print('Max_index: ',max_index)
                #min_index = np.where(Dice_list == min_dice)
                #idx_min = print('Min_index: ',min_index)

                #Plot the histogram#
                plt.hist(non_zero_dice)
                plt.axvline(0.1, color='r')
                plt.xlabel('Dice Coefficient')
                plt.ylabel('Frequency')

                plt.show()

                output_text.append("Maximum Overlap of " + str(max_dice) + " at " + str(labels[max_idx]) + " in " + atlas_folder)
                #print(output)

                #Visualize the input image with the atlas area of Maximum overlap
                fig = plt.figure(figsize=(5, 3), facecolor='w')
                display = plotting.plot_glass_brain(None, plot_abs=False, annotate=True, cmap='YlGnBu', figure=fig, display_mode='lyrz', title='Max overlap')   
                max_file = os.path.join(ref_dir+ left[max_idx])
                display.add_contours(input_img, filled=True, colors='b')
                display.add_contours(max_file, filled=False, colors='r')
                plt.savefig(input_dir+'max_overlap_plot.png')
                c = canvas.Canvas(input_dir+"example.pdf", pagesize=letter)
                c.drawImage(input_dir+'max_overlap_plot.png', 50, 525, width=450, height=200)
                c.drawString(50, 750, str(output_text))
            c.showPage()
        c.save()
        return Dice_dict, output_text