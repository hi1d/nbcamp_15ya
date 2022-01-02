$(document).ready(function() {
    
    searching()
    right_col_fixed()
    $(window).resize(function(){
        right_col_fixed()
    $('#search_input').empty()
    });
    
    
    //search_box_view
    let search_input = $('#search_input')

    // search_box_display
    search_input.click(function () {
        $('.search_box').css('display', 'block');
    });

    $('#header , .nav_items, section').click(function () {
        $('.search_box').css('display', 'none');
    });

    // user_list print
    search_input.on('input keyup paste change propertychange', function () {
        var search_keyword = $(this).val().toLowerCase();
        if (search_keyword === '') {
            $('.search_box').css('overflow-y', 'hidden');
            $('.recent_searches_box').show();
            $('.search_result_list').hide();
        } else {
            $('.search_box').css('overflow-y', 'scroll');
            $('.recent_searches_box').hide();
            $('.search_result_list').show();
            // searching_result(search_keyword)
        }
    });
    search_input.on("keyup", function() {
        var search_keyword = $(this).val().toLowerCase();
        $("#search_result_list a").filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(search_keyword) > -1)
        });
    });

    function searching() {
        $.ajax({
            type: 'GET',
            url: '/users',
            data: {},
            success: function (response) {
                let users = response['users']
                for (let i = 0; i < users.length; i++) {
                    let user_proflie = users[i]['profile_image'] //이미지 주소 맞는지 확인 요청
                    let user_name = users[i]['nickname']
                    let user_email = users[i]['email']
                    let search_result_html = `<a href=/mypage/${user_email }>
                                                    <div class="info">
                                                        <div class="user">
                                                            <div class="profile_pic">
                                                                <img src="${user_proflie}" alt="${user_name}_proflie">
                                                            </div>
                                                            <p class="username">${user_name}</p>
                                                        </div>
                                                    </div>
                                                    </a>`
                    $('#search_result_list').append(search_result_html)
                }
            }
        });
    };

    // right column fixed
    function right_col_fixed(){
            var body_width = $('body').width()
            var main_width = $('section.wrap main').width()
            var left_col = $('.left_col').width()
            var pixed_size = (body_width - main_width)/2 + left_col
            if (pixed_size < left_col){
                $('.right_col').hide()
            } else{
                $('.right_col').css('left', pixed_size)
                $('.right_col').show()
            }
    };
});
