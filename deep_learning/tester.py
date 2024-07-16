from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.metrics import ConfusionMatrixDisplay
import numpy as np
import torch
import matplotlib.pyplot as plt
import seaborn as sns

def per_class_performance(loader, net, device):
    correct = 0
    total = 0
    y_pred = []
    y_true = []

    all_test_res = {
        "entropies": [],
        "predicted_labels": [],
        "true_labels": []
    }

    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        y_true.extend(labels.cpu().numpy())

        out = net(images)
        entropies = -torch.sum(out * torch.log(out), dim=1)
        _, predicted_labels = torch.max(out, 1)

        all_test_res["entropies"].extend(entropies.cpu().numpy())
        all_test_res["predicted_labels"].extend(predicted_labels.cpu().numpy())
        all_test_res["true_labels"].extend(labels.cpu().numpy())

        y_pred.extend(predicted_labels.cpu().numpy())
        correct += (predicted_labels == labels).sum().item()
        total += labels.size(0)

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1, 2, 3, 4, 5])
    classification_rep = classification_report(y_true, y_pred, output_dict=True, zero_division=0)

    return cm, classification_rep, all_test_res

def test_all(test_loaders, net, device):
    dict_cm = {}
    dict_classification_rep = {}
    all_test_res_dict = {}

    for key in test_loaders:
        print(f"Testing on {key} data")
        cm, classification_rep, all_test_res = per_class_performance(test_loaders[key], net, device)
        dict_cm[key] = cm
        dict_classification_rep[key] = classification_rep
        all_test_res_dict[key] = all_test_res

    return dict_cm, dict_classification_rep, all_test_res_dict
