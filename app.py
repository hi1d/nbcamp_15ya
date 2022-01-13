from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import re
from uuid import uuid4
from bson.json_util import dumps
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator


app = Flask(__name__)

SECRET_KEY = '15ya'


client = MongoClient(
    'mongodb+srv://15ya:camp15team@cluster0.hn03w.mongodb.net/cluster0?retryWrites=true&w=majority')
# client = MongoClient('localhost', 27017)
db = client.db15ya

model = tf.keras.models.load_model('./static/model/flower_model.h5')

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
            return redirect(url_for('login'))
        else:
            profile_image = search['profile_image']
            like_feed = search['like_feed']
            follow_list = search['follow_list']
            name = search['name']
            return {'result': True, 'email': payload['id'], 'nickname': nickname,
                    'profile_image': profile_image, 'like_feed': like_feed,
                    'follow_list': follow_list, 'name': name}


# 이메일 중복체크


def email_check(email):
    return bool(db.users.find_one({'email': email}))


def nickname_check(nickname):
    return bool(db.users.find_one({'nickname': nickname}))


# 메인화면


@app.route('/')
def home():
    valid = valid_token()
    try:
        if valid['result'] == True:
            user_info = db.users.find_one({'email': valid['email']}, {
                                          '_id': 0, 'password': 0})
            feeds = (list(db.feeds.find(
                {}, {'_id': 0})))[::-1]

            # 스토리 컨테이너
            all_info = list(db.storyarchive.find({}))
            off_info = list(db.story_off.find({}))

            # story-on 리스트
            all_count = len(all_info)
            off_count = len(off_info)

            if len(off_info) != 0:
                on_list = []
                for i in range(all_count):
                    for j in range(off_count):
                        if off_info[j]['nickname'] == all_info[i]['nickname']:
                            break
                        elif off_info[j]['nickname'] != all_info[i]['nickname'] and j == off_count - 1:
                            on_list.append(all_info[i])
                on_list = list(
                    {one['nickname']: one for one in on_list}.values())
            elif off_count == 0:
                on_list = list(
                    {one['nickname']: one for one in all_info}.values())

            # story-off 리스트 (중복처리)
            off_list = list(
                {off['nickname']: off for off in off_info}.values())

            return render_template('index.html', feeds=feeds, user=user_info, on_list=on_list, off_list=off_list)
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
        # 중복 닉네임 검사
        elif nickname_check(nickname_receive):
            return jsonify({'result': 'failed', 'msg': '중복된 닉네임이 있습니다.'})
        elif re.search('[^a-zA-Z0-9-_.]+', nickname_receive) is not None:
            return jsonify({'result': 'failed', 'msg': ' 영문, 숫자, -_. 만 사용이 가능합니다.'})

        doc = {
            'email': email_receive,
            'name': name_receive,
            'nickname': nickname_receive,
            'password': password_hash,
            'profile_image': '/static/media/profile/default.jpeg',
            'posting': 0,
            'status_message': '',
            'bookmark': [],
            'like_feed': [],
            'follow_list': [],
            'follower_list': []
        }
        db.users.insert_one(doc)
        return jsonify({'result': 'success'})

# 피드업로드


@ app.route('/api/feed_upload', methods=['POST'])
def feed_upload():
    valid = valid_token()
    try:
        if valid['result'] == True:
            # 로그인 상태로 접근시
            file = request.files['file']
            file_name = str(uuid4().hex)
            email = valid['email']
            author = valid['nickname']
            profile_image = valid['profile_image']
            file.save('./static/media/feed/' + secure_filename(file_name))
            image = f'../static/media/feed/'+file_name
            content = request.form.get('content')
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
                user = db.users.find_one({'email': email})
                posting = int(user['posting'])
                like_feed = user['like_feed']
                bookmark_feed = user['bookmark']
                if index_receive in like_feed:
                    like_feed.pop(like_feed.index(index_receive))
                    db.users.update_one({'email': email}, {
                                        '$set': {'like_feed': like_feed}})
                elif index_receive in bookmark_feed:
                    bookmark_feed.pop(bookmark_feed.index(index_receive))
                    db.users.update_one({'email': email}, {
                                        '$set': {'bookmark': bookmark_feed}})

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

    return redirect(url_for('home'))


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
            comment = (db.feeds.find_one({'index': index}))['comment']
            profile = valid['profile_image']

            try:
                last_comment_index = comment[-1]['comment_index']
            except IndexError:
                comment_index = 1
            else:
                comment_index = last_comment_index+1
            comment.append({'comment_index': comment_index, 'email': email,
                            'content': content, 'author': author,
                            'comment_like': 0, 'profile_image': profile})

            db.feeds.update_one({'index': index}, {
                                '$set': {'comment': comment}})

            return jsonify({'result': 'success', 'msg': '댓글이 입력되었습니다.'})
    except TypeError:
        return redirect(url_for('login'))

# comment 삭제


@ app.route('/api/comment_delete/', methods=['POST'])
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


@ app.route('/bookmark_show', methods=['POST'])
def bookmark_show():
    print('1')
    email = request.form['email_give']
    target_bookmark = (db.users.find_one(
        {'email': email}))['bookmark']
    feeds = db.feeds.find({}, {'_id': 0, 'email': 0})
    bookmark_feed = []
    for feed in feeds:
        if feed['index'] in target_bookmark:
            bookmark_feed.append(feed['image'])
        else:
            continue
    return jsonify({'bookmark': bookmark_feed})


@ app.route('/bookmark', methods=['POST'])
def bookmark():
    valid = valid_token()
    try:
        if valid['result'] == True:
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


# 검색 기능 ############ 수정 요청 1. 검색 시 나오는 user_list(프로필 이미지, 아이디 or 닉네임)################
#############################  2. ../js/index.js ajex부분, function searching() 확인 요청 ################
@app.route("/users", methods=["GET"])
def users_search():
    user_list = list(db.users.find({}, {'_id': False}))

    return jsonify({'users': user_list})
# 최근 검색 기록 : 차후 추가 예정


##스토리 페이지##


@app.route('/story/<nickname>')
def showStories(nickname):
    def onORoff(nickname):
        all_info = list(db.storyarchive.find({}))
        all_info = list({one['nickname']: one for one in all_info}.values())
        all_count = len(all_info)
        off_info = list(db.story_off.find({}))
        off_count = len(off_info)
        # on 리스트
        if len(off_info) != 0:
            on_list = []
            for i in range(all_count):
                for j in range(off_count):
                    if off_info[j]['nickname'] == all_info[i]['nickname']:
                        break
                    elif off_info[j]['nickname'] != all_info[i]['nickname'] and j == off_count - 1:
                        on_list.append(all_info[i])
        elif off_count == 0:
            on_list = all_info
        # off 리스트
        off_info = list(db.story_off.find({}))
        off_list = list({off['nickname']: off for off in off_info}.values())

        if next((x for x in on_list if x["nickname"] == nickname), None) is not None:
            return on_list
        elif next((x for x in off_list if x["nickname"] == nickname), None) is not None:
            return off_list

    def idInfo(array, nickname):
        cur_index = next((i for i, x in enumerate(
            array) if x['nickname'] == nickname), None)

        all_count = len(array)

        if all_count == 1 and cur_index == 0:
            id_list = ['/', '/']
        elif all_count != 1 and cur_index == 0:
            id_list = ['/', array[cur_index + 1]['nickname']]
        elif cur_index == all_count - 1:
            id_list = [array[cur_index - 1]['nickname'], '/']
        else:
            id_list = [array[cur_index - 1]['nickname'],
                       array[cur_index + 1]['nickname']]
        return id_list

    id_list = idInfo(onORoff(nickname), nickname)

    whos_story = list(db.users.find({'nickname': nickname}))
    img_list = list(db.storyarchive.find({'nickname': nickname}))

    return render_template('story-page.html', imgs=img_list, id=id_list, account=whos_story)


@app.route('/upload/story', methods=['POST'])
def uploadStory():
    nickname = request.form['nickname']
    story_img = request.form['story_img']
    profile = request.form['profile']

    doc = {'nickname': nickname, 'story_img': story_img, 'profile_image': profile}
    db.storyarchive.insert_one(doc)
    return jsonify({'msg': '업로드 완료!'})


@app.route('/off-list/add', methods=['POST'])
def addOffList():
    nickname = request.form['nickname']
    profile = request.form['profile']

    doc = {'nickname': nickname, 'profile_image': profile}
    db.story_off.insert_one(doc)
    return True


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

# 내 이메일로 내 프로필 정보 찾기 > 프로필 사진, 이름, 닉네임, 전화번호, 상태메시지


@app.route("/users_setting/", methods=["GET", 'POST'])
def user_setting_get():
    valid = valid_token()
    try:
        if valid['result'] == True:
            if request.method == 'GET':
                user_list = (db.users.find_one(
                    {'email': valid['email']}, {'_id': False, 'password': 0}))
                return render_template('user_setting.html', user=user_list)
            else:
                name_receive = request.form['name_give']
                nickname_receive = request.form['nickname_give']
                status_message_receive = request.form['status_message_give']
                if valid['nickname'] == nickname_receive:
                    pass
                elif nickname_check(nickname_receive):
                    return jsonify({'result': 'failed', 'msg': '중복된 닉네임이 있습니다.'})
                elif re.search('[^a-zA-Z0-9-_.]+', nickname_receive) is not None:
                    return jsonify({'result': 'failed', 'msg': ' 영문, 숫자, -_. 만 사용이 가능합니다.'})
                db.users.update_one({'email': valid['email']}, {'$set': {'name': name_receive, 'nickname': nickname_receive,
                                                                         'status_message': status_message_receive}})
                db.feeds.update_many({'email': valid['email']},
                                     {'$set': {'author': nickname_receive}})
                return jsonify({'msg': '프로필이 저장되었습니다.'})
    except TypeError:
        return redirect(url_for('login'))


# 내 이메일로 내 계정 찾아서 수정한 내 프로필 정보 업데이트 해주기 > 이름, 닉네임, 전화번호, 상태메시지


@ app.route('/api/change_profile/', methods=['POST'])
def change_profile():
    valid = valid_token()
    file = request.files['file']
    file_name = str(uuid4().hex)
    file.save('./static/media/profile/' + secure_filename(file_name))
    image = f'/static/media/profile/'+file_name

    db.users.update_one({'email': valid['email']}, {
                        '$set': {'profile_image': image}})
    db.feeds.update_many({'email': valid['email']},
                         {'$set': {'profile_image': image}})
    return jsonify({'result': 'success', 'msg': '프로필변경'})


@app.route('/api/feed_show/', methods=['POST'])
def feed_show():
    valid = valid_token()
    index = int(request.form['index_give'])
    feed = db.feeds.find_one({'index': index})
    comment_user = db.users.find_one({'email': valid['email']}, {
        '_id': 0, 'password': 0})
    if feed is None:
        return redirect(url_for('home'))
    feed = dumps(feed)
    return jsonify({'result': 'success', 'feed': feed, 'user': comment_user})


@app.route('/flower', methods=['GET', 'POST'])
def flower():
    valid = valid_token()
    if request.method == 'GET':
        user_info = db.users.find_one({'email': valid['email']}, {
            '_id': 0, 'password': 0})
        return render_template('flower.html', user=user_info)
    else:
        file = request.files['file_give']
        save_to = f'./static/img/flower/save/1.png'
        file.save(save_to)

        return redirect(url_for('flower_show'))


@app.route('/api/flower_show')
def flower_show():
    test_datagen = ImageDataGenerator(rescale=1./255)
    test_dir = './static/img/flower'
    test_generator = test_datagen.flow_from_directory(
        test_dir,
        target_size=(224, 224),
        color_mode="rgb",
        shuffle=False,
        class_mode=None,
        batch_size=1)
    pred = model.predict(test_generator)
    classes = {0: 'daisy', 1: 'dandelion',
               2: 'rose', 3: 'sunflower', 4: 'tulip'}
    kor_name = {'daisy':'데이지','dandelion':'민들레속',
                'rose':'장미','sunflower':'해바라기','tulip':'튤립'}
    pred_label = classes[np.argmax(pred[-1])]
    img = '../static/img/flower/'+pred_label+'.jpeg'
    name = kor_name[pred_label]


    return jsonify({'result':'success','img':img,'name':name})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
