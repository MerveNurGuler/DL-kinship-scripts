import numpy as np
import torch
import torch.nn as nn
import os
from model import CNN
from trainer import train
from data_loaders import get_loaders
from data_preprocess import pre_processes_all
from tester import test_all

def class_weighting(y_train):
    """
    Compute class weights for balancing the training data.
    :param y_train: Training labels
    :return: Dictionary and array of class weights
    """
    from sklearn.utils import class_weight
    unique_classes = np.unique(y_train)
    class_weights = class_weight.compute_class_weight('balanced', classes=unique_classes, y=y_train)
    class_weights_dict = dict(zip(unique_classes, class_weights))    
    return class_weights_dict, class_weights

# Set device to GPU if available
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(device)

# Load and preprocess data
X_train, X_val, y_train, y_val, test_data = pre_processes_all()

# Compute class weights
class_weights_dict, class_weights = class_weighting(y_train)

# Hyperparameter search
max_num_epochs = 200
learning_rates = [0.001, 0.0001, 0.00001]
batch_sizes = [128, 256]

for bs in batch_sizes:
    train_loader, val_loader, test_loaders = get_loaders(X_train, y_train, X_val, y_val, test_data, batch_size=bs)
    print(f"Loaders created with batch size {bs}")

    for lr in learning_rates:
        model = CNN().to(device)

        # Define loss function with class weights
        loss_fun = nn.CrossEntropyLoss(weight=torch.tensor(np.log1p(class_weights), dtype=torch.float32)).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        print(f"Training model with lr={lr} and bs={bs}")

        # Model base path
        model_dir_path = os.path.join("models_CNN_20050", f"lr_{lr}_bs_{bs}")

        # Create model directory if it doesn't exist
        if not os.path.exists(model_dir_path):
            os.makedirs(model_dir_path)

        # Train and test the model at each epoch
        train(model, train_loader, val_loader, test_loaders, loss_fun, optimizer, device, max_num_epochs, model_dir_path)
