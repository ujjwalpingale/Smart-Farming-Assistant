"""Validate disease model on a folder of sample images.

Usage:
  python scripts/validate_disease_model.py --images PATH_TO_IMAGES [--labels CSV]

If --labels CSV is provided, it should be a two-column CSV: filename,label
"""
import os
import argparse
from PIL import Image
import numpy as np

from user_app.ml_disease import _load_model, _load_labels


def main(images_dir, labels_csv=None, top_k=3):
    model = _load_model()
    labels = _load_labels()

    # optional ground truth
    gt = {}
    if labels_csv and os.path.exists(labels_csv):
        import csv
        with open(labels_csv, 'r', encoding='utf-8') as f:
            r = csv.reader(f)
            for row in r:
                if len(row) >= 2:
                    gt[row[0]] = row[1]

    files = sorted([f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg','.jpeg','.png'))])
    total = 0
    correct = 0
    for fn in files:
        path = os.path.join(images_dir, fn)
        with open(path, 'rb') as fh:
            best, prevention, confs = ('', '', [])
            try:
                best, prevention, confs = __import__('user_app.ml_disease', fromlist=['predict_disease']).predict_disease(fh, top_k=top_k)
            except Exception as e:
                print(fn, 'ERROR', e)
                continue
        total += 1
        gt_label = gt.get(fn)
        ok = (gt_label == best) if gt_label else None
        if ok:
            correct += 1
        print(fn, '=>', best, 'top_confidences=', confs, 'gt=', gt_label, 'OK=', ok)

    if total and gt:
        print('Accuracy:', correct, '/', total, '=', correct/total)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--images', required=True, help='Folder with images')
    p.add_argument('--labels', help='Optional CSV with filename,label')
    p.add_argument('--topk', type=int, default=3)
    args = p.parse_args()
    main(args.images, args.labels, top_k=args.topk)