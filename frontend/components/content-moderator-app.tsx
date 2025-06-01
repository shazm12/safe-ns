"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Header } from "@/components/header";
import { InputSection } from "@/components/input-section";
import { ResultsSection } from "@/components/results-section";
import { ModerationType, ModeratedContent } from "@/lib/types";
import { moderateContent } from "@/actions/moderateContent";
import { toast } from "sonner";

interface SafetyResult {
  is_toxic: boolean;
  summary: string;
}

export function ContentModeratorApp() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState<ModeratedContent | null>(null);

  const handleSubmit = async (type: ModerationType, content: string | File) => {
    try {
      setIsAnalyzing(true);

      let moderationInput: string | File;

      // Convert image File to base64 if needed by your API
      if (type === "image" && content instanceof File) {
        moderationInput = await fileToBase64(content);
      } else {
        moderationInput = content;
      }

      const result = await moderateContent(type, moderationInput);

      const isSafe = !result?.is_toxic;
      const summary = result?.summary;
      const confidence = result?.confidence * 100;

      setResults({
        type,
        isSafe,
        confidence: confidence,
        content:
          type === "text"
            ? (content as string)
            : URL.createObjectURL(content as File),
        summary,
      });
    } catch (error) {
      toast.error("Failed in analyzing content: Something went wrong", {
        id: "error ",
      });
      console.error("Error analyzing content:", error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Helper function to convert File to base64
  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = (error) => reject(error);
    });
  };
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-950 py-12 px-4 sm:px-6">
      <div className="max-w-4xl mx-auto">
        <Header />

        <Card className="mt-8 p-6 bg-white/80 dark:bg-slate-800/60 backdrop-blur-sm shadow-lg">
          <div className="space-y-6">
            <InputSection onSubmit={handleSubmit} isAnalyzing={isAnalyzing} />

            {(isAnalyzing || results) && (
              <ResultsSection results={results} isAnalyzing={isAnalyzing} />
            )}
          </div>
        </Card>
      </div>
    </main>
  );
}
