$(document).ready(function() {
    $.ajax({

        type: 'GET',
        url: '/users',
        data: {},
        success: function (response) {
            console.log(response['user'])
            let name = response['user']['name']
            let nickname = response['user']['nickname']
            let profile_image = response['user']['profile_image']
            let posting = response['user']['posting']
            let follower = response['user']['follower']
            let follow = response['user']['follow']
            let status_message = response['user']['status_message']

                let temp_html = `<div id="left-wrapper">
                                    <img src=${profile_image}>
                                </div>
                                <div id="right-wrapper">
                                    <div id="box1">
                                        <p id="id">${nickname}</p>
                                        <button id="follow-button">팔로우</button>
                                    </div>
                                    <div id="box2">
                                        <p>게시물 <strong>${posting}</strong></p>
                                        <p class="count">팔로워 <strong>${follower}</strong></p>
                                        <p class="count">팔로우 <strong>${follow}</strong></p>
                                    </div>
                                    <div id="box3">
                                        <p id="myname"><strong>${name}</strong></p>
                                        <p id="status-message">${status_message}</p>
                                    </div>
                                </div>`
                $('#myinfo-container').append(temp_html)
            }
        });
    //    마이페이지에 내가 포스팅한 이미지 가져오기
    $.ajax({
        type: 'GET',
        url: '/post',
        data: {},
        success: function (response) {
            let rows = response['post_image']
            for (let i = 0; i < rows.length; i++) {
                let post_image = rows[i]['image']

                let temp_html = `<div class="post-box">
                                    <img src=${post_image}>
                                </div>`
                $('#post-boxes').append(temp_html)
            }
        }
    });
});