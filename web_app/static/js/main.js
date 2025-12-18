// main.js - 커스텀 JavaScript

// 페이지 로드 시 실행
document.addEventListener('DOMContentLoaded', function() {
    // 자동으로 사라지는 알림 메시지
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000); // 5초 후 자동 닫기
    });
    
    // 폼 유효성 검사
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});

// 확인 대화상자
function confirmAction(message) {
    return confirm(message);
}

// 숫자만 입력 가능하도록
function onlyNumbers(event) {
    const charCode = (event.which) ? event.which : event.keyCode;
    if (charCode > 31 && (charCode < 48 || charCode > 57)) {
        event.preventDefault();
        return false;
    }
    return true;
}
