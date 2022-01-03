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
    if (currentIdx < slideCount - 8) {
        moveSlide(currentIdx + 1)
    }
});
prevBtn.addEventListener('click', function () {
    if (currentIdx > 0) {
        moveSlide(currentIdx - 1);
    }
});

function dropStoryOffList() {
    $.ajax({
        type: 'POST',
        url: '/off-list/drop',
        data: {},
    })
}