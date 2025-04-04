"use client";

import { useState } from "react";
import Image from "next/image";
import { Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Spinner } from "@/components/ui/spinner";
import { toast } from "sonner";

interface ImageUploaderProps {
  initialImageUrl?: string;
  onImageUploaded: (url: string) => void;
  label?: string;
  height?: string;
  maxWidth?: string;
}

export function ImageUploader({
  initialImageUrl = "/eventplaceholder.png",
  onImageUploaded,
  label = "Image",
  height = "400px",
  maxWidth = "100%",
}: ImageUploaderProps) {
  const [imageUrl, setImageUrl] = useState<string>(initialImageUrl);
  const [isUploading, setIsUploading] = useState<boolean>(false);

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];

      // Validate file type
      if (!file.type.startsWith("image/")) {
        toast.error("Please upload an image file");
        return;
      }

      // Validate file size (5MB max)
      if (file.size > 5 * 1024 * 1024) {
        toast.error("Image size should be less than 5MB");
        return;
      }

      try {
        setIsUploading(true);

        // Create FormData to send file
        const formData = new FormData();
        formData.append("file", file);

        // Upload to S3 via our API route
        const response = await fetch("/api/upload", {
          method: "POST",
          body: formData,
        });

        // Try to get response as text first for debugging
        const responseText = await response.text();

        // Parse the response if it's valid JSON
        let data;
        try {
          data = JSON.parse(responseText);
        } catch (jsonError) {
          console.error("Error parsing response as JSON:", jsonError);
          throw new Error("Invalid response format from server");
        }

        if (!response.ok) {
          throw new Error(
            data.error || `Upload failed with status: ${response.status}`
          );
        }

        if (!data.url) {
          throw new Error("No URL returned from server");
        }

        setImageUrl(data.url);
        onImageUploaded(data.url);
        toast.success("Image uploaded successfully");
      } catch (err) {
        console.error("Image upload error:", err);
        toast.error(
          err instanceof Error ? err.message : "Failed to upload image"
        );
      } finally {
        setIsUploading(false);
      }
    }
  }

  return (
    <div className="space-y-4">
      {label && <Label className="font-bold">{label}</Label>}

      {/* Main image display */}
      <div
        className="relative bg-primary-foreground dark:bg-secondary border border-1 rounded-lg"
        style={{
          minHeight: height,
          maxWidth: maxWidth,
        }}
      >
        <Image
          src={imageUrl}
          alt="Uploaded Image"
          fill
          className="rounded-lg object-contain"
        />
        <div className="absolute bottom-4 right-4 flex gap-2">
          <Button
            variant="outline"
            className="relative"
            type="button"
            disabled={isUploading}
            onClick={() => {
              // Trigger the hidden file input click
              const fileInput = document.getElementById("image-upload");
              if (fileInput) fileInput.click();
            }}
          >
            {isUploading ? (
              <Spinner className="mr-2 h-4 w-4" />
            ) : (
              <Upload className="mr-2 h-4 w-4" />
            )}
            {isUploading ? "Uploading..." : "Upload Image"}
          </Button>
          <input
            id="image-upload"
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handleFileChange}
          />
        </div>
      </div>

      {/* Success message when image is uploaded */}
      {imageUrl !== initialImageUrl &&
        imageUrl.includes("s3.amazonaws.com") && (
          <div className="mt-2">
            <p className="text-xs text-muted-foreground">
              Image uploaded successfully
            </p>
          </div>
        )}
    </div>
  );
}
