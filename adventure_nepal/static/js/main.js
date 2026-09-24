document.addEventListener("DOMContentLoaded", () => {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (window.AOS) AOS.init({ duration: 700, once: true, disable: reduceMotion });

  if (window.Swiper && document.querySelector(".heroSwiper")) {
    new Swiper(".heroSwiper", {
      slidesPerView: 1,
      spaceBetween: 24,
      loop: true,
      autoplay: reduceMotion ? false : { delay: 4000, disableOnInteraction: false },
      pagination: { el: ".heroSwiper .swiper-pagination", clickable: true },
      breakpoints: { 768: { slidesPerView: 2 }, 1024: { slidesPerView: 3 } },
    });
  }

  if (window.Swiper && document.querySelector(".testimonialSwiper")) {
    new Swiper(".testimonialSwiper", {
      slidesPerView: 1,
      spaceBetween: 20,
      pagination: { el: ".testimonialSwiper .swiper-pagination", clickable: true },
      breakpoints: { 768: { slidesPerView: 2 }, 1024: { slidesPerView: 3 } },
    });
  }

  // Navbar: solid after scrolling; solid while the mobile menu is open
  const navbar = document.getElementById("mainNavbar");
  if (navbar) {
    const onScroll = () => navbar.classList.toggle("scrolled", window.scrollY > 60);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    const menu = document.getElementById("mainNav");
    if (menu) {
      menu.addEventListener("show.bs.collapse", () => navbar.classList.add("menu-open"));
      menu.addEventListener("hidden.bs.collapse", () => navbar.classList.remove("menu-open"));
    }
  }

  // Hero background rotation (paused for reduced-motion users)
  const heroSlides = document.querySelectorAll(".hero-slide");
  if (heroSlides.length > 1 && !reduceMotion) {
    let current = 0;
    setInterval(() => {
      heroSlides[current].classList.remove("active");
      current = (current + 1) % heroSlides.length;
      heroSlides[current].classList.add("active");
    }, 5500);
  }

  // Forms marked data-once: block double submits
  document.querySelectorAll("form[data-once]").forEach((form) => {
    form.addEventListener("submit", () => {
      const btn = form.querySelector('[type="submit"]');
      if (btn) setTimeout(() => { btn.disabled = true; }, 0);
    });
  });
});