import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import resnet18, ResNet18_Weights
from PIL import Image
import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity

# Load pretrained ResNet18 and remove the classification head
model_base = resnet18(weights=ResNet18_Weights.DEFAULT)
model = nn.Sequential(*list(model_base.children())[:-1])  # remove the final FC layer
model.eval()

# Image transform pipeline
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# Optional cache to speed up repeat comparisons
feature_cache = {}

def extract_features(image_path):
    if image_path in feature_cache:
        return feature_cache[image_path]
    image = Image.open(image_path).convert("RGB")
    img_t = transform(image).unsqueeze(0)  # shape: [1, 3, 224, 224]

    with torch.no_grad():
        features = model(img_t)  # shape: [1, 512, 1, 1]
    feat_array = features.squeeze().cpu().numpy()
    feature_cache[image_path] = feat_array
    return feat_array

def recognize_image(target_path, all_paths):
    if not all_paths:
        return []
    target_feat = extract_features(target_path).reshape(1, -1)
    all_feats = [extract_features(p) for p in all_paths]
    all_feats = np.array(all_feats)
    similarities = cosine_similarity(target_feat, all_feats)[0]
    return list(zip(all_paths, similarities))
