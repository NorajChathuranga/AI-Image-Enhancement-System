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
    });
    return response.data;
  } catch (error) {
    throw new Error(parseError(error, "Unable to download enhanced image."));
  }
}
