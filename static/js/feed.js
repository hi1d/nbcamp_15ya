$(document).ready(function(){
    init()
})


// 초기화 함수
function init(){
    $('#modal-container').hide()
    $('.modal_wrap_write_wrap').hide()
    $('#modal_upload').hide()
    $('#modal_next').show()
    $('.modal_wrap_content_wrap').show()
    $('.modal_wrap_header').show()
    $('.modal_wrap_show_wrap').hide()


    $('.modal_wrap').css({
        width: "700px",

    })
    $('.modal_wrap_write_content_left').css({
        "background-image": "none"
    })
    $('#modal_upload').css({
        color: '#fff'
    })
    $('#write_content').val(null)
}

// 모달 실행
$('#feed_upload').click(function() {
    $('#modal-container').show()
    $('.right_col').hide()
})

// 모달 종료

function close(){
    init()
    $('.right_col').show()
}

$('#modal_close').click(function() {
    close()
})

$('.modal_back').click(function() {
    close()
})

$('#modal-container').on('scroll touchmove mousewheel', function(event) {

    event.preventDefault();
    event.stopPropagation();
    return false;
  
  });



// 모달 이미지 올리기 & 올린 후 작성 모달변경
$('.modal_wrap_content_wrap')
            .on("dragover", dragOver)
            .on("dragleave", dragOver)
            .on("drop", uploadFiles)
        
            function dragOver(event){
                event.stopPropagation();
                event.preventDefault();

                if (event.type == "dragover") {
                    document.getElementById("modal_content_image").src ="../static/img/icon/imagegallery_on.png"
                } else {
                    document.getElementById("modal_content_image").src ="../static/img/icon/imagegallery.png"
                }
            }

            function uploadFiles(event){
                event.stopPropagation();
                event.preventDefault()

                event.dataTransfer = event.originalEvent.dataTransfer;
                files = event.target.files || event.dataTransfer.files;
                console.log("Test:" + files[0].name)

                if (files.length > 1) {
                    alert ('One File Only.');
                    return;
                }

                if (files[0].type.match(/image.*/)) {
                    $('.modal_wrap').css({
                        width: "960px",
  
                    })
                    $('.modal_wrap_write_content_left').css({
                        "background-image": "url("+ window.URL.createObjectURL(files[0]) + ")",
                        "outline": "none",
                        "background-size": "100%",
                        "background-position": "center",
                        "background-repeat": "no-repeat"
                    })
                    $('.modal_wrap_content_wrap').hide()
                    $('.modal_wrap_write_wrap').show()
                    
                    $('#modal_upload').show()
                    $('#modal_next').hide()
                    $('#modal_upload').css({
                        color: '#0095f6',
                        cursor: 'pointer',
                    })

                } else {
                    alert('이미지가 아닙니다.')
                    return;
                }
            }
    
$('#modal_upload').click(function(){
    let file = files[0] 
    let image = files[0].name
    let content = $('#write_content').val()
    let fd = new FormData()
    fd.append('file',file);
    fd.append('image',image);
    fd.append('content',content);

    $.ajax({
        url: '/api/feed_upload',
        data: fd,
        method: "POST",
        processData: false,
        contentType: false,
        success: function (response){
            if (response['result'] == 'success'){
                alert(response['msg'])
                window.location.replace('/')
            } else {
                alert('업로드 실패입니다.')
            }
        }
    })
})

function feed_delete(index){
    $.ajax({
        type: "POST",
        url: "/api/feed_delete",
        data: {
            index_give:index
        },
        success: function (response) {
            if (response['result'] == 'success') {
                alert(response['msg'])
                window.location.replace('/')
            }
            else{
                alert(response['msg'])
                window.location.replace('/')

            }
        },
    });
    
}


function bookmark(index){
    $.ajax({
    type: "POST",
    url: "/bookmark",
    data: {
        index_give:index
    },
    success: function (response) {
        if (response['result'] == 'success'){
            alert(response['msg'])
            window.location.replace('/')
        } else {
            alert('북마크 실패')
        }
    },
});
}

function feed_show(index){
    $.ajax({
        type: "POST",
        url: "/api/feed_show/",
        data: {
            index_give:index
        },
        success: function (response) {
            if (response['result'] == 'success'){
                let feed = JSON.parse(response['feed'])
                let image = feed['image']
                let profile_image = feed['profile_image']
                let author = feed['author']
                let email = feed['email']
                let content = feed['content']
                let comment = feed['comment']
                let like = feed['like']
                var index = feed['index']
                
                let user = response['user']
                let like_feed = user['like_feed']
                let user_email = user['email']
                let like_icon = "../static/img/icon/heart.svg"
                
                for (let i=0; i<like_feed.length;i++){
                    if (like_feed[i] == index){
                        like_icon = "../static/img/icon/heart_full.svg"
                    }
                }
                
                $('#modal-container').show()
                $('.modal_wrap_show_wrap').empty()
                $('.modal_wrap_show_wrap').show()
                $('.modal_wrap_content_wrap').hide()
                $('.right_col').hide()
                $('.modal_wrap_header').hide()
                $('.modal_wrap').css({
                    width: "960px",
                })
                if (email == user_email){
                    let temp_html = `
                
                    <img class="modal_wrap_write_content_left" src="${image}">
                        
                        <div class="modal_wrap_write_content_right">
                            <div class="write_header">
                                <img src="${profile_image}" alt="">
                                <div class="show_text">
                                    <p> ${author} </p>
                                    <span>${content}</span>
                                </div>
                            </div>
                            <hr>
                            <div class="feed_comment">
                            </div>
                            <div class="comment_info">
                                <div class="comment_icon">
                                <div>
                                    <img onclick='window.location.href = "/api/feed_like/${ index }"' src="${like_icon}" alt="">  
                                    <img onclick="feed_delete(${index})" src="../static/img/icon/delete.png">                          
                                </div>
                                    <img onclick="bookmark(${index})" src="../static/img/icon/bookmark.svg" alt="">
                                </div>
                                <p>좋아요 ${like}개</p>
                            </div>
        
                            <div class="write_comment">
                                <input type="text" id="comment_up" class="comment_write" placeholder="댓글 달기...">
                                <a onclick="write_comment(${index})">게시</a>
                            </div>
                        </div>`
                                       
                            $('.modal_wrap_show_wrap').append(temp_html)
                } else {
                    let temp_html = `
                
            <img class="modal_wrap_write_content_left" src="${image}">
                
                <div class="modal_wrap_write_content_right">
                    <div class="write_header">
                        <img src="${profile_image}" alt="">
                        <div class="show_text">
                            <p> ${author} </p>
                            <span>${content}</span>
                        </div>
                    </div>
                    <hr>
                    <div class="feed_comment">
                    </div>
                    <div class="comment_info">
                        <div class="comment_icon">
                        <div>
                            <img onclick='window.location.href = "/api/feed_like/${index}"' src="${like_icon}" alt="">  
                        </div>
                            <img onclick="bookmark(${index})" src="../static/img/icon/bookmark.svg" alt="">
                        </div>
                        <p>좋아요 ${like}개</p>
                    </div>

                    <div class="write_comment">
                        <input type="text" id="comment_up" class="comment_write" placeholder="댓글 달기...">
                        <a onclick="write_comment(${index})">게시</a>
                    </div>
                </div>`
                               
                    $('.modal_wrap_show_wrap').append(temp_html)
                }
                


                    

                    for (let i=0;i<comment.length; i++){
                        if (comment[i]['email'] == user_email){
                            temp_html2 = `
                            <div class=comment_user>
                                             <div>
                                                 <img src="${comment[i]['profile_image']}">
                                                 <span> ${comment[i]['author']} </span>
                                                 <p> ${comment[i]['content']} </p>
                                             </div>
                                             <a onclick="delete_comment(${index},${comment[i]['comment_index']})">삭제</a>
                                         </div>       
                            </div>                 
                                     `
                            $('.feed_comment').append(temp_html2)             
                        }else {
                        temp_html2 = `
                        <div class=comment_user>
                                         <div>
                                             <img src="${comment[i]['profile_image']}">
                                             <span> ${comment[i]['author']} </span>
                                             <p> ${comment[i]['content']} </p>
                                         </div>
                                     </div>       
                        </div>                 
                                 `
                        $('.feed_comment').append(temp_html2)
                        }
                    }
            } else {
                alert('불러오기 실패')
                window.location.reload()
            }
        },
    });
}
