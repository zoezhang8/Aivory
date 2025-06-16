#image recognition 

import torch
import torchvision.transforms as transforms
from torchvision.models import resnet18
from PIL import Image
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load model once
model = resnet18(pretrained=True)
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

def extract_features(image_path):
    image = Image.open(image_path).convert("RGB")
    img_t = transform(image).unsqueeze(0)
    with torch.no_grad():
        features = model(img_t)
    return features.numpy().flatten()



def recognize_image(target_path, all_paths):
    target_feat = extract_features(target_path).reshape(1, -1)
    all_feats = [extract_features(p) for p in all_paths]
    similarities = cosine_similarity(target_feat, all_feats)[0]
    return list(zip(all_paths, similarities))
