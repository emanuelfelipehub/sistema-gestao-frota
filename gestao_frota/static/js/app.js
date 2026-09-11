document.addEventListener('DOMContentLoaded', function () {
  var toggle = document.querySelector('[data-menu-toggle]');
  var sidebar = document.querySelector('.sidebar');

  if (toggle && sidebar) {
    toggle.addEventListener('click', function () {
      sidebar.classList.toggle('is-open');
    });

    document.addEventListener('click', function (event) {
      var isClickInside = sidebar.contains(event.target) || toggle.contains(event.target);
      if (!isClickInside && sidebar.classList.contains('is-open')) {
        sidebar.classList.remove('is-open');
      }
    });
  }
});
