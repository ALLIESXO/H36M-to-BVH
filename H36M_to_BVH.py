""" Creates a file in BVH format for the H36M Dataset (http://vision.imar.ro/human3.6m/description.php).
    The BVH file is prefilled with missing Motion content and is completed with a cdf D3 Angle pose file of H36M.
    As the standard skeleton structure - the metadata.xml in H36M matlab code has been used as a reference.
"""
import argparse 
import cdflib
import os, sys, shutil

def file_path(path):
    if os.path.isfile(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_file:{path} is not a valid file.")

parser = argparse.ArgumentParser(description="Translate cdf motion file to bvh file.")
parser.add_argument("-pose", type=file_path, help="Path to the cdf pose file. (Must be 'D3 Angles' pose)")
parser.add_argument("-dest", default="", type=str, help="Saves the created file at the given path. (Default: bvh-file folder in script directory.)")
args = parser.parse_args()
use_dest = False

if args.dest != "" and os.path.isdir(args.dest):
    use_dest = True
else: 
    print("Will use default destination for file creation.")

# initialize global variables 
cdf_angles = cdflib.CDF(args.pose)
angles = cdf_angles.varget("Pose")[0]

# List of rotation indexes in the bvh hierarchy order 
rot_order = [[5,6,4], [32,33,31], [35,36,34], [38,39,37], [41,42,40],
[44,45,43], [47,48,46], [50,51,49], [53,54,52], [56,57,55], [59,60,58],
[62,63,61], [65,66,64], [68,69,67], [71,72,70], [74,75,73], [77,78,76],
[20,21,19], [23,24,22], [26,27,25], [29,30,28],
[8,9,7], [11,12,10], [14,15,13], [17,18,16]]

frame_time = 0.02
frames = len(angles)

dst_dir = args.dest
src_dir = os.getcwd()
if not use_dest:
    dst_dir = src_dir + "\\" + 'bvh-files'

try: 
    os.mkdir(dst_dir) 
except OSError as error: 
    print(error)

src_file = os.path.join(src_dir, "base_H36M_hierarchy.bvh")
#copy the base file to destination dir
src_file = shutil.copy(src_file, dst_dir)
new_dst_file_name = os.path.join(dst_dir, cdf_angles.file.stem + '.bvh')

try:
    os.rename(src_file, new_dst_file_name) #rename
except OSError as error:
    print(error)
    print("Deleting existing files...")
    os.remove(new_dst_file_name)
    os.rename(src_file, new_dst_file_name)


#Append content to new bvh file 
with open(new_dst_file_name, 'a') as file:
    file.write("\nMOTION \n")
    file.write("Frames:\t" + str(frames) + " \n")
    file.write("Frame Time: " + str(frame_time) + " \n")

    for frame in angles:
        xp = frame[0] / 100
        yp = frame[1] / 100
        zp = frame[2] / 100
        file.write(" " + str(xp) + " " + str(yp) + " " + str(zp)+ " ")

        for rot_indexes in rot_order:
            # channels order
            zr = frame[rot_indexes[2] - 1]
            xr = frame[rot_indexes[0] - 1]
            yr = frame[rot_indexes[1] - 1]
            file.write(str(zr) + " " + str(xr) + " " + str(yr)+ " ")
            
        #end of frame
        file.write("\n ")

print("Created new file:" + new_dst_file_name)

