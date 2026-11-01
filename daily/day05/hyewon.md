2026. 10. 27. 5일차 과제 진행 활동


1. 환자 관리 및 진료기록 API 설계·구현

-> 담당 기능인 환자 삭제 API와 진료기록 등록 API를 설계하고 구현

-> 작업 브랜치에서 작업 후 팀원 피드백을 반영하여 main branch 병합 과정 진행

1) 환자 삭제 API

•
Method / Path: DELETE /practice_api/patients/{patient_id}

•
환자와 연결된 진료기록 및 X-Ray 정보 삭제

•
실제 X-Ray 파일도 함께 정리

•
성공 시 204 No Content, 대상이 없으면 404 반환


2) 진료기록 등록 API

•
Method / Path: POST /practice_api/patients/{patient_id}/medical-records

•
Content-Type: multipart/form-data

•
차트 번호, 증상, JPG·PNG X-Ray 파일 등록

•
DB 오류 발생 시 rollback 및 업로드 파일 삭제


3) 테스트 및 결과

-> Swagger에서 진료기록 등록과 환자 삭제 API를 테스트

-> 정상 등록 시 201, 삭제 성공 시 204 응답 확인

-> 파일 형식 오류, 환자 없음, 필수값 누락 상황의 예외 처리도 확인

