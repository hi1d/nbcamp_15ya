from collections import UserString
from os import pwrite, terminal_size
from flask.wrappers import Response
from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import re
from uuid import uuid4

app = Flask(__name__)

SECRET_KEY = '15ya'


client = MongoClient(
    'mongodb+srv://15ya:camp15team@cluster0.hn03w.mongodb.net/cluster0?retryWrites=true&w=majority')
db = client.db15ya


# 토큰 유효성 검사
def valid_token():
    token_receive = request.cookies.get('15ya_token')

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return "로그인 시간이 만료되었습니다."
    except jwt.exceptions.DecodeError:
        return "로그인 정보가 존재하지 않습니다."

    else:
        search = db.users.find_one({'email': payload['id']})
        try:
            nickname = search['nickname']
        except TypeError:
            return redirect(url_for('check_status'))
        else:
            profile_image = search['profile_image']
            like_feed = search['like_feed']
            like_comment = search['like_comment']
            follow_list = search['follow_list']
            return {'result': True, 'email': payload['id'], 'nickname': nickname,
                    'profile_image': profile_image, 'like_feed': like_feed, 'like_comment': like_comment,
                    'follow_list': follow_list}


@app.route('/api/check_status')
def check_status():
    valid = valid_token()
    if type(valid) == dict:
        return jsonify({'result': True})
    else:
        return jsonify({'result': False})

# 이메일 중복체크


def email_check(email):
    return bool(db.users.find_one({'email': email}))


# 작성 시간 구하기

def nowtime(time):
    time = str(datetime.utcnow() - time).split(':')
    if int(time[0]) == 0:
        if int(time[1]) == 0:
            time = str(time[2])+'초전'
        else:
            time = str(time[1])+'분전'
    elif int(time[0]) > 24:
        time = str(time[0]//24)+'일전'
    else:
        time = str(time[0])+'시간전'

    return time


# 메인화면


@app.route('/')
def home():
    valid = valid_token()
    try:
        if valid['result'] == True:
            return render_template('index.html')
    except TypeError:
        return redirect(url_for("login"))


# 로그인


@ app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # 로그인상태로 접근 시
        valid = valid_token()
        try:
            if valid['result'] == True:
                return redirect(url_for('home'))
        # 로그인화면 이동
        except TypeError:
            return render_template('login.html', msg=valid)
    else:
        # 로그인 기능
        email_receive = request.form['email_give']
        password_receive = request.form['password_give']

        password_hash = hashlib.sha256(
            password_receive.encode('utf-8')).hexdigest()
        target = db.users.find_one(
            {'email': email_receive, 'password': password_hash})

    if target is not None:
        payload = {
            'id': email_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60*60)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'failed', 'msg': '아이디 또는 비밀번호가 일치하지 않습니다.'})

# 회원가입


@ app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        # 로그인 상태로 접근시
        valid = valid_token()
        try:
            if valid['result'] == True:
                return redirect(url_for('home'))
        # 회원가입 화면 이동
        except TypeError:
            return render_template('register.html')
    else:
        # 회원가입 기능
        email_receive = request.form['email_give']
        name_receive = request.form['name_give']
        nickname_receive = request.form['nickname_give']
        password_receive = request.form['password_give']
        # 비밀번호 암호화
        password_hash = hashlib.sha256(
            password_receive.encode('utf-8')).hexdigest()
        # 이메일 유효성 검사
        if (re.search('[^a-zA-Z0-9-_.@]+', email_receive) is not None
                or not (9 < len(email_receive) < 26)):
            return jsonify({'result': 'failed', 'msg': '휴대폰번호 또는 이메일의 형식을 확인해주세요. 영문과, 숫자, 일부 특수문자(.-_) 사용 가능. 10~25자 길이'})
        # 비밀번호 유효성 검사
        elif (re.search('[^a-zA-Z0-9!@#$%^&*]+', password_receive) is not None or
                not(7 < len(password_receive) < 21) or
                re.search('[0-9]+', password_receive) is None or
                re.search('[a-zA-Z]+', password_receive) is None):
            return jsonify({'result': 'failed', 'msg': '비밀번호의 형식을 확인해주세요. 영문과 숫자 필수 포함, 일부 특수문자(!@#$%^&*) 사용 가능. 8~20자 길이'})
        # 빈칸 검사
        elif not(email_receive and name_receive and nickname_receive and password_hash):
            return jsonify({'result': 'failed', 'msg': '빈칸을 입력해주세요.'})
        # 중복 이메일 검사
        elif email_check(email_receive):
            return jsonify({'result': 'failed', 'msg': '가입된 내역이 있습니다.'})

        doc = {
            'email': email_receive,
            'name': name_receive,
            'nickname': nickname_receive,
            'password': password_hash,
            'profile_image': '../static/media/profile/default.jpeg',
            'posting': 0,
            'status_message': '',
            'bookmark': [],
            'like_feed': [],
            'like_comment': [],
            'follow_list': [],
            'follower_list': []
        }
        db.users.insert_one(doc)
        return jsonify({'result': 'success'})

# 피드업로드


@ app.route('/api/feed_upload', methods=['GET', 'POST'])
def feed_upload():
    valid = valid_token()
    try:
        if valid['result'] == True:
            # 로그인 상태로 접근시
            if request.method == 'GET':
                user_info = {
                    'nickname': valid['nickname'],
                    'profile': valid['profile_image'],
                    'email': valid['email'],
                    'like_feed': valid['like_feed'],
                    'like_comment': valid['like_comment']
                }

                feeds = (list(db.feeds.find(
                    {}, {'_id': 0})))[::-1]
                return render_template('feed.html', feeds=feeds, user=user_info)

            else:
                file = request.files['file']
                file_name = str(uuid4().hex)
                email = valid['email']
                author = valid['nickname']
                profile_image = valid['profile_image']

                file.save('./static/media/feed/' + secure_filename(file_name))
                image = f'../static/media/feed/'+file_name
                content = request.form.get('content')
                time = datetime.utcnow()

                latest_index = (db.feeds.find_one(
                    {"$query": {}, "$orderby": {"index": -1}}))
                try:
                    index = latest_index['index']
                except TypeError:
                    index = 0
                doc = {
                    'index': 1+index,
                    'image': image,
                    'content': content,
                    'author': author,
                    'profile_image': profile_image,
                    'like': 0,
                    'email': email,
                    'time': time,
                    'comment': [],
                }

                db.feeds.insert_one(doc)
                posting = int((db.users.find_one({'email': email}))['posting'])
                db.users.update_one({'email': email}, {
                                    '$set': {'posting': posting+1}})

                return jsonify({'result': 'success', 'msg': '업로드완료'})
    except TypeError:
        return redirect(url_for('home'))


# 피드 삭제


@ app.route('/api/feed_delete', methods=['POST'])
def feed_delete():
    valid = valid_token()
    try:
        if valid['result'] == True:
            email = valid['email']
            index_receive = int(request.form['index_give'])
            result = db.feeds.find_one(
                {'email': email, 'index': index_receive})
            if result is not None:
                db.feeds.delete_one({'email': email, 'index': index_receive})
                posting = int((db.users.find_one({'email': email}))['posting'])
                db.users.update_one({'email': email}, {
                                    '$set': {'posting': posting-1}})
                return jsonify({'result': 'success', 'msg': '삭제완료!'})
            else:
                return jsonify({'result': 'failed', 'msg': '작성자만 삭제가 가능합니다.'})
    except TypeError:
        return redirect(url_for('home'))

# 유저, 피드구하기


def like(index):
    valid = valid_token()
    try:
        if valid['result'] == True:
            feed = db.feeds.find_one({'index': index})
            user = (db.users.find_one({'email': valid['email']}))
            return {'feed': feed, 'user': user}
    except TypeError:
        return redirect(url_for('login'))

# 피드_like


@ app.route('/api/feed_like/<index>')
def feed_like(index):
    index = int(index)
    data = like(index)
    user_like_list = data['user']['like_feed']
    feed_like_count = data['feed']['like']

    if index in user_like_list:
        user_like_list.pop(user_like_list.index(index))
        feed_like_count -= 1
    else:
        user_like_list.append(index)
        feed_like_count += 1

    db.users.update_one({'email': data['user']['email']}, {
                        '$set': {'like_feed': user_like_list}})
    db.feeds.update_one({'index': index}, {'$set': {'like': feed_like_count}})

    return redirect(url_for('feed_upload'))


# comment 생성

@ app.route('/api/comment', methods=['POST'])
def comment():
    valid = valid_token()
    try:
        if valid['result'] == True:
            email = valid['email']
            index = int(request.form['index_give'])
            content = request.form['content_give']
            author = valid['nickname']
            time = datetime.utcnow()
            comment = (db.feeds.find_one({'index': index}))['comment']

            try:
                last_comment_index = comment[-1]['comment_index']
            except IndexError:
                comment_index = 1
            else:
                comment_index = last_comment_index+1
            comment.append({'comment_index': comment_index, 'email': email,
                            'content': content, 'author': author, 'time': time,
                            'comment_like': 0})
            # time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")

            db.feeds.update_one({'index': index}, {
                                '$set': {'comment': comment}})

            return jsonify({'result': 'success', 'msg': '댓글이 입력되었습니다.'})
    except TypeError:
        return redirect(url_for('login'))

# comment 삭제


@ app.route('/api/comment_delete', methods=['POST'])
def comment_delete():
    valid = valid_token()
    try:
        if valid['result'] == True:
            email = valid['email']
            index_receive = int(request.form['index_give'])
            comment_index_receive = int(request.form['comment_index_give'])
            result = (db.feeds.find_one(
                {'index': index_receive}))['comment']
            index = -1

            for i in range(len(result)):
                if result[i]['comment_index'] == comment_index_receive and result[i]['email'] == email:
                    index = i
            if index == -1:
                return jsonify({'result': 'failed', 'msg': '작성자만 삭제가능합니다.'})
            result.pop(index)

            db.feeds.update_one({'index': index_receive}, {
                '$set': {'comment': result}})

            return jsonify({'result': 'success', 'msg': '삭제완료!'})

    except TypeError:
        return redirect(url_for('home'))


# comment_like


@ app.route('/api/comment_like/<index>,<comment_index>')
def comment_like(index, comment_index):
    index = int(index)
    comment_index = int(comment_index)
    data = like(index)
    user_like_list = data['user']['like_comment']
    comment_like_count = data['feed']['comment']
    target_index = -1
    for i in range(len(comment_like_count)):
        if comment_like_count[i]['comment_index'] == comment_index:
            target_index = i
    if comment_index in user_like_list:
        user_like_list.pop(user_like_list.index(comment_index))
        comment_like_count[target_index]['comment_like'] -= 1
    else:
        user_like_list.append(comment_index)
        comment_like_count[target_index]['comment_like'] += 1

    db.users.update_one({'email': data['user']['email']}, {
                        '$set': {'like_comment': user_like_list}})
    db.feeds.update_one({'index': index}, {
                        '$set': {'comment': comment_like_count}})

    return redirect(url_for('feed_upload'))


#-------------은경(마이페이지 부분)----------------------#

# 내 이메일로 내 프로필 정보 찾기


@ app.route("/mypage/<email>", methods=["GET"])
def mypage(email):
    valid = valid_token()
    try:
        if valid['result'] == True:
            user_list = (db.users.find_one(
                {'email': email}, {'_id': 0, 'password': 0}))
            feed_list = db.feeds.find(
                {'email': email}, {'_id': 0, 'password': 0, 'email': 0})
            my_email = valid['email']
            my_follow_list = valid['follow_list']
            return render_template('mypage.html', user=user_list, feed=feed_list, my_email=my_email, follow_list=my_follow_list)
    except TypeError:
        return redirect(url_for('login'))

        # 내 이메일로 내가 포스팅한 이미지 가져오기

        # ---------------------------------------------------

# 북마크


@ app.route('/bookmark', methods=['GET', 'POST'])
def bookmark():
    valid = valid_token()
    try:
        if valid['result'] == True:
            if request.method == 'GET':
                target_bookmark = (db.users.find_one(
                    {'email': valid['email']}))['bookmark']
                feeds = db.feeds.find({}, {'_id': 0, 'email': 0})
                bookmark_feed = []
                for feed in feeds:
                    if feed['index'] in target_bookmark:
                        bookmark_feed.append(feed['image'])
                    else:
                        continue
                return jsonify({'bookmark': bookmark_feed})
            else:
                email = valid['email']
                index = int(request.form['index_give'])
                target = (db.users.find_one({'email': email}))['bookmark']
                if index in target:
                    target.pop(target.index(index))
                    db.users.update_one({'email': email}, {
                                        '$set': {'bookmark': target}})
                    return jsonify({'result': 'success', 'msg': '북마크 취소'})
                target.append(index)
                db.users.update_one({'email': email}, {
                                    '$set': {'bookmark': target}})
                return jsonify({'result': 'success', 'msg': '북마크완료'})
    except TypeError:
        return redirect(url_for('login'))

##스토리 페이지##


@app.route('/story/<userid>')
def storyView(userid):
    img_list = list(db.users.find({'email': userid}, {'_id': False}))
    current = img_list[0]['index']
    prev = db.users.find_one({'index': current-1})
    next = db.users.find_one({'index': current+1})
    if prev and next is not None:
        parameter_list = [prev['id'], next['id']]
    else:
        parameter_list = ['../', '../']
    return render_template('story-page.html', arr=img_list, para=parameter_list)

# 팔로우


@app.route('/api/follow/<email>')
def follow(email):
    # 2. 팔로우한사람만 피드 보이기
    valid = valid_token()
    try:
        if valid['result'] == True:
            my_email = valid['email']
            my_info = (db.users.find_one({'email': my_email}))['follow_list']
            target_info = (db.users.find_one({'email': email}))[
                'follower_list']
            if email in my_info:
                my_info.pop(my_info.index(email))
                target_info.pop(target_info.index(my_email))
            else:
                my_info.append(email)
                target_info.append(my_email)
            db.users.update_one({'email': my_email}, {
                                '$set': {'follow_list': my_info}})
            db.users.update_one({'email': email}, {
                                '$set': {'follower_list': target_info}})
            return redirect(url_for('mypage', email=email))

    except TypeError:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
