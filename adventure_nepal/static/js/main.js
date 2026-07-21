document.addEventListener("DOMContentLoaded", function () {
  AOS.init({ duration: 800, once: true });
  new Swiper(".heroSwiper", {
    slidesPerView: 1,
    spaceBetween: 24,
    loop: true,
    autoplay: { delay: 3500, disableOnInteraction: false },
    pagination: { el: ".swiper-pagination", clickable: true },
    breakpoints: { 768: { slidesPerView: 2 }, 1024: { slidesPerView: 3 } },
  });
});