import os
import torch
import numpy as np

def entropy(softmax_output):
    """
    Calculate the entropy of a softmax output.
    
    Args:
    - softmax_output (list or np.array): The probabilities from the softmax activation.
    
    Returns:
    - float: The entropy value.
    """
    if isinstance(softmax_output, list):
        softmax_output = np.array(softmax_output)
    
    assert np.abs(np.sum(softmax_output) - 1) < 1e-6, "Probabilities don't sum up to 1!"
    
    return -np.sum(softmax_output * np.log(softmax_output))

def saver(model_dir_path, model, train_loss_data, val_loss_data, dict_cm, dict_classification_rep, all_test_res_dict):
    if not os.path.exists(model_dir_path):
        os.makedirs(model_dir_path)

    model_path = os.path.join(model_dir_path, "model.pt")
    try:
        torch.save(model.state_dict(), model_path)
        print(f"Model saved to {model_path}")
    except Exception as e:
        print(f"Failed to save model: {e}")

    try:
        np.save(os.path.join(model_dir_path, "train_loss.npy"), train_loss_data)
        print(f"train_loss_data saved to {os.path.join(model_dir_path, 'train_loss.npy')}")
    except Exception as e:
        print(f"Failed to save train_loss_data: {e}")

    try:
        np.save(os.path.join(model_dir_path, "val_loss.npy"), val_loss_data)  
        print(f"val_loss_data saved to {os.path.join(model_dir_path, 'val_loss.npy')}")  
    except Exception as e:
        print(f"Failed to save val_loss_data: {e}")

    for key in dict_cm:
        path = os.path.join(model_dir_path, f"confusion_matrix_{key}.npy")
        try:
            np.save(path, dict_cm[key])
            print(f"dict_cm[{key}] saved to {path}")
        except Exception as e:
            print(f"Failed to save dict_cm[{key}]: {e}")

    for key in dict_classification_rep:
        path = os.path.join(model_dir_path, f"classification_report_{key}.npy")
        try:
            np.save(path, dict_classification_rep[key])
            print(f"dict_classification_rep[{key}] saved to {path}")
        except Exception as e:
            print(f"Failed to save dict_classification_rep[{key}]: {e}")

    for key in all_test_res_dict:
        path = os.path.join(model_dir_path, f"test_result_{key}.npy")
        try:    
            np.save(path, all_test_res_dict[key])
            print(f"all_test_res_dict[{key}] saved to {path}")
        except Exception as e:
            print(f"Failed to save all_test_res_dict[{key}]: {e}")
