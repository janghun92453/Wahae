# data.py
# 프로그램 실행 중 메모리에 로드될 데이터를 위한 전역 변수 선언
# 실제 데이터는 common_module.py의 load/save 함수를 통해 JSON 파일에서 관리됩니다.

users = {}
students = {}
professors = {}
admins = {}
courses = {}
grades = {} 

# --- 새로 추가된 데이터 ---

# 공지사항 (리스트 형태)
# 예: [ {'id': 'n1', 'title': '서버 점검', 'content': '...', 'author': 'admin1'} ]
notices = []

# 학적 변동 신청 (리스트 형태)
# 예: [ {'req_id': 'r1', 'student_id': 'student1', 'type': '휴학', 'status': 'pending'} ]
academic_requests = []

# 출석부 (딕셔너리 형태)
# 예: { 'course_id': { 'student_id': {'1주차': '출석', '2주차': '결석'} } }
attendance = {}
