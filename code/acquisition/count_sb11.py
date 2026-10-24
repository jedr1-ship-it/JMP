import sys, os, re, collections, io, gzip, unicodedata
AUC = {"54810":"Tibu","54250":"El Tarra","54800":"Teorama","54206":"Convencion","13244":"El Carmen de Bolivar","70713":"San Onofre","70508":"Ovejas","13442":"Maria la Baja","76834":"Tulua","76111":"Buga","76113":"Bugalagrande","20001":"Valledupar","20238":"El Copey","47288":"Fundacion","47189":"Cienaga","05649":"San Carlos","05313":"Granada","05197":"Cocorna","13688":"Santa Rosa del Sur","13670":"San Pablo","05604":"Remedios","05736":"Segovia","85001":"Yopal","50568":"Puerto Gaitan","50325":"Mapiripan"}
# fallback by (municipio, departamento) names, accents stripped
DEPT_ALIAS = {"NORTE SANTANDER":"NORTE DE SANTANDER","VALLE":"VALLE DEL CAUCA","BOGOTA":"BOGOTA D.C."}
NAME2CODE = {("TIBU","NORTE DE SANTANDER"):"54810",("EL TARRA","NORTE DE SANTANDER"):"54250",("TEORAMA","NORTE DE SANTANDER"):"54800",("CONVENCION","NORTE DE SANTANDER"):"54206",
 ("EL CARMEN DE BOLIVAR","BOLIVAR"):"13244",("SAN ONOFRE","SUCRE"):"70713",("OVEJAS","SUCRE"):"70508",("MARIA LA BAJA","BOLIVAR"):"13442",
 ("TULUA","VALLE DEL CAUCA"):"76834",("BUGA","VALLE DEL CAUCA"):"76111",("GUADALAJARA DE BUGA","VALLE DEL CAUCA"):"76111",("BUGALAGRANDE","VALLE DEL CAUCA"):"76113",
 ("VALLEDUPAR","CESAR"):"20001",("EL COPEY","CESAR"):"20238",("FUNDACION","MAGDALENA"):"47288",("CIENAGA","MAGDALENA"):"47189",
 ("SAN CARLOS","ANTIOQUIA"):"05649",("GRANADA","ANTIOQUIA"):"05313",("COCORNA","ANTIOQUIA"):"05197",("REMEDIOS","ANTIOQUIA"):"05604",("SEGOVIA","ANTIOQUIA"):"05736",
 ("SANTA ROSA DEL SUR","BOLIVAR"):"13688",("SAN PABLO","BOLIVAR"):"13670",("YOPAL","CASANARE"):"85001",("PUERTO GAITAN","META"):"50568",("MAPIRIPAN","META"):"50325"}
def nrm(s):
    s = unicodedata.normalize('NFKD', s.strip().strip('"').upper()); s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'\s+',' ',s)
def norm_code(s):
    s = s.strip().strip('"')
    if s.endswith('.0'): s = s[:-2]
    if not s or not s.isdigit(): return None
    return s.zfill(5)
def birth_year(fecha, anno):
    if anno:
        a = anno.strip().strip('"')
        if a.endswith('.0'): a=a[:-2]
        return a if re.fullmatch(r'\d{4}', a) else None
    if fecha:
        f = fecha.strip().strip('"')
        if re.fullmatch(r'\d{1,2}/\d{1,2}/\d{4}.*', f): return f.split('/')[2][:4]
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}.*', f): return f[:4]
        if re.fullmatch(r'\d{8}', f): return f[:4] if f[:2] in ('19','20') else f[4:]
        m = re.search(r'(\d{4})', f); return m.group(1) if m else None
    return None
def process(path, label):
    raw = gzip.open(path,'rb') if path.endswith('.gz') else open(path,'rb')
    hdrb = raw.readline()
    if hdrb.startswith(b'\xef\xbb\xbf'): hdrb = hdrb[3:]; enc='utf-8'
    elif b'\xc2\xac' in hdrb: enc='utf-8'
    elif b'\xac' in hdrb: enc='latin-1'
    else:
        try: hdrb.decode('utf-8'); enc='utf-8'
        except UnicodeDecodeError: enc='latin-1'
    header = hdrb.decode(enc, errors='replace').rstrip('\r\n')
    delim = '¬¬' if '¬¬' in header else ('¬' if '¬' in header else ('|' if '|' in header else (';' if ';' in header else ',')))
    cols = [c.strip().upper() for c in header.split(delim)]
    idx = {c:i for i,c in enumerate(cols)}
    i_m = idx.get('ESTU_COD_RESIDE_MCPIO'); i_f = idx.get('ESTU_FECHANACIMIENTO'); i_a = idx.get('ESTU_NACIMIENTO_ANNO'); i_p = idx.get('PERIODO')
    i_nm = idx.get('ESTU_MCPIO_RESIDE', idx.get('ESTU_RESIDE_MCPIO')); i_nd = idx.get('ESTU_DEPTO_RESIDE', idx.get('ESTU_RESIDE_DEPTO'))
    f = io.TextIOWrapper(raw, encoding=enc, errors='replace', newline='')
    n=0; n_m=0; n_by=0; n_name=0; periods=collections.Counter(); nat=collections.Counter(); auc=collections.Counter()
    for line in f:
        line=line.rstrip('\r\n')
        if not line: continue
        p = line.split(delim); n+=1
        if i_p is not None and i_p < len(p): periods[p[i_p].strip()] += 1
        code = norm_code(p[i_m]) if (i_m is not None and i_m < len(p)) else None
        if code is None and i_nm is not None and i_nd is not None and i_nm < len(p) and i_nd < len(p):
            d = nrm(p[i_nd]); d = DEPT_ALIAS.get(d, d); code = NAME2CODE.get((nrm(p[i_nm]), d))
            if code: n_name+=1
        by = birth_year(p[i_f] if (i_f is not None and i_f < len(p)) else None, p[i_a] if (i_a is not None and i_a < len(p)) else None)
        if code: n_m+=1
        if by: n_by+=1; nat[by]+=1
        if code in AUC: auc[(code,by)]+=1
    return dict(label=label, enc=enc, delim=delim, ncols=len(cols), n=n, n_muni=n_m, n_by=n_by, n_name=n_name, periods=dict(periods.most_common(3)), has=(i_m is not None, i_f is not None, i_a is not None, i_nm is not None), nat=nat, auc=auc)
if __name__=='__main__':
    out = sys.argv[1]; files = sys.argv[2:]
    w_long = open(out+'_auc_long.csv','a'); w_nat = open(out+'_nat_birthyear.csv','a'); w_sum = open(out+'_summary.csv','a')
    for pth in files:
        label = re.sub(r'\.gz$','',os.path.basename(pth))
        r = process(pth, label)
        print(f"{label}: enc={r['enc']} delim={r['delim']!r} ncols={r['ncols']} N={r['n']} N_muni={r['n_muni']} (by_name={r['n_name']}) N_birthyear={r['n_by']} periods={r['periods']} has(cod,fecha,anno,nombre)={r['has']}", flush=True)
        w_sum.write(f"{label},{r['n']},{r['n_muni']},{r['n_by']},{r['ncols']},{r['enc']},\"{r['periods']}\"\n")
        for (code,by),v in sorted(r['auc'].items(), key=lambda kv: (kv[0][0], str(kv[0][1]))): w_long.write(f"{label},{code},{AUC[code]},{by},{v}\n")
        for by,v in sorted(r['nat'].items(), key=lambda kv: str(kv[0])): w_nat.write(f"{label},{by},{v}\n")
        w_sum.flush(); w_long.flush(); w_nat.flush()
