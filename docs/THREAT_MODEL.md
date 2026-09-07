# Threat Model & STRIDE Security Analysis

## 1. STRIDE Analysis & Mitigations

| Threat Category | Potential Attack Vector | LocalCompute Commons Mitigation |
| :--- | :--- | :--- |
| **Spoofing** | Rogue node joins cluster claiming high GPU capabilities | Rotating JWT worker node tokens signed with HMAC-SHA256. Mutual handshake registration. |
| **Tampering** | Man-in-the-middle modifies inference outputs or audit records | Output payload SHA-256 checksums and HMAC task signatures. Cryptographically chained audit event hashes. |
| **Repudiation** | Operator denies revoking a node or cancelling jobs | All critical operations generate immutable `AuditEventDB` records with actor ID, timestamp, and hash proofs. |
| **Information Disclosure** | Untrusted worker reads confidential documents | Strict privacy classes (`local_only` vs `trusted_nodes`) with pre-dispatch metadata redaction. |
| **Denial of Service** | Rogue task floods node memory with infinite input strings | Maximum document input bounds (500,000 chars) and strict inference timeouts (60s). |
| **Elevation of Privilege** | LLM agent or MCP client invokes node revocation directly | Administrative operations are hard-gated by the `ApprovalEngine` requiring explicit human authorization. |

---

## 2. Prompt Injection & Jailbreak Defenses

LocalCompute Commons neutralizes special LLM delimiters (e.g. `<|im_start|>`, `<|im_end|>`) and scans incoming task descriptions using heuristic regular expression classifiers before passing inputs to Ollama.
