function write_comment(index){
    let content = $(`#comment_write_${index}`).val()
    $.ajax({
        type: "POST",
        url: "/api/comment",
        data: {
            index_give: index,
            content_give : content
        },
        success: function (response) {
            if (response['result'] == 'success') {
                alert(response['msg'])
                window.location.replace('/api/feed_upload')
            }
            else{
                alert(response['msg'])
            }

        },
    })
}

function delete_comment(index, comment_index){
    $.ajax({
        type: "POST",
        url: "/api/comment_delete",
        data: {
            index_give : index,
            comment_index_give: comment_index
        },
        success: function (response) {
            if (response['result'] == 'success') {
                alert(response['msg'])
                window.location.replace('/api/feed_upload')
            }
            else{
                alert(response['msg'])
                window.location.replace('/api/feed_upload')
            }

        },
    })
}