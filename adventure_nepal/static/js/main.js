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
  // Navbar solid-on-scroll
  const navbar = document.getElementById("mainNavbar");
  if (navbar) {
    window.addEventListener("scroll", () => {
      navbar.classList.toggle("scrolled", window.scrollY > 60);
    });
  }
});

// Hero background carousel
  const heroSlides = document.querySelectorAll(".hero-slide");
  if (heroSlides.length > 1) {
    let currentSlide = 0;
    setInterval(() => {
      heroSlides[currentSlide].classList.remove("active");
      currentSlide = (currentSlide + 1) % heroSlides.length;
      heroSlides[currentSlide].classList.add("active");
    }, 5000);
  }