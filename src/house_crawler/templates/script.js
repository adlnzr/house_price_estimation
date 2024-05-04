const sliderContainer = document.querySelector('.slider-container');
let currentIndex = 0;
let interval;

const imageUrls = [
    'image1.jpg',
    'image2.jpg',
    'image3.jpg',
    'image4.jpg',
    'image5.jpg',
    'image6.jpg',
    'image7.jpg',
    'image8.jpg',
    'image9.jpg',
    'image10.jpg'
];

function createImageSlide(url) {
    const slide = document.createElement('div');
    slide.classList.add('slider-image');
    slide.style.backgroundImage = `url(${url})`;
    sliderContainer.appendChild(slide);
}

function startSlider() {
    interval = setInterval(() => {
        currentIndex++;

        if (currentIndex === imageUrls.length) {
            currentIndex = 0;
        }

        sliderContainer.style.transform = `translateX(-${currentIndex * 100}%)`;
    }, 3000);
}

function stopSlider() {
    clearInterval(interval);
}

imageUrls.forEach(url => createImageSlide(url));
startSlider();

sliderContainer.addEventListener('mouseenter', stopSlider);
sliderContainer.addEventListener('mouseleave', startSlider);