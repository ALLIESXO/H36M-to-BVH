""" Creates a file in BVH format for the H36M Dataset (http://vision.imar.ro/human3.6m/description.php).
    The BVH file is prefilled with missing Motion content and is completed with a cdf D3 Angle pose file of H36M.
    As the standard skeleton structure - the metadata.xml in H36M matlab code has been used as a reference.
"""
import argparse 
import cdflib
import os, sys, shutil
from pathlib import Path

"""
Converts all given files (either by given root folder where files are inside or absolute path of file)
int .bvh files with the correct MOTION section.

Input:
argFile   - PathToFile (str)
argFolder - PathToFolder (str)
argDest   - PathToDestinationFolder (str)
"""
def convert(argFile, argFolder, argDest, skelScale=100):

    proced = checkArguments(argFile, argFolder, argDest)
    
    # add files which needs to be converted 
    poses = []
    skelScale = float(skelScale)
    if proced[0] is True:
        poses.append(argFile)
    
    if proced[1] is True:
        for path in Path(argFolder).rglob('*.cdf'):
            poses.append(path)

    src_dir = os.getcwd()
    if proced[2] is not True:
        print("Will use default destination for file creation.")
    else:
        dst_dir = argDest
    
    for index, pose in enumerate(poses):
        # initialize global variables 
        cdf_angles = cdflib.CDF(pose)
        angles = cdf_angles.varget("Pose")[0]

        # List of rotation indexes in the bvh hierarchy order 
        rot_order = [[5,6,4], [32,33,31], [35,36,34], [38,39,37], [41,42,40],
        [44,45,43], [47,48,46], [50,51,49], [53,54,52], [56,57,55], [59,60,58],
        [62,63,61], [65,66,64], [68,69,67], [71,72,70], [74,75,73], [77,78,76],
        [20,21,19], [23,24,22], [26,27,25], [29,30,28],
        [8,9,7], [11,12,10], [14,15,13], [17,18,16]]

        frame_time = 0.02
        frames = len(angles)

        if proced[2] is not True:
            dst_dir = os.path.dirname(pose)

        src_file = os.path.join(src_dir, "base_H36M_hierarchy.bvh")
        #copy the base file to destination dir
        src_file = shutil.copy(src_file, dst_dir)
        new_dst_file_name = os.path.join(dst_dir, (cdf_angles.file.stem + '.bvh').replace(" ",""))
        # if file with same name exist we append unique id
        if os.path.isfile(new_dst_file_name):
            new_dst_file_name = os.path.join(dst_dir, (cdf_angles.file.stem + "_" + str(index) + '.bvh').replace(" ",""))

        try:
            os.rename(src_file, new_dst_file_name)
        except OSError as error:
            print(error)

        #Append content to new bvh file 
        with open(new_dst_file_name, 'a') as file:
            file.write("\nMOTION \n")
            file.write("Frames:\t" + str(frames) + " \n")
            file.write("Frame Time: " + str(frame_time) + " \n")

            for frame in angles:
                xp = frame[0] / skelScale
                yp = frame[1] / skelScale
                zp = frame[2] / skelScale
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


"""
Checks if any of those arguments are valid.
Returns triplet of bool (file, folder, dest),
indicating if either a whole folder should be queried for
pose files or only a single file needs to be converted.  
"""
def checkArguments(filePath, folder, dest):
    use_file = False
    use_folder = False
    use_dest = False 

    if filePath != "":
        use_file = True
        if not os.path.isfile(filePath):
            print("Error: Provided File does not exist.")
            sys.exit(1)

    if folder != "":
        use_folder = True
        if not os.path.isdir(folder):
            print("Error: Provided Path to folder does not exist.")
            sys.exit(1)
    
    if dest != "":
        use_dest = True
        if not os.path.isdir(dest):
            print("Error: Provided Path to folder does not exsit.")
            sys.exit(1)

    if use_file or use_folder is True:
        return (use_file, use_folder, use_dest)
    else:
        print("Error: No provided path to cdf filde or folder provided containing those files!")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translate cdf motion (of Human36M dataset) file to bvh file.")
    parser.add_argument("-SkelScale", default=100 , help="Number to which the size of the skeleton is divided by.")
    parser.add_argument("-file", default="", help="Path to the cdf pose file. (Must be 'D3 Angles' pose)")
    parser.add_argument("-folder", default="", help="Path to the pose files folder. All files will be converted.")
    parser.add_argument("-dest", default="", type=str, help="Path where to store the converted files. (Default: Same directory as given cdf files.)")
    args = parser.parse_args()
    convert(args.file, args.folder, args.dest, args.SkelScale)
    print("Done converting.")