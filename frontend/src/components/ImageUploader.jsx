import { useMemo } from "react";
import { useDropzone } from "react-dropzone";

function formatBytes(size) {
  if (size < 1024) {
    return `${size} B`;
  }
  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`;
  }
  return `${(size / (1024 * 1024)).toFixed(2)} MB`;
}

export default function ImageUploader({ selectedFile, onFileSelected, disabled }) {
  const dropzoneConfig = useMemo(
    () => ({
      accept: {
        "image/jpeg": [],
        "image/png": [],
        "image/webp": [],
      },
      maxSize: 10 * 1024 * 1024,
      multiple: false,
      onDropAccepted: (acceptedFiles) => {
        if (acceptedFiles.length > 0) {
          onFileSelected(acceptedFiles[0]);
        }
      },
    }),
    [onFileSelected]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone(dropzoneConfig);

  return (
    <section className="card">
      <h2>Upload Image</h2>
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? "dropzone-active" : ""} ${
          disabled ? "dropzone-disabled" : ""
        }`}
      >
        <input {...getInputProps()} disabled={disabled} />
        <p>Drop JPG, PNG, or WebP here</p>
        <p className="muted">or click to browse (max 10MB)</p>
      </div>

      {selectedFile ? (
        <div className="file-meta">
          <span>{selectedFile.name}</span>
          <span>{formatBytes(selectedFile.size)}</span>
        </div>
      ) : (
        <p className="muted">No file selected yet.</p>
      )}
    </section>
  );
}
