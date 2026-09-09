#!specpp 0.1

# Meta

- name: std/collections/collection
- version: 0.1.0
- description: 이 폴더의 자료구조들이 공통으로 만족하는 최소 계약.

# Intent

[`set`](set.md), [`queue`](queue.md), [`stack`](stack.md)이 공통으로 갖는
"담긴 개수를 세고, 비어있는지 확인한다"는 동작을 한 곳에 정의해서 중복을 없앤다.

# Domain

## Interface: Collection<T>

메서드:
- size() -> int
  설명: 담긴 항목 개수를 반환한다.
- isEmpty() -> boolean
  설명: 비어있는지 확인한다.
  절차: `size() == 0`을 반환한다.

# Interface

## Library

이 인터페이스를 직접 쓰기보다, [`set`](set.md)·[`queue`](queue.md)·
[`stack`](stack.md)처럼 이를 `implements`하는 구체 클래스를 씁니다.

# Examples

## 예제: 기본 구현 상속

`Set<T>`가 `size()`만 스스로 구현하면, `implements Collection<T>`를 통해
`isEmpty()`는 따로 적지 않아도 `size() == 0`으로 동작한다.
