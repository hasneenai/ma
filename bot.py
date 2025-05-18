from flask import Flask, render_template_string, request, redirect, url_for
import subprocess
import os
import uuid
import requests
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'scripts'
app.config['TELEGRAM_BOT_TOKEN'] = '6391443468:AAEKdGOdUMgckicD5qG-ttWaOwus_hjKp_w'
app.config['TELEGRAM_CHAT_ID'] = '5376094649'
app.config['ALLOWED_EXTENSIONS'] = {'py'}


os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def generate_filename():

    random_part = uuid.uuid4().hex[:5]
    return f"isvso_{random_part}.py"

def send_telegram_notification(filename):

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"🔔 تم رفع ملف Python جديد\n\n"
    message += f"🕒 الوقت: {current_time}\n"
    message += f"📂 اسم الملف: {filename}\n"
    
    url = f"https://api.telegram.org/bot{app.config['TELEGRAM_BOT_TOKEN']}/sendMessage"
    params = {
        'chat_id': app.config['TELEGRAM_CHAT_ID'],
        'text': message
    }
    try:
        requests.post(url, params=params)
    except Exception as e:
        print(f"⚠️ فشل إرسال إشعار Telegram: {e}")

def run_python_script(filepath):

    try:
        subprocess.Popen(["python3", filepath], 
                       stdout=subprocess.DEVNULL, 
                       stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        print(f"⚠️ خطأ في تشغيل الملف: {e}")
        return False

BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <style>
        :root {
            --primary-color: #4e73df;
            --secondary-color: #f8f9fc;
            --success-color: #1cc88a;
            --danger-color: #e74a3b;
        }
        body {
            background-color: var(--secondary-color);
            font-family: 'Tajawal', sans-serif;
        }
        .main-card {
            border-radius: 15px;
            box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
            border: none;
        }
        .card-header {
            background-color: var(--primary-color);
            border-radius: 15px 15px 0 0 !important;
        }
        .code-area {
            font-family: 'Courier New', monospace;
            min-height: 250px;
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 15px;
        }
        .nav-tabs .nav-link {
            color: #6e707e;
            font-weight: 600;
        }
        .nav-tabs .nav-link.active {
            color: var(--primary-color);
            border-bottom: 3px solid var(--primary-color);
        }
        .alert-message {
            border-radius: 10px;
        }
    </style>
</head>
<body>
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card main-card">
                    <div class="card-header text-white text-center">
                        <h4 class="mb-0"><i class="bi bi-code-slash me-2"></i> استضافة بايثون مجانية</h4>
                    </div>
                    
                    <div class="card-body">
                        <ul class="nav nav-tabs mb-4" id="myTab" role="tablist">
                            <li class="nav-item" role="presentation">
                                <button class="nav-link active" id="upload-tab" data-bs-toggle="tab" data-bs-target="#upload" type="button">
                                    <i class="bi bi-upload me-2"></i> رفع ملف
                                </button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="create-tab" data-bs-toggle="tab" data-bs-target="#create" type="button">
                                    <i class="bi bi-file-earmark-plus me-2"></i> إنشاء ملف
                                </button>
                            </li>
                        </ul>
                        
                        <div class="tab-content p-3" id="myTabContent">
                            <!-- قسم رفع الملف -->
                            <div class="tab-pane fade show active" id="upload" role="tabpanel">
                                <form method="POST" enctype="multipart/form-data" action="/upload">
                                    <div class="mb-4">
                                        <label for="script" class="form-label fw-bold">اختر ملف Python</label>
                                        <input class="form-control form-control-lg" type="file" name="script" accept=".py" required>
                                        <div class="form-text">يجب أن يكون امتداد الملف .py فقط</div>
                                    </div>
                                    <button type="submit" class="btn btn-primary btn-lg w-100 py-2">
                                        <i class="bi bi-play-circle me-2"></i> تشغيل الملف
                                    </button>
                                </form>
                            </div>
                            
                            <!-- قسم إنشاء الملف -->
                            <div class="tab-pane fade" id="create" role="tabpanel">
                                <form method="POST" action="/create">
                                    <div class="mb-3">
                                        <label class="form-label fw-bold">الكود البرمجي</label>
                                        <textarea class="form-control code-area" name="code" rows="12" placeholder="أدخل كود Python هنا..." required></textarea>
                                    </div>
                                    <button type="submit" class="btn btn-success btn-lg w-100 py-2">
                                        <i class="bi bi-save me-2"></i> حفظ وتشغيل
                                    </button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
                
                {% if message %}
                <div class="alert alert-{{ message_type }} alert-message mt-4 text-center">
                    <h5><i class="bi {{ message_icon }} me-2"></i>{{ message }}</h5>
                    {% if filename %}
                    <div class="mt-2">
                        <span class="badge bg-dark">اسم الملف: {{ filename }}</span>
                    </div>
                    {% endif %}
                </div>
                {% endif %}
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''


@app.route("/", methods=["GET"])
def index():
    return render_template_string(BASE_TEMPLATE)

@app.route("/upload", methods=["POST"])
def upload_file():
    if 'script' not in request.files:
        return render_template_string(BASE_TEMPLATE,
                                  message="لم يتم اختيار ملف",
                                  message_type="danger",
                                  message_icon="bi-exclamation-circle")
    
    file = request.files['script']
    if file.filename == '':
        return render_template_string(BASE_TEMPLATE,
                                  message="لم يتم اختيار ملف",
                                  message_type="danger",
                                  message_icon="bi-exclamation-circle")
    
    if not allowed_file(file.filename):
        return render_template_string(BASE_TEMPLATE,
                                  message="يجب أن يكون الملف من نوع .py",
                                  message_type="danger",
                                  message_icon="bi-exclamation-circle")
    
    try:

        filename = generate_filename()
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
 
        if run_python_script(filepath):
            send_telegram_notification(filename)
            
            return render_template_string(BASE_TEMPLATE,
                                      message="تم تشغيل الملف بنجاح",
                                      message_type="success",
                                      message_icon="bi-check-circle",
                                      filename=filename)
        else:
            return render_template_string(BASE_TEMPLATE,
                                      message="حدث خطأ أثناء تشغيل الملف",
                                      message_type="danger",
                                      message_icon="bi-exclamation-circle")
    except Exception as e:
        return render_template_string(BASE_TEMPLATE,
                                  message=f"حدث خطأ: {str(e)}",
                                  message_type="danger",
                                  message_icon="bi-exclamation-circle")

@app.route("/create", methods=["POST"])
def create_file():
    code = request.form.get('code', '').strip()
    
    if not code:
        return render_template_string(BASE_TEMPLATE,
                                   message="يجب إدخال الكود البرمجي",
                                   message_type="danger",
                                   message_icon="bi-exclamation-circle")
    
    try:
        # توليد اسم ملف جديد حسب الطلب
        filename = generate_filename()
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # تشغيل الملف
        if run_python_script(filepath):
            # إرسال إشعار Telegram
            send_telegram_notification(filename)
            
            return render_template_string(BASE_TEMPLATE,
                                       message="تم إنشاء وتشغيل الملف بنجاح",
                                       message_type="success",
                                       message_icon="bi-check-circle",
                                       filename=filename)
        else:
            return render_template_string(BASE_TEMPLATE,
                                       message="حدث خطأ أثناء تشغيل الملف",
                                       message_type="danger",
                                       message_icon="bi-exclamation-circle")
    except Exception as e:
        return render_template_string(BASE_TEMPLATE,
                                   message=f"حدث خطأ: {str(e)}",
                                   message_type="danger",
                                   message_icon="bi-exclamation-circle")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=60485, debug=True)
