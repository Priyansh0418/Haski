"""
Prototype training script (PyTorch) for skin_type classification using transfer learning.

Expected data layout:
ml/data/
  train/
    class_a/
      img1.jpg
    class_b/
  val/
    class_a/
    class_b/

This script:
- Loads an ImageFolder dataset with torchvision transforms
- Uses EfficientNet (preferred) or MobileNet as a backbone with a new classifier head
- Fine-tunes the model and prints basic metrics
- Saves the final model to ml/exports/skin_classifier.pth

TODO:
- Convert this into a multi-task model (skin_type + hair_type + condition detection)
- Add detection/localization models (e.g., Faster R-CNN) for lesions/pimples
"""

import argparse
import os
import time
from typing import Tuple

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models


def get_dataloaders(data_dir: str, input_size: int, batch_size: int) -> Tuple[DataLoader, DataLoader, int]:
    train_dir = os.path.join(data_dir, 'train')
    val_dir = os.path.join(data_dir, 'val')

    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

    train_transforms = transforms.Compose([
        transforms.RandomResizedCrop(input_size),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.15, contrast=0.1, saturation=0.1, hue=0.02),
        transforms.ToTensor(),
        normalize,
    ])

    val_transforms = transforms.Compose([
        transforms.Resize(int(input_size * 1.15)),
        transforms.CenterCrop(input_size),
        transforms.ToTensor(),
        normalize,
    ])

    train_ds = datasets.ImageFolder(train_dir, transform=train_transforms)
    val_ds = datasets.ImageFolder(val_dir, transform=val_transforms)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=4, pin_memory=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=4, pin_memory=True)

    num_classes = len(train_ds.classes)
    print(f'Found classes: {train_ds.classes} (num_classes={num_classes})')
    return train_loader, val_loader, num_classes


def build_model(num_classes: int, use_efficientnet: bool = True):
    # Prefer EfficientNet if available, else MobileNetV2
    try:
        if use_efficientnet and hasattr(models, 'efficientnet_b0'):
            model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
            in_features = model.classifier[1].in_features
            model.classifier[1] = nn.Linear(in_features, num_classes)
            print('Using EfficientNet-B0 backbone')
            return model
    except Exception:
        pass

    # Fallback
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    print('Using MobileNet-V2 backbone')
    return model


def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    running_corrects = 0
    total = 0

    for inputs, labels in loader:
        inputs = inputs.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        _, preds = torch.max(outputs, 1)
        running_loss += loss.item() * inputs.size(0)
        running_corrects += torch.sum(preds == labels.data).item()
        total += inputs.size(0)

    epoch_loss = running_loss / total
    epoch_acc = running_corrects / total
    return epoch_loss, epoch_acc


def evaluate(model, loader, criterion, device):
    model.eval()
    running_loss = 0.0
    running_corrects = 0
    total = 0

    with torch.no_grad():
        for inputs, labels in loader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            _, preds = torch.max(outputs, 1)
            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels.data).item()
            total += inputs.size(0)

    epoch_loss = running_loss / total
    epoch_acc = running_corrects / total
    return epoch_loss, epoch_acc


def save_model(model, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    torch.save(model.state_dict(), path)
    print(f'Model saved to {path}')


def main():
    parser = argparse.ArgumentParser(description='Train skin_type classifier (transfer learning)')
    parser.add_argument('--data-dir', default='ml/data', help='dataset root (expects train/ and val/ subfolders)')
    parser.add_argument('--epochs', type=int, default=5)
    parser.add_argument('--batch-size', type=int, default=16)
    parser.add_argument('--lr', type=float, default=1e-4)
    parser.add_argument('--input-size', type=int, default=224)
    parser.add_argument('--device', default='cuda' if torch.cuda.is_available() else 'cpu')
    parser.add_argument('--export-path', default='ml/exports/skin_classifier.pth')
    args = parser.parse_args()

    device = torch.device(args.device)
    print(f'Using device: {device}')

    train_loader, val_loader, num_classes = get_dataloaders(args.data_dir, args.input_size, args.batch_size)

    model = build_model(num_classes)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)

    best_acc = 0.0
    for epoch in range(1, args.epochs + 1):
        start = time.time()
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = evaluate(model, val_loader, criterion, device)
        elapsed = time.time() - start

        print(f'Epoch {epoch}/{args.epochs} - {elapsed:.1f}s')
        print(f'  train loss: {train_loss:.4f} acc: {train_acc:.4f}')
        print(f'  val   loss: {val_loss:.4f} acc: {val_acc:.4f}')

        # save best
        if val_acc > best_acc:
            best_acc = val_acc
            save_model(model, args.export_path)

    print('Training complete')


if __name__ == '__main__':
    main()

