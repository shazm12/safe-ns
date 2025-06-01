"use client";

import { useState, useEffect } from "react";
import { Check, AlertTriangle, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { ModeratedContent } from "@/lib/types";

interface ResultsSectionProps {
  results: ModeratedContent | null;
  isAnalyzing: boolean;
}

export function ResultsSection({ results, isAnalyzing }: ResultsSectionProps) {
  const [progress, setProgress] = useState(false);

  useEffect(() => {
    if (isAnalyzing) {
      setProgress(true);
    } else {
      setProgress(false);
    }
  }, [isAnalyzing, results]);

  return (
    <div className="mt-8 border border-slate-200 dark:border-slate-700 rounded-lg overflow-hidden animate-fade-in-down transition-all duration-1200">
      <div className="bg-slate-100 dark:bg-slate-800 p-4">
        <h3 className="font-medium">Content Analysis Results</h3>
      </div>

      <div className="p-6 space-y-6 animate-in fade-in duration-300">
        {isAnalyzing ? (
          <div className="space-y-4">
            <div className="flex items-center justify-center">
              <Loader2 className="h-8 w-8 text-blue-500 animate-spin" />
            </div>
            <p className="text-center text-slate-600 dark:text-slate-300">
              Analyzing your content...
            </p>
          </div>
        ) : results ? (
          <div className="space-y-6">
            <div
              className={cn(
                "p-4 rounded-lg flex items-center gap-3",
                results.isSafe
                  ? "bg-green-50 dark:bg-green-950/30 text-green-700 dark:text-green-300"
                  : "bg-red-50 dark:bg-red-950/30 text-red-700 dark:text-red-300"
              )}
            >
              {results.isSafe ? (
                <Check className="h-5 w-5 flex-shrink-0" />
              ) : (
                <AlertTriangle className="h-5 w-5 flex-shrink-0" />
              )}
              <div>
                <p className="font-medium">
                  {results.isSafe
                    ? "Content appears to be safe"
                    : "Potentially unsafe content detected"}
                </p>
                <p className="text-sm opacity-90">
                  Confidence: {results.confidence}%
                </p>
              </div>
            </div>

            <div>
              <h4 className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-2">
                Analyzed Summary:
              </h4>
              {results.type === "text" ? (
                <div className="p-3 bg-slate-50 dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800">
                  <p className="text-slate-700 dark:text-slate-300 whitespace-pre-wrap">
                    {results.summary as string}
                  </p>
                </div>
              ) : (
                <div className="bg-slate-50 dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800 p-2">
                  <p className="text-slate-700 dark:text-slate-300 whitespace-pre-wrap">
                    {results.summary as string}
                  </p>
                </div>
              )}
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
