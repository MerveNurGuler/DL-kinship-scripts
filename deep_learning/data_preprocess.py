import os
import numpy as np
import pandas as pd
from scipy.io.arff import loadarff
from sklearn.preprocessing import LabelEncoder

# Global variables
classes = ['1stdeg', '2ndeg', '3rdeg', 'twin']
downsample_sizes = [1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 6000, 7000, 8000, 10000, 12500, 15000, 20000, 25000, 30000, 35000, 40000, 50000, 100000]
split_sizes = [1000, 3000, 5000, 10000, 25000, 50000]
dataframes = {}
train_dfs = []
val_dfs = []
test_datasets = {}

split_indices = {
    b'Cousins': {"test_indices": [], "val_indices": [], "train_indices": []},
    b'GreatGrandparent-GreatGrandchild': {"test_indices": [], "val_indices": [], "train_indices": []},
    b'GreatAvuncular': {"test_indices": [], "val_indices": [], "train_indices": []},
    b'Half-Siblings': {"test_indices": [], "val_indices": [], "train_indices": []},
    b'Grandparent-Grandchild': {"test_indices": [], "val_indices": [], "train_indices": []},
    b'Avuncular': {"test_indices": [], "val_indices": [], "train_indices": []},
    b'Parent-Offspring': {"test_indices": [], "val_indices": [], "train_indices": []},
    b'Siblings': {"test_indices": [], "val_indices": [], "train_indices": []},
    b'Unrelated': {"test_indices": [], "val_indices": [], "train_indices": []},
    b'Twin': {"test_indices": [], "val_indices": [], "train_indices": []}
}

def add_to_test_datasets(class_, df):
    if class_ not in test_datasets:
        test_datasets[class_] = {'test_data': df.drop(columns=['class1']), 'test_labels': df['class1']}
    else:
        test_datasets[class_]['test_data'] = pd.concat([test_datasets[class_]['test_data'], df.drop(columns=['class1'])], ignore_index=True)
        test_datasets[class_]['test_labels'] = pd.concat([test_datasets[class_]['test_labels'], df['class1']], ignore_index=True)

def get_sub_sampling_indices(df, class_, is_test, random_split=True):
    if is_test:
        if len(split_indices[class_]["test_indices"]) != 0 and len(split_indices[class_]["val_indices"]) != 0: 
            return split_indices[class_]["test_indices"], split_indices[class_]["val_indices"]
        else:
            if random_split:
                test_indices = np.random.choice(df.index, size=int(len(df) * 0.25), replace=False)
                remaining_indices = df.index.difference(test_indices)
                val_indices = np.random.choice(remaining_indices, size=int(len(remaining_indices) * 0.2), replace=False)
            else:
                total_length = len(df)
                test_size = int(total_length * 0.25)
                val_size = int((total_length - test_size) * 0.2)
                test_indices = df.index[:test_size]
                val_indices = df.index[test_size:test_size + val_size]
            train_indices = df.index.difference(test_indices).difference(val_indices)
            split_indices[class_].update({"test_indices": test_indices, "val_indices": val_indices, "train_indices": train_indices})
            return test_indices, val_indices
    else:
        if len(split_indices[class_]["val_indices"]) != 0:
            return split_indices[class_]["val_indices"]
        else:
            if random_split:
                indices = np.random.choice(df.index, size=int(len(df) * 0.2), replace=False)
            else:
                total_length = len(df)
                indices_size = int(total_length * 0.2)
                indices = df.index[:indices_size]
            split_indices[class_]["val_indices"] = indices
            return indices

def load_data():
    base_path = "dataset"
    substring_to_search = 'wl200ws50_norm.arff'
    for class_ in classes:
        for ds_size in downsample_sizes:
            filename = f"{class_}_ds{ds_size}_{substring_to_search}"
            full_path = os.path.join(base_path, filename)
            if os.path.exists(full_path):
                df_name = f"df_{class_.split('deg')[0]}_data_down_{ds_size}"
                dataframes[df_name] = pd.DataFrame(loadarff(full_path)[0])
            else:
                print(f"File {full_path} does not exist!")

def df_split():
    for df_name in dataframes.keys():
        curr_ds = int(df_name.split("_")[-1])
        if curr_ds in split_sizes:
            df_grouped = dataframes[df_name].groupby('class1')
            for class_ in df_grouped.groups:
                group_df = df_grouped.get_group(class_).reset_index(drop=True)
                test_indices, val_indices = get_sub_sampling_indices(group_df, class_, is_test=True, random_split=False)
                add_to_test_datasets(curr_ds, group_df.iloc[test_indices])
                val_dfs.append(group_df.iloc[val_indices])
                train_dfs.append(group_df.drop(group_df.index[test_indices], inplace=False).drop(group_df.index[val_indices], inplace=False))
        else:
            df_grouped = dataframes[df_name].groupby('class1')
            for class_ in df_grouped.groups:
                group_df = df_grouped.get_group(class_).reset_index(drop=True)
                indices = get_sub_sampling_indices(group_df, class_, is_test=False, random_split=False)
                val_dfs.append(group_df.iloc[indices])
                train_dfs.append(group_df.drop(group_df.index[indices], inplace=False))

def label_encoding(labels_df): 
    label_mapping = {
        b'Cousins': '3rdegree',
        b'GreatGrandparent-GreatGrandchild': '3rdegree',
        b'GreatAvuncular': '3rdegree',
        b'Half-Siblings': '2ndegree',
        b'Grandparent-Grandchild': '2ndegree',
        b'Avuncular': '2ndegree',
        b'Parent-Offspring': 'Parent-Offspring',
        b'Siblings': 'Siblings',
        b'Unrelated': 'Unrelated',
        b'Twin': 'Twin',
    }    
    labels_df_mapped = labels_df.map(label_mapping)
    le = LabelEncoder()
    labels_encoded = le.fit_transform(labels_df_mapped) 
    return labels_encoded

def reshape(df):
    df_values = df.values
    reshaped_data = [np.concatenate(row.reshape(-1, 10, 10), axis=1) for row in df_values]
    reshaped_data = np.stack(reshaped_data)
    reshaped_data = reshaped_data[:, np.newaxis, :, :]
    return reshaped_data

def save_split_indices():
    np.save('split_indices.npy', split_indices)

def pre_processes_all():
    load_data()
    df_split()
    save_split_indices()

    train_df = pd.concat(train_dfs, ignore_index=True)
    val_df = pd.concat(val_dfs, ignore_index=True)

    X_train = train_df.drop(columns=['class1'])
    y_train = train_df['class1']
    X_val = val_df.drop(columns=['class1'])
    y_val = val_df['class1']

    y_train_encoded = label_encoding(y_train)
    X_train = reshape(X_train)
    y_val_encoded = label_encoding(y_val)
    X_val = reshape(X_val)

    for key in test_datasets.keys():
        test_datasets[key]['test_labels'] = label_encoding(test_datasets[key]['test_labels'])
        test_datasets[key]['test_data'] = reshape(test_datasets[key]['test_data'])

    return X_train, X_val, y_train_encoded, y_val_encoded, test_datasets
