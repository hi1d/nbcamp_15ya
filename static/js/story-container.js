// story 업로드 모달
$( document ).ready(function() {
    $('.add-story-modal').hide();
});

function openModal() {
    $('.add-story-modal').show()
}

function closeModal() {
    $('.add-story-modal').hide()
}

//story 업로드
function addToStory() {
    let nickname = $('#give-url').attr('name')
    let url = $('#give-url').val()
    let profile = $('#give-url').attr('class')
    $.ajax({
        type: 'POST',
        url: '/upload/story',
        data: {'nickname': nickname , 'story_img': url, 'profile':profile},
        success: function (response) {
            alert(response['msg'])
            window.location.reload()
        }
    })
}


// 슬라이드
const slides = document.querySelector('#story-slide');
const slide = document.querySelectorAll('.story-wrapper');
let currentIdx = 0;
const slideCount = slide.length;
const prevBtn = document.querySelector('#prev');
const slideWidth = 4.3;
const slideMargin = 1.2;
const nextBtn = document.querySelector('#next');

slides.style.width = (slideWidth + slideMargin) * slideCount - slideMargin + 'rem';

function moveSlide(num) {
    slides.style.left = -num * 5.5 + 'rem';
    currentIdx = num;
}

nextBtn.addEventListener('click', function () {
    if (currentIdx < slideCount - 7) {
        moveSlide(currentIdx + 1)
    }
});
prevBtn.addEventListener('click', function () {
    if (currentIdx > 0) {
        moveSlide(currentIdx - 1);
    }
});
