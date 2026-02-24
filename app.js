const STORAGE_KEY = "language-app-cards";

const form = document.getElementById("vocab-form");
const sourceInput = document.getElementById("source-word");
const targetInput = document.getElementById("target-word");
const notesInput = document.getElementById("notes");
const list = document.getElementById("vocab-list");
const emptyState = document.getElementById("empty-state");
const clearAllBtn = document.getElementById("clear-all");

const quizPrompt = document.getElementById("quiz-prompt");
const quizForm = document.getElementById("quiz-form");
const quizAnswer = document.getElementById("quiz-answer");
const quizFeedback = document.getElementById("quiz-feedback");
const quizScore = document.getElementById("quiz-score");
const newQuestionBtn = document.getElementById("new-question");

let cards = loadCards();
let currentQuestion = null;
let correctCount = 0;
let attempts = 0;

function loadCards() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
  } catch {
    return [];
  }
}

function saveCards() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(cards));
}

function renderCards() {
  list.innerHTML = "";
  emptyState.style.display = cards.length ? "none" : "block";

  cards.forEach((card, index) => {
    const item = document.createElement("li");
    item.className = "vocab-item";

    const details = document.createElement("div");
    details.innerHTML = `
      <div class="wordpair">${card.source} → ${card.target}</div>
      ${card.notes ? `<div class="notes">${card.notes}</div>` : ""}
    `;

    const removeBtn = document.createElement("button");
    removeBtn.className = "ghost";
    removeBtn.textContent = "Delete";
    removeBtn.addEventListener("click", () => {
      cards.splice(index, 1);
      saveCards();
      renderCards();
      setNewQuestion();
    });

    item.append(details, removeBtn);
    list.appendChild(item);
  });
}

function updateScore() {
  quizScore.textContent = `Score: ${correctCount} / ${attempts}`;
}

function setNewQuestion() {
  quizFeedback.textContent = "";
  quizAnswer.value = "";

  if (!cards.length) {
    currentQuestion = null;
    quizPrompt.textContent = "Add at least one card to start quizzing.";
    return;
  }

  const randomCard = cards[Math.floor(Math.random() * cards.length)];
  currentQuestion = randomCard;
  quizPrompt.textContent = `Translate: ${randomCard.source}`;
}

form.addEventListener("submit", (event) => {
  event.preventDefault();

  const source = sourceInput.value.trim();
  const target = targetInput.value.trim();
  const notes = notesInput.value.trim();

  if (!source || !target) return;

  cards.push({ source, target, notes });
  saveCards();
  renderCards();
  setNewQuestion();

  form.reset();
  sourceInput.focus();
});

quizForm.addEventListener("submit", (event) => {
  event.preventDefault();
  if (!currentQuestion) return;

  attempts += 1;
  const guess = quizAnswer.value.trim().toLowerCase();
  const expected = currentQuestion.target.trim().toLowerCase();

  if (guess === expected) {
    correctCount += 1;
    quizFeedback.textContent = "✅ Correct!";
    setNewQuestion();
  } else {
    quizFeedback.textContent = `Not yet — correct answer: ${currentQuestion.target}`;
  }

  updateScore();
});

newQuestionBtn.addEventListener("click", setNewQuestion);

clearAllBtn.addEventListener("click", () => {
  cards = [];
  saveCards();
  renderCards();
  setNewQuestion();
  correctCount = 0;
  attempts = 0;
  updateScore();
});

renderCards();
setNewQuestion();
updateScore();
