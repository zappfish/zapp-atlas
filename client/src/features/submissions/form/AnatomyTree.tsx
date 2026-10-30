import { useEffect, useMemo, useRef } from "react";
import { Path, type Hierarchy, type OBOGraphNode } from "frogpot";
import {
  AnatomyLabel,
  AnatomyLeaf,
  AnatomyList,
  AnatomyRow,
  AnatomyToggle,
} from "@/styles/elements";

/** Rem per level. */
const INDENT = 0.75;

/** Also drops descendants: projectFlatView keeps anything above an expanded
 *  path open. */
const toggled = (expanded: ReadonlySet<string>, path: Path) => {
  const next = new Set(expanded);
  if (!expanded.has(path.key)) return next.add(path.key);
  for (const key of expanded) {
    if (Path.fromKey(key).startsWith(path)) next.delete(key);
  }
  return next;
};

/** One row per path: a term appears under each of its parents. */
const AnatomyTree = ({
  hierarchy,
  expanded,
  selectedUri,
  onExpandedChange,
  onSelect,
}: {
  hierarchy: Hierarchy<OBOGraphNode>;
  expanded: ReadonlySet<string>;
  selectedUri?: string;
  onExpandedChange: (expanded: ReadonlySet<string>) => void;
  onSelect: (node: OBOGraphNode) => void;
}) => {
  const rows = useMemo(
    () =>
      hierarchy.projectFlatView({
        expandPaths: [...expanded].map((key) => Path.fromKey(key)),
      }),
    [hierarchy, expanded],
  );

  const selected = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    selected.current?.scrollIntoView({ block: "nearest" });
  }, [selectedUri]);

  return (
    <AnatomyList>
      {rows.map(({ item, depth, path }) => {
        const label = item.label ?? item.uri;
        const isSelected = item.uri === selectedUri;
        const isExpanded = expanded.has(path.key);
        const hasChildren = hierarchy.graph.childrenByURI[item.uri]?.length;

        return (
          <AnatomyRow key={path.key} style={{ paddingLeft: `${depth * INDENT}rem` }}>
            {hasChildren ? (
              <AnatomyToggle
                type="button"
                aria-expanded={isExpanded}
                aria-label={`${isExpanded ? "Collapse" : "Expand"} ${label}`}
                onClick={() => onExpandedChange(toggled(expanded, path))}
              >
                <span aria-hidden="true">{isExpanded ? "▾" : "▸"}</span>
              </AnatomyToggle>
            ) : (
              <AnatomyLeaf aria-hidden="true">•</AnatomyLeaf>
            )}
            <AnatomyLabel
              ref={isSelected ? selected : undefined}
              type="button"
              title={label}
              aria-current={isSelected ? "true" : undefined}
              onClick={() => onSelect(item)}
            >
              {label}
            </AnatomyLabel>
          </AnatomyRow>
        );
      })}
    </AnatomyList>
  );
};

export default AnatomyTree;
