import sys
import numpy as np
from PIL import Image
paths = {'f':'/mnt/user-data/attachments/c6fd022c-1e0e-5afe-aa94-910f82742c39/9e4f121a-image.png','m':'/mnt/user-data/attachments/c6fd022c-1e0e-5afe-aa94-910f82742c39/60866c37-image.png'}
for k,p in paths.items():
    a = np.asarray(Image.open(p).convert('RGB')).astype(int)
    h,w,_ = a.shape
    # panel bg slightly lighter than page bg: use luminance of a row/col profile
    lum = a.sum(axis=2)
    colmean = lum[int(h*0.3):int(h*0.45)].mean(axis=0)
    rowmean = lum[:, :].mean(axis=1)
    # print gaps: positions where column profile is at its minimum (page bg)
    base = np.percentile(colmean, 5)
    gaps = colmean < base + 3
    xs = np.where(np.diff(gaps.astype(int)) != 0)[0]
    print(k, w, h, 'col transitions', xs.tolist()[:40])
    rbase = np.percentile(rowmean, 3)
    rg = rowmean < rbase + 3
    ys = np.where(np.diff(rg.astype(int)) != 0)[0]
    print(k, 'row transitions', ys.tolist()[:40])
