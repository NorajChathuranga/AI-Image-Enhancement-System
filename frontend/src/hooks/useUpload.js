import { useCallback, useState } from "react";

import { submitEnhancement } from "../services/apiClient";

export function useUpload() {
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");

  const resetUploadState = useCallback(() => {
    setUploadProgress(0);
    setUploadError("");
  }, []);

  const uploadImage = useCallback(async (file) => {
    setUploadError("");
    setUploadProgress(0);
    setIsUploading(true);

    try {
      const payload = await submitEnhancement(file, (event) => {
        if (!event.total) {
          return;
        }
        const percent = Math.round((event.loaded / event.total) * 100);
        setUploadProgress(Math.max(0, Math.min(100, percent)));
      });

      setUploadProgress(100);
      return payload;
    } catch (error) {
      setUploadError(error.message);
      throw error;
    } finally {
      setIsUploading(false);
    }
  }, []);

  return {
    uploadImage,
    uploadProgress,
    isUploading,
    uploadError,
    resetUploadState,
    setUploadError,
  };
}
