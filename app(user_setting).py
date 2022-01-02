#-------------은경(user_setting 부분)----------------------#

from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.zqv19.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

@app.route('/')
def home():
    return render_template('user_setting.html')

# 내 이메일로 내 프로필 정보 찾기 > 프로필 사진, 이름, 닉네임, 전화번호, 상태메시지
@app.route("/users", methods=["GET"])
def user_setting_get():
    user_list = (db.users.find_one({'email':'15ya@gmail.com'}, {'_id': False}))
    return jsonify({'user': user_list})

# 내 이메일로 내 계정 찾아서 수정한 내 프로필 정보 업데이트 해주기 > 이름, 닉네임, 전화번호, 상태메시지
@app.route("/users", methods=["POST"])
def user_setting_post():
    name_receive = request.form['name_give']
    nickname_receive = request.form['nickname_give']
    phone_number_receive = request.form['phone_number_give']
    status_message_receive = request.form['status_message_give']

    db.users.update_one({'email':'15ya@gmail.com'},{'$set':{'name':name_receive, 'nickname':nickname_receive, 'phone_number':phone_number_receive, 'status_message':status_message_receive}})

    return jsonify({'msg': '프로필이 저장되었습니다.'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)