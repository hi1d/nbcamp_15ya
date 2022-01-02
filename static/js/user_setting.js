$(document).ready(function() {
    $.ajax({
        type: 'GET',
        url: '/users',
        data: {},
        success: function (response) {
            console.log(response['user'])
            let profile_image = response['user']['profile_image']

            let temp_html = `<div id="left-profile-image">
                                <img src=${profile_image}>
                            </div>
                            <div id="right-profile-image">
                                <button>프로필 사진 바꾸기</button>
                            </div>`
            $('#profile-image-box').append(temp_html)
        }
    });
    $.ajax({
        type: 'GET',
        url: '/users',
        data: {},
        success: function (response) {
            console.log(response['user'])
            let name = response['user']['name']

            let temp_html = `<div id="left-name-box">
                                <p class="left-p">이름</p>
                            </div>
                            <div id="right-name-box">
                                <input id="name-input" type="text" value=${name}>
                                <div class="desc-box">
                                    <div class="desc">사람들이 이름, 별명 또는 비즈니스 이름 등 회원님의 알려진 이름을 사용하여 회원님의 계정을 찾을 수 있도록 도와주세요.</div>
                                    <div id="div1"></div>
                                    <div class="desc">이름은 14일 안에 두 번만 변경할 수 있습니다.</div>
                                </div>
                            </div>`
            $('#name-box').append(temp_html)
        }
    });
   $.ajax({
        type: 'GET',
        url: '/users',
        data: {},
        success: function (response) {
            console.log(response['user'])
            let nickname = response['user']['nickname']

            let temp_html = `<div id="left-user-nickname-box">
                                <p class="left-p">사용자 이름</p>
                            </div>
                            <div id="right-user-nickname-box">
                                <input id="nickname-input" type="text" value=${nickname}>
                                <div class="desc-box">
                                    <div class="desc">대부분의 경우 14일 이내에 사용자 이름을 다시 15_ya(으)로 변경할 수 있습니다.</div>
                                </div>
                            </div>`
            $('#user-nickname-box').append(temp_html)
        }
    });
   $.ajax({
        type: 'GET',
        url: '/users',
        data: {},
        success: function (response) {
            console.log(response['user'])
            let phone_number = response['user']['phone_number']

            let temp_html = `<div id="left-phone-number-box">
                                <p class="left-p">전화번호</p>
                            </div>
                            <div id="right-phone-number-box">
                                <input id="phone-number-input" class="input-box" type="text" value=${phone_number}>
                            </div>`
            $('#phone-number-box').append(temp_html)
        }
    });
   $.ajax({
        type: 'GET',
        url: '/users',
        data: {},
        success: function (response) {
            console.log(response['user'])
            let status_message = response['user']['status_message']

            let temp_html = `<div id="left-status-message-box">
                                <p class="left-p">상태 메세지</p>
                            </div>
                            <div id="right-status-message-box">
                                <input id="status-message-input" type="text" value=${status_message}>
                            </div>`
            $('#status-message-box').append(temp_html)
        }
    });
});

function save_profile() {
    let name = $('#name-input').val()
    let nickname = $('#nickname-input').val()
    let phone_number = $('#phone-number-input').val()
    let status_message = $('#status-message-input').val()



    $.ajax({
        type: 'POST',
        url: '/users',
        data: {name_give: name, nickname_give: nickname, phone_number_give: phone_number, status_message_give: status_message},
        success: function (response) {
            alert(response['msg'])
            window.location.reload()
        }
    });
}