ref_atlas=/Users/shreyasindurkar/Desktop/Data/Atlases/EconomoCT

cd $ref_atlas

filename=<'atlas in MNI space'>.nii.gz
fslroi $filename Left 0 127 0 255 0 255
#Extract Left Side

fslroi $filename Right 128 255 0 255 0 255
#Extract Right side

#Determine the intensity range/no. of regions in the atlas
#fslstats <atlas_Left>.nii.gz -R
#fslstats <atlas_Right>.nii.gz -R


mkdir Left Right

echo "Extracting left brain regions"
for i in `cat left_regions.txt`; do
  fslmaths <atlas_Left>.nii.gz -uthr $i -thr $i $ref_atlas/Left/$i
done

echo "Extrating Right brain regions"
for i in `cat right_regions.txt`; do
  fslmaths <atlas_Right>.nii.gz -uthr $i -thr $i $ref_atlas/Right/$i
done

#ref_atlas=/Users/shreyasindurkar/Desktop/Data/Atlases/EconomoCT/Left

#cd $ref_atlas
#ls *.nii.gz | sort -V > list.txt