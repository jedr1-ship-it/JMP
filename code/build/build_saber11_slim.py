#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_saber11_slim.py
=====================
Construye un archivo analitico "slim" a partir de los 36 archivos oficiales de
Saber 11 (ICFES, FTP DataIcfes), periodos 2005-1 ... 2022-2.

Entradas
  /home/user/JMP/data/raw/saber11/saber11_sb11/      periodo 1 (texto plano)
  /home/user/JMP/data/raw/saber11/saber11_sb11_p2/   periodo 2 (.gz, se leen con compression='gzip')
Salidas
  /home/user/JMP/data/derived/saber11_slim.parquet
  /home/user/JMP/data/derived/saber11_slim_codebook.md
  /home/user/JMP/data/derived/saber11_muni_name_map_2010.csv  (mapa nombre->codigo DANE usado para 2009-2)
  /home/user/JMP/data/derived/saber11_slim_build_summary.json (estadisticas del build)

Uso:  python3 -I build_saber11_slim.py [--periods 20051,20052,...] [--outdir DIR]

Diseno:
  * Se procesa archivo a archivo, leyendo solo las columnas necesarias (usecols) con dtype=str,
    y se escribe cada periodo de forma incremental al parquet (pyarrow.ParquetWriter) para no
    acumular los ~9.3M de filas en memoria.
  * Delimitador y encoding se detectan inspeccionando la primera linea (bytes) de cada archivo.
    pandas no soporta el separador '¬' (2 bytes en utf-8) con el motor C, asi que se usa engine='python'.
  * Si un periodo falla, se registra el error y se continua con los demas.
"""
import argparse
import csv
import gc
import glob
import gzip
import io
import json
import os
import re
import sys
import time
import traceback
import unicodedata
from collections import Counter, defaultdict
from datetime import date

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

RAW1 = '/home/user/JMP/data/raw/saber11/saber11_sb11/'
RAW2 = '/home/user/JMP/data/raw/saber11/saber11_sb11_p2/'
OUTDIR = '/home/user/JMP/data/derived/'

# Departamentos DANE validos (2 digitos)
VALID_DEPTS = {'05', '08', '11', '13', '15', '17', '18', '19', '20', '23', '25', '27', '41', '44', '47',
               '50', '52', '54', '63', '66', '68', '70', '73', '76', '81', '85', '86', '88', '91', '94',
               '95', '97', '99'}

# Columnas crudas candidatas (en MAYUSCULAS; los encabezados se normalizan a mayusculas)
AREA_COLS = ['PUNT_LENGUAJE', 'PUNT_MATEMATICAS', 'PUNT_C_SOCIALES', 'PUNT_CIENCIAS_SOCIALES', 'PUNT_HISTORIA',
             'PUNT_GEOGRAFIA', 'PUNT_FILOSOFIA', 'PUNT_BIOLOGIA', 'PUNT_QUIMICA', 'PUNT_FISICA', 'PUNT_IDIOMA',
             'PUNT_INGLES']
WANTED = ['ESTU_CONSECUTIVO', 'PERIODO', 'ESTU_GENERO',
          'ESTU_NACIMIENTO_DIA', 'ESTU_NACIMIENTO_MES', 'ESTU_NACIMIENTO_ANNO', 'ESTU_FECHANACIMIENTO',
          'ESTU_COD_RESIDE_MCPIO', 'ESTU_COD_RESIDE_DEPTO',
          'ESTU_MCPIO_RESIDE', 'ESTU_RESIDE_MCPIO', 'ESTU_DEPTO_RESIDE', 'ESTU_RESIDE_DEPTO',
          'COLE_COD_MCPIO_UBICACION', 'COLE_COD_DANE_INSTITUCION', 'COLE_NATURALEZA',
          'FAMI_ESTRATO_VIVIENDA', 'FAMI_ESTRATOVIVIENDA', 'FAMI_EDUCA_MADRE', 'FAMI_EDUCACIONMADRE',
          'ESTU_INSE_INDIVIDUAL', 'PUNT_GLOBAL', 'PUNT_LECTURA_CRITICA'] + AREA_COLS

OUT_SCHEMA = pa.schema([
    ('periodo', pa.string()), ('year', pa.int16()), ('sem', pa.int8()), ('consecutivo', pa.string()),
    ('birth_year', pa.int16()), ('birth_month', pa.int8()), ('birth_day', pa.int8()), ('age_at_exam', pa.float32()),
    ('muni_res', pa.string()), ('dpto_res', pa.string()), ('muni_cole', pa.string()), ('cole_naturaleza', pa.string()),
    ('sexo', pa.string()), ('estrato', pa.int8()), ('educ_madre', pa.string()), ('inse', pa.float32()),
    ('score_global_raw', pa.float32()), ('score_z', pa.float32()), ('math_z', pa.float32()), ('lang_z', pa.float32()),
    ('periodo_icfes', pa.string()), ('flag_truncated_file', pa.bool_()),
])
TRUNCATED_FILES = {'SB11_20172.TXT.gz'}   # archivo truncado en el FTP (73.293 filas, ultima incompleta)


# ----------------------------------------------------------------------------- utilidades
def log(msg):
    print(time.strftime('%H:%M:%S'), msg, flush=True)


def nrm_name(s):
    """Normaliza nombre de municipio/departamento: mayusculas, sin acentos, espacios colapsados."""
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return ''
    s = unicodedata.normalize('NFKD', str(s).strip().upper())
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'\s+', ' ', s)


def period_from_filename(path):
    b = os.path.basename(path)
    m = re.search(r'(20\d\d)[-_]?([12])', b)
    return m.group(1) + m.group(2)


def list_files():
    f1 = sorted(glob.glob(RAW1 + '*'))
    f2 = sorted(glob.glob(RAW2 + '*'))
    files = [(period_from_filename(p), p) for p in f1 + f2]
    return sorted(files, key=lambda t: t[0])


def detect_format(path):
    """Inspecciona la primera linea: BOM, encoding, delimitador y encabezado."""
    op = gzip.open if path.endswith('.gz') else open
    with op(path, 'rb') as f:
        hdrb = f.readline()
    bom = hdrb.startswith(b'\xef\xbb\xbf')
    h = hdrb[3:] if bom else hdrb
    if b'\xc2\xac' in h:
        enc = 'utf-8'
    elif b'\xac' in h:
        enc = 'latin-1'
    else:
        try:
            h.decode('utf-8'); enc = 'utf-8'
        except UnicodeDecodeError:
            enc = 'latin-1'
    header = h.decode(enc, errors='replace').rstrip('\r\n')
    if '¬' in header:
        delim = '¬'
    elif '|' in header:
        delim = '|'
    elif ';' in header:
        delim = ';'
    else:
        delim = ','
    cols = [c.strip().upper() for c in header.split(delim)]
    return dict(bom=bom, enc=enc, delim=delim, cols=cols, ncols=len(cols))


def read_raw(path, fmt, wanted):
    """Lee solo las columnas 'wanted' presentes en el archivo, todo como str. Devuelve (df, n_bad_lines)."""
    cols = fmt['cols']
    pos = sorted({i for i, c in enumerate(cols) if c in wanted})
    names = [cols[i] for i in pos]
    ncols = fmt['ncols']
    bad = Counter()

    def on_bad(row):              # fila con mas campos de los esperados: se recorta y se cuenta
        bad['n'] += 1
        return row[:ncols]

    enc = 'utf-8-sig' if fmt['enc'] == 'utf-8' else fmt['enc']
    df = pd.read_csv(path, sep=fmt['delim'], encoding=enc, dtype=str, usecols=pos, header=0,
                     engine='python', quoting=csv.QUOTE_NONE, keep_default_na=False, na_values=[''], encoding_errors='replace',
                     compression='gzip' if path.endswith('.gz') else None, on_bad_lines=on_bad)
    df.columns = names
    for c in df.columns:
        df[c] = df[c].str.strip()
    df = df.replace({'': np.nan})
    return df, bad['n']


def to_num(s):
    """Convierte puntajes con coma o punto decimal a float."""
    return pd.to_numeric(s.astype('string').str.replace(',', '.', regex=False), errors='coerce').astype('float64')


def clean_code(s, width):
    """Codigo numerico como string con ceros a la izquierda (acepta '5001', '5001.0'); NaN si no es digito."""
    s = s.astype('string').str.strip().str.replace(r'\.0+$', '', regex=True)
    ok = s.str.fullmatch(r'\d+')
    s = s.where(ok.fillna(False).astype(bool), pd.NA).str.zfill(width)
    return s


def valid_muni(s):
    """Codigo DANE municipal de 5 digitos con departamento valido; '99999' y similares -> NaN."""
    s = clean_code(s, 5)
    ok = ((s.str.len() == 5).fillna(False).astype(bool) & s.str[:2].isin(VALID_DEPTS).fillna(False).astype(bool)
          & (s != '99999').fillna(False).astype(bool))
    return s.where(ok, pd.NA)


def zscore(x):
    """Estandariza dentro del periodo (media 0, sd 1, ddof=0) usando solo valores > 0 (0 y -1 = ausente/no presento)."""
    x = x.where(x > 0)
    mu = x.mean(); sd = x.std(ddof=0)
    if not np.isfinite(sd) or sd == 0:
        return pd.Series(np.nan, index=x.index, dtype='float64')
    return (x - mu) / sd


def standardize(x):
    """Media 0, sd 1 (ddof=0) dentro del periodo, sin filtro de valores (para re-estandarizar el promedio de z-scores)."""
    mu = x.mean(); sd = x.std(ddof=0)
    if not np.isfinite(sd) or sd == 0:
        return pd.Series(np.nan, index=x.index, dtype='float64')
    return (x - mu) / sd


def first_present(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


# ----------------------------------------------------------------------------- mapa nombre -> codigo (2010)
def build_name_map(files, outdir):
    """Mapa (municipio, departamento) normalizados -> codigo DANE, observado en 2010-1 y 2010-2."""
    counts = defaultdict(Counter)
    for per, path in files:
        if per not in ('20101', '20102'):
            continue
        fmt = detect_format(path)
        df, _ = read_raw(path, fmt, {'ESTU_MCPIO_RESIDE', 'ESTU_DEPTO_RESIDE', 'ESTU_COD_RESIDE_MCPIO'})
        df['code'] = valid_muni(df['ESTU_COD_RESIDE_MCPIO'])
        df = df.dropna(subset=['code', 'ESTU_MCPIO_RESIDE', 'ESTU_DEPTO_RESIDE'])
        keys = list(zip(df['ESTU_MCPIO_RESIDE'].map(nrm_name), df['ESTU_DEPTO_RESIDE'].map(nrm_name)))
        for k, c in zip(keys, df['code']):
            counts[k][c] += 1
        log(f'  name map: {per} -> {len(counts)} claves acumuladas')
        del df; gc.collect()
    rows = []
    for (m, d), cc in counts.items():
        code, n = cc.most_common(1)[0]
        rows.append(dict(muni_name=m, depto_name=d, code=code, n_obs=n, n_codes=len(cc)))
    mp = pd.DataFrame(rows).sort_values(['depto_name', 'muni_name'])
    mp.to_csv(os.path.join(outdir, 'saber11_muni_name_map_2010.csv'), index=False)
    log(f'  name map guardado: {len(mp)} claves, {int((mp.n_codes > 1).sum())} ambiguas (se usa el codigo mas frecuente)')
    return {(r.muni_name, r.depto_name): r.code for r in mp.itertuples()}


# ----------------------------------------------------------------------------- procesamiento de un periodo
def process_period(per, path, fmt, name_map):
    info = dict(periodo=per, file=os.path.basename(path), delim=fmt['delim'], enc=fmt['enc'], bom=fmt['bom'],
                ncols_file=fmt['ncols'], mapping={}, notes=[])
    year, sem = int(per[:4]), int(per[4])
    df, nbad = read_raw(path, fmt, set(WANTED))
    info['n_raw'] = int(len(df)); info['n_bad_lines_trimmed'] = int(nbad)
    cols_read = list(df.columns)

    # --- deduplicacion
    df = df.drop_duplicates()
    info['n_after_exact_dedup'] = int(len(df))
    if 'ESTU_CONSECUTIVO' in df.columns:
        has = df['ESTU_CONSECUTIVO'].notna()
        df = pd.concat([df[has].drop_duplicates(subset=['ESTU_CONSECUTIVO'], keep='first'), df[~has]])
        info['mapping']['consecutivo'] = 'ESTU_CONSECUTIVO'
    else:
        info['mapping']['consecutivo'] = None
    info['n_after_consec_dedup'] = int(len(df))
    df = df.reset_index(drop=True)
    n = len(df)

    out = pd.DataFrame(index=df.index)
    out['periodo'] = per
    out['year'] = np.int16(year)
    out['sem'] = np.int8(sem)
    out['consecutivo'] = df['ESTU_CONSECUTIVO'] if 'ESTU_CONSECUTIVO' in df.columns else pd.Series(pd.NA, index=df.index, dtype='string')
    out['periodo_icfes'] = df['PERIODO'] if 'PERIODO' in df.columns else pd.Series(pd.NA, index=df.index, dtype='string')
    info['mapping']['periodo_icfes'] = 'PERIODO' if 'PERIODO' in df.columns else None

    # --- fecha de nacimiento
    if 'ESTU_FECHANACIMIENTO' in df.columns:
        f = df['ESTU_FECHANACIMIENTO'].astype('string').str.extract(r'^\s*(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{1,4})')
        bd, bm, by = (pd.to_numeric(f[i], errors='coerce').astype('float64') for i in range(3))
        info['mapping']['birth'] = 'ESTU_FECHANACIMIENTO (dd/mm/aaaa)'
    else:
        by = bm = bd = None
    if by is not None and by.notna().any():
        # anios sin siglo ('0003' en 2020-1 = 2003; '0096' en 2013-2 = 1996): se completa con el siglo (1900 o 2000) que
        # implique una edad al examen entre 10 y 40 anios; si ninguno la da (p.ej. '0027' en 2013-2, registros corruptos) queda NaN.
        short = by.notna() & (by < 100)
        c20 = by + 2000; c19 = by + 1900
        ok20 = short & ((year - c20) >= 10) & ((year - c20) <= 40)
        ok19 = short & ~ok20 & ((year - c19) >= 10) & ((year - c19) <= 40)
        by = by.mask(ok20, c20).mask(ok19, c19).mask(short & ~ok20 & ~ok19, np.nan)
        info['n_birth_year_2digit_fixed'] = int((ok20 | ok19).sum()); info['n_birth_year_2digit_unrecoverable'] = int((short & ~ok20 & ~ok19).sum())
    if 'ESTU_FECHANACIMIENTO' in df.columns:
        pass
    elif 'ESTU_NACIMIENTO_ANNO' in df.columns:
        by = to_num(df['ESTU_NACIMIENTO_ANNO'])
        bm = to_num(df['ESTU_NACIMIENTO_MES']) if 'ESTU_NACIMIENTO_MES' in df.columns else pd.Series(np.nan, index=df.index)
        bd = to_num(df['ESTU_NACIMIENTO_DIA']) if 'ESTU_NACIMIENTO_DIA' in df.columns else pd.Series(np.nan, index=df.index)
        info['mapping']['birth'] = 'ESTU_NACIMIENTO_DIA / _MES / _ANNO'
    else:
        by = bm = bd = pd.Series(np.nan, index=df.index); info['mapping']['birth'] = None
    bad_year = ~((by > 1900) & (by <= year))          # 1900 = placeholder (01/01/1900), >anio examen = error
    by = by.where(~bad_year); bm = bm.where(~bad_year & (bm >= 1) & (bm <= 12)); bd = bd.where(~bad_year & (bd >= 1) & (bd <= 31))
    bdate = pd.to_datetime(pd.DataFrame({'year': by, 'month': bm, 'day': bd}), errors='coerce')
    # si dia/mes invalidos pero anio valido: aproximar con 1 de julio
    approx = bdate.isna() & by.notna()
    bdate = bdate.where(~approx, pd.to_datetime(pd.DataFrame({'year': by.where(approx), 'month': 7, 'day': 1}), errors='coerce'))
    exam = pd.Timestamp(year, 3 if sem == 1 else 8, 15)
    age = (exam - bdate).dt.days / 365.25
    implaus = age.notna() & ((age < 10) | (age > 90))      # edades imposibles para un examinado -> fecha de nacimiento erronea
    by = by.where(~implaus); bm = bm.where(~implaus); bd = bd.where(~implaus); age = age.where(~implaus)
    out['birth_year'] = by.astype('Int16'); out['birth_month'] = bm.astype('Int8'); out['birth_day'] = bd.astype('Int8')
    out['age_at_exam'] = age.astype('float32')
    info['n_birth_approx_july1'] = int(approx.sum()); info['n_birth_implausible_age'] = int(implaus.sum())
    info.setdefault('n_birth_year_2digit_fixed', 0); info.setdefault('n_birth_year_2digit_unrecoverable', 0)

    # --- residencia
    if 'ESTU_COD_RESIDE_MCPIO' in df.columns:
        out['muni_res'] = valid_muni(df['ESTU_COD_RESIDE_MCPIO'])
        info['mapping']['muni_res'] = 'ESTU_COD_RESIDE_MCPIO'
    else:
        cm = first_present(df, ['ESTU_MCPIO_RESIDE', 'ESTU_RESIDE_MCPIO']); cd = first_present(df, ['ESTU_DEPTO_RESIDE', 'ESTU_RESIDE_DEPTO'])
        if cm and cd:
            keys = pd.Series(list(zip(df[cm].map(nrm_name), df[cd].map(nrm_name))), index=df.index)
            out['muni_res'] = keys.map(lambda k: name_map.get(k, pd.NA) if k[0] else pd.NA).astype('string')
            nonblank = int((df[cm].notna()).sum()); matched = int(out['muni_res'].notna().sum())
            info['mapping']['muni_res'] = f'{cm} + {cd} (nombres) -> codigo via mapa 2010-1/2010-2'
            info['notes'].append(f'muni_res por nombre: {matched:,} de {nonblank:,} filas con nombre no vacio emparejadas ({matched / max(nonblank, 1):.1%}); {n - nonblank:,} filas sin nombre.')
            unm = keys[out['muni_res'].isna() & df[cm].notna()].value_counts().head(10)
            info['unmatched_names_top'] = {f'{k[0]} | {k[1]}': int(v) for k, v in unm.items()}
        else:
            out['muni_res'] = pd.Series(pd.NA, index=df.index, dtype='string'); info['mapping']['muni_res'] = None
    if 'ESTU_COD_RESIDE_DEPTO' in df.columns:
        d = clean_code(df['ESTU_COD_RESIDE_DEPTO'], 2)
        d = d.where(d.isin(VALID_DEPTS), pd.NA)
        out['dpto_res'] = d.fillna(out['muni_res'].str[:2])
        info['mapping']['dpto_res'] = 'ESTU_COD_RESIDE_DEPTO (si falta: muni_res[:2])'
    else:
        out['dpto_res'] = out['muni_res'].str[:2]; info['mapping']['dpto_res'] = 'muni_res[:2]'

    # --- colegio
    if 'COLE_COD_MCPIO_UBICACION' in df.columns:
        out['muni_cole'] = valid_muni(df['COLE_COD_MCPIO_UBICACION']); info['mapping']['muni_cole'] = 'COLE_COD_MCPIO_UBICACION'
    elif 'COLE_COD_DANE_INSTITUCION' in df.columns:
        dane = df['COLE_COD_DANE_INSTITUCION'].astype('string').str.strip()
        mc = dane.where(dane.str.fullmatch(r'\d{12}').fillna(False).astype(bool)).str[1:6]
        out['muni_cole'] = valid_muni(mc)
        info['mapping']['muni_cole'] = 'COLE_COD_DANE_INSTITUCION[1:6] (digitos 2-6 del codigo DANE de 12 digitos del establecimiento)'
    else:
        out['muni_cole'] = pd.Series(pd.NA, index=df.index, dtype='string'); info['mapping']['muni_cole'] = None
    if 'COLE_NATURALEZA' in df.columns:
        nat = df['COLE_NATURALEZA'].astype('string').str.strip().str.upper()
        out['cole_naturaleza'] = nat.map({'O': 'oficial', 'OFICIAL': 'oficial', 'N': 'no oficial', 'NO OFICIAL': 'no oficial'}).astype('string')
        info['mapping']['cole_naturaleza'] = 'COLE_NATURALEZA'
    else:
        out['cole_naturaleza'] = pd.Series(pd.NA, index=df.index, dtype='string'); info['mapping']['cole_naturaleza'] = None

    # --- demograficas / SES
    if 'ESTU_GENERO' in df.columns:
        g = df['ESTU_GENERO'].astype('string').str.strip().str.upper()
        out['sexo'] = g.where(g.isin(['F', 'M']), pd.NA); info['mapping']['sexo'] = 'ESTU_GENERO'
    else:
        out['sexo'] = pd.Series(pd.NA, index=df.index, dtype='string'); info['mapping']['sexo'] = None
    ce = first_present(df, ['FAMI_ESTRATOVIVIENDA', 'FAMI_ESTRATO_VIVIENDA'])
    if ce:
        e = df[ce].astype('string').str.strip().str.upper()
        num = pd.to_numeric(e.str.extract(r'^(?:ESTRATO\s*)?(\d)$')[0], errors='coerce')
        num = num.where((num >= 1) & (num <= 6))
        num = num.mask(e.str.contains('SIN ESTRATO', na=False), 0)
        out['estrato'] = num.astype('Int8'); info['mapping']['estrato'] = f'{ce} (1-6; 0 = "Sin Estrato"; otros -> NaN)'
        info['estrato_raw_values'] = {str(k): int(v) for k, v in df[ce].value_counts(dropna=False).head(12).items()}
    else:
        out['estrato'] = pd.Series(pd.NA, index=df.index, dtype='Int8'); info['mapping']['estrato'] = None
    cmad = first_present(df, ['FAMI_EDUCACIONMADRE', 'FAMI_EDUCA_MADRE'])
    if cmad and df[cmad].notna().any():
        out['educ_madre'] = df[cmad].astype('string'); info['mapping']['educ_madre'] = f'{cmad} (texto/codigo crudo)'
    else:
        out['educ_madre'] = pd.Series(pd.NA, index=df.index, dtype='string'); info['mapping']['educ_madre'] = (cmad + ' (vacia en este periodo)') if cmad else None
    if 'ESTU_INSE_INDIVIDUAL' in df.columns:
        out['inse'] = to_num(df['ESTU_INSE_INDIVIDUAL']).astype('float32'); info['mapping']['inse'] = 'ESTU_INSE_INDIVIDUAL'
    else:
        out['inse'] = np.float32(np.nan); info['mapping']['inse'] = None

    # --- puntajes
    if 'PUNT_MATEMATICAS' in df.columns:
        m = to_num(df['PUNT_MATEMATICAS']); out['math_z'] = zscore(m).astype('float32'); info['mapping']['math_z'] = 'PUNT_MATEMATICAS'
    else:
        out['math_z'] = np.float32(np.nan); info['mapping']['math_z'] = None
    cl = first_present(df, ['PUNT_LECTURA_CRITICA', 'PUNT_LENGUAJE'])
    if cl:
        l = to_num(df[cl]); out['lang_z'] = zscore(l).astype('float32'); info['mapping']['lang_z'] = cl
    else:
        out['lang_z'] = np.float32(np.nan); info['mapping']['lang_z'] = None

    if 'PUNT_GLOBAL' in df.columns:
        g = to_num(df['PUNT_GLOBAL'])
        out['score_global_raw'] = g.astype('float32')
        out['score_z'] = zscore(g).astype('float32')
        info['mapping']['score_global_raw'] = 'PUNT_GLOBAL'
        info['score_def'] = 'z(PUNT_GLOBAL) dentro del periodo (valores <= 0 tratados como ausentes)'
        info['score_areas_used'] = ['PUNT_GLOBAL']
    else:
        out['score_global_raw'] = np.float32(np.nan); info['mapping']['score_global_raw'] = None
        areas = [c for c in AREA_COLS if c in df.columns]
        A = pd.DataFrame({c: to_num(df[c]) for c in areas})
        A = A.where(A > 0)
        # columnas duplicadas (p.ej. 2007-1: punt_ingles es copia exacta de punt_lenguaje) -> se descarta la segunda
        dropped = []
        for i, c1 in enumerate(areas):
            for c2 in areas[i + 1:]:
                if c2 in dropped or c1 in dropped:
                    continue
                both = A[c1].notna() & A[c2].notna()
                if both.sum() > 1000 and np.allclose(A.loc[both, c1], A.loc[both, c2]):
                    dropped.append(c2)
        used = [c for c in areas if c not in dropped]
        Z = pd.DataFrame({c: zscore(A[c]) for c in used})
        navail = Z.notna().sum(axis=1)
        comp = Z.mean(axis=1).where(navail >= max(4, int(np.ceil(len(used) / 2))))
        out['score_z'] = standardize(comp).astype('float32')  # re-estandariza el promedio dentro del periodo
        info['score_def'] = (f'promedio de z-scores por area (cada area estandarizada dentro del periodo, valores <= 0 ausentes), '
                             f'con al menos {max(4, int(np.ceil(len(used) / 2)))} areas no ausentes; el promedio se re-estandariza dentro del periodo')
        info['score_areas_used'] = used
        if dropped:
            info['notes'].append(f'Areas descartadas por ser copia exacta de otra columna: {dropped}')
        info['score_areas_dropped_duplicate'] = dropped
        info['n_areas_dist'] = {int(k): int(v) for k, v in navail.value_counts().sort_index().items()}
    out['flag_truncated_file'] = os.path.basename(path) in TRUNCATED_FILES

    # --- estadisticas del periodo
    both = out['muni_res'].notna() & out['muni_cole'].notna()
    info.update(
        n_final=int(n),
        pct_birth_year=float(out['birth_year'].notna().mean()), pct_birth_full_date=float((out['birth_day'].notna() & out['birth_month'].notna() & out['birth_year'].notna()).mean()),
        pct_muni_res=float(out['muni_res'].notna().mean()), pct_muni_cole=float(out['muni_cole'].notna().mean()),
        n_both_muni=int(both.sum()), n_res_eq_cole=int((out.loc[both, 'muni_res'] == out.loc[both, 'muni_cole']).sum()),
        pct_score_z=float(out['score_z'].notna().mean()), pct_math_z=float(out['math_z'].notna().mean()), pct_lang_z=float(out['lang_z'].notna().mean()),
        pct_sexo=float(out['sexo'].notna().mean()), pct_estrato=float(out['estrato'].notna().mean()), pct_educ_madre=float(out['educ_madre'].notna().mean()),
        pct_inse=float(out['inse'].notna().mean()), pct_naturaleza=float(out['cole_naturaleza'].notna().mean()),
        age_mean=float(out['age_at_exam'].mean()), age_p05=float(out['age_at_exam'].quantile(.05)), age_p95=float(out['age_at_exam'].quantile(.95)),
        cols_read=cols_read,
    )
    out = out[[f.name for f in OUT_SCHEMA]]
    # tipos finales
    for c in ['periodo', 'consecutivo', 'muni_res', 'dpto_res', 'muni_cole', 'cole_naturaleza', 'sexo', 'educ_madre', 'periodo_icfes']:
        out[c] = out[c].astype('string')
    table = pa.Table.from_pandas(out, schema=OUT_SCHEMA, preserve_index=False)
    del df, out; gc.collect()
    return table, info


# ----------------------------------------------------------------------------- codebook
def write_codebook(path, infos, failures, name_map_n, parquet_path, total_rows):
    L = []
    L.append('# Codebook: saber11_slim.parquet\n')
    L.append(f'Generado por `/home/user/JMP/code/build/build_saber11_slim.py` el {date.today().isoformat()}. '
             f'Fuente: 36 archivos oficiales Saber 11 (ICFES, FTP DataIcfes), periodos 2005-1 a 2022-2. '
             f'Archivo: `{parquet_path}` ({total_rows:,} filas).\n')
    L.append('## Columnas de salida\n')
    L.append('| columna | tipo | definicion |')
    L.append('|---|---|---|')
    defs = [
        ('periodo', 'string', "Periodo segun el nombre del archivo: aaaa + semestre ('20152'). OJO: desde 2019-2 el ICFES codifica el 2o semestre como 4 en la variable PERIODO ('20194'); ver `periodo_icfes`."),
        ('year', 'int16', 'Anio del examen (de `periodo`).'),
        ('sem', 'int8', 'Semestre/calendario del archivo: 1 = archivo periodo 1 (marzo-abril, calendario B), 2 = archivo periodo 2 (agosto-septiembre, calendario A).'),
        ('consecutivo', 'string', 'ESTU_CONSECUTIVO (identificador anonimo del ICFES, unico dentro del periodo tras deduplicar).'),
        ('birth_year / birth_month / birth_day', 'Int16 / Int8 / Int8', 'Fecha de nacimiento. 2005-1..2009-1: ESTU_NACIMIENTO_ANNO/MES/DIA; 2009-2+: ESTU_FECHANACIMIENTO (dd/mm/aaaa). NaN si falta o si el anio <= 1900 (placeholder 01/01/1900) o > anio del examen; mes/dia NaN si fuera de rango. Anios sin siglo (p.ej. "0003" en 2020-1, "0096" en 2013-2; 23% de 2020-1 y 10% de 2021-1) se completan con el siglo (1900 o 2000) que implica una edad al examen entre 10 y 40 anios; si ninguno la da quedan NaN (en 2013-2 ~4.100 registros con fecha corrupta: el campo dia contiene la edad). Conteos por periodo en la tabla de N.'),
        ('age_at_exam', 'float32', 'Edad en anios = (fecha examen - fecha nacimiento)/365.25, con fecha de examen aproximada 15-mar (sem 1) y 15-ago (sem 2). Si dia/mes invalidos pero anio valido se usa 1-jul del anio de nacimiento. Si la edad implicada es < 10 o > 90 anios se consideran erroneos y se ponen NaN la edad y los tres campos de nacimiento (conteos por periodo en la tabla de N).'),
        ('muni_res', 'string', "Codigo DANE (5 digitos, con ceros) del municipio de residencia (ESTU_COD_RESIDE_MCPIO). NaN si falta, no es numerico, departamento invalido o '99999'. 2009-2: construido por nombre (ESTU_MCPIO_RESIDE + ESTU_DEPTO_RESIDE) con el mapa nombre->codigo observado en 2010-1/2010-2."),
        ('dpto_res', 'string', 'Departamento de residencia (2 digitos): ESTU_COD_RESIDE_DEPTO si existe y es valido; si no, primeros 2 digitos de muni_res.'),
        ('muni_cole', 'string', 'Codigo DANE del municipio del colegio: COLE_COD_MCPIO_UBICACION (2006+). 2005-1/2005-2 no traen esa columna: se derivan los digitos 2-6 del codigo DANE de 12 digitos del establecimiento (COLE_COD_DANE_INSTITUCION), que contienen el municipio.'),
        ('cole_naturaleza', 'string', "'oficial' / 'no oficial' (COLE_NATURALEZA: O/N en 2005-2009-1, OFICIAL/NO OFICIAL despues)."),
        ('sexo', 'string', "ESTU_GENERO: 'F'/'M'; otros valores -> NaN."),
        ('estrato', 'Int8', "Estrato de la vivienda 1-6; 0 = 'Sin Estrato' (solo 2022-2); NaN si falta u otro codigo (en 2008-1..2009-1 el archivo trae codigos numericos 1-6 y 8; 8 -> NaN). Vacio en 2005-1/2005-2 y no existe en 2006-2007."),
        ('educ_madre', 'string', 'Educacion de la madre tal como viene en el archivo (FAMI_EDUCA_MADRE / FAMI_EDUCACIONMADRE). 2008-1..2009-1 son codigos numericos del ICFES (0, 9-17, 99), 2009-2+ son etiquetas de texto. Vacia en 2005; no existe en 2006-2007.'),
        ('inse', 'float32', 'Indice socioeconomico individual del ICFES (ESTU_INSE_INDIVIDUAL), disponible desde 2014-2.'),
        ('score_global_raw', 'float32', 'PUNT_GLOBAL tal como viene (escala 0-500), disponible desde 2014-2 (nuevo examen). NaN antes.'),
        ('score_z', 'float32', 'Puntaje estandarizado DENTRO de cada periodo (media 0, sd 1, ddof=0). Si existe PUNT_GLOBAL: z(PUNT_GLOBAL). Si no: promedio de los z-scores de las areas del nucleo comun disponibles ese periodo (cada una estandarizada dentro del periodo), exigiendo al menos 4 areas no ausentes, y luego re-estandarizado dentro del periodo. Valores crudos <= 0 (0 y -1) se tratan como ausentes. Ver tabla por periodo.'),
        ('math_z', 'float32', 'z(PUNT_MATEMATICAS) dentro del periodo (valores <= 0 ausentes).'),
        ('lang_z', 'float32', 'z(PUNT_LENGUAJE) hasta 2014-1; z(PUNT_LECTURA_CRITICA) desde 2014-2; dentro del periodo (valores <= 0 ausentes).'),
        ('periodo_icfes', 'string', 'Valor crudo de la columna PERIODO del archivo (p.ej. 20194 para 2019-2).'),
        ('flag_truncated_file', 'bool', 'True para 2017-2: el archivo SB11_20172.TXT.gz del FTP esta truncado (73.293 filas, la ultima incompleta; el periodo real tiene ~550 mil evaluados). Se incluye tal cual.'),
    ]
    for a, b, c in defs:
        L.append(f'| {a} | {b} | {c} |')
    L.append('')
    L.append('## Deduplicacion\n')
    L.append('1. Se eliminan filas exactamente duplicadas (sobre el conjunto de columnas crudas leidas de cada archivo). '
             '2. Dentro de cada periodo se conserva la primera fila por ESTU_CONSECUTIVO (las filas sin consecutivo se conservan todas).\n')
    L.append('## N por periodo (antes y despues de deduplicar) y cobertura\n')
    L.append('| periodo | archivo | delim | BOM | ncols | N crudo | N tras dup. exactos | N tras dup. consecutivo | % fecha nac. completa | n anio sin siglo reparado | n anio sin siglo irrecuperable | n fecha aprox. 1-jul | n edad implausible (NaN) | % muni_res | % muni_cole | % score_z | % estrato | % educ_madre | % inse | edad media (p5-p95) |')
    L.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for i in infos:
        L.append(f"| {i['periodo']} | {i['file']} | `{i['delim']}` | {'si' if i['bom'] else 'no'} | {i['ncols_file']} | {i['n_raw']:,} | {i['n_after_exact_dedup']:,} | {i['n_after_consec_dedup']:,} | "
                 f"{i['pct_birth_full_date']:.1%} | {i['n_birth_year_2digit_fixed']:,} | {i['n_birth_year_2digit_unrecoverable']:,} | {i['n_birth_approx_july1']:,} | {i['n_birth_implausible_age']:,} | {i['pct_muni_res']:.1%} | {i['pct_muni_cole']:.1%} | {i['pct_score_z']:.1%} | {i['pct_estrato']:.1%} | {i['pct_educ_madre']:.1%} | {i['pct_inse']:.1%} | "
                 f"{i['age_mean']:.1f} ({i['age_p05']:.0f}-{i['age_p95']:.0f}) |")
    L.append('')
    if failures:
        L.append('### Periodos que fallaron\n')
        for per, err in failures.items():
            L.append(f'- **{per}**: `{err}`')
        L.append('')
    L.append('## Correspondencia de columnas por periodo\n')
    keys = ['consecutivo', 'birth', 'muni_res', 'dpto_res', 'muni_cole', 'cole_naturaleza', 'sexo', 'estrato', 'educ_madre', 'inse', 'score_global_raw', 'math_z', 'lang_z']
    L.append('| periodo | ' + ' | '.join(keys) + ' |')
    L.append('|---|' + '---|' * len(keys))
    for i in infos:
        L.append(f"| {i['periodo']} | " + ' | '.join(str(i['mapping'].get(k)) if i['mapping'].get(k) is not None else '-' for k in keys) + ' |')
    L.append('')
    L.append('## Definicion exacta de score_z por periodo\n')
    L.append('| periodo | definicion | columnas usadas | descartadas (duplicadas) | notas |')
    L.append('|---|---|---|---|---|')
    for i in infos:
        L.append(f"| {i['periodo']} | {i['score_def']} | {', '.join(i['score_areas_used'])} | {', '.join(i.get('score_areas_dropped_duplicate', [])) or '-'} | {' '.join(i['notes']) or '-'} |")
    L.append('')
    L.append('## Notas y advertencias\n')
    L.append(f'- Mapa nombre->codigo para 2009-2: {name_map_n:,} claves (municipio, departamento) normalizadas (mayusculas, sin acentos) observadas en 2010-1/2010-2; guardado en `saber11_muni_name_map_2010.csv`.')
    for i in infos:
        if i.get('unmatched_names_top'):
            L.append(f"- 2009-2: nombres sin emparejar (top): {i['unmatched_names_top']}")
    L.append('- 2007-1: la columna punt_ingles es copia exacta de punt_lenguaje en el archivo oficial; se excluye del promedio de areas.')
    L.append('- 2005-1 contiene 5.760 filas exactamente duplicadas (mismo consecutivo y contenido); se eliminan.')
    L.append('- 2005-2 no trae la columna PERIODO (periodo_icfes NaN); el periodo se toma del nombre del archivo.')
    L.append('- 2012-1 a 2014-1 traen ademas columnas RECAF_* (puntajes recalificados a la escala del nuevo examen); NO se usan: score_z usa las areas originales del periodo.')
    L.append('- Los puntajes por area 2005-2009-1 vienen con coma decimal; 2009-2 en adelante con punto. Ambos se parsean.')
    L.append('- Valores de puntaje 0 y -1 se consideran ausentes para las estandarizaciones (ausencia a una sesion); son raros en 2010+ (decenas por periodo) y mas frecuentes en inglés/idioma 2005-2009.')
    L.append('- En 2015-1, 2016-1, 2013-2, 2019-2, 2020-2 aparecen codigos de residencia 99999 (extranjero/no informado): se ponen NaN.')
    L.append('- `estrato` en 2008-1..2009-1: el archivo trae codigos 1-6 y 8 (8 = sin informacion/no aplica segun el patron de frecuencias); solo se conservan 1-6.')
    L.append('- 2010-1 (archivo periodo 1) tiene ~12% de filas sin codigo de residencia; 2009-2 ~7% sin nombre de municipio.')
    L.append('- Lectura: las columnas enteras con nulos (birth_year, birth_month, birth_day, estrato) estan almacenadas como int16/int8 nullable en parquet; `pandas.read_parquet` las devuelve como float64 por defecto (usar `dtype_backend="numpy_nullable"` o pyarrow para conservarlas como enteros).')
    L.append('- Columnas adicionales a las solicitadas: `periodo_icfes` (PERIODO crudo) y `flag_truncated_file` (marca 2017-2).')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--periods', default='', help='lista separada por comas de periodos a procesar (p.ej. 20051,20092); vacio = todos')
    ap.add_argument('--outdir', default=OUTDIR)
    args = ap.parse_args()
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    sel = set(args.periods.split(',')) if args.periods else None

    files = list_files()
    log(f'{len(files)} archivos encontrados')
    t0 = time.time()
    log('Construyendo mapa nombre->codigo DANE con 2010-1/2010-2 ...')
    name_map = build_name_map(files, outdir)

    parquet_path = os.path.join(outdir, 'saber11_slim.parquet')
    writer = pq.ParquetWriter(parquet_path, OUT_SCHEMA, compression='zstd')
    infos, failures = [], {}
    total = 0
    try:
        for per, path in files:
            if sel and per not in sel:
                continue
            t1 = time.time()
            try:
                fmt = detect_format(path)
                log(f"{per}: {os.path.basename(path)} delim={fmt['delim']!r} enc={fmt['enc']} bom={fmt['bom']} ncols={fmt['ncols']}")
                table, info = process_period(per, path, fmt, name_map)
                writer.write_table(table)
                total += table.num_rows
                info['secs'] = round(time.time() - t1, 1)
                infos.append(info)
                log(f"{per}: N={info['n_raw']:,} -> {info['n_after_exact_dedup']:,} -> {info['n_final']:,}  "
                    f"muni_res={info['pct_muni_res']:.1%} fecha={info['pct_birth_full_date']:.1%} score_z={info['pct_score_z']:.1%}  "
                    f"areas={info['score_areas_used']}  ({info['secs']}s)")
                del table; gc.collect()
            except Exception as e:  # seguir con los demas periodos
                failures[per] = f'{type(e).__name__}: {e}'
                log(f'{per}: FALLO -> {failures[per]}\n{traceback.format_exc()}')
    finally:
        writer.close()
    log(f'parquet escrito: {parquet_path} ({total:,} filas) en {round((time.time() - t0) / 60, 1)} min')

    cb_path = os.path.join(outdir, 'saber11_slim_codebook.md')
    write_codebook(cb_path, infos, failures, len(name_map), parquet_path, total)
    log(f'codebook escrito: {cb_path}')
    summ = dict(parquet=parquet_path, total_rows=total, n_raw_total=int(sum(i['n_raw'] for i in infos)),
                n_after_exact_dedup_total=int(sum(i['n_after_exact_dedup'] for i in infos)),
                periods_included=[i['periodo'] for i in infos], periods_failed=failures, periods=infos)
    with open(os.path.join(outdir, 'saber11_slim_build_summary.json'), 'w', encoding='utf-8') as f:
        json.dump(summ, f, ensure_ascii=False, indent=1, default=str)
    if failures:
        log(f'PERIODOS FALLIDOS: {failures}')


if __name__ == '__main__':
    main()
