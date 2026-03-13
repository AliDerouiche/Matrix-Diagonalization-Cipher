"""
Matrix Diagonalization Cipher
==============================
An experimental asymmetric encryption scheme based on matrix diagonalization
and inverted ASCII representation of characters.

Author : Ali Derouiche
Paper  : "Méthode de Chiffrement avec Diagonalisation Matricielle"
"""

import numpy as np


# ──────────────────────────────────────────────
#  Core helpers
# ──────────────────────────────────────────────

def reversed_ascii(c: str) -> int:
    """Return the digit-reversed ASCII code of character *c*.

    Example: 'm' → ord('m') = 109 → reversed = 901
    """
    return int(str(ord(c))[::-1])


def pad_message(msg: str) -> tuple[str, int]:
    """Pad *msg* with its last character until its length equals n² for the
    smallest integer n such that n² >= len(msg).

    Returns
    -------
    (padded_message, n)
    """
    length = len(msg)
    n = 1
    while n * n < length:
        n += 1
    pad_length = n * n - length
    padded_msg = msg + msg[-1] * pad_length
    return padded_msg, n


# ──────────────────────────────────────────────
#  Matrix construction
# ──────────────────────────────────────────────

def construct_matrix_from_message(msg: str) -> tuple[np.ndarray, str, int]:
    """Convert a text message into an n×n matrix of inverted ASCII values.

    Returns
    -------
    (matrix_A, padded_message, n)
    """
    padded_msg, n = pad_message(msg)
    reversed_ascii_vals = [reversed_ascii(c) for c in padded_msg]
    matrix = np.array(reversed_ascii_vals).reshape((n, n))
    return matrix, padded_msg, n


def inverse_or_regularize(matrix: np.ndarray, epsilon: float = 1e-3) -> np.ndarray:
    """Return *matrix* as-is if invertible, or add εI to make it invertible."""
    det = np.linalg.det(matrix)
    if abs(det) < 1e-6:
        matrix = matrix + epsilon * np.eye(matrix.shape[0])
    return matrix


# ──────────────────────────────────────────────
#  Decomposition
# ──────────────────────────────────────────────

def diagonalize_or_triangulate(
    matrix: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, str]:
    """Attempt eigendecomposition; fall back to Schur triangularization.

    Returns
    -------
    (T_or_D, P, P_inv, method_name)
      - If diagonalizable : D  (diagonal eigenvalue matrix), P, P⁻¹
      - Otherwise         : T  (upper-triangular Schur form),  P, P⁻¹
    """
    try:
        eigvals, P = np.linalg.eig(matrix)
        if np.linalg.matrix_rank(P) == matrix.shape[0]:
            D = np.diag(eigvals)
            P_inv = np.linalg.inv(P)
            return D, P, P_inv, "diagonalization"
        raise np.linalg.LinAlgError("Matrix not diagonalizable")
    except Exception:
        T, P = np.linalg.schur(matrix)
        P_inv = np.linalg.inv(P)
        return T, P, P_inv, "triangularization (Schur)"


# ──────────────────────────────────────────────
#  Encryption / Decryption
# ──────────────────────────────────────────────

def encrypt_message(A: np.ndarray, msg_matrix: np.ndarray) -> np.ndarray:
    """Encrypt message matrix *M* as C = A · M."""
    return A @ msg_matrix


def decrypt_message(A: np.ndarray, encrypted_matrix: np.ndarray) -> np.ndarray:
    """Decrypt ciphertext matrix *C* as M = A⁻¹ · C."""
    inv_A = np.linalg.inv(A)
    msg_matrix = inv_A @ encrypted_matrix
    return np.round(msg_matrix).astype(int)


# ──────────────────────────────────────────────
#  Decoding
# ──────────────────────────────────────────────

def decode_reversed_ascii_matrix(matrix: np.ndarray, original_length: int) -> str:
    """Convert a matrix of inverted-ASCII integers back to a readable string."""
    ascii_reverse = {int(str(i)[::-1]): chr(i) for i in range(32, 127)}
    flat = matrix.flatten()[:original_length]
    return "".join(ascii_reverse.get(int(val), "?") for val in flat)


# ──────────────────────────────────────────────
#  Main pipeline
# ──────────────────────────────────────────────

def cipher_pipeline(message: str, verbose: bool = True) -> dict:
    """Run the full encrypt-then-decrypt pipeline on *message*.

    Parameters
    ----------
    message : str   Plain-text input (non-empty).
    verbose : bool  Print step-by-step details when True.

    Returns
    -------
    dict with keys: ciphertext, decrypted, method, P, T_or_D, P_inv
    """
    if not message:
        raise ValueError("Message must not be empty.")

    # 1. Build matrix A from the message
    A, padded_msg, n = construct_matrix_from_message(message)
    A = inverse_or_regularize(A)

    # 2. Decompose A = P · (T or D) · P⁻¹
    T_or_D, P, P_inv, method = diagonalize_or_triangulate(A)

    # 3. Reconstruct A from decomposition (numerical sanity check)
    full_matrix = P @ T_or_D @ P_inv

    # 4. Build message matrix M
    msg_matrix = np.array([reversed_ascii(c) for c in padded_msg]).reshape((n, n))

    # 5. Encrypt
    cipher = encrypt_message(full_matrix, msg_matrix)

    # 6. Decrypt
    decrypted_matrix = decrypt_message(full_matrix, cipher)
    decoded = decode_reversed_ascii_matrix(decrypted_matrix, len(message))

    if verbose:
        sep = "─" * 52
        print(sep)
        print(f"  Encryption method : {method}")
        print(f"  Original message  : {message}")
        print(f"  Padded message    : {padded_msg}  (size {n}×{n})")
        print(sep)
        print("  Message matrix M:")
        print(msg_matrix)
        print("\n  Ciphertext matrix C = A·M:")
        print(np.round(cipher).astype(int))
        print("\n  Keys — Public (P, T/D) | Private (P⁻¹):")
        print("  P =\n", np.round(P, 4))
        print("  T/D =\n", np.round(T_or_D, 4))
        print("  P⁻¹ =\n", np.round(P_inv, 4))
        print(sep)
        print(f"  Decrypted message : {decoded}")
        print(sep)

    return {
        "method":   method,
        "ciphertext": np.round(cipher).astype(int),
        "decrypted":  decoded,
        "P":        P,
        "T_or_D":   T_or_D,
        "P_inv":    P_inv,
    }


# ──────────────────────────────────────────────
#  Entry point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    msg = input("Enter a message to encrypt: ").strip()
    cipher_pipeline(msg)
