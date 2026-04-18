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
