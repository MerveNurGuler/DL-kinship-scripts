import os
import numpy as np
import pandas as pd
import statistics

def add_data(relation, relation_vector, f):
    '''
    Add previously created vectors (lists) into the output file.
    :param relation: Type of the relation (e.g., 'Parent-offspring', 'Sibling', etc.)
    :param relation_vector: The relation vector (with 22*xs*ys elements)
    :param f: The output arff file
    '''
    for px in relation_vector:
        f.write(str(px) + ",")
    f.write(relation + "\n")

def form_parOff_vector(path, xs, ys, norm_value):
    '''
    Form vectors from parent-offspring log files.
    :param path: The path of the input log file
    :param xs: The number of grids in X axis (windows)
    :param ys: The number of grids in Y axis (r)
    :return: 3 lists with respect to Parents (unrelated), Parent1-Offspring, and Parent2-Offspring (all with xs*ys elements)
    '''
    parents, par1Off, par2Off = [], [], []
    with open(path) as file:
        file = file.readlines()[1:]
        for line in file:
            tmp = line.split('\t')
            if len(tmp) >= 5 and tmp[1] != '0':
                parents.append(float(tmp[2].strip()))
                par1Off.append(float(tmp[3].strip()))
                par2Off.append(float(tmp[4].strip()))

    parents, par1Off, par2Off = np.asarray(parents), np.asarray(par1Off), np.asarray(par2Off)
    parents = np.where(2 * (1 - (parents / norm_value)) < -0.5, -0.5, np.where(2 * (1 - (parents / norm_value)) > 1.5, 1.5, 2 * (1 - (parents / norm_value))))
    par1Off = np.where(2 * (1 - (par1Off / norm_value)) < -0.5, -0.5, np.where(2 * (1 - (par1Off / norm_value)) > 1.5, 1.5, 2 * (1 - (par1Off / norm_value))))
    par2Off = np.where(2 * (1 - (par2Off / norm_value)) < -0.5, -0.5, np.where(2 * (1 - (par2Off / norm_value)) > 1.5, 1.5, 2 * (1 - (par2Off / norm_value))))

    boundaries = [-0.51, 1.51]
    right = len(parents) / xs
    down = (boundaries[1] - boundaries[0]) / ys

    vec_parents, vec_par1Off, vec_par2Off = [0] * (xs * ys), [0] * (xs * ys), [0] * (xs * ys)
    for i in range(len(parents)):
        if boundaries[0] < parents[i] < boundaries[1]:
            vec_parents[int((boundaries[1] - parents[i]) / down) * xs + int(i / right)] += 1
        if boundaries[0] < par1Off[i] < boundaries[1]:
            vec_par1Off[int((boundaries[1] - par1Off[i]) / down) * xs + int(i / right)] += 1
        if boundaries[0] < par2Off[i] < boundaries[1]:
            vec_par2Off[int((boundaries[1] - par2Off[i]) / down) * xs + int(i / right)] += 1

    return vec_parents, vec_par1Off, vec_par2Off

def form_sibling_vector(path, xs, ys, norm_value):
    '''
    Form vectors from sibling log files.
    :param path: The path of the input log file
    :param xs: The number of grids in X axis (windows)
    :param ys: The number of grids in Y axis (ASCs)
    :return: 6 lists with respect to 2 sibling pairs and 4 unrelated pairs (all with xs*ys elements)
    '''
    siblingPair1, siblingPair2 = [], []
    unrelated1, unrelated2, unrelated3, unrelated4 = [], [], [], []

    with open(path) as file:
        file = file.readlines()[1:]
        for line in file:
            tmp = line.split('\t')
            if len(tmp) == 8 and tmp[1] != '0':
                siblingPair1.append(float(tmp[2].strip()))
                siblingPair2.append(float(tmp[7].strip()))
                unrelated1.append(float(tmp[3].strip()))
                unrelated2.append(float(tmp[4].strip()))
                unrelated3.append(float(tmp[5].strip()))
                unrelated4.append(float(tmp[6].strip()))

    siblingPair1, siblingPair2 = np.asarray(siblingPair1), np.asarray(siblingPair2)
    unrelated1, unrelated2, unrelated3, unrelated4 = np.asarray(unrelated1), np.asarray(unrelated2), np.asarray(unrelated3), np.asarray(unrelated4)

    siblingPair1 = np.where(2 * (1 - (siblingPair1 / norm_value)) < -0.5, -0.5, np.where(2 * (1 - (siblingPair1 / norm_value)) > 1.5, 1.5, 2 * (1 - (siblingPair1 / norm_value))))
    siblingPair2 = np.where(2 * (1 - (siblingPair2 / norm_value)) < -0.5, -0.5, np.where(2 * (1 - (siblingPair2 / norm_value)) > 1.5, 1.5, 2 * (1 - (siblingPair2 / norm_value))))
    unrelated1 = np.where(2 * (1 - (unrelated1 / norm_value)) < -0.5, -0.5, np.where(2 * (1 - (unrelated1 / norm_value)) > 1.5, 1.5, 2 * (1 - (unrelated1 / norm_value))))
    unrelated2 = np.where(2 * (1 - (unrelated2 / norm_value)) < -0.5, -0.5, np.where(2 * (1 - (unrelated2 / norm_value)) > 1.5, 1.5, 2 * (1 - (unrelated2 / norm_value))))
    unrelated3 = np.where(2 * (1 - (unrelated3 / norm_value)) < -0.5, -0.5, np.where(2 * (1 - (unrelated3 / norm_value)) > 1.5, 1.5, 2 * (1 - (unrelated3 / norm_value))))
    unrelated4 = np.where(2 * (1 - (unrelated4 / norm_value)) < -0.5, -0.5, np.where(2 * (1 - (unrelated4 / norm_value)) > 1.5, 1.5, 2 * (1 - (unrelated4 / norm_value))))

    boundaries = [-0.51, 1.51]
    right = len(siblingPair1) / xs
    down = (boundaries[1] - boundaries[0]) / ys

    vec_siblingPair1, vec_siblingPair2 = [0] * (xs * ys), [0] * (xs * ys)
    vec_unrelated1, vec_unrelated2, vec_unrelated3, vec_unrelated4 = [0] * (xs * ys), [0] * (xs * ys), [0] * (xs * ys), [0] * (xs * ys)

    for i in range(len(siblingPair1)):
        if boundaries[0] < siblingPair1[i] < boundaries[1]:
            vec_siblingPair1[int((boundaries[1] - siblingPair1[i]) / down) * xs + int(i / right)] += 1
        if boundaries[0] < siblingPair2[i] < boundaries[1]:
            vec_siblingPair2[int((boundaries[1] - siblingPair2[i]) / down) * xs + int(i / right)] += 1
        if boundaries[0] < unrelated1[i] < boundaries[1]:
            vec_unrelated1[int((boundaries[1] - unrelated1[i]) / down) * xs + int(i / right)] += 1
        if boundaries[0] < unrelated2[i] < boundaries[1]:
            vec_unrelated2[int((boundaries[1] - unrelated2[i]) / down) * xs + int(i / right)] += 1
        if boundaries[0] < unrelated3[i] < boundaries[1]:
            vec_unrelated3[int((boundaries[1] - unrelated3[i]) / down) * xs + int(i / right)] += 1
        if boundaries[0] < unrelated4[i] < boundaries[1]:
            vec_unrelated4[int((boundaries[1] - unrelated4[i]) / down) * xs + int(i / right)] += 1

    return vec_siblingPair1, vec_siblingPair2, vec_unrelated1, vec_unrelated2, vec_unrelated3, vec_unrelated4

def write_to_out_file(files, path, msm_norm, downsample, xs, ys):
    '''
    Write the output file based on the processed vectors.
    :param files: List of files to process
    :param path: Path to the files
    :param msm_norm: Normalization values
    :param downsample: Downsample value
    :param xs: Number of pixels in X axis (windows)
    :param ys: Number of pixels in Y axis (ASCs)
    '''
    output_file = f"/path/to/gen_vecs_new/1stdeg_ds{downsample}_wl200ws50_norm.arff"
    with open(output_file, "w") as f:
        f.write("@RELATION kinship\n\n")
        for m in range(22 * xs * ys):
            f.write(f"@ATTRIBUTE pixel{m}\tNUMERIC\n")
        f.write("@ATTRIBUTE class1\t{Parent-Offspring,Siblings,Unrelated}\n\n@DATA\n")

        if len(files) > 0:
            files = [x for x in files if "X" not in x and x.endswith("_MSM.log")]
            files_sep = [x.split('_') for x in files]
            df = pd.DataFrame(files_sep)
            num_runs = df[0].nunique()

            for i in range(1, 201):
                for j in range(1, 4):
                    sibling_rel_1, sibling_rel_2 = [], []
                    unr1, unr2, unr3, unr4 = [], [], [], []
                    for k in range(1, 23):
                        filename_siblings = f"run_{i}_siblings_{j}_{k}_MSM.log"
                        filepath_siblings = os.path.join(path, filename_siblings)
                        norm_value = msm_norm.iloc[k - 1][str(downsample)]
                        vec_siblingPair1, vec_siblingPair2, vec_unrelated1, vec_unrelated2, vec_unrelated3, vec_unrelated4 = form_sibling_vector(filepath_siblings, xs, ys, norm_value)
                        sibling_rel_1 += vec_siblingPair1
                        sibling_rel_2 += vec_siblingPair2
                        unr1 += vec_unrelated1
                        unr2 += vec_unrelated2
                        unr3 += vec_unrelated3
                        unr4 += vec_unrelated4
                    add_data("Siblings", sibling_rel_1, f)
                    add_data("Siblings", sibling_rel_2, f)
                    add_data("Unrelated", unr1, f)
                    add_data("Unrelated", unr2, f)
                    add_data("Unrelated", unr3, f)
                    add_data("Unrelated", unr4, f)

            for i in range(1, 301):
                for j in range(1, 3):
                    parent_rel1, parent_rel2 = [], []
                    unrelated1 = []
                    for k in range(1, 23):
                        filename_parent = f"run_{i}_parent-offspring_{j}_{k}_MSM.log"
                        filepath_parent = os.path.join(path, filename_parent)
                        norm_value = msm_norm.iloc[k - 1][str(downsample)]
                        vec_parents, vec_par1Off, vec_par2Off = form_parOff_vector(filepath_parent, xs, ys, norm_value)
                        parent_rel1 += vec_par1Off
                        parent_rel2 += vec_par2Off
                        unrelated1 += vec_parents
                    add_data("Parent-Offspring", parent_rel1, f)
                    add_data("Parent-Offspring", parent_rel2, f)
                    add_data("Unrelated", unrelated1, f)

# Main script execution
downsample_values = [1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 6000, 7000, 8000, 10000, 12500, 15000, 20000, 25000, 30000, 35000, 40000, 50000]
xs, ys = 10, 10  # Number of pixels in X and Y axes

for downsample in downsample_values:
    msm_norm = pd.read_csv("/path/to/normalization_files/normalization_wl200ws50.csv")
    path = f"/path/to/analysis/wl200_ws50/downsample_{downsample}/"
    files = os.listdir(path)
    write_to_out_file(files, path, msm_norm, downsample, xs, ys)
