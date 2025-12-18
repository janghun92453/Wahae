# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import data
import common_module as common
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'  # 프로덕션에서는 변경 필요

# 데이터 로드
common.load_all_data()

# 로그인 체크 데코레이터
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('로그인이 필요합니다.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 역할 체크 데코레이터
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('로그인이 필요합니다.', 'warning')
                return redirect(url_for('login'))
            if session.get('role') != role:
                flash('접근 권한이 없습니다.', 'danger')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ===== 공통 라우트 =====

@app.route('/')
def index():
    if 'user_id' in session:
        role = session.get('role')
        if role == 'student':
            return redirect(url_for('student_dashboard'))
        elif role == 'professor':
            return redirect(url_for('professor_dashboard'))
        elif role == 'admin':
            return redirect(url_for('admin_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        
        if user_id not in data.users:
            flash('존재하지 않는 사용자 ID입니다.', 'danger')
            return redirect(url_for('login'))
        
        user_info = data.users[user_id]
        
        if user_info['password'] != password:
            flash('비밀번호가 일치하지 않습니다.', 'danger')
            return redirect(url_for('login'))
        
        # 로그인 성공
        session['user_id'] = user_id
        session['role'] = user_info['role']
        
        # 이름 가져오기
        if user_info['role'] == 'student':
            session['name'] = data.students[user_id]['name']
        elif user_info['role'] == 'professor':
            session['name'] = data.professors[user_id]['name']
        elif user_info['role'] == 'admin':
            session['name'] = data.admins[user_id]['name']
        
        flash(f'{session["name"]}님 환영합니다!', 'success')
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('login'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        user_id = session['user_id']
        
        if data.users[user_id]['password'] != current_password:
            flash('현재 비밀번호가 일치하지 않습니다.', 'danger')
            return redirect(url_for('change_password'))
        
        if new_password != confirm_password:
            flash('새 비밀번호가 일치하지 않습니다.', 'danger')
            return redirect(url_for('change_password'))
        
        if not new_password:
            flash('비밀번호는 비워둘 수 없습니다.', 'danger')
            return redirect(url_for('change_password'))
        
        data.users[user_id]['password'] = new_password
        common.save_users()
        flash('비밀번호가 성공적으로 변경되었습니다.', 'success')
        return redirect(url_for('index'))
    
    return render_template('change_password.html')

@app.route('/notices')
@login_required
def notices():
    return render_template('notices.html', notices=sorted(data.notices, key=lambda x: x['id'], reverse=True))

# ===== 학생 라우트 =====

@app.route('/student/dashboard')
@role_required('student')
def student_dashboard():
    user_id = session['user_id']
    student = data.students[user_id]
    gpa, earned_credits = common.calculate_gpa(user_id)
    
    return render_template('student/dashboard.html', 
                         student=student,
                         gpa=gpa,
                         earned_credits=earned_credits)

@app.route('/student/register', methods=['GET', 'POST'])
@role_required('student')
def student_register():
    user_id = session['user_id']
    student = data.students[user_id]
    
    if request.method == 'POST':
        course_id = request.form.get('course_id').upper()
        
        if course_id not in data.courses:
            flash('존재하지 않는 과목 코드입니다.', 'danger')
        elif course_id in student['courses']:
            flash('이미 수강 중인 과목입니다.', 'warning')
        elif len(data.courses[course_id]['student_user_ids']) >= data.courses[course_id].get('max_capacity', float('inf')):
            flash('수강 인원이 마감되었습니다.', 'warning')
        elif common.check_time_conflict(student['courses'], course_id):
            flash('시간표가 겹쳐 수강 신청할 수 없습니다.', 'warning')
        else:
            student['courses'].append(course_id)
            data.courses[course_id]['student_user_ids'].append(user_id)
            common.save_students()
            common.save_courses()
            flash(f'{data.courses[course_id]["title"]} 과목 수강 신청이 완료되었습니다.', 'success')
            return redirect(url_for('student_register'))
    
    # 수강 가능한 강좌 목록
    available_courses = []
    for cid, course in data.courses.items():
        prof_name = data.professors.get(course['professor_user_id'], {}).get('name', 'N/A')
        current_count = len(course['student_user_ids'])
        max_cap = course.get('max_capacity', 'N/A')
        time_info = course.get('time', {})
        time_str = f"{time_info.get('day', 'N/A')} {time_info.get('start', '')}-{time_info.get('end', '')}"
        
        available_courses.append({
            'id': cid,
            'title': course['title'],
            'professor': prof_name,
            'credits': course.get('credits', 0),
            'time': time_str,
            'current': current_count,
            'max': max_cap,
            'enrolled': cid in student['courses']
        })
    
    return render_template('student/register.html', courses=available_courses)

@app.route('/student/drop/<course_id>', methods=['POST'])
@role_required('student')
def student_drop(course_id):
    user_id = session['user_id']
    student = data.students[user_id]
    
    if course_id not in student['courses']:
        flash('수강 중인 과목이 아닙니다.', 'danger')
    else:
        course = data.courses.get(course_id)
        student['courses'].remove(course_id)
        if course and user_id in course['student_user_ids']:
            course['student_user_ids'].remove(user_id)
        
        common.save_students()
        common.save_courses()
        flash(f'{course["title"] if course else ""} 과목 수강 취소가 완료되었습니다.', 'success')
    
    return redirect(url_for('student_timetable'))

@app.route('/student/timetable')
@role_required('student')
def student_timetable():
    user_id = session['user_id']
    student = data.students[user_id]
    
    my_courses = []
    for cid in student['courses']:
        course = data.courses.get(cid)
        if course:
            prof_name = data.professors.get(course['professor_user_id'], {}).get('name', 'N/A')
            time_info = course.get('time', {})
            time_str = f"{time_info.get('day', 'N/A')} {time_info.get('start', '')}-{time_info.get('end', '')}"
            
            my_courses.append({
                'id': cid,
                'title': course['title'],
                'professor': prof_name,
                'credits': course.get('credits', 0),
                'time': time_str
            })
    
    return render_template('student/timetable.html', courses=my_courses)

@app.route('/student/grades')
@role_required('student')
def student_grades():
    user_id = session['user_id']
    my_grades = data.grades.get(user_id, {})
    
    grade_list = []
    for course_id, grade in my_grades.items():
        course = data.courses.get(course_id)
        if course:
            grade_list.append({
                'id': course_id,
                'title': course['title'],
                'credits': course.get('credits', 0),
                'grade': grade,
                'score': common.GRADE_TO_SCORE.get(grade, 0.0)
            })
    
    gpa, earned_credits = common.calculate_gpa(user_id)
    
    return render_template('student/grades.html', 
                         grades=grade_list,
                         gpa=gpa,
                         earned_credits=earned_credits)

# ===== 교수 라우트 =====

@app.route('/professor/dashboard')
@role_required('professor')
def professor_dashboard():
    user_id = session['user_id']
    professor = data.professors[user_id]
    
    my_courses = []
    for cid in professor['courses_taught']:
        course = data.courses.get(cid)
        if course:
            student_count = len(course['student_user_ids'])
            my_courses.append({
                'id': cid,
                'title': course['title'],
                'credits': course.get('credits', 0),
                'students': student_count
            })
    
    return render_template('professor/dashboard.html', 
                         professor=professor,
                         courses=my_courses)

@app.route('/professor/courses')
@role_required('professor')
def professor_courses():
    user_id = session['user_id']
    professor = data.professors[user_id]
    
    my_courses = []
    for cid in professor['courses_taught']:
        course = data.courses.get(cid)
        if course:
            student_count = len(course['student_user_ids'])
            time_info = course.get('time', {})
            time_str = f"{time_info.get('day', 'N/A')} {time_info.get('start', '')}-{time_info.get('end', '')}"
            
            my_courses.append({
                'id': cid,
                'title': course['title'],
                'credits': course.get('credits', 0),
                'time': time_str,
                'students': student_count,
                'syllabus': course.get('syllabus', '등록된 강의 계획서가 없습니다.')
            })
    
    return render_template('professor/courses.html', courses=my_courses)

@app.route('/professor/course/<course_id>/students')
@role_required('professor')
def professor_course_students(course_id):
    user_id = session['user_id']
    professor = data.professors[user_id]
    
    if course_id not in professor['courses_taught']:
        flash('담당하고 있는 과목이 아닙니다.', 'danger')
        return redirect(url_for('professor_courses'))
    
    course = data.courses[course_id]
    students = []
    for sid in course['student_user_ids']:
        student = data.students.get(sid)
        if student:
            students.append({
                'id': sid,
                'student_id': student['student_id'],
                'name': student['name'],
                'major': student['major'],
                'status': student.get('status', 'N/A')
            })
    
    return render_template('professor/students.html', 
                         course=course,
                         course_id=course_id,
                         students=students)

@app.route('/professor/grades', methods=['GET', 'POST'])
@role_required('professor')
def professor_grades():
    user_id = session['user_id']
    professor = data.professors[user_id]
    
    if request.method == 'POST':
        course_id = request.form.get('course_id')
        
        if course_id not in professor['courses_taught']:
            flash('담당하고 있는 과목이 아닙니다.', 'danger')
            return redirect(url_for('professor_grades'))
        
        course = data.courses[course_id]
        grades_changed = False
        
        for sid in course['student_user_ids']:
            grade = request.form.get(f'grade_{sid}', '').upper()
            if grade and grade in common.GRADE_TO_SCORE:
                if sid not in data.grades:
                    data.grades[sid] = {}
                data.grades[sid][course_id] = grade
                grades_changed = True
        
        if grades_changed:
            common.save_grades()
            flash('성적이 저장되었습니다.', 'success')
        
        return redirect(url_for('professor_grades'))
    
    # GET 요청
    course_id = request.args.get('course_id')
    
    my_courses = []
    for cid in professor['courses_taught']:
        course = data.courses.get(cid)
        if course:
            my_courses.append({
                'id': cid,
                'title': course['title']
            })
    
    selected_course = None
    students_grades = []
    
    if course_id and course_id in professor['courses_taught']:
        selected_course = data.courses[course_id]
        for sid in selected_course['student_user_ids']:
            student = data.students.get(sid)
            if student:
                current_grade = data.grades.get(sid, {}).get(course_id, '미입력')
                students_grades.append({
                    'id': sid,
                    'student_id': student['student_id'],
                    'name': student['name'],
                    'grade': current_grade
                })
    
    return render_template('professor/grades.html',
                         my_courses=my_courses,
                         selected_course_id=course_id,
                         selected_course=selected_course,
                         students=students_grades,
                         grade_options=list(common.GRADE_TO_SCORE.keys()))

# ===== 관리자 라우트 =====

@app.route('/admin/dashboard')
@role_required('admin')
def admin_dashboard():
    stats = {
        'students': len(data.students),
        'professors': len(data.professors),
        'courses': len(data.courses),
        'pending_requests': len([r for r in data.academic_requests if r['status'] == 'pending'])
    }
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/courses', methods=['GET', 'POST'])
@role_required('admin')
def admin_courses():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'create':
            course_id = request.form.get('course_id').upper()
            title = request.form.get('title')
            prof_user_id = request.form.get('professor')
            credits = float(request.form.get('credits'))
            max_capacity = int(request.form.get('max_capacity'))
            day = request.form.get('day')
            start = int(request.form.get('start'))
            end = int(request.form.get('end'))
            
            if course_id in data.courses:
                flash('이미 존재하는 강좌 코드입니다.', 'danger')
            elif prof_user_id not in data.professors:
                flash('존재하지 않는 교수 ID입니다.', 'danger')
            else:
                data.courses[course_id] = {
                    'title': title,
                    'professor_user_id': prof_user_id,
                    'student_user_ids': [],
                    'max_capacity': max_capacity,
                    'credits': credits,
                    'time': {'day': day, 'start': start, 'end': end},
                    'syllabus': '등록된 강의 계획서가 없습니다.',
                    'weekly_content': []
                }
                data.professors[prof_user_id]['courses_taught'].append(course_id)
                common.save_courses()
                common.save_professors()
                flash(f'{title} 강좌가 개설되었습니다.', 'success')
        
        elif action == 'delete':
            course_id = request.form.get('delete_course_id')
            
            if course_id not in data.courses:
                flash('존재하지 않는 강좌입니다.', 'danger')
            else:
                course = data.courses[course_id]
                prof_user_id = course['professor_user_id']
                
                # 교수의 담당 강좌에서 제거
                if prof_user_id in data.professors and course_id in data.professors[prof_user_id]['courses_taught']:
                    data.professors[prof_user_id]['courses_taught'].remove(course_id)
                    common.save_professors()
                
                # 학생들의 수강 목록에서 제거
                for sid in course['student_user_ids']:
                    if sid in data.students and course_id in data.students[sid]['courses']:
                        data.students[sid]['courses'].remove(course_id)
                common.save_students()
                
                # 성적 정보 제거
                for sid in list(data.grades.keys()):
                    if course_id in data.grades[sid]:
                        del data.grades[sid][course_id]
                common.save_grades()
                
                # 출석 정보 제거
                if course_id in data.attendance:
                    del data.attendance[course_id]
                    common.save_attendance()
                
                # 강좌 삭제
                del data.courses[course_id]
                common.save_courses()
                
                flash(f'강좌가 삭제되었습니다.', 'success')
        
        return redirect(url_for('admin_courses'))
    
    # GET 요청
    course_list = []
    for cid, course in data.courses.items():
        prof_name = data.professors.get(course['professor_user_id'], {}).get('name', 'N/A')
        student_count = len(course['student_user_ids'])
        max_cap = course.get('max_capacity', 'N/A')
        time_info = course.get('time', {})
        time_str = f"{time_info.get('day', 'N/A')} {time_info.get('start', '')}-{time_info.get('end', '')}"
        
        course_list.append({
            'id': cid,
            'title': course['title'],
            'professor': prof_name,
            'credits': course.get('credits', 0),
            'time': time_str,
            'current': student_count,
            'max': max_cap
        })
    
    return render_template('admin/courses.html', 
                         courses=course_list,
                         professors=data.professors)

@app.route('/admin/users', methods=['GET', 'POST'])
@role_required('admin')
def admin_users():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            role = request.form.get('role')
            user_id = request.form.get('user_id')
            password = request.form.get('password') or '1234'
            name = request.form.get('name')
            
            if user_id in data.users:
                flash('이미 존재하는 아이디입니다.', 'danger')
            else:
                data.users[user_id] = {'password': password, 'role': role}
                
                if role == 'student':
                    student_id = request.form.get('student_id')
                    major = request.form.get('major')
                    data.students[user_id] = {
                        'name': name,
                        'student_id': student_id,
                        'major': major,
                        'courses': [],
                        'status': '재학'
                    }
                    data.grades[user_id] = {}
                    common.save_students()
                    common.save_grades()
                elif role == 'professor':
                    professor_id = request.form.get('professor_id')
                    department = request.form.get('department')
                    data.professors[user_id] = {
                        'name': name,
                        'professor_id': professor_id,
                        'department': department,
                        'courses_taught': []
                    }
                    common.save_professors()
                elif role == 'admin':
                    admin_id = request.form.get('admin_id')
                    department = request.form.get('department')
                    data.admins[user_id] = {
                        'name': name,
                        'admin_id': admin_id,
                        'department': department
                    }
                    common.save_admins()
                
                common.save_users()
                flash(f'{name}({user_id}) 계정이 추가되었습니다.', 'success')
        
        elif action == 'delete':
            del_user_id = request.form.get('delete_user_id')
            
            if del_user_id not in data.users:
                flash('존재하지 않는 사용자입니다.', 'danger')
            elif del_user_id == session['user_id']:
                flash('현재 로그인한 본인의 계정은 삭제할 수 없습니다.', 'danger')
            else:
                user_role = data.users[del_user_id]['role']
                
                if user_role == 'student':
                    data.students.pop(del_user_id, None)
                    # 수강 강좌 정리
                    for course in data.courses.values():
                        if del_user_id in course['student_user_ids']:
                            course['student_user_ids'].remove(del_user_id)
                    data.grades.pop(del_user_id, None)
                    common.save_students()
                    common.save_courses()
                    common.save_grades()
                elif user_role == 'professor':
                    data.professors.pop(del_user_id, None)
                    # 담당 강좌 정리
                    for course in data.courses.values():
                        if course['professor_user_id'] == del_user_id:
                            course['professor_user_id'] = 'TBD'
                    common.save_professors()
                    common.save_courses()
                elif user_role == 'admin':
                    data.admins.pop(del_user_id, None)
                    common.save_admins()
                
                del data.users[del_user_id]
                common.save_users()
                flash('사용자가 삭제되었습니다.', 'success')
        
        elif action == 'reset_password':
            reset_user_id = request.form.get('reset_user_id')
            new_password = request.form.get('new_password') or '1234'
            
            if reset_user_id not in data.users:
                flash('존재하지 않는 사용자입니다.', 'danger')
            else:
                data.users[reset_user_id]['password'] = new_password
                common.save_users()
                flash(f'{reset_user_id} 사용자의 비밀번호가 초기화되었습니다.', 'success')
        
        return redirect(url_for('admin_users'))
    
    # GET 요청
    users_list = {
        'students': [],
        'professors': [],
        'admins': []
    }
    
    for uid, student in data.students.items():
        users_list['students'].append({
            'user_id': uid,
            'id_number': student['student_id'],
            'name': student['name'],
            'major': student['major'],
            'status': student.get('status', 'N/A')
        })
    
    for uid, prof in data.professors.items():
        users_list['professors'].append({
            'user_id': uid,
            'id_number': prof['professor_id'],
            'name': prof['name'],
            'department': prof['department']
        })
    
    for uid, adm in data.admins.items():
        users_list['admins'].append({
            'user_id': uid,
            'id_number': adm['admin_id'],
            'name': adm['name'],
            'department': adm['department']
        })
    
    return render_template('admin/users.html', users=users_list)

@app.route('/admin/notices', methods=['GET', 'POST'])
@role_required('admin')
def admin_notices():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            title = request.form.get('title')
            content = request.form.get('content')
            new_id = str(len(data.notices) + 1)
            
            data.notices.append({
                'id': new_id,
                'title': title,
                'content': content,
                'author': session['name']
            })
            common.save_notices()
            flash('공지사항이 등록되었습니다.', 'success')
        
        elif action == 'delete':
            notice_id = request.form.get('notice_id')
            data.notices = [n for n in data.notices if n['id'] != notice_id]
            common.save_notices()
            flash('공지사항이 삭제되었습니다.', 'success')
        
        return redirect(url_for('admin_notices'))
    
    return render_template('admin/notices.html', 
                         notices=sorted(data.notices, key=lambda x: x['id'], reverse=True))

@app.route('/admin/requests', methods=['GET', 'POST'])
@role_required('admin')
def admin_requests():
    if request.method == 'POST':
        req_id = request.form.get('req_id')
        action = request.form.get('action')
        
        for req in data.academic_requests:
            if req['req_id'] == req_id and req['status'] == 'pending':
                if action == 'approve':
                    req['status'] = 'approved'
                    student_id = req['student_user_id']
                    if student_id in data.students:
                        if req['type'] == '복학':
                            data.students[student_id]['status'] = '재학'
                        else:
                            data.students[student_id]['status'] = req['type']
                        common.save_students()
                    flash(f"{req['student_name']} 학생의 {req['type']}이(가) 승인되었습니다.", 'success')
                elif action == 'reject':
                    req['status'] = 'rejected'
                    flash('반려 처리되었습니다.', 'info')
                
                common.save_academic_requests()
                break
        
        return redirect(url_for('admin_requests'))
    
    pending_requests = [r for r in data.academic_requests if r['status'] == 'pending']
    
    return render_template('admin/requests.html', requests=pending_requests)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
