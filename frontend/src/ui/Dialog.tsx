import { useEffect, useRef } from "react";
import type { ReactNode } from "react";

interface Props {
  titleId: string;
  busy: boolean;
  onClose: () => void;
  children: ReactNode;
}
export function Dialog({ titleId, busy, onClose, children }: Props) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const element = ref.current;
    element?.showModal();
    return () => element?.close();
  }, []);
  return (
    <dialog
      ref={ref}
      className="modal"
      aria-labelledby={titleId}
      onCancel={(event) => {
        if (busy) event.preventDefault();
        else onClose();
      }}
    >
      <button
        className="dialog-close"
        disabled={busy}
        onClick={onClose}
        aria-label="بستن"
      >
        ×
      </button>
      {children}
    </dialog>
  );
}
