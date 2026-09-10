#!specpp 0.1

# Meta

- name: std/system/crypto
- version: 0.1.0
- description: 해싱·HMAC·대칭 암호화·암호학적으로 안전한 난수를 위한 수단.

# Intent

비밀번호 저장, 토큰 발급, 데이터 무결성 검증(체크섬), 민감한 데이터
암호화가 필요할 때 쓴다. [`std/system/random.md`](random.md)는 일반
목적 난수만 다루고 암호학적 안전성은 명시적으로 범위 밖이라고
했다(그 파일 Open Points) — 이 패키지의 `SecureRandom`이 그 공백을
채운다.

# Domain

## Class: Hash

[Static]
- sha256(data: bytes) -> bytes
- md5(data: bytes) -> bytes
  설명: 128비트 다이제스트. **보안 목적(비밀번호, 서명, 토큰 등)으로
  쓰지 않는다** — 충돌이 알려진 알고리즘이라 순수 체크섬(다운로드
  무결성 확인 등) 용도로만 쓴다.

결과를 사람이 읽을 문자열로 남기려면
[`std/text/encoding.md`](../text/encoding.md)의 `Hex.encode`/
`Base64.encode`와 조합한다.

## Class: Hmac

메시지 인증 코드(MAC) — 받은 메시지가 key를 아는 쪽에서 왔고 변조되지
않았는지 검증한다.

[Static]
- sign(algorithm: string, key: bytes, data: bytes) -> bytes
  설명: `algorithm`은 `"HMAC-SHA256"` 등.
- verify(algorithm: string, key: bytes, data: bytes, signature: bytes) -> boolean
  설명: **상수 시간 비교**로 구현해야 한다(아래 Constraints) — 타이밍
  공격을 막기 위해서다.

## Class: PasswordHash

비밀번호 저장 전용이다 — `Hash`(SHA-256 등)와 다르다: 일부러 느리게
설계되어 있고, 매번 다른 salt를 자동으로 섞는다.

[Static]
- hash(password: string) -> string
  설명: 내부적으로 매번 새 salt를 생성해 그 salt까지 함께 인코딩된
  문자열 하나로 반환한다(실제로는 bcrypt/scrypt/Argon2 계열).
- verify(password: string, hashedValue: string) -> boolean
  설명: `hash`가 반환한 문자열과 평문 비밀번호를 비교한다.

## Class: SymmetricCipher

[Static]
- encrypt(algorithm: string, key: bytes, plaintext: bytes) -> bytes
  설명: `algorithm`은 `"AES-256-GCM"` 등 — 인증된 암호화(AEAD)를
  권장한다(아래 Constraints). 복호화에 필요한 nonce·인증 태그가
  반환값에 함께 인코딩되어 있다고 전제한다 — 정확한 레이아웃은 구현이
  정한다.
- decrypt(algorithm: string, key: bytes, ciphertext: bytes) -> bytes
  설명: 인증 태그 검증에 실패하면(변조됨) 오류를 낸다 — 복호화된 값을
  조용히 반환하지 않는다.

## Class: SecureRandom

[Static]
- nextBytes(count: int) -> bytes
  설명: [`std/system/random.md`](random.md)의 Open Points가 미뤄둔
  암호학적으로 안전한 난수(CSPRNG)를 채운다 — 토큰, 세션 ID, 암호화
  키 생성에 쓴다. 일반 시뮬레이션·게임 난수에는 여전히
  `std/system/random.md`의 `Random`을 쓴다(속도가 더 중요하고
  예측 불가능성은 필요 없는 경우가 많다).

# Interface

## Library

비밀번호는 `PasswordHash.hash(password)`로 저장하고
`PasswordHash.verify(입력값, 저장된값)`으로 확인합니다. 토큰·API 키는
`SecureRandom.nextBytes(32)`로 만들고
`Base64.encodeUrlSafe(...)`([`std/text/encoding.md`](../text/encoding.md))로
문자열화합니다. 민감한 데이터를 암호화해 저장해야 하면
`SymmetricCipher.encrypt("AES-256-GCM", key, data)`를 씁니다.

# Constraints

- 타겟 언어의 표준/검증된 암호 라이브러리(Python `hashlib`/`hmac`/
  `secrets`/`cryptography`, Node.js `crypto`, Java `javax.crypto`, C#
  `System.Security.Cryptography`, C++ OpenSSL/libsodium 등)에 매핑한다
  — **직접 암호 알고리즘을 구현하지 않는다.**
- `Hmac.verify`는 반드시 상수 시간 비교를 쓴다 — 일반 문자열 `==`
  비교로 구현하면 타이밍 공격에 노출된다(비교에 걸리는 시간 차이로
  올바른 바이트를 한 글자씩 추측당할 수 있다).
- `SymmetricCipher`는 인증된 암호화(AEAD, 예: AES-GCM)를 권장한다 —
  인증 없는 모드(AES-CBC 단독 등)는 패딩 오라클 공격에 취약할 수
  있다.
- 이 패키지가 다루는 키(key) 자체의 안전한 보관·배포는 범위 밖이다 —
  [`std/cloud/secrets.md`](../cloud/secrets.md) 같은 시크릿 저장소와
  조합해 쓴다.

# Examples

## 예제: 비밀번호 해시·검증

호출 (순서대로): `h = PasswordHash.hash("s3cr3t")`,
`PasswordHash.verify("s3cr3t", h)`, `PasswordHash.verify("wrong", h)`

기대 동작: 두 번째 호출은 `true`, 세 번째 호출은 `false`를 반환한다.

## 예제: 변조된 암호문은 복호화 실패

호출: `ciphertext = SymmetricCipher.encrypt("AES-256-GCM", key, data)`한
뒤 `ciphertext`의 마지막 바이트를 하나 바꾸고
`SymmetricCipher.decrypt("AES-256-GCM", key, 변조된ciphertext)`

기대 동작: 오류를 낸다 — 변조를 조용히 통과시키지 않는다.

# Open Points

- 키 유도 함수(KDF)의 파라미터를 직접 제어하는 것(PBKDF2 반복 횟수
  등), 비대칭 암호화(RSA·타원곡선), 디지털 서명은 이 버전의 범위
  밖이다.
