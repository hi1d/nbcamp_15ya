$(document).ready(function(){
});

function save_profile() {
    let name = $('#name-input').val()
    let nickname = $('#nickname-input').val()
    let status_message = $('#status-message-input').val()



    $.ajax({
        type: 'POST',
        url: '/users_setting/',
        data: {name_give: name, nickname_give: nickname, status_message_give: status_message},
        success: function (response) {
            alert(response['msg'])
            window.location.reload()
        }
    });
}

function open_input(){
    $("#profile_image").trigger("click");
}

function change_profile(){
    let file = $('#profile_image')[0].files[0]
    let form_data = new FormData()

    form_data.append('file',file)
    $.ajax({
        type: 'POST',
        url: '/api/change_profile/',
        data: form_data,
        cache: false,
        contentType:false,
        processData: false,
        success: function (response) {
            alert(response['msg'])
            window.location.reload()
        }
    });
}
