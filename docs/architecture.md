# DotVoice — Architecture

## Pipeline Overview

```
Camera Frame
    │
    ▼
┌─────────────────┐
│   preprocess    │  grayscale → perspective correct → lighting normalize → CLAHE
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  detect_dots    │  SimpleBlobDetector + connected-components fallback
└────────┬────────┘
         │ (x, y, r) dot centers
         ▼
┌─────────────────┐
│  segment_grid   │  estimate unit u → cluster cols/rows → assign dot positions 1-6
└────────┬────────┘
         │ list of dot-sets per cell
         ▼
┌─────────────────┐
│  decode_cells   │  Grade-1 Braille map → English text (capital/number state machine)
└────────┬────────┘
         │ text string
         ▼
┌─────────────────┐
│ multi-frame vote│  Counter over last 5 frames → stable text
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GuidanceEngine  │  quality metrics → spoken camera cue OR read text
└────────┬────────┘
         │
         ▼
  TTS (pyttsx3)     Web Speech API (browser)
```

## Camera Guidance State Machine

```
coverage too low  →  "No Braille detected. Move camera over the page."
blur too low      →  "Hold steady."
dots too few      →  "Move closer."
coverage too high →  "Move back."
text unstable     →  "Adjust camera for clearer Braille."
text stable (K=4) →  "Braille detected." + read text aloud
```

## Key Design Decisions

- **Unit estimation:** The base unit `u` is derived from the median nearest-neighbor distance between detected dots. All grid thresholds are ratios of `u`, making the pipeline resolution- and distance-agnostic.
- **Two-path detection:** SimpleBlobDetector runs first; if it finds nothing, an Otsu-threshold + connected-components fallback runs. This handles both clean and noisy inputs.
- **Multi-frame voting:** The last 5 decoded strings are majority-voted before output. This eliminates single-frame misreads without adding latency.
- **Eyes-free guidance:** Quality metrics (blur, coverage, dot count) drive spoken cues so a blind user can aim the camera without seeing the screen.
- **Offline TTS:** pyttsx3 runs fully offline on a worker thread. Browser Web Speech API is used as the primary in the web UI, with pyttsx3 as fallback.
