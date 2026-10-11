import json, hashlib, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def load(n): return json.loads((ROOT/n).read_text(encoding="utf-8"))
def canon(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def norm_date(s):
    if not s: return s
    for pat in ("%m/%d/%Y","%Y-%m-%d"):
        import datetime
        try: return datetime.datetime.strptime(s,pat).strftime("%Y-%m-%d")
        except ValueError: pass
    return s
def transform():
    ds=load("DEMO-DATASET-001.json"); tax=load("DEMO-TAXONOMY-001.json")
    aliases=tax["terpene_aliases"]; pii=set(tax["pii_fields"]); out=[]
    def base_record(source_idx, image, rec):
        o={"source_record_index":source_idx,"image_filename":image}
        for k,v in rec.items():
            if k in ("cannabinoids","terpenes","entry_1","entry_2","products","image_filename"): continue
            if k in pii: o[k]="[REDACTED]"
            elif k.endswith("_date") or k=="handwritten_header": o[k]=norm_date(v)
            else: o[k]=v
        if "cannabinoids" in rec: o["cannabinoids"]=rec["cannabinoids"]
        if "terpenes" in rec:
            o["terpenes"]={aliases.get(k,k.strip().lower().replace(" ","_").replace("-","_")):v for k,v in rec["terpenes"].items()}
        return o
    for i,rec in enumerate(ds["records"]):
        image=rec.get("image_filename")
        if "products" in rec:
            for j,p in enumerate(rec["products"],1):
                o={"source_record_index":i,"source_subrecord":f"products[{j-1}]","image_filename":image}
                o["product_name"]=p.get("name")
                o["batch_number"]=p.get("Batch")
                cannabinoids={}; terpenes={}
                for k,v in p.items():
                    if k in ("name","Batch"): continue
                    if k in ("THC","THCA","THCV","CBD","CBDA","CBDV","CBN","CBG","CBGA","CBC","CBL"): cannabinoids[k]=v
                    else: terpenes[aliases.get(k,k.strip().lower().replace(" ","_").replace("-","_"))]=v
                if cannabinoids:o["cannabinoids"]=cannabinoids
                if terpenes:o["terpenes"]=terpenes
                out.append(o)
        elif any(k.startswith("entry_") for k in rec):
            for k in sorted(x for x in rec if x.startswith("entry_")):
                p=rec[k]; o={"source_record_index":i,"source_subrecord":k,"image_filename":image}
                o["brand_producer"]=p.get("brand"); o["product_name"]=p.get("product")
                cannabinoids={}; terpenes={}
                for kk,v in p.items():
                    if kk in ("brand","product"): continue
                    if kk in ("THC","THCA","THCV","CBD","CBDA","CBDV","CBN","CBG","CBGA","CBC","CBL"): cannabinoids[kk]=v
                    else: terpenes[aliases.get(kk,kk.strip().lower().replace(" ","_").replace("-","_"))]=v
                if cannabinoids:o["cannabinoids"]=cannabinoids
                if terpenes:o["terpenes"]=terpenes
                out.append(o)
        else: out.append(base_record(i,image,rec))
    return out
def compare(actual, expected):
    rows=[]
    for i,(a,e) in enumerate(zip(actual,expected)):
        keys=sorted(set(e.keys()))
        for k in keys:
            if k not in a: d="FAIL_MISSING"
            elif a[k]==e[k]: d="PASS"
            else: d="FAIL_VALUE"
            rows.append({"record":i,"field":k,"disposition":d})
    if len(actual)!=len(expected): rows.append({"record":"*","field":"record_count","disposition":"FAIL_VALUE"})
    n=sum(r["disposition"]=="PASS" for r in rows); d=len(rows)
    return rows,n,d,(100.0*n/d if d else 0.0)
if __name__=="__main__":
    actual=transform()
    gt=load("DEMO-GROUND-TRUTH-001.json")["records"]
    rows,n,d,acc=compare(actual,gt)
    pii_leak=any((r.get("customer") not in (None,"[REDACTED]") or r.get("customer_license") not in (None,"[REDACTED]")) for r in actual)
    result={"artifact_id":"REPLAY-RESULT","normalized_records":actual,"field_results":rows,
            "numerator":n,"denominator":d,"accuracy":acc,
            "critical_errors":([] if not pii_leak else ["CRIT-PII-001"])}
    print(canon(result))
