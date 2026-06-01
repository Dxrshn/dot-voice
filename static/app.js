let lastText = '';
const transcript = document.getElementById('transcript');
const guidance = document.getElementById('guidance');
const dotsEl = document.getElementById('dots-count');
const blurEl = document.getElementById('blur-score');
const fpsEl = document.getElementById('fps-display');
const confBar = document.getElementById('confidence-bar');
const confLabel = document.getElementById('confidence-label-val');

let liveScanOn = false;
let lastGuidance = '';

let speechUnlocked = false;
function unlockSpeech() {
  if (speechUnlocked) return;
  if ('speechSynthesis' in window) {
    speak('DotVoice ready. Press D to read a built-in Braille sample, U to upload your own image, L to start live scanning, R to repeat, and S to hear status.');
    speechUnlocked = true;
  }
}
document.addEventListener('click', unlockSpeech);
document.addEventListener('keydown', unlockSpeech);

function speak(text) {
  if (!text) return;
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const utt = new SpeechSynthesisUtterance(text);
    utt.rate = 0.95;
    window.speechSynthesis.speak(utt);
  }
}
function speakText(text) { speak(text); }

const sse = new EventSource('/events');
sse.onmessage = (e) => {
  const [text, guide, dots, blur, fps, conf, doSpeak, toSpeak] = e.data.split('||');
  if (text && text !== lastText) {
    transcript.textContent = text;
    lastText = text;
  }
  if (doSpeak === '1' && toSpeak) {
    speak(toSpeak);
  }
  if (guide) {
    guidance.textContent = guide;
    lastGuidance = guide;
    if (guide.indexOf('Scan stopped') !== -1) {
      liveScanOn = false;
      document.getElementById('btn-scan').textContent = 'Start Live Scan';
    }
  }
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

function readAloud() {
  if (lastText) speak('Detected text: ' + lastText);
  else speak('No Braille has been detected yet.');
}
function repeatLast() { readAloud(); }

function speakStatus() {
  const scanState = liveScanOn ? 'Live scanning is on.' : 'Live scanning is off.';
  const g = lastGuidance ? lastGuidance : '';
  const t = lastText ? 'Last detected text: ' + lastText + '.' : 'No Braille detected yet.';
  speak(scanState + ' ' + g + ' ' + t);
}

function toggleScan() {
  fetch('/toggle_scan', { method: 'POST' })
    .then(r => r.json())
    .then(d => {
      liveScanOn = d.live_scan;
      document.getElementById('btn-scan').textContent = liveScanOn ? 'Stop Live Scan' : 'Start Live Scan';
      speak(liveScanOn
        ? 'Live scanning started. Point the camera at Braille. I will guide you, and stop once I have a clear reading.'
        : 'Live scanning stopped.');
    })
    .catch(() => {});
}

function readSample() {
  speak('Reading the built-in Braille sample.');
  fetch('/sample', { method: 'POST' })
    .then(r => r.json())
    .then(d => {
      if (d.error) { speak('Sample not found.'); return; }
      const txt = d.text || '(no text detected)';
      lastText = txt;
      transcript.textContent = txt;
      document.getElementById('upload-result').textContent = `Sample result: ${txt}`;
      speak('Detected text: ' + txt);
    })
    .catch(() => speak('Could not read the sample.'));
}

function triggerUpload() {
  document.getElementById('file-input').click();
}

function uploadImage() {
  const input = document.getElementById('file-input');
  const out = document.getElementById('upload-result');
  if (!input.files || !input.files[0]) return;
  out.textContent = 'Reading...';
  speak('Reading the uploaded Braille image.');
  const fd = new FormData();
  fd.append('image', input.files[0]);
  fetch('/upload', { method: 'POST', body: fd })
    .then(r => r.json())
    .then(d => {
      if (d.error) { out.textContent = 'Error: ' + d.error; speak('Sorry, that image could not be read.'); return; }
      const txt = d.text || '(no text detected)';
      out.textContent = `Result: ${txt}  (dots: ${d.dots}, confidence: ${d.confidence})`;
      lastText = txt;
      transcript.textContent = txt;
      speak('Detected text: ' + txt);
    })
    .catch(() => { out.textContent = 'Upload failed.'; speak('Upload failed. Please try again.'); });
}

function toggleContrast() {
  document.body.classList.toggle('high-contrast');
  speak('High contrast toggled.');
}

let fontSize = 2;
function increaseFontSize() {
  fontSize = Math.min(fontSize + 0.2, 3.5);
  transcript.style.fontSize = fontSize + 'rem';
  speak('Text size increased.');
}
function decreaseFontSize() {
  fontSize = Math.max(fontSize - 0.2, 1);
  transcript.style.fontSize = fontSize + 'rem';
  speak('Text size decreased.');
}

document.addEventListener('keydown', (e) => {
  if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) return;
  if (e.code === 'Space') { e.preventDefault(); readAloud(); }
  else if (e.code === 'KeyR') repeatLast();
  else if (e.code === 'KeyC') toggleContrast();
  else if (e.code === 'KeyL') toggleScan();
  else if (e.code === 'KeyU') triggerUpload();
  else if (e.code === 'KeyS') speakStatus();
  else if (e.code === 'KeyD') readSample();
});