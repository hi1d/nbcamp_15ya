function bookmark_show(email){
    $.ajax({
type: "POST",
url: "/bookmark_show",
data: {email_give:email},
success: function (response) {
    let bookmark = response['bookmark']
    $('.post-box').hide()
    $('.bookmark-box').show()
    $('.bookmark-box').empty()

            
    for(let i=0; i < bookmark.length; i++){
        let temp_html = `
        <img src="${bookmark[i]}">
        `
        $('#bookmark_box').append(temp_html)
    }
}
});
}

function mypage_feed(){
    $('.bookmark-box').hide()
    $('.post-box').show()
}
