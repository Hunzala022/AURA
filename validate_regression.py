"""Reproducible regression evidence; opt-in real local Chromium fixtures."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
def source_fingerprint():
    root=Path(__file__).resolve().parent
    paths=sorted([*root.glob('core/*.py'),*root.glob('agents/*.py'),*root.glob('tests/*.py')])
    return {str(p.relative_to(root)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
if __name__=='__main__':
    root=Path(__file__).resolve().parent
    result=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s','tests','-v'],cwd=root,capture_output=True,text=True)
    report={'command':'python -B -m unittest discover -s tests -v','browser_opt_in':os.environ.get('AURA_BROWSER_TEST')=='1','exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'source_sha256':source_fingerprint()}
    (root/'reports').mkdir(exist_ok=True)
    (root/'reports/regression.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(result.stdout);print(result.stderr);raise SystemExit(result.returncode)
