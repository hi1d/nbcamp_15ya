const slides = document.querySelector('.img-slide');
const slide = document.querySelectorAll('._img');
let currentIdx = 0;
const slideCount = slide.length;
const prevBtn = document.querySelector('#prev');
const slideWidth = 17;
const nextBtn = document.querySelector('#next');

slides.style.width = (slideWidth * slideCount) + 'rem';

const prevPage = document.getElementById('prev').alt;
const nextPage = document.getElementById('next').alt;

function moveSlide(num) {
    slides.style.left = -num * 17 + 'rem';
    currentIdx = num;
}

nextBtn.addEventListener('click', function () {
    if (currentIdx < slideCount - 1) {
        moveSlide(currentIdx + 1)
    } else if (currentIdx == slideCount - 1) {

        let offId = $('#user-nick').html()
        let offProfile = $('#user-profile').attr('src')
        let offImg = $('._img').attr('src')
        let form_data = new FormData()

        form_data.append('id', offId)
        form_data.append('profile', offProfile)
        form_data.append('story_img_url',offImg)

        $.ajax({
            type: 'POST',
            url: '/off-list/add',
            data: form_data,
            cache: false,
            contentType: false,
            processData: false,
        });
        window.location.href = nextPage
    }
})
;
prevBtn.addEventListener('click', function () {
    if (currentIdx > 0) {
        moveSlide(currentIdx - 1);
    } else if (currentIdx == 0) {
        window.location.href = prevPage
    }
});
