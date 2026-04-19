import { useEffect, useState } from "react";

export function useImageCompare(selectedFile, enhancedBlob) {
  const [beforeUrl, setBeforeUrl] = useState("");
  const [afterUrl, setAfterUrl] = useState("");

  useEffect(() => {
    if (!selectedFile) {
      setBeforeUrl("");
      return undefined;
    }

    const objectUrl = URL.createObjectURL(selectedFile);
    setBeforeUrl(objectUrl);
    return () => {
      URL.revokeObjectURL(objectUrl);
    };
  }, [selectedFile]);

  useEffect(() => {
    if (!enhancedBlob) {
      setAfterUrl("");
      return undefined;
    }

    const objectUrl = URL.createObjectURL(enhancedBlob);
    setAfterUrl(objectUrl);
    return () => {
      URL.revokeObjectURL(objectUrl);
    };
  }, [enhancedBlob]);

  return { beforeUrl, afterUrl };
}
