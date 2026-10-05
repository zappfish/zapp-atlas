import { useCallback, useRef, useState } from "react";

/**
 * The entries of a repeating section. Keyed by id rather than counted, so
 * removing one does not renumber the state of those after it.
 */
export const useEntries = (initial = 1) => {
  const [ids, setIds] = useState(() =>
    Array.from({ length: initial }, (_, i) => i),
  );
  const next = useRef(initial);

  const add = useCallback(() => setIds((was) => [...was, next.current++]), []);
  const remove = useCallback(
    (id: number) => setIds((was) => was.filter((each) => each !== id)),
    [],
  );

  return { ids, add, remove };
};
