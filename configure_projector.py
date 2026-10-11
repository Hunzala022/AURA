"""Reproduce the approved same-model projector import. No downloads or activation by default."""
import argparse,hashlib,json
from pathlib import Path
import requests
BASE='http://localhost:11434'
WEIGHTS='5c74c0ede371924357dff0cb6ba145bd67208b9b2389ded681adfff3f7608db7'
PROJECTOR='659b59dd44b73b1cd34af6cc424669484b06dc80f4340adf8ea84ad776eef813'
def create(projector_path):
    path=Path(projector_path)
    with path.open('rb') as f:
        if hashlib.file_digest(f,'sha256').hexdigest()!=PROJECTOR:
            raise ValueError('Unexpected projector checksum; refusing import')
    requests.head(BASE+'/api/blobs/sha256:'+WEIGHTS,timeout=15).raise_for_status()
    with path.open('rb') as f:
        requests.post(BASE+'/api/blobs/sha256:'+PROJECTOR,data=f,timeout=180).raise_for_status()
    r=requests.post(BASE+'/api/create',json={'model':'aura-qwen-vision-candidate','files':{'Qwen_Qwen3.5-4B-Q8_0.gguf':'sha256:'+WEIGHTS,'mmproj-Qwen_Qwen3.5-4B-f16.gguf':'sha256:'+PROJECTOR},'stream':False},timeout=180)
    r.raise_for_status()
    if r.json().get('status')!='success':raise RuntimeError('Candidate import failed')
    print('Candidate created; test image understanding and grounding before explicit activation.')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('projector_path');args=parser.parse_args();create(args.projector_path)
