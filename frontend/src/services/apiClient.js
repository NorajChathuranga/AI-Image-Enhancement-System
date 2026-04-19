import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
});

function parseError(error, fallback) {
  if (axios.isAxiosError(error)) {
    return error.response?.data?.detail ?? fallback;
  }
  return fallback;
}

async function parseDownloadError(error, fallback) {
  if (!axios.isAxiosError(error)) {
    return fallback;
  }

  if (!error.response) {
    return error.message || fallback;
  }

  const responseData = error.response.data;
  if (responseData instanceof Blob) {
    try {
      const text = await responseData.text();
      if (text) {
        try {
          const parsed = JSON.parse(text);
          if (typeof parsed?.detail === "string") {
            return parsed.detail;
          }
        } catch {
          return text;
        }
      }
    } catch {
      return fallback;
    }
  }

  return error.response?.data?.detail ?? error.message ?? fallback;
}

export async function submitEnhancement(file, onUploadProgress) {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await apiClient.post("/v1/enhance", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress,
    });
    return response.data;
  } catch (error) {
    throw new Error(parseError(error, "Unable to submit enhancement request."));
  }
}

export async function fetchJobStatus(jobId) {
  try {
    const response = await apiClient.get(`/v1/status/${jobId}`);
    return response.data;
  } catch (error) {
    throw new Error(parseError(error, "Unable to fetch job status."));
  }
}

export async function fetchJobResult(jobId, format = "webp") {
  try {
    const response = await apiClient.get(`/v1/result/${jobId}`, {
      responseType: "blob",
      params: { format },
      timeout: Number(import.meta.env.VITE_DOWNLOAD_TIMEOUT_MS ?? 600000),
    });
    return response.data;
  } catch (error) {
    const message = await parseDownloadError(error, "Unable to download enhanced image.");
    throw new Error(message);
  }
}
