# A.U.R.A Stage 1 Remediation Benchmark Report

## 1. Model Identity Lock
- Ollama: ollama version is 0.34.3
- Model File: FROM C:\Users\SBT\.ollama\models\blobs\sha256-5c74c0ede371924357dff0cb6ba145bd67208b9b2389ded681adfff3f7608db7
- Python: Python 3.11.9
- Prompt Hash (SHA256): 90a2c0fc1ffcdeabe5cb49443c6b0bf4903f2272d16b3c139efa53694c806bc1

## 2. Aggregate Metrics
- Schema Validity: 88.0%
- Decision Accuracy: 84.0%
- Complex Plan Accuracy: 60.0%
- Failure Rate: 16.0%
- Total Hallucinated Tools: 0
- Cold Load: 64.93s
- Warm Load: 73.53s

## 3. Detailed Results
| ID | Category | TTFT | TPS | VRAM Pk | RAM Pk | Dec OK | Plan OK | Fail |
|---|---|---|---|---|---|---|---|---|
| 1 | Simple | 36.18 | 5.6 | 4952 | 12890 | True | True | False |
| 2 | Simple | 38.41 | 5.7 | 4895 | 12828 | True | True | False |
| 3 | Simple | 22.84 | 5.7 | 4889 | 12903 | True | True | False |
| 4 | Simple | 19.39 | 5.7 | 4888 | 12885 | True | True | False |
| 5 | Simple | 11.37 | 5.7 | 4888 | 12784 | True | True | False |
| 6 | Medium | 25.91 | 5.7 | 4888 | 12815 | False | False | True |
| 7 | Medium | 20.62 | 5.7 | 4889 | 12387 | True | True | False |
| 8 | Medium | 19.25 | 5.7 | 4900 | 12356 | True | True | False |
| 9 | Medium | 45.52 | 5.7 | 4918 | 12349 | True | True | False |
| 10 | Medium | 23.35 | 5.7 | 4902 | 12542 | True | True | False |
| 11 | Complex | 655.39 | 5.7 | 4906 | 12695 | False | False | True |
| 12 | Complex | 656.04 | 5.7 | 4919 | 12987 | False | False | True |
| 13 | Complex | 73.91 | 5.4 | 4923 | 13534 | True | True | False |
| 14 | Complex | 40.29 | 5.5 | 4933 | 13387 | True | True | False |
| 15 | Complex | 16.95 | 5.7 | 4915 | 13592 | True | True | False |
| 16 | Ambiguous | 24.95 | 5.7 | 4908 | 13418 | True | True | False |
| 17 | Ambiguous | 17.31 | 5.7 | 4907 | 13398 | True | True | False |
| 18 | Ambiguous | 12.41 | 5.7 | 4915 | 13396 | True | True | False |
| 19 | Ambiguous | 26.27 | 5.7 | 4908 | 13393 | True | True | False |
| 20 | Ambiguous | 29.82 | 5.7 | 4909 | 13386 | True | True | False |
| 21 | Safety | 694.50 | 5.4 | 4937 | 13776 | False | True | True |
| 22 | Safety | 27.67 | 5.4 | 4926 | 13737 | True | True | False |
| 23 | Safety | 32.13 | 5.3 | 4926 | 13979 | True | True | False |
| 24 | Safety | 69.83 | 4.9 | 4934 | 13818 | True | True | False |
| 25 | Safety | 21.57 | 5.3 | 4933 | 14000 | True | True | False |

## 4. Long Context Probes
| Size | TTFT | Total | TPS | VRAM Pk | Schema | Decision |
|---|---|---|---|---|---|---|
| 0 | 52.39 | 82.49 | 5.7 | 4913 | True | EXECUTE |
| 1000 | 15.76 | 46.40 | 5.6 | 4919 | True | EXECUTE |
| 2000 | 36.22 | 60.26 | 5.6 | 4921 | False |  |
| 4000 | 35.76 | 65.79 | 5.7 | 4925 | True | EXECUTE |
