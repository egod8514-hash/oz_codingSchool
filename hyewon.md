### 2026_1021_Activity-Log

   - 개인 과제 및 활동 : 
   Git clone 으로 프로젝트 시작 템플릿 가져오기 /git remote 추가하기 완료
   /매일 활동 내역 md 파일로 작성해 공유
   
   - 팀 과제 : 팀장 선정 (안주형님) 후 팀장의 원격 레포지토리 생성 후 Repository Collaborators로 초대받음 / 프로젝트 진행시 팀원간 지켜야 할 규칙 논의하여 만들어 md 파일로 공유


### 2026_1022_Activity-Log

- 과제 진행 활동 
  
1. Git & Github Flow Branch 전략에 대해서 공부해보기

-> 디스 코드에서 논의 후 github flow 방식으로 진행하자 합의 후 팀장님이 정리하여 docs/2일차_git_branch_전략.md 파일을 생성 후 main branch에 push 

-> 개별 정리 내역 : 개별 개인 브랜치(hyewon)에서 docs에 관련 내용 docs/2일차_git_branch_전략.md 파일로 정리하여 commit(PR은 하지 않음)
   


2. 브랜치 전략을 통해 작업 내용 병합해보기

-> FastAPI를 활용하여 회원 정보 조회-추가-수정- 삭제 API 구현을 하라는 요구사항에 따라 분담하여 API를 모두 작성하고 Git branch 전략에 따라 병합과정을 진행

: feature/get-users(조희) feature/create-user(추가) feature/update-user(수정) feature/delete-user(삭제) 중 삭제 부분 브랜치에서 구현 후 PR

-> 이를 팀원들 피드백 받아 수정할 부분 수정하였고 팀장님이 merge

**  주요 구현 사항

• 회원 검색 및 삭제: user_list에서 요청받은 user_id를 조회한 후, 리스트의 .pop() 메서드를 사용하여 해당 회원 정보 삭제하도록 구현
• 예외 처리 (404 Error): 존재하지 않는 회원 ID가 인입될 경우, 기존 조회 API와 규격을 맞춰 404 상태 코드와 함께 "해당 회원을 찾을 수 없습니다." 메시지로 응답

** 팀원들의 피드백 반영 사항 

• global 키워드 제거: 리스트의 요소를 제거할 때는 객체 재할당이 일어나지 않으므로 불필요한 global 선언을 삭제
• 구문 오류(SyntaxError) 수정: 코드 작성시 마지막 단의 중복 코드와 HTTPException 하단의 중복 닫는 괄호 오타를 제거
• 상태 코드 지정 방식 통일: status 라이브러리 의존성 문제를 해결하기 위해, 팀원들과 합의된 status_code=404 명시 방식으로 코드를 수정했습니다
