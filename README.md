# Matrix-Diagonalization-Cipher
Overview
This project implements a novel symmetric-key cipher that operates on square matrices of reversed-ASCII values rather than on raw bytes. The encryption key is derived from the eigendecomposition (or Schur triangularization) of the message matrix itself.
The method is described in the accompanying paper:

"Méthode de Chiffrement avec Diagonalisation Matricielle" — Ali Derouiche
EPI Digital School · Cybersecurity Engineering


How It Works
Plain text
    │
    ▼  reversed-ASCII encoding
Message matrix  M  (n × n)
    │
    ▼  eigendecomposition (or Schur)
    A  =  P · D · P⁻¹        (diagonalizable case)
    A  =  P · T · P⁻¹        (Schur fallback)
    │
    ▼  encryption
Ciphertext  C  =  A · M
Key Structure
ComponentRolePPublic key (eigenvector matrix)D or TPublic key (diagonal or upper-triangular eigenvalue matrix)P⁻¹Private key (used only for decryption)
Decryption
M  =  A⁻¹ · C   where  A⁻¹ = P · (D or T)⁻¹ · P⁻¹

Quick Start
1. Clone the repository
bashgit clone https://github.com/<your-username>/matrix-diagonalization-cipher.git
cd matrix-diagonalization-cipher
2. Install dependencies
bashpip install numpy
3. Run
bashpython matrix_cipher.py
Enter a message to encrypt: episousse
────────────────────────────────────────────────────
  Encryption method : diagonalization
  Original message  : episousse
  Padded message    : episousse  (size 3×3)
────────────────────────────────────────────────────
  Message matrix M:
  [[101 211 501]
   [511 111 711]
   [511 511 101]]

  Ciphertext matrix C = A·M:
  ...
────────────────────────────────────────────────────
  Decrypted message : episousse
────────────────────────────────────────────────────
4. Use as a library
pythonfrom matrix_cipher import cipher_pipeline

result = cipher_pipeline("hello", verbose=False)
print(result["method"])       # "diagonalization" or "triangularization (Schur)"
print(result["ciphertext"])   # numpy array — the encrypted matrix
print(result["decrypted"])    # "hello"

Project Structure
matrix-diagonalization-cipher/
├── matrix_cipher.py   # Full implementation
├── README.md          # This file
└── LICENSE            # MIT License

Security Analysis
Strengths

Asymmetric structure — encryption and decryption keys are mathematically distinct.
Double transformation — digit-reversal of ASCII codes obscures the raw character encoding.
Matrix complexity — recovering P and D from A alone requires solving the full eigenvalue problem.

Known Limitations

⚠️ This cipher is experimental and not production-ready.

LimitationDetailMatrix sizeLarge messages produce large matrices, increasing time and memory usage.Floating-point errorsEigendecomposition accumulates rounding errors for ill-conditioned matrices.No padding randomnessIdentical messages always produce identical ciphertexts (deterministic).Key derivationKeys are derived directly from the plaintext — a structural weakness.Not peer-reviewedThe security assumptions have not been formally proven.

Possible Extensions

🔒 Random salt matrix — XOR or multiply by a random matrix before decomposition to break determinism.
🔁 Iterated rounds — apply the cipher multiple times with different key matrices.
🧮 Post-quantum hardening — replace the matrix basis with a lattice structure (e.g., NTRU-style).
⚡ Block parallelism — process independent matrix blocks concurrently.
🗜️ Pre-compression — compress the plaintext before encryption to reduce matrix size.


Requirements
PackageVersionPython≥ 3.10NumPy≥ 1.24

Author
Ali Derouiche
Computer Engineering Student — Cybersecurity Track
