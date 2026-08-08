import { generateSkillMarkdown } from '../utils/skillTemplate.js';
import { downloadFile } from '../utils/download.js';

export function SkillExporter({ results, formData }) {
  const handleExport = (format) => {
    if (format === 'markdown') {
      const markdown = generateSkillMarkdown(results, formData);
      downloadFile(markdown, 'scooter-challenge-skill.md', 'text/markdown');
    } else {
      const json = JSON.stringify({ results, formData }, null, 2);
      downloadFile(json, 'scooter-challenge-results.json', 'application/json');
    }
  };

  return (
    <div className="rounded-sheet border border-rule bg-sheet p-5">
      <h3 className="font-display text-lg text-ink">Download your analysis</h3>
      <p className="mt-1 text-sm text-note">Re-run this in Claude, ChatGPT, or Gemini with fresh data any time.</p>

      <div className="mt-3 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() => handleExport('markdown')}
          className="rounded-sheet border border-river px-4 py-2 font-mono text-xs uppercase tracking-wide text-river hover:bg-river hover:text-sheet"
        >
          Claude skill (.md)
        </button>
        <button
          type="button"
          onClick={() => handleExport('json')}
          className="rounded-sheet border border-note px-4 py-2 font-mono text-xs uppercase tracking-wide text-note hover:bg-note hover:text-sheet"
        >
          Results snapshot (.json)
        </button>
      </div>
    </div>
  );
}
