import React from 'react';
import FileInput from '@/ui/FileInput';
import FormSection from '@/ui/FormSection';
import TextArea from '@/ui/TextArea';
import { IMAGE_UPLOAD } from './explanations';
type ImageMeta = { name?: string; type?: string; size?: number } | null;

export default function ImageSection({
  setImageFile,
  previewSrc,
  fileMeta,
  imageNotes,
  setImageNotes
}: {
  setImageFile: (file: File | null) => void;
  previewSrc: string | null;
  fileMeta: ImageMeta;
  imageNotes: string;
  setImageNotes: (val: string) => void;
}) {
  const [dragOver, setDragOver] = React.useState(false);
  const [fullscreen, setFullscreen] = React.useState(false);
  const [showNotes, setShowNotes] = React.useState(false);

  const handleDrop: React.DragEventHandler<HTMLDivElement> = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith('image/')) {
      setImageFile(file);
    }
  };

  const handleDragOver: React.DragEventHandler<HTMLDivElement> = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave: React.DragEventHandler<HTMLDivElement> = () => setDragOver(false);

  const triggerBrowse = () => {
    const el = document.getElementById('image-file-input') as HTMLInputElement | null;
    el?.click();
  };

  const removeImage = () => {
    setImageFile(null);
    const el = document.getElementById('image-file-input') as HTMLInputElement | null;
    if (el) el.value = '';
  };

  const formatBytes = (bytes?: number) => {
    if (!bytes && bytes !== 0) return '';
    if (bytes < 1024) return `${bytes} B`;
    const kb = bytes / 1024;
    if (kb < 1024) return `${kb.toFixed(1)} KB`;
    const mb = kb / 1024;
    return `${mb.toFixed(2)} MB`;
  };
  return (
    <div className="row">
      <FormSection title="Image of Observation">
        <div className="col-6">
          <div
            className={`drop-zone ${dragOver ? 'drag-over' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={triggerBrowse}
          >
            <FileInput
              id="image-file-input"
              label="Upload image"
              tooltip={IMAGE_UPLOAD}
              accept="image/jpeg,image/png,image/tiff"
              onChange={(e) => setImageFile((e.target as HTMLInputElement).files?.[0] || null)}
              hint="Drag & drop an image here, or click to browse. Accepted: .jpeg, .png, .tiff"
            />
          </div>
        </div>
        <div className="col-6">
          <div className="field">
            <label>Preview</label>
            {previewSrc ? (
              <>
                <img
                  src={previewSrc}
                  alt="Selected observation"
                  className="img-preview"
                  onClick={() => setFullscreen(true)}
                />
                {fileMeta && (
                  <small className="hint">
                    {fileMeta.name || 'unnamed'} • {fileMeta.type || 'unknown type'} • {formatBytes(fileMeta.size)}
                  </small>
                )}
                <div className="inline" style={{ marginTop: 8 }}>
                  <button type="button" onClick={triggerBrowse}>Replace image</button>
                  <button type="button" onClick={removeImage}>Remove image</button>
                </div>
                {fullscreen && previewSrc && (
                  <div
                    className="image-overlay"
                    onClick={() => setFullscreen(false)}
                    role="dialog"
                    aria-modal="true"
                    aria-label="Full screen image preview"
                  >
                    <img src={previewSrc} alt="Full screen observation preview" />
                  </div>
                )}
              </>
            ) : (
              <small className="hint">No image selected yet.</small>
            )}
          </div>
        </div>
      <div className="col-12">
        <button type="button" onClick={() => setShowNotes((s) => !s)}>
          {showNotes ? 'Hide notes' : 'Add notes'}
        </button>
      </div>
      {showNotes && (
        <div className="col-12">
          <TextArea
            label="Additional notes"
            placeholder="Additional notes not captured by the fields in this section"
            value={imageNotes}
            onChange={(e) => setImageNotes((e.target as HTMLTextAreaElement).value)}
          />
        </div>
      )}
      </FormSection>
      {previewSrc && !fullscreen && (
        <button
          type="button"
          className="floating-thumb"
          onClick={() => setFullscreen(true)}
          aria-label="Open full screen image preview from thumbnail"
          title="Open preview"
        >
          <img src={previewSrc} alt="Thumbnail of uploaded image" />
        </button>
      )}
    </div>
  );
}
