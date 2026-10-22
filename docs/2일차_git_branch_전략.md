## 1조 Git Branch 전략

### 1. Git Flow

- `main`, `develop`, `feature`, `release`, `hotfix` 등의 브랜치를 사용한다.

- 개발, 테스트, 배포 버전을 단계별로 나누어 관리하는 방식이다.

- 규모가 크거나 버전 관리가 필요한 프로젝트에 적합하다.


### 2. GitHub Flow

- `main`을 기준으로 기능별 브랜치를 생성하여 작업한다.

- 기능 개발이 완료되면 `Commit → Push → PR → Review → Merge` 순서로 진행한다.

- 완료된 기능을 검토한 후 `main`에 바로 병합하는 방식이다.


### 3. 우리 팀의 Branch 전략

- 팀원들과 논의한 결과 `GitHub Flow` 방식으로 진행하기로 결정했다.

- 이번 프로젝트는 별도의 배포 버전을 나누어 관리할 필요가 크지 않아 기능별로 브랜치를 생성하여 작업하기로 했다.

- 각자 담당 기능의 브랜치에서 작업한 후 `PR`을 생성하고, 팀원 리뷰 후 `main`에 병합한다.


### 4. Branch 사용 예시

- 회원 조회 : `feature/get-users`

- 회원 생성 : `feature/create-user`

- 회원 수정 : `feature/update-user`

- 회원 삭제 : `feature/delete-user`