# common_module.py

import json
import os
import data  # data.py의 전역 변수를 사용하기 위해 import

DATA_DIR = 'system_data'

# GPA 계산을 위한 상수
GRADE_TO_SCORE = {
    'A+': 4.5, 'A0': 4.0, 'B+': 3.5, 'B0': 3.0, 'C+': 2.5,
    'C0': 2.0, 'D+': 1.5, 'D0': 1.0, 'F': 0.0, 'P': 0.0, 'NP': 0.0
}
PASS_GRADES = ['P']
FAILED_GRADES = ['F', 'NP']

# 졸업에 필요한 최소 학점 (임의 설정)
MIN_GRADUATION_CREDITS = 130 

# --- 1. 파일 로드 및 저장 기본 함수 ---

def load_data(filename, default_value):
    """지정된 JSON 파일을 로드하거나, 파일이 없거나 오류 발생 시 기본값으로 초기화"""
    filepath = os.path.join(DATA_DIR, filename)
    
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = json.load(f)
            print(f"✔️ {filename} 로드 성공.")
            return content
        except json.JSONDecodeError:
            # 파일 내용이 비어있거나 문법 오류가 있을 경우 처리
            print(f"⚠️ {filename} 로드 실패: JSON 문법 오류 또는 파일 비어있음. 빈 데이터로 초기화합니다.")
            return default_value
        except Exception as e:
            print(f"⚠️ {filename} 로드 중 예상치 못한 오류 발생 ({e}). 빈 데이터로 초기화합니다.")
            return default_value
    else:
        # 파일이 존재하지 않으면 기본값 반환
        return default_value

def save_data(filename, data_to_save):
    """데이터를 JSON 파일에 저장"""
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"데이터 저장 실패: {filename}, 오류: {e}")

# --- 2. 전체 데이터 로드/초기화 및 디렉토리 생성 함수 ---

def load_all_data():
    """모든 데이터 파일을 로드하고, 없으면 빈 파일로 초기화 및 저장"""
    
    # 데이터 폴더가 없으면 생성
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"\n📁 '{DATA_DIR}' 폴더를 새로 생성했습니다.")

    print("\n--- 데이터 로드 시작 ---")

    # 각 변수에 파일 데이터 할당
    data.users = load_data('users.json', {})
    data.students = load_data('students.json', {})
    data.professors = load_data('professors.json', {})
    data.admins = load_data('admins.json', {})
    data.courses = load_data('courses.json', {})
    data.grades = load_data('grades.json', {})
    data.notices = load_data('notices.json', [])  # 리스트로 저장되는 데이터
    data.academic_requests = load_data('academic_requests.json', [])
    data.attendance = load_data('attendance.json', {})

    # 파일이 존재하지 않았거나 오류로 빈 데이터로 초기화된 경우, 저장하여 파일 생성
    save_all_data()
    print("--- 데이터 로드 완료 ---")

# --- 3. 편의를 위한 전체 저장 함수 및 개별 저장 함수 ---

def save_all_data():
    """변경된 모든 데이터를 파일에 저장"""
    save_data('users.json', data.users)
    save_data('students.json', data.students)
    save_data('professors.json', data.professors)
    save_data('admins.json', data.admins)
    save_data('courses.json', data.courses)
    save_data('grades.json', data.grades)
    save_data('notices.json', data.notices)
    save_data('academic_requests.json', data.academic_requests)
    save_data('attendance.json', data.attendance)

# 개별 저장 함수 (성능 최적화 및 안정성 향상을 위해 사용)
def save_users(): save_data('users.json', data.users)
def save_students(): save_data('students.json', data.students)
def save_professors(): save_data('professors.json', data.professors)
def save_admins(): save_data('admins.json', data.admins)
def save_courses(): save_data('courses.json', data.courses)
def save_grades(): save_data('grades.json', data.grades)
def save_notices(): save_data('notices.json', data.notices)
def save_academic_requests(): save_data('academic_requests.json', data.academic_requests)
def save_attendance(): save_data('attendance.json', data.attendance)


# --- 4. 공통 유틸리티 함수 ---

def check_time_conflict(existing_courses, new_course_id):
    """새 강좌의 시간표가 기존 강좌들과 충돌하는지 확인"""
    if new_course_id not in data.courses:
        return False
        
    target_time = data.courses[new_course_id]['time']
    target_day = target_time['day']
    target_start = target_time['start']
    target_end = target_time['end']

    for course_id in existing_courses:
        if course_id in data.courses:
            existing_time = data.courses[course_id]['time']
            exist_day = existing_time['day']
            exist_start = existing_time['start']
            exist_end = existing_time['end']

            # 요일이 같을 때만 시간 비교
            if target_day == exist_day:
                # 시간 충돌 확인: (새 강좌 시작 시각 < 기존 강좌 종료 시각) AND (새 강좌 종료 시각 > 기존 강좌 시작 시각)
                if max(target_start, exist_start) < min(target_end, exist_end):
                    return True  # 충돌 발생
    return False  # 충돌 없음

def calculate_gpa(student_id):
    """학생의 총 평점 평균 및 이수 학점 계산 (GPA 계산용 학점만 반영)"""
    
    if student_id not in data.grades:
        return 0.0, 0
        
    total_score_points = 0.0  # (등급 점수 * 학점)의 합
    total_gpa_credits = 0.0   # GPA 계산에 사용된 학점의 합 (P/NP 제외)
    total_earned_credits = 0.0  # 총 이수 학점 (P 학점 포함)
    
    student_grades = data.grades[student_id]
    
    for course_id, grade in student_grades.items():
        if course_id in data.courses and grade in GRADE_TO_SCORE:
            credits = data.courses[course_id]['credits']
            score = GRADE_TO_SCORE[grade]
            
            # 1. P/NP 과목은 평점 계산에서 제외
            if grade not in PASS_GRADES and grade not in FAILED_GRADES:
                total_score_points += score * credits
                total_gpa_credits += credits
                
            # 2. P 학점 및 평점 계산에 포함된 학점은 이수 학점에 포함 (F/NP는 미포함)
            if grade not in FAILED_GRADES:
                 total_earned_credits += credits

    gpa = total_score_points / total_gpa_credits if total_gpa_credits > 0 else 0.0
    
    # GPA는 소수점 둘째 자리까지 반올림
    return round(gpa, 2), total_earned_credits
