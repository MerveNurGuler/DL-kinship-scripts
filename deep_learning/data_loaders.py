import torch
from torch.utils.data import DataLoader, TensorDataset

def get_loaders(X_train, y_train, X_val, y_val, test_data, batch_size=64):
    """
    Create DataLoader objects for training, validation, and test datasets.
    
    :param X_train: Training data features
    :param y_train: Training data labels
    :param X_val: Validation data features
    :param y_val: Validation data labels
    :param test_data: Dictionary of test datasets with keys as test names and values as dictionaries with 'test_data' and 'test_labels'
    :param batch_size: Size of each batch
    :return: train_loader, val_loader, test_loaders
    """
    # Convert data to PyTorch tensors
    X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
    y_train_tensor = torch.tensor(y_train, dtype=torch.int64)
    X_val_tensor = torch.tensor(X_val, dtype=torch.float32)
    y_val_tensor = torch.tensor(y_val, dtype=torch.int64)

    # Create datasets
    train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
    val_dataset = TensorDataset(X_val_tensor, y_val_tensor)

    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    # Create data loaders for test datasets
    test_loaders = {}
    for key in test_data:
        X_test_tensor = torch.tensor(test_data[key]['test_data'], dtype=torch.float32)
        y_test_tensor = torch.tensor(test_data[key]['test_labels'], dtype=torch.int64)
        test_dataset = TensorDataset(X_test_tensor, y_test_tensor)
        test_loaders[key] = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    return train_loader, val_loader, test_loaders
