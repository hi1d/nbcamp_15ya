const slides = document.querySelector('.img-slide');
const slide = document.querySelectorAll('._img');
let currentIdx = 0;
const slideCount = slide.length;
const prevBtn = document.querySelector('#prev');
const slideWidth = 17;
const nextBtn = document.querySelector('#next');

    slides.style.width = (slideWidth * slideCount) + 'rem';

const prevPage = document.getElementById('prev').alt
const nextPage = document.getElementById('next').alt
const imgBorder = document.querySelector('.story-off')

function moveSlide(num) {
    slides.style.left = -num * 17 + 'rem';
    currentIdx = num;
}

nextBtn.addEventListener('click', function () {
    if (currentIdx < slideCount - 1) {
        moveSlide(currentIdx + 1)
    }
    else if (currentIdx == slideCount -1) {
        window.location.href = nextPage
    }
});
prevBtn.addEventListener('click', function () {
    if (currentIdx > 0) {
        moveSlide(currentIdx - 1);
    }
    else if (currentIdx == 0) {
        window.location.href = prevPage
    }
});

