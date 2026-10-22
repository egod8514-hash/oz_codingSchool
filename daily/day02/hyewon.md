### 2026_1022_Activity-Log

- 과제 진행 활동 
  
#### 1. Git & Github Flow Branch 전략에 대해서 공부해보기

-> 디스 코드에서 논의 후 github flow 방식으로 진행하자 합의 후 팀장님이 정리하여 docs/2일차_git_branch_전략.md 파일을 생성 후 main branch에 push 

-> 개별 정리 내역 : 개별 개인 브랜치(hyewon)에서 docs에 관련 내용 2일차_개별 정리_Git branch 전략 관련 정리.md 로 commit( 개별 정리 내역은 main에 PR은 하지 않음)
   


#### 2. 브랜치 전략을 통해 작업 내용 병합해보기

-> FastAPI를 활용하여 회원 정보 조회-추가-수정- 삭제 API 구현을 하라는 요구사항에 따라 분담하여 API를 모두 작성하고 Git branch 전략에 따라 병합과정을 진행

: feature/get-users(조희) feature/create-user(추가) feature/update-user(수정) feature/delete-user(삭제) 중 삭제 부분 브랜치에서 구현 후 main에 PR

-> 이를 팀원들 피드백 받아 수정할 부분 수정하였고 팀장님이 merge

#### 1) 회원 정보 삭제 API 주요 구현 사안

- **기능**: 특정 회원의 데이터 삭제
- **Method / Path**: `DELETE` `/users/{user_id}`
- **Path Parameter**: 
  - `user_id` (int): 삭제할 회원의 고유 식별자

#### 2) 처리 흐름
1. 회원 목록(`user_list`) 전체 순회 및 `user_id` 일치 여부 확인
2. 일치하는 회원 존재 시: 리스트에서 해당 데이터 삭제 후 성공 메시지 반환
3. 일치하는 회원 부재 시: HTTP 404 (Not Found) 예외 발생

#### 3) 응답 예시

**성공 (200 OK)**
```json
{
    "message": "ID {user_id}번 회원의 모든 정보를 삭제했습니다."
}
```

**실패 (404 Not Found)**
```json
{
    "detail": "해당 회원을 찾을 수 없습니다."
}
```

#### 4) 팀원들의 피드백 반영 사항 

• global 키워드 제거: 리스트의 요소를 제거할 때는 객체 재할당이 일어나지 않으므로 불필요한 global 선언을 삭제
• 구문 오류(SyntaxError) 수정: 코드 작성시 마지막 단의 중복 코드와 HTTPException 하단의 중복 닫는 괄호 오타를 제거
• 상태 코드 지정 방식 통일: status 라이브러리 의존성 문제를 해결하기 위해, 팀원들과 합의된 status_code=404 명시 방식으로 코드를 수정
