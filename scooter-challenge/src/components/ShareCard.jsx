import { useMemo, useState } from 'react';
import { generateShareCardSVG } from '../utils/shareCard.js';
import { downloadSvgAsPng } from '../utils/download.js';

const CARD_WIDTH = 1200;
const CARD_HEIGHT = 630;

export function ShareCard({ results, formData }) {
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState(null);
  const svg = useMemo(() => generateShareCardSVG(results, formData), [results, formData]);

  const handleDownload = async () => {
    setDownloading(true);
    setError(null);
    try {
      await downloadSvgAsPng(svg, 'curb-your-spending-result.png', CARD_WIDTH, CARD_HEIGHT);
    } catch (err) {
      setError(err.message || 'Could not generate the share image.');
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="rounded-sheet border border-rule bg-sheet p-5">
      <h3 className="font-display text-lg text-ink">Share this result</h3>
      <p className="mt-1 text-sm text-note">
        Screenshot the card below, or download it as an image to share and encourage others to compare their own
        rides.
      </p>

      <div
        className="share-card-svg-wrap mt-3 w-full overflow-hidden rounded border border-rule"
        // eslint-disable-next-line react/no-danger
        dangerouslySetInnerHTML={{ __html: svg }}
      />

      <div className="mt-3 flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={handleDownload}
          disabled={downloading}
          className="rounded-sheet border border-river px-4 py-2 font-mono text-xs uppercase tracking-wide text-river hover:bg-river hover:text-sheet disabled:opacity-50"
        >
          {downloading ? 'Rendering…' : '📸 Download share image'}
        </button>
        {error && <span className="font-mono text-xs text-brick">{error}</span>}
      </div>
    </div>
  );
}
