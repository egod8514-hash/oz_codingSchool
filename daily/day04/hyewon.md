2026. 10. 26 4일차 과제 진행 활동

1. User API 설계 및 구현

-> 사용자 요구사항 정의서를 참고하여 신혜원 담당 기능인 비밀번호 변경 API와 회원 탈퇴 API를 구현

-> 작업 브랜치에서 구현 후 팀원 피드백을 반영하여 main branch 병합 과정 진행

1) 비밀번호 변경 API

•
Method / Path: PATCH /api/v1/users/me/password

•
기존 비밀번호 확인

•
새 비밀번호 복잡도 검증

•
새 비밀번호 해싱 후 DB 저장

2) 회원 탈퇴 API

•
Method / Path: DELETE /api/v1/users/me

•
현재 사용자 DB 정보 삭제

•
Refresh Token 쿠키 만료 처리

3) 테스트 및 결과

-> Swagger에서 비밀번호 변경 성공·실패와 회원 탈퇴 API를 테스트

-> 잘못된 비밀번호 입력 시 400, 정상 요청 시 200 응답 확인

