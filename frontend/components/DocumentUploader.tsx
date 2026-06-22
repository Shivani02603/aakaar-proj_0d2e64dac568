'use client';

import React, { useState } from 'react';

interface DocumentUploaderProps {
  sessionId: string;
}

export default function DocumentUploader({ sessionId }: DocumentUploaderProps) {
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [chunksIndexed, setChunksIndexed] = useState<number | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleFileUpload = async (file: File) => {
    setUploadProgress(0);
    setChunksIndexed(null);
    setErrorMessage(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', sessionId);

    try {
      const xhr = new XMLHttpRequest();
      xhr.open('POST', '/api/ai/ingest', true);

      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const progress = Math.round((event.loaded / event.total) * 100);
          setUploadProgress(progress);
        }
      };

      xhr.onload = () => {
        if (xhr.status === 200) {
          const response = JSON.parse(xhr.responseText);
          setChunksIndexed(response.chunks_indexed);
        } else {
          const errorResponse = JSON.parse(xhr.responseText);
          setErrorMessage(errorResponse.message || 'Failed to upload file.');
        }
      };

      xhr.onerror = () => {
        setErrorMessage('An error occurred during the file upload.');
      };

      xhr.send(formData);
    } catch (error) {
      setErrorMessage('An unexpected error occurred.');
    }
  };

  const handleFileDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const files = event.dataTransfer.files;
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  return (
    <div className="border border-dashed border-gray-300 rounded-md p-4">
      <div
        className="flex flex-col items-center justify-center h-32 bg-gray-100 rounded-md cursor-pointer"
        onDragOver={(event) => event.preventDefault()}
        onDrop={handleFileDrop}
      >
        <p className="text-gray-600">Drag and drop a file here</p>
        <p className="text-gray-400 text-sm">Accepted formats: .xlsx, .xls, .pdf, .docx</p>
      </div>
      <div className="mt-4">
        <label
          htmlFor="file-upload"
          className="block text-sm font-medium text-gray-700"
        >
          Or select a file
        </label>
        <input
          id="file-upload"
          type="file"
          accept=".xlsx,.xls,.pdf,.docx"
          className="mt-2 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border file:border-gray-300 file:text-sm file:font-medium file:bg-gray-50 file:text-gray-700 hover:file:bg-gray-100"
          onChange={handleFileSelect}
        />
      </div>
      {uploadProgress > 0 && uploadProgress < 100 && (
        <div className="mt-4">
          <div className="w-full bg-gray-200 rounded-full h-4">
            <div
              className="bg-blue-500 h-4 rounded-full"
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-600 mt-2">{uploadProgress}% uploaded</p>
        </div>
      )}
      {chunksIndexed !== null && (
        <div className="mt-4">
          <span className="inline-block bg-green-100 text-green-800 text-sm font-medium px-3 py-1 rounded-full">
            ✓ Indexed {chunksIndexed} chunks
          </span>
        </div>
      )}
      {errorMessage && (
        <div className="mt-4">
          <span className="inline-block bg-red-100 text-red-800 text-sm font-medium px-3 py-1 rounded-full">
            {errorMessage}
          </span>
        </div>
      )}
    </div>
  );
}