import json,hashlib,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent
def H(p): return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((R/"DEMO-EVIDENCE-001.json").read_text())
fail=[]
for a in m["artifacts"]:
    p=R/a["name"]
    if not p.exists() or H(p)!=a["sha256"]: fail.append("HASH:"+a["name"])
if not fail:
    cp=subprocess.run([sys.executable,str(R/"benchmark_runner.py")],capture_output=True,text=True)
    if cp.returncode: fail.append("RUNNER")
    else:
        x=json.loads(cp.stdout); b=json.loads((R/"DEMO-BENCHMARK-REPORT-001.json").read_text())
        n=json.loads((R/"DEMO-NORMALIZED-001.json").read_text())
        if x["normalized_records"]!=n: fail.append("NORMALIZED_OUTPUT")
        for k in ("numerator","denominator","accuracy","critical_errors","field_results"):
            if x[k]!=b[k]: fail.append("BENCHMARK:"+k)
result={"artifact_id":"DEMO-INDEPENDENT-VERIFICATION-001","status":"PASS" if not fail else "FAIL",
        "failures":fail,"manifest_signature_status":m["signature_status"],
        "note":"PASS verifies hash integrity and exact deterministic replay. Cryptographic signer verification is NOT performed while manifest is UNSIGNED."}
(R/"DEMO-INDEPENDENT-VERIFICATION-001.json").write_text(json.dumps(result,sort_keys=True,separators=(",",":"))+"\n")
print(json.dumps(result,indent=2))
