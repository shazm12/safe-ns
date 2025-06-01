"use server";
import { ModerationType, ModeratedContent } from "@/lib/types";

const API_URL = "http://localhost:8000/moderate";

export async function moderateContent(
  type: ModerationType,
  content: string | File
): Promise<Object> {
  try {
    let response;
    const formData = new FormData();

    if (type === "image") {
      if (content instanceof File) {
        formData.append("image", content, content.name || "image.png");
      } else if (typeof content === "string") {
        // Handle base64 string
        const base64Data = content.split(",")[1];
        const binaryData = atob(base64Data);
        const bytes = new Uint8Array(binaryData.length);
        for (let i = 0; i < binaryData.length; i++) {
          bytes[i] = binaryData.charCodeAt(i);
        }

        // Determine MIME type from base64 prefix or default to PNG
        const mimeMatch = content.match(/^data:([^;]+);base64,/);
        const mimeType = mimeMatch ? mimeMatch[1] : "image/png";
        const extension = mimeType.split("/")[1] || "png";

        const blob = new Blob([bytes], { type: mimeType });
        formData.append("image", blob, `image.${extension}`);
      } else {
        throw new Error(
          "Invalid image content type. Expected File or base64 string."
        );
      }
    } else {
      if (typeof content !== "string") {
        throw new Error("Text content must be a string.");
      }
      formData.append("text", content);
    }

    response = await fetch(API_URL, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(
        `Failed to moderate content: ${response.status} ${response.statusText}`
      );
    
    }
    
    const data = await response.json();
    const result = data?.result; 
    return result;
    
  } catch (error) {
    console.error("Error moderating content:", error);
    throw new Error(
      `Failed to moderate content: ${
        error instanceof Error ? error.message : "Unknown error"
      }`
    );
  }
}
