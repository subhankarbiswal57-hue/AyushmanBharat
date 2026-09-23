# Security, Privacy & Consent Architecture

## Data Security Policies
1. **Encryption-in-Transit**: Mandatory TLS 1.3 for all microservice communication.
2. **Encryption-at-Rest**: AES-256 encryption across persistent database storage and health record attachments.
3. **Password Hashing**: Bcrypt with minimum work factor of 12.
4. **Token Security**: PyJWT signed with asymmetric RS256/HMAC SHA-256 keys with 15-minute expiration and rotating refresh tokens.

## Tamper-Evident Audit Ledger
All clinical reads and mutations append an immutable record to the audit service. Each entry computes a SHA-256 checksum incorporating the previous entry's hash, preventing retroactive tampering with audit trails.
