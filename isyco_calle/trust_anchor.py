"""Pinned Ed25519 public key for authority-grant verification.

Only the public verifier belongs in the runtime. The corresponding issuer
private key must remain outside the repository and outside calling agents.
Rotating this anchor requires a reviewed application release.
"""

TRUSTED_GRANT_PUBLIC_KEY_PEM = b"""-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAJQKkfUhqdWwq+zJujjqAq2MFAqwj/F3R1W4MTp3Kzwk=
-----END PUBLIC KEY-----
"""
