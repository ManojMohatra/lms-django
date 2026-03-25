
document.addEventListener("DOMContentLoaded", function () {
    const stars = document.querySelectorAll(".star");
    const ratingInput = document.getElementById("ratingInput");

    if (!stars.length || !ratingInput) return;
    let selectedRating = 0;

    stars.forEach(star => {
        star.addEventListener("mouseover", function () {
            let value = this.getAttribute("data-value");

            stars.forEach(s => {
                s.classList.remove("hover");
                if (s.getAttribute("data-value") <= value) {
                    s.classList.add("hover");
                }
            });
        });

        star.addEventListener("mouseout", function () {
            stars.forEach(s => s.classList.remove("hover"));
        });

        star.addEventListener("click", function () {
            selectedRating = this.getAttribute("data-value");
            ratingInput.value = selectedRating;

            stars.forEach(s => {
                s.classList.remove("selected");
                if (s.getAttribute("data-value") <= selectedRating) {
                    s.classList.add("selected");
                }
            });
        });
    });


    stars.forEach(star => {
    star.addEventListener('click', () => {
        let value = star.getAttribute('data-value');
        ratingInput.value = value;

        stars.forEach(s => s.classList.remove('active'));

        for (let i = 0; i < value; i++) {
            stars[i].classList.add('active');
        }
    });
});

    // Prevent submit without rating
    const form = document.getElementById("reviewForm");
    if (form) {
        form.addEventListener("submit", function (e) {
            if (!ratingInput.value) {
                e.preventDefault();
                alert("Please select a rating!");
            }
        });
    }

});


// ===== Enrollment Chart =====
const enrollLabels = JSON.parse(document.getElementById('enroll-labels').textContent);
const enrollData = JSON.parse(document.getElementById('enroll-data').textContent);

new Chart(document.getElementById('enrollmentChart'), {
    type: 'line',
    data: {
        labels: enrollLabels,
        datasets: [{
            label: 'Enrollments',
            data: enrollData,
            fill: true,
            tension: 0.3
        }]
    }
});


// ===== Performance Chart =====
const quizAvg = JSON.parse(document.getElementById('quiz-avg').textContent);
const assignmentAvg = JSON.parse(document.getElementById('assignment-avg').textContent);

new Chart(document.getElementById('performanceChart'), {
    type: 'bar',
    data: {
        labels: ['Quiz', 'Assignment'],
        datasets: [{
            label: 'Average Score',
            data: [quizAvg, assignmentAvg]
        }]
    }
});