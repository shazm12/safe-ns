export function Header() {
  return (
    <header className="text-center">
      <h1 className="text-4xl md:text-5xl py-2 font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-blue-400 tracking-tight">
        Content Safety Moderator
      </h1>
      <p className="mt-4 text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto">
        Our AI-powered tool helps you ensure your content is safe to share. 
        Simply enter text or upload an image to check if it contains NSFW or inappropriate content.
      </p>
    </header>
  );
}