import torch
import os
import numpy as np

from tester import test_all
from utils import saver 

# Train function applying early stopping
def train(model, train_loader, val_loader, test_loaders, criterion, optimizer, device, n_epochs, model_dir_path, patience=10):
    model.train()

    # Initialize lists to monitor training progress
    train_loss_data = []
    val_loss_data = []

    # Initialize early stopping variables
    best_val_loss = float('inf')
    patience_counter = 0

    for epoch in range(n_epochs):
        running_loss = 0.0
        for i, data in enumerate(train_loader):
            inputs, labels = data
            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()

            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        epoch_loss = running_loss / len(train_loader)
        train_loss_data.append(epoch_loss)
        print(f'Epoch {epoch + 1} loss: {epoch_loss:.3f}')

        # Validation phase
        model.eval()
        running_val_loss = 0.0
        with torch.no_grad():
            for data in val_loader:
                inputs, labels = data
                inputs, labels = inputs.to(device), labels.to(device)

                outputs = model(inputs)
                val_loss = criterion(outputs, labels)
                running_val_loss += val_loss.item()

        epoch_val_loss = running_val_loss / len(val_loader)
        val_loss_data.append(epoch_val_loss)
        print(f'Validation loss: {epoch_val_loss:.3f}')

        # Test the model
        dict_cm, dict_classification_rep, all_test_res_dict = test_all(test_loaders, model, device)

        # Save the model, losses, and test results
        model_path = os.path.join(model_dir_path, f"model_epoch_{epoch+1}.pt")
        saver(model_path, model, train_loss_data, val_loss_data, dict_cm, dict_classification_rep, all_test_res_dict)

        # Early stopping logic
        if epoch_val_loss < best_val_loss:
            best_val_loss = epoch_val_loss
            patience_counter = 0
        else:
            patience_counter += 1
            print(f'EarlyStopping counter: {patience_counter} out of {patience}')
            if patience_counter >= patience:
                print('Early stopping due to validation loss not decreasing')
                break

    return model, np.asarray(train_loss_data), np.asarray(val_loss_data)
