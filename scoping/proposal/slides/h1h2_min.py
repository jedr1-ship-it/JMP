import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np
plt.rcParams.update({"font.family":"serif","font.size":9,"axes.spines.top":False,"axes.spines.right":False})
x=np.arange(5); lab=["in utero","0-2","3-5","6-11","nacidos tras\nel fin"]
fig,ax=plt.subplots(1,2,figsize=(8,2.6),sharey=True)
acc="#8B1A1A"; blue="#2A78D6"; ink="#1F1F1F"
h1=[-0.6,-1.0,-0.6,-0.3,-0.3]; h2=[0,0,-0.6,-1.0,0]
for a,y,c,t in zip(ax,[h1,h2],[acc,blue],["H1: canal del hogar (estrés del cuidador, huida)","H2: exposición directa (memoria, desde ~3 años)"]):
    a.axhline(0,color="#BBBBBB",lw=0.8); a.plot(x[:4],y[:4],"-o",color=c,ms=4,lw=1.6); a.plot([4],[y[4]],"s",color=c,ms=5)
    a.set_xticks(x); a.set_xticklabels(lab,fontsize=8); a.set_title(t,fontsize=9,loc="left"); a.set_yticks([]); a.tick_params(axis="x",length=0)
ax[0].set_ylabel(r"$\beta_a$ (forma, no magnitud)",fontsize=8); ax[0].set_ylim(-1.2,0.3)
ax[0].annotate("los nacidos tras el fin\nheredan parte",(4,-0.3),xytext=(2.6,0.1),fontsize=7,color=ink,arrowprops=dict(arrowstyle="-",color=ink,lw=0.6))
ax[1].annotate("nada antes de los 3;\nnada tras el fin",(1,0),xytext=(0.2,-0.9),fontsize=7,color=ink,arrowprops=dict(arrowstyle="-",color=ink,lw=0.6))
fig.tight_layout(); fig.savefig("fig_h1h2_min.pdf")
