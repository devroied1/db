from flask import Flask, request, jsonify, redirect, url_for
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, BooleanField
from flask_admin.form import SecureForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///activation_codes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# نموذج الأكواد في قاعدة البيانات
class ActivationCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), nullable=False)
    used = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<ActivationCode {self.code}>'

# إنشاء قاعدة البيانات والجداول
with app.app_context():
    db.create_all()

# إضافة نموذج إدخال الأكواد للوحة التحكم
class ActivationCodeView(ModelView):
    # استخدام نموذج آمن لمنع الثغرات
    form_base_class = SecureForm

    # تخصيص الحقول المعروضة في النموذج
    column_list = ('code', 'used')
    form_columns = ('code', 'used')

# إضافة Flask-Admin للوحة التحكم
admin = Admin(app, name='Activation Codes', template_mode='bootstrap3')
admin.add_view(ActivationCodeView(ActivationCode, db.session))

# نقطة نهاية للتحقق من الأكواد
@app.route('/validate_code', methods=['POST'])
def validate_code():
    data = request.json
    code = data.get('code')

    if not code:
        return jsonify({"status": "error", "message": "لم يتم تقديم كود التفعيل."})

    # البحث عن الكود في قاعدة البيانات
    activation_code = ActivationCode.query.filter_by(code=code).first()

    if activation_code:
        if not activation_code.used:
            activation_code.used = True
            db.session.commit()  # حفظ التغيير في قاعدة البيانات
            return jsonify({"status": "success", "message": "كود التفعيل صحيح!"})
        else:
            return jsonify({"status": "error", "message": "الكود تم استخدامه بالفعل."})
    else:
        return jsonify({"status": "error", "message": "الكود غير موجود."})

# تشغيل التطبيق
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
