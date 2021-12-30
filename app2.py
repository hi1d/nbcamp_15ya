#-------------은경(마이페이지 부분)----------------------#

from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.zqv19.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

@app.route('/')
def home():
    return render_template('mypage.html')

# 내 이메일로 내 프로필 정보 찾기
@app.route("/users", methods=["GET"])
def users_get():
    user_list = (db.users.find_one({'e-mail':'15ya@gmail.com'}, {'_id': False}))
    return jsonify({'user': user_list})

# 내 이메일로 내가 포스팅한 이미지 가져오기
@app.route("/post", methods=["GET"])
def post_get():
    post_list = list(db.post.find({'email':'15ya@gmail.com'}, {'_id': False}))
    return jsonify({'post_image': post_list})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)