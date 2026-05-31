let lastText = '';
const transcript = document.getElementById('transcript');
const guidance = document.getElementById('guidance');
const dotsEl = document.getElementById('dots-count');
const blurEl = document.getElementById('blur-score');

const sse = new EventSource('/events');
sse.onmessage = (e) => {
  const [text, guide, dots, blur, fps] = e.data.split('||');
  if (text && text !== lastText) {
    transcript.textContent = text;
    lastText = text;
    speakText(text);
  }
  guidance.textContent = guide || '';
  dotsEl.textContent = `Dots: ${dots}`;
  blurEl.textContent = `Blur: ${blur}  FPS: ${fps || '—'}`;
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

document.addEventListener('keydown', (e) => {
  if (e.code === 'Space' && e.target === document.body) {
    e.preventDefault();
    readAloud();
  }
  if (e.code === 'KeyR') repeatLast();
});