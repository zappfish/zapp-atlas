import React, { useEffect } from 'react';

interface Props {
  src: string;
  alt: string;
  onClose: () => void;
}

/** Full-screen click-to-dismiss overlay for an image thumbnail. */
export default function ImageOverlay({ src, alt, onClose }: Props) {
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose();
    }
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [onClose]);

  return (
    <div
      className="image-overlay"
      role="dialog"
      aria-label="Enlarged image"
      onClick={onClose}
    >
      <img src={src} alt={alt} />
    </div>
  );
}
