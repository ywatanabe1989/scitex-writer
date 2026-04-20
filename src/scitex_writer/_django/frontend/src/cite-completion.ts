/**
 * Monaco LaTeX `\cite{}` completion + hover providers.
 *
 * Ported from scitex-cloud's `_monaco-editor/init/CitationHover.ts`
 * and companion completion provider. Uses the writer's `api/bib/entries`
 * endpoint, which now returns scholar-enriched metadata when available.
 */
import { type BibEntry, bibEntries } from "./api";

const CACHE_TTL_MS = 60_000;

let cache: BibEntry[] | null = null;
let cacheTime = 0;
let inflight: Promise<BibEntry[]> | null = null;

async function fetchEntries(): Promise<BibEntry[]> {
  const now = Date.now();
  if (cache && now - cacheTime < CACHE_TTL_MS) return cache;
  if (inflight) return inflight;
  inflight = bibEntries()
    .then((r) => {
      cache = r.entries;
      cacheTime = Date.now();
      return cache;
    })
    .finally(() => {
      inflight = null;
    });
  return inflight;
}

/** Call after a user action that may have added/removed entries. */
export function invalidateCitationCache(): void {
  cache = null;
  cacheTime = 0;
}

const CITE_RE = /\\cite[tp]?\*?\{([^}]*)$/;

export function registerCiteProviders(monaco: any): void {
  monaco.languages.registerCompletionItemProvider("latex", {
    triggerCharacters: ["{", ","],
    provideCompletionItems: async (model: any, position: any) => {
      const line = model.getLineContent(position.lineNumber);
      const before = line.substring(0, position.column - 1);
      const m = before.match(CITE_RE);
      if (!m) return { suggestions: [] };
      const entries = await fetchEntries();
      const word = model.getWordUntilPosition(position);
      const range = {
        startLineNumber: position.lineNumber,
        endLineNumber: position.lineNumber,
        startColumn: word.startColumn,
        endColumn: word.endColumn,
      };
      const suggestions = entries.map((e) => ({
        label: e.citation_key,
        kind: monaco.languages.CompletionItemKind.Reference,
        detail: titleOf(e),
        documentation: { value: cardMarkdown(e), isTrusted: false },
        insertText: e.citation_key,
        range,
        filterText: filterTextOf(e),
      }));
      return { suggestions };
    },
  });

  monaco.languages.registerHoverProvider("latex", {
    provideHover: async (model: any, position: any) => {
      const line = model.getLineContent(position.lineNumber);
      const word = model.getWordAtPosition(position);
      if (!word) return null;
      const before = line.substring(0, position.column - 1);
      const after = line.substring(position.column - 1);
      if (!/\\cite[tp]?\*?\{[^}]*$/.test(before)) return null;
      if (!/^[^}]*\}/.test(after)) return null;
      const entries = await fetchEntries();
      const entry = entries.find((e) => e.citation_key === word.word);
      if (!entry) return null;
      return {
        range: {
          startLineNumber: position.lineNumber,
          endLineNumber: position.lineNumber,
          startColumn: word.startColumn,
          endColumn: word.endColumn,
        },
        contents: [{ value: cardMarkdown(entry) }],
      };
    },
  });
}

function titleOf(e: BibEntry): string {
  return e.scholar?.title || e.title || e.entry_type;
}

function filterTextOf(e: BibEntry): string {
  const parts = [e.citation_key];
  if (e.scholar?.title) parts.push(e.scholar.title);
  else if (e.title) parts.push(e.title);
  if (e.doi) parts.push(e.doi);
  return parts.join(" ");
}

function cardMarkdown(e: BibEntry): string {
  const s = e.scholar;
  const title = s?.title || e.title || e.citation_key;
  const lines = [`**${title}**`];
  if (s?.authors?.length) {
    const authors = s.authors.slice(0, 4).join(", ");
    const suffix = s.authors.length > 4 ? ", et al." : "";
    lines.push(`*${authors}${suffix}*`);
  }
  const meta: string[] = [];
  if (s?.year) meta.push(String(s.year));
  if (s?.short_journal || s?.journal) meta.push(s.short_journal || s.journal!);
  if (s?.impact_factor != null)
    meta.push(`IF ${Number(s.impact_factor).toFixed(1)}`);
  if (s?.citation_count != null) meta.push(`cited ${s.citation_count}×`);
  if (s?.is_open_access) meta.push("OA");
  if (meta.length) lines.push(meta.join(" · "));
  if (e.doi || s?.doi) lines.push(`DOI: \`${s?.doi || e.doi}\``);
  if (s?.abstract) lines.push("", s.abstract);
  return lines.join("\n\n");
}
