#!specpp 0.1

# Meta

- name: std/cloud/gcp/storage
- version: 0.1.0
- description: 버킷과 객체(블롭)로 접근하는 GCP Cloud Storage 실체 명세.
- kind: native

# Intent

이 패키지는 [`std/cloud/objectstorage.md`](../objectstorage.md) 추상
계약의 GCP 구현이다 — 같은 계약의 [AWS 구현](../aws/s3.md)/[Azure
구현](../azure/blobstorage.md)도 참고할 수 있다. 실제 존재하는
서비스이므로 새로 설계할 대상이 아니다(`kind: native`, SPEC.md
1.2절).

# Domain

## Class: GcsStorage.ObjectSummary

멤버:
- key: string — 실제 GCS의 object name.
- size: int
- lastModified: DateTime
- eTag: string

## Class: GcsStorage.Client

생성자:
- GcsStorage.Client(bucket: string, project: string?)

메서드:
- putObject(key: string, content: bytes, contentType: string?) -> void
  설명: 실제 `Blob.upload_from_string`/`upload_from_file`에 대응한다.
- getObject(key: string) -> bytes
  설명: `Blob.download_as_bytes`에 대응한다. 없으면 오류를 낸다.
- exists(key: string) -> boolean
  설명: `Blob.exists()`에 대응한다.
- deleteObject(key: string) -> void
  설명: `Blob.delete()`에 대응한다.
- listObjects(prefix: string?) -> list<GcsStorage.ObjectSummary>
  설명: `Bucket.list_blobs(prefix=...)`에 대응한다.
- getPresignedUrl(key: string, expiresInSeconds: int) -> string
  설명: `Blob.generate_signed_url(expiration=...)`에 대응한다.

# Interface

## Library

`client = GcsStorage.Client("my-bucket", "my-project")`로 클라이언트를
만든 뒤 `putObject`/`getObject`를 씁니다.

# Constraints

- 실제 클라이언트 라이브러리 `google-cloud-storage`(Python
  `google.cloud.storage`, Node.js `@google-cloud/storage` 등)에
  매핑한다.
- GCS는 모든 연산에 대해 강한 일관성을 보장한다(리스트 연산 포함) —
  [`std/cloud/aws/s3.md`](../aws/s3.md)와 같은 지점이다.
- 스토리지 클래스(Standard/Nearline/Coldline/Archive)는 비용·조회
  지연에만 영향을 주고 이 계약의 메서드 시그니처에는 영향을 주지
  않는다.
- 권한은 GCP IAM 역할(예: `roles/storage.objectViewer`)을 버킷·
  프로젝트에 바인딩하는 방식이다 —
  [`std/cloud/gcp/iam.md`](iam.md) 참조. 접근 키를 코드에 직접 넣지
  않는다.

# Examples

## 예제: 쓰고 다시 읽기

호출 (순서대로): `client.putObject("images/logo.png", pngBytes, "image/png")`,
`client.getObject("images/logo.png")`

기대 동작: 두 번째 호출은 `pngBytes`와 동일한 바이트를 반환한다.

# Open Points

- 멀티파트(재개 가능) 업로드, 객체 버전 관리, 수명 주기 규칙은 이
  버전의 범위 밖이다.
