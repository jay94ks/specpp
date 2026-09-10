#!specpp 0.1

# Meta

- name: std/cloud/objectstorage
- version: 0.1.0
- description: 버킷과 키로 접근하는, 크고 공유 가능한 바이너리 객체 저장소에 대한 추상 계약.

# Intent

이미지·빌드 산출물·저장 파일처럼 크기가 크거나 여러 서버·클라이언트가
공유해서 읽어야 하는 바이너리 데이터를 다룰 때 쓴다. 목적은
[`std/io/file.md`](../io/file.md)(로컬 디스크 임의 경로)나
[`std/web/storage.md`](../web/storage.md)(브라우저 오리진 안의 작은
값)와 비슷하게 "데이터를 남기고 다시 읽는다"는 것이지만, **모양이
다르다**: 경로 계층이 아니라 버킷 하나 안의 평평한(flat) 문자열
키(key)로 접근하고, 네트워크 너머의 공유 저장소이며, 여러 클라이언트가
동시에 같은 객체를 읽고 쓸 수 있다.

이 계약 하나로 클라우드 제공자를 바꿔도 참조 코드가 그대로 유지되게
하는 것이 목적이다 — [`std/ui/widgets.md`](../ui/widgets.md)가
Windows/웹 GUI 구현을 추상화하는 것과 같은 패턴이다. 실제 호출은 항상
아래 Constraints가 가리키는 `kind: native` 구현(`std/cloud/aws/`,
`std/cloud/gcp/`, `std/cloud/azure/`) 중 하나로 트랜스파일된다 — 이
파일 자체는 실행 가능한 코드를 생성하지 않는다.

# Domain

## Class: ObjectStorage.ObjectSummary

`listObjects`의 결과 한 항목이다.

멤버:
- key: string
- size: int — 바이트 단위.
- lastModified: DateTime
- eTag: string — 내용이 바뀌면 값도 바뀌는 불투명한 식별자.

## Class: ObjectStorage.Client

생성자:
- ObjectStorage.Client(bucket: string, region: string)
  설명: 접근 키는 인자로 받지 않는다 — 실제로는 환경/워크로드 아이덴티티
  (IAM 역할·서비스 계정 등)에서 읽는다.

메서드:
- putObject(key: string, content: bytes, contentType: string?) -> void
  설명: key가 이미 있으면 덮어쓴다.
- getObject(key: string) -> bytes
  설명: key가 없으면 오류를 낸다.
- exists(key: string) -> boolean
  설명: 본문은 내려받지 않고 존재만 확인한다.
- deleteObject(key: string) -> void
  설명: key가 없어도 오류를 내지 않는다(멱등적).
- listObjects(prefix: string?) -> list<ObjectStorage.ObjectSummary>
- getPresignedUrl(key: string, expiresInSeconds: int) -> string
  설명: 자격 증명 없이도 일정 시간 동안 이 key에 접근할 수 있는 서명된
  URL을 만든다.

# Interface

## Library

`client = ObjectStorage.Client("my-bucket", "ap-northeast-2")`로
클라이언트를 만든 뒤 `putObject`/`getObject`로 객체를 올리고
내려받습니다.

# Constraints

- 실제 구현은 타겟 클라우드 제공자에 따라 다음 중 하나를 고른다 —
  [`std/cloud/aws/s3.md`](aws/s3.md)(AWS S3),
  [`std/cloud/gcp/storage.md`](gcp/storage.md)(GCP Cloud Storage),
  [`std/cloud/azure/blobstorage.md`](azure/blobstorage.md)(Azure Blob
  Storage). 세 구현 모두 이 계약의 메서드 시그니처를 그대로 따르지만,
  버킷/컨테이너 명명 규칙, 권한 모델([`std/cloud/accesscontrol.md`](accesscontrol.md)),
  서명 URL 발급 방식은 실제로는 조금씩 다르다 — 정확한 차이는 각 구현
  파일의 Constraints를 참고한다.
- 이름 바꾸기(rename)에 해당하는 API는 어느 제공자에도 없다 — 바꾸려면
  `getObject` + `putObject`(새 key) + `deleteObject`(옛 key)로 복사 후
  지워야 한다.
- [`std/io/file.md`](../io/file.md)와 달리 경로 계층(디렉터리)이 실제로
  존재하지 않는다 — key에 `/`가 들어 있어도 콘솔에서 폴더처럼 보일
  뿐, 실제로는 평평한 문자열 키 하나다.
- 접근 키를 안전하게 보관할 수 있는 서버/백엔드 환경에서만 써야 한다 —
  브라우저(클라이언트) 코드에 직접 심으면 안 된다. 브라우저에서 직접
  올려야 한다면 서버가 발급한 `getPresignedUrl`을 쓴다.

# Examples

## 예제: 쓰고 다시 읽기

호출 (순서대로): `client.putObject("images/logo.png", pngBytes, "image/png")`,
`client.getObject("images/logo.png")`

기대 동작: 두 번째 호출은 `pngBytes`와 동일한 바이트를 반환한다.

## 예제: 없는 키

호출: `client.getObject("없는/키")`

기대 동작: 오류를 낸다.

# Open Points

- 멀티파트 업로드, 버전 관리, 세밀한 버킷 정책, 수명 주기 규칙은 이
  버전의 범위 밖이다 — 필요하면 실제 구현 파일(`aws/s3.md` 등)을
  직접 참조한다.
- `listObjects`의 페이지네이션(제공자마다 한 번에 반환하는 최대
  개수가 다르다)은 다루지 않는다.
- 정확한 일관성 모델(읽기가 항상 최신 쓰기를 반영하는지)은 제공자마다
  검증이 필요할 수 있다 — 각 구현 파일의 Constraints를 참고한다.
