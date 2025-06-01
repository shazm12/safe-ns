'use client';

import { useState, useRef } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Upload, Send, Loader2, Image as ImageIcon } from 'lucide-react';
import { ModerationType } from '@/lib/types';

interface InputSectionProps {
  onSubmit: (type: ModerationType, content: string | File) => void;
  isAnalyzing: boolean;
}

export function InputSection({ onSubmit, isAnalyzing }: InputSectionProps) {
  const [text, setText] = useState('');
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleTextSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim()) {
      onSubmit('text', text);
    }
  };

  const handleImageSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedImage) {
      onSubmit('image', selectedImage);
    }
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      createBlurredPreview(file).then(blurredUrl => {
        setImagePreview(blurredUrl);
      });
    }
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file);
      createBlurredPreview(file).then(blurredUrl => {
        setImagePreview(blurredUrl);
      });
    }
  };

  const createBlurredPreview = (file: File): Promise<string> => {
    return new Promise((resolve) => {
      const img = new Image();
      const url = URL.createObjectURL(file);
      
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // Reduce size for faster blurring
        const scale = 0.2;
        canvas.width = img.width * scale;
        canvas.height = img.height * scale;
        
        if (ctx) {
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
          
          // Apply blur effect
          ctx.filter = 'blur(8px)';
          ctx.drawImage(canvas, 0, 0);
          
          // Convert back to data URL
          const blurredUrl = canvas.toDataURL('image/jpeg', 0.7);
          resolve(blurredUrl);
        }
      };
      
      img.src = url;
    });
  };

  return (
    <Tabs defaultValue="text" className="w-full">
      <TabsList className="grid w-full grid-cols-2">
        <TabsTrigger value="text">Text</TabsTrigger>
        <TabsTrigger value="image">Image</TabsTrigger>
      </TabsList>
      
      <TabsContent value="text">
        <form onSubmit={handleTextSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="content">Enter text to moderate:</Label>
            <Textarea
              id="content"
              placeholder="Type your content here..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              className="min-h-[150px] resize-none"
              disabled={isAnalyzing}
            />
          </div>
          <Button 
            type="submit" 
            disabled={!text.trim() || isAnalyzing}
            className="w-full sm:w-auto"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" /> 
                Analyzing...
              </>
            ) : (
              <>
                <Send className="mr-2 h-4 w-4" /> 
                Check Content
              </>
            )}
          </Button>
        </form>
      </TabsContent>
      
      <TabsContent value="image">
        <form onSubmit={handleImageSubmit} className="space-y-4">
          <div 
            className="border-2 border-dashed border-slate-300 dark:border-slate-600 rounded-lg p-6 text-center cursor-pointer hover:border-blue-400 dark:hover:border-blue-500 transition-colors"
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            onClick={handleBrowseClick}
          >
            <input 
              type="file" 
              ref={fileInputRef} 
              className="hidden" 
              accept="image/*" 
              onChange={handleImageChange}
              disabled={isAnalyzing}
            />
            
            {imagePreview ? (
              <div className="relative">
                <img 
                  src={imagePreview} 
                  alt="Preview" 
                  className="max-h-[250px] mx-auto rounded-md object-contain"
                />
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
                  {selectedImage?.name}
                </p>
              </div>
            ) : (
              <div className="py-6">
                <div className="flex justify-center mb-3">
                  <ImageIcon className="h-12 w-12 text-slate-400" />
                </div>
                <p className="text-slate-500 dark:text-slate-400 mb-2">
                  Drag and drop an image here, or click to browse
                </p>
                <p className="text-xs text-slate-400 dark:text-slate-500">
                  Supported formats: JPG, PNG, GIF
                </p>
              </div>
            )}
          </div>
          
          <Button 
            type="submit" 
            disabled={!selectedImage || isAnalyzing}
            className="w-full sm:w-auto"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" /> 
                Analyzing...
              </>
            ) : (
              <>
                <Upload className="mr-2 h-4 w-4" /> 
                Check Image
              </>
            )}
          </Button>
        </form>
      </TabsContent>
    </Tabs>
  );
}