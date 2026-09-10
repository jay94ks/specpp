#!specpp 0.1

# Meta

- name: std/cloud/azure/blobstorage
- version: 0.1.0
- description: 컨테이너와 블롭으로 접근하는 Azure Blob Storage 실체 명세.
- kind: native

# Intent

이 패키지는 [`std/cloud/objectstorage.md`](../objectstorage.md) 추상
계약의 Azure 구현이다 — 같은 계약의 [AWS 구현](../aws/s3.md)/[GCP
구현](../gcp/storage.md)도 참고할 수 있다. 실제 존재하는 서비스이므로
새로 설계할 대상이 아니다(`kind: native`, SPEC.md 1.2절).

# Domain

## Class: BlobStorage.ObjectSummary

멤버:
- key: string — 실제 Azure의 blob name.
- size: int
- lastModified: DateTime
- eTag: string

## Class: BlobStorage.Client

생성자:
- BlobStorage.Client(containerName: string, accountName: string)
  설명: 이 계약의 `bucket`은 Azure의 "컨테이너(container)"에
  대응한다 — 용어가 다르다.

메서드:
- putObject(key: string, content: bytes, contentType: string?) -> void
  설명: 실제 `ContainerClient.upload_blob(name, data, overwrite=True)`에
  대응한다.
- getObject(key: string) -> bytes
  설명: `BlobClient.download_blob().readall()`에 대응한다.
- exists(key: string) -> boolean
- deleteObject(key: string) -> void
  설명: `BlobClient.delete_blob()`에 대응한다.
- listObjects(prefix: string?) -> list<BlobStorage.ObjectSummary>
  설명: `ContainerClient.list_blobs(name_starts_with=prefix)`에
  대응한다.
- getPresignedUrl(key: string, expiresInSeconds: int) -> string
  설명: SAS(Shared Access Signature) 토큰이 붙은 URL을 만든다
  (`generate_blob_sas`에 대응) — AWS/GCP의 서명 URL과 개념은
  같지만, 스토리지 계정 키 또는 사용자 위임 키로 직접 서명한다는
  점이 다르다(아래 Constraints).

# Interface

## Library

`client = BlobStorage.Client("my-container", "myaccount")`로
클라이언트를 만든 뒤 `putObject`/`getObject`를 씁니다.

# Constraints

- 실제 클라이언트 라이브러리 `azure-storage-blob`(Python
  `azure.storage.blob`)에 매핑한다.
- SAS 토큰은 스토리지 계정 키로 직접 서명하거나, 사용자 위임 키
  (Azure AD 신원 기반)로 서명할 수 있다 — 후자가 권장된다(계정 키를
  코드에 두지 않아도 되기 때문이다).
- 권한은 [`std/cloud/azure/rbac.md`](rbac.md)의 역할 할당(예:
  `"Storage Blob Data Reader"`)으로도, 컨테이너 접근 정책으로도 걸 수
  있다 — RBAC 쪽이 최신 권장 방식이다.
- 모든 연산이 강한 일관성을 갖는다 —
  [`std/cloud/aws/s3.md`](../aws/s3.md)/[`std/cloud/gcp/storage.md`](../gcp/storage.md)와
  같은 지점이다.

# Examples

## 예제: 쓰고 다시 읽기

호출 (순서대로): `client.putObject("images/logo.png", pngBytes, "image/png")`,
`client.getObject("images/logo.png")`

기대 동작: 두 번째 호출은 `pngBytes`와 동일한 바이트를 반환한다.

# Open Points

- 블록 블롭 이외의 블롭 타입(Append/Page Blob), 라이프사이클 관리
  정책, 계층(Hot/Cool/Archive) 관리는 이 버전의 범위 밖이다.
