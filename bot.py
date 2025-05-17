from flask import Flask, render_template_string, request, redirect, url_for
import subprocess
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'scripts'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Python Runner</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container mt-5">
    <h2 class="text-center mb-4">تشغيل ملفات Python</h2>
    <form method="POST" enctype="multipart/form-data" class="card p-4 shadow">
        <div class="mb-3">
            <label for="script" class="form-label">اختر ملف بايثون (.py)</label>
            <input class="form-control" type="file" name="script" accept=".py" required>
        </div>
        <button type="submit" class="btn btn-primary w-100">تشغيل الملف</button>
    </form>
    {% if filename %}
    <div class="alert alert-success mt-3 text-center">
        تم تشغيل الملف بنجاح: <strong>{{ filename }}</strong>
    </div>
    {% endif %}
</div>
</body>
</html>
'''

@app.route("/", methods=["GET", "POST"])
def index():
    filename = None
    if request.method == "POST":
        file = request.files["script"]
        if file and file.filename.endswith(".py"):
            filename = f"{uuid.uuid4().hex}_{file.filename}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            subprocess.Popen(["python3", filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return render_template_string(HTML_TEMPLATE, filename=filename)
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
