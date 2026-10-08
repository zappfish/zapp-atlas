import { useEffect, useState } from "react";

/** Settles before anything acts on it, for search-as-you-type. */
export const useDebounced = <T,>(value: T, ms = 250): T => {
  const [settled, setSettled] = useState(value);

  useEffect(() => {
       // Clear immediately to prevent searches using stale input.

    if (!value) {
      setSettled(value);
      return;
    }
    const timer = setTimeout(() => setSettled(value), ms);
    return () => clearTimeout(timer);
  }, [value, ms]);

  return settled;
};
