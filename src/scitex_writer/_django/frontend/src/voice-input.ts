/**
 * OS / browser voice → text — a loosely-coupled Web Speech wrapper (ADR 0001).
 *
 * Deliberately ZERO PDF/annotation coupling: it only turns speech into text and
 * hands it to a callback. That keeps it a cheap future promotion into
 * `@scitex/ui` L1 if hub ever wants dictation (scitex-ui's guidance on #274) —
 * for now it lives writer-side with no second consumer (YAGNI).
 *
 * OS-level dictation already types into any <textarea>; this only adds an in-app
 * mic button for browsers exposing SpeechRecognition, and degrades to
 * `supported = false` (button hidden) everywhere else — it never throws.
 */

interface SpeechRecognitionAlternativeLike {
  transcript: string;
}
interface SpeechRecognitionResultLike {
  0: SpeechRecognitionAlternativeLike;
  isFinal: boolean;
}
interface SpeechRecognitionEventLike {
  resultIndex: number;
  results: {
    length: number;
    [index: number]: SpeechRecognitionResultLike;
  };
}
interface SpeechRecognitionLike {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  start(): void;
  stop(): void;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
  onend: (() => void) | null;
  onerror: (() => void) | null;
}
type SpeechRecognitionCtor = new () => SpeechRecognitionLike;

export interface VoiceInputOptions {
  /** Fired per recognition chunk; `isFinal` marks a committed phrase. */
  onResult: (text: string, isFinal: boolean) => void;
  /** Fired whenever listening starts/stops (incl. auto-stop). */
  onStateChange?: (listening: boolean) => void;
  lang?: string;
}

export interface VoiceInputHandle {
  readonly supported: boolean;
  readonly listening: boolean;
  toggle(): void;
  stop(): void;
}

function resolveCtor(): SpeechRecognitionCtor | null {
  const w = window as unknown as {
    SpeechRecognition?: SpeechRecognitionCtor;
    webkitSpeechRecognition?: SpeechRecognitionCtor;
  };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

export function createVoiceInput(opts: VoiceInputOptions): VoiceInputHandle {
  const Ctor = resolveCtor();
  let rec: SpeechRecognitionLike | null = null;
  let listening = false;

  const setListening = (value: boolean): void => {
    if (listening === value) return;
    listening = value;
    opts.onStateChange?.(value);
  };

  const stop = (): void => {
    rec?.stop();
    setListening(false);
  };

  const start = (): void => {
    if (!Ctor) return;
    rec = new Ctor();
    rec.lang = opts.lang ?? navigator.language ?? "en-US";
    rec.continuous = true;
    rec.interimResults = true;
    rec.onresult = (event) => {
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        opts.onResult(result[0].transcript, result.isFinal);
      }
    };
    rec.onend = () => setListening(false);
    rec.onerror = () => setListening(false);
    rec.start();
    setListening(true);
  };

  return {
    supported: Ctor !== null,
    get listening() {
      return listening;
    },
    toggle() {
      if (listening) stop();
      else start();
    },
    stop,
  };
}
