import sys, csv, io, collections, os
AUC = {"54810":"Tibu","54250":"El Tarra","54800":"Teorama","54206":"Convencion","13244":"El Carmen de Bolivar","70713":"San Onofre","70508":"Ovejas","13442":"Maria la Baja","76834":"Tulua","76111":"Buga","76113":"Bugalagrande","20001":"Valledupar","20238":"El Copey","47288":"Fundacion","47189":"Cienaga","05649":"San Carlos","05313":"Granada","05197":"Cocorna","13688":"Santa Rosa del Sur","13670":"San Pablo","05604":"Remedios","05736":"Segovia","85001":"Yopal","50568":"Puerto Gaitan","50325":"Mapiripan"}
out=open(sys.argv[1],'a')
for p in sys.argv[2:]:
    raw=open(p,'rb'); head=raw.read(100000); raw.seek(0)
    enc='utf-8'
    try: head.decode('utf-8')
    except UnicodeDecodeError: enc='latin-1'
    f=io.TextIOWrapper(raw,encoding=enc,errors='replace',newline='')
    r=csv.reader(f); hdr=[c.strip().upper().lstrip('﻿') for c in next(r)]
    ix={c:i for i,c in enumerate(hdr)}
    n=0; res=collections.Counter(); occ=collections.Counter(); anos=collections.Counter(); miss=0
    for row in r:
        if not row: continue
        n+=1
        try:
            dre=row[ix['CODPTORE']].strip().zfill(2); mre=row[ix['CODMUNRE']].strip().zfill(3)
            doc=row[ix['COD_DPTO']].strip().zfill(2); moc=row[ix['COD_MUNIC']].strip().zfill(3)
            anos[row[ix['ANO']].strip()]+=1
        except Exception: miss+=1; continue
        cr=dre+mre; co=doc+moc
        if cr in AUC: res[cr]+=1
        if co in AUC: occ[co]+=1
    lab=os.path.basename(p)
    print(f"{lab}: enc={enc} ncols={len(hdr)} N={n} anos={dict(anos.most_common(3))} has CODMUNRE={'CODMUNRE' in ix} FECHA_NACM={'FECHA_NACM' in ix}", flush=True)
    for c,name in AUC.items(): out.write(f"{lab},{c},{name},{res.get(c,0)},{occ.get(c,0)},{n}\n")
    out.flush()
