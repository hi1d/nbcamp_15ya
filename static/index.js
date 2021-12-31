$(document).ready(function(){
    $.ajax({
        type: "GET",
        url: "/api/check_status",
        data: {
        },
        success: function (response) {
            if (response['result'] != true){
                $.removeCookie('15ya_token')
            }
        },
    });
});