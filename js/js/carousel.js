
const images = [
    'examples/1.png',
    'examples/2.png',
    'examples/3.png',
    'examples/4.png',
    'examples/5.png',
    'examples/6.png',
    'examples/7.png'
];


const carousel = document.querySelector('.carousel');
const prevButton = document.querySelector('.prev-button');
const nextButton = document.querySelector('.next-button');

nextButton.style.display = "none";
prevButton.style.display = "none";

let currentSlide = 0;


images.forEach((imageUrl, index) => {
    const slide = document.createElement('div');
    slide.className = 'slide';
    var img = new Image();
    img.src = imageUrl;
    
    img.onload = () => {
        var resized_image = new Image();
        resized_image.src = resizeImage(img, "image/png", 500)
        resized_image.id = `carouselImg${index}`;
        slide.appendChild(resized_image);
        carousel.appendChild(slide)

    };
});



updateCarousel();

function updateCarousel() {
    carousel.style.transform = `translateX(${(images.length - currentSlide-4) * (500)}px)`;

    if (currentSlide === 0) {
        prevButton.disabled = true;
        prevButton.classList.add("gray");
    } else {
        prevButton.disabled = false;
        prevButton.classList.remove("gray");
    }

    if (currentSlide === images.length - 1) {
        nextButton.disabled = true;
        nextButton.classList.add("gray");
    } else {
        nextButton.disabled = false;
        nextButton.classList.remove("gray");
    }
}

prevButton.addEventListener('click', () => {
    currentSlide = (currentSlide - 1 + images.length) % images.length;
    updateCarousel();
});

nextButton.addEventListener('click', () => {
    currentSlide = (currentSlide + 1) % images.length;
    updateCarousel();
});