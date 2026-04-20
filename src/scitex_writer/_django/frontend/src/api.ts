/**
 * Writer API client — reads API_BASE from the rendered template.
 * Cloud deployment serves at /writer/; local at /.
 */

const root = document.querySelector<HTMLElement>(".writer-app");
export const API_BASE: string =
  (root?.dataset.apiBase as string | undefined) || "/";
export const PROJECT_DIR: string =
  (root?.dataset.projectDir as string | undefined) || "";

function withWd(url: string): string {
  const sep = url.includes("?") ? "&" : "?";
  return `${url}${sep}working_dir=${encodeURIComponent(PROJECT_DIR)}`;
}

export async function apiGet<T>(endpoint: string): Promise<T> {
  const url = withWd(API_BASE + endpoint);
  const response = await fetch(url);
  if (!response.ok)
    throw new Error(`${response.status} ${response.statusText}`);
  return (await response.json()) as T;
}

export async function apiPost<T>(endpoint: string, body: unknown): Promise<T> {
  const url = withWd(API_BASE + endpoint);
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok)
    throw new Error(`${response.status} ${response.statusText}`);
  return (await response.json()) as T;
}

export async function apiDelete<T>(endpoint: string): Promise<T> {
  const url = withWd(API_BASE + endpoint);
  const response = await fetch(url, { method: "DELETE" });
  if (!response.ok)
    throw new Error(`${response.status} ${response.statusText}`);
  return (await response.json()) as T;
}

// Endpoint shapes for convenience
export interface FileContent {
  path: string;
  content: string;
  name: string;
  extension: string;
}

export interface SectionEntry {
  name: string;
  path: string;
  filename: string;
}

export interface SectionsResponse {
  doc_type: string;
  sections: SectionEntry[];
}

export interface ProjectInfo {
  project_dir: string;
  project_name: string;
  doc_types: string[];
  has_shared: boolean;
}

export function getFile(path: string): Promise<FileContent> {
  return apiGet<FileContent>(`api/file?path=${encodeURIComponent(path)}`);
}

export function saveFile(
  path: string,
  content: string,
): Promise<{ success: boolean; path: string }> {
  return apiPost("api/file", { path, content });
}

export function listSections(docType: string): Promise<SectionsResponse> {
  return apiGet<SectionsResponse>(
    `api/sections?doc_type=${encodeURIComponent(docType)}`,
  );
}

export function projectInfo(): Promise<ProjectInfo> {
  return apiGet<ProjectInfo>("api/project-info");
}

export interface ScholarMeta {
  paper_id: string | null;
  title: string | null;
  authors: string[] | null;
  year: number | null;
  abstract: string | null;
  doi: string | null;
  arxiv_id: string | null;
  pmid: string | null;
  journal: string | null;
  short_journal: string | null;
  impact_factor: number | null;
  citation_count: number | null;
  is_open_access: boolean | null;
  oa_url: string | null;
}

export interface BibEntry {
  citation_key: string;
  entry_type: string;
  bibfile: string;
  doi: string | null;
  title: string | null;
  scholar?: ScholarMeta;
}

export interface ScholarStatus {
  scholar_importable: boolean;
  scholar_cli_on_path: boolean;
  library_root: string | null;
  index_db_present: boolean;
}
export interface ScholarLibraryEntry {
  paper_id: string;
  doi: string | null;
  arxiv_id: string | null;
  pmid: string | null;
  title: string | null;
  year: number | null;
  venue: string | null;
  is_oa?: boolean | null;
}
export interface ScholarLibraryResponse {
  entries: ScholarLibraryEntry[];
  count: number;
  offset?: number;
  reason?: string;
}

export function scholarStatus(): Promise<ScholarStatus> {
  return apiGet<ScholarStatus>("api/scholar/status");
}
export function scholarLibrary(
  limit = 200,
  offset = 0,
): Promise<ScholarLibraryResponse> {
  return apiGet<ScholarLibraryResponse>(
    `api/scholar/library?limit=${limit}&offset=${offset}`,
  );
}
export function scholarEnrich(): Promise<{ ok: boolean; log: string }> {
  return apiPost("api/scholar/enrich", {});
}
export function scholarAddToManuscript(
  paperId: string,
): Promise<{ ok: boolean; citation_key?: string; error?: string }> {
  return apiPost("api/scholar/add-to-manuscript", { paper_id: paperId });
}
export interface BibEntriesResponse {
  entries: BibEntry[];
  count: number;
}
export function bibEntries(): Promise<BibEntriesResponse> {
  return apiGet<BibEntriesResponse>("api/bib/entries");
}

export interface MediaEntry {
  name: string;
  path: string;
  label: string | null;
  insert: string;
  media_path?: string | null;
  media_ext?: string | null;
  thumbnail_url?: string | null;
}
export interface FiguresResponse {
  doc_type: string;
  figures: MediaEntry[];
}
export interface TablesResponse {
  doc_type: string;
  tables: MediaEntry[];
}
export function listFigures(docType: string): Promise<FiguresResponse> {
  return apiGet<FiguresResponse>(
    `api/figures?doc_type=${encodeURIComponent(docType)}`,
  );
}
export function listTables(docType: string): Promise<TablesResponse> {
  return apiGet<TablesResponse>(
    `api/tables?doc_type=${encodeURIComponent(docType)}`,
  );
}
