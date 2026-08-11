(() => {
  const button = document.getElementById('grade');
  if (!button) return;

  button.addEventListener('click', () => {
    const quiz = button.closest('.quiz');
    const questions = [...quiz.querySelectorAll('.q')];
    let score = 0;

    questions.forEach((question) => {
      const correct = question.dataset.correct.split(',');
      const selected = [...question.querySelectorAll('input:checked')]
        .map((input) => input.value)
        .sort()
        .join(',');
      const isCorrect = selected === correct.slice().sort().join(',');

      question.classList.toggle('ok', isCorrect);
      question.classList.toggle('bad', !isCorrect);
      question.querySelectorAll('input').forEach((input) => {
        const label = input.closest('label');
        label.classList.remove('correct-answer', 'selected-wrong');
        if (correct.includes(input.value)) label.classList.add('correct-answer');
        else if (input.checked) label.classList.add('selected-wrong');
      });
      question.querySelector('.explain').style.display = 'block';
      if (isCorrect) score += 1;
    });

    const result = quiz.querySelector('#result');
    const message = score === questions.length ? quiz.dataset.success : quiz.dataset.retry;
    result.textContent = `${score}/${questions.length} richtig. ${message}`;
    result.style.display = 'block';
    result.scrollIntoView({ behavior: 'smooth' });
  });
})();
