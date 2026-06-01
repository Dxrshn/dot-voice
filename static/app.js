let lastText = '';
const transcript = document.getElementById('transcript');
const guidance = document.getElementById('guidance');
const dotsEl = document.getElementById('dots-count');
const blurEl = document.getElementById('blur-score');
const fpsEl = document.getElementById('fps-display');
const confBar = document.getElementById('confidence-bar');
const confLabel = document.getElementById('confidence-label-val');

const sse = new EventSource('/events');
sse.onmessage = (e) => {
  const [text, guide, dots, blur, fps, conf] = e.data.split('||');
  if (text && text !== lastText) {
    transcript.textContent = text;
    lastText = text;
    speakText(text);
  }
  if (guide) guidance.textContent = guide;
  dotsEl.textContent = `Dots: ${dots}`;
  blurEl.textContent = `Blur: ${blur}`;
  fpsEl.textContent = `FPS: ${fps || '—'}`;

  if (conf !== undefined) {
    const pct = Math.round(parseFloat(conf) * 100);
    confBar.style.width = `${pct}%`;
    confBar.style.background = pct > 60 ? 'var(--accent)' : pct > 30 ? 'orange' : '#ff5252';
    confLabel.textContent = `${pct}%`;
  }
};

function speakText(text) {
  if (!text) return;
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const utt = new SpeechSynthesisUtterance(text);
    utt.rate = 0.95;
    window.speechSynthesis.speak(utt);
  }
}

function readAloud() { speakText(lastText); }
function repeatLast() { speakText(lastText); }

function toggleContrast() {
  document.body.classList.toggle('high-contrast');
}

let fontSize = 2;
function increaseFontSize() {
  fontSize = Math.min(fontSize + 0.2, 3.5);
  document.getElementById('transcript').style.fontSize = fontSize + 'rem';
}
function decreaseFontSize() {
  fontSize = Math.max(fontSize - 0.2, 1);
  document.getElementById('transcript').style.fontSize = fontSize + 'rem';
}

document.addEventListener('keydown', (e) => {
  if (e.code === 'Space' && e.target === document.body) {
    e.preventDefault();
    readAloud();
  }
  if (e.code === 'KeyR') repeatLast();
  if (e.code === 'KeyC') toggleContrast();
});
