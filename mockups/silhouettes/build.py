import numpy as np, json
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
src = {'f':'/mnt/user-data/attachments/c6fd022c-1e0e-5afe-aa94-910f82742c39/9e4f121a-image.png','m':'/mnt/user-data/attachments/c6fd022c-1e0e-5afe-aa94-910f82742c39/60866c37-image.png'}
cols = {'f':[(18,327),(340,648),(661,970),(984,1292)],'m':[(17,377),(393,759),(776,1142),(1159,1518)]}
rows = {'f':[(27,598),(613,1170)],'m':[(15,507),(521,1005)]}
names = ['chest','biceps','triceps','delts','abs','lats','glutes','quads']
LIME = np.array([183,227,91],float)
out='assets/'
meta={}
for g in 'fm':
    im = np.asarray(Image.open(src[g]).convert('RGB')).astype(float)
    crops=[]
    for r in rows[g]:
        for c in cols[g]:
            crops.append(im[r[0]+50:r[1]-6, c[0]+6:c[1]-6])
    # panel bg
    bgc = np.median(np.concatenate([c[:10,:10].reshape(-1,3) for c in crops]),axis=0)
    H = min(c.shape[0] for c in crops); W=min(c.shape[1] for c in crops)
    crops=[c[:H,:W] for c in crops]
    # figure bbox per panel (grey figure, not blue)
    boxes=[]
    for c in crops:
        lum=c.mean(axis=2)
        m = lum>70
        m = ndi.binary_opening(m, iterations=2)
        ys,xs=np.where(m)
        boxes.append((xs.min(),ys.min(),xs.max(),ys.max()))
    print(g,'bboxes',boxes,'bg',bgc)
    ref=crops[0]
    def isblue(c): return (c[...,2]-c[...,0]>55)&(c[...,2]>120)
    refb=ndi.binary_dilation(isblue(ref),iterations=3)
    g0=ndi.gaussian_filter(ref.mean(axis=2),1.5)
    al=[]
    for i,c in enumerate(crops):
        cb=ndi.binary_dilation(isblue(c),iterations=3)
        valid=~(refb|cb)
        gc=ndi.gaussian_filter(c.mean(axis=2),1.5)
        best=None
        if i==0: best=(0,1.0,0,0)
        for sc in ([] if i==0 else np.arange(0.97,1.035,0.004)):
            for dy in range(-12,13,2):
                for dx in range(-8,9,2):
                    # output(y,x)=input(sc*y+dy', ...) about centre-top: use affine_transform
                    M=np.array([1/sc,1/sc]); off=np.array([dy,dx],float)
                    t=ndi.affine_transform(gc,M,offset=off,order=1,mode='nearest',output_shape=gc.shape)
                    e=np.abs(t-g0)[valid].mean()
                    if best is None or e<best[0]: best=(e,sc,dy,dx)
        e,sc,dy,dx=best
        M=np.array([1/sc,1/sc,1]); off=np.array([dy,dx,0],float)
        sh=ndi.affine_transform(c,M,offset=off,order=1,mode='nearest',output_shape=c.shape)
        print(g,i,'best',round(e,2),round(sc,3),dy,dx)
        al.append(sh[:H,:W])
    al=np.array(al)
    blue=(al[...,2]-al[...,0]>55)&(al[...,2]>120)
    blue=np.array([ndi.binary_dilation(b,iterations=2) for b in blue])
    ma=np.ma.masked_array(al,mask=np.repeat(blue[...,None],3,axis=3))
    base=np.ma.median(ma,axis=0).filled(0)
    Image.fromarray(base.clip(0,255).astype(np.uint8)).save(out+f'{g}_base.png')
    meta[g]={'w':W,'h':H,'bg':[int(x) for x in bgc],'parts':{}}
    for k,n in enumerate(names):
        mk=blue[k]
        # soft alpha from colour saturation
        sat=(al[k][...,2]-al[k][...,0]).clip(0,255)
        a=np.where(mk,(sat/110.0).clip(0.0,1),0)
        a=np.where(mk,np.maximum(a,0.0),0)
        a=ndi.gaussian_filter(a,0.7)
        f=(al[k][...,2]/235.0).clip(0.35,1.15)[...,None]
        rgb=(LIME*f).clip(0,255)
        rgba=np.dstack([rgb,(a.clip(0,1)*255)]).astype(np.uint8)
        # keep only large components
        lab,nl=ndi.label(mk)
        sizes=ndi.sum(mk,lab,range(1,nl+1))
        keep=np.isin(lab,[i+1 for i,s in enumerate(sizes) if s>150])
        rgba[...,3]=np.where(ndi.binary_dilation(keep,iterations=2),rgba[...,3],0)
        Image.fromarray(rgba).save(out+f'{g}_{n}.png')
        ys,xs=np.where(rgba[...,3]>40)
        meta[g]['parts'][n]=[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]
    # diagnostics: residual between aligned panels and base outside blue
    err=[np.abs(al[k]-base)[~blue[k]].mean() for k in range(8)]
    print(g,'err',np.round(err,2))
json.dump(meta,open(out+'meta.json','w'))
print(json.dumps(meta))
