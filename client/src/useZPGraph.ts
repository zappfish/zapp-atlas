import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Hierarchy,
  OBOGraphLoader,
  type OBOGraphNode,
} from 'frogpot';
import { keys } from "@/api/hooks";

const ZP_ROOT = "http://purl.obolibrary.org/obo/ZP_0000000";
const ZFA_ROOT = "http://purl.obolibrary.org/obo/ZFA_0100000";
const UPHENO_ASSOCIATED_WITH = "http://purl.obolibrary.org/obo/UPHENO_0000003";

export type ZPData = {
  zpHierarchy: Hierarchy<OBOGraphNode>;
  zfaHierarchy: Hierarchy<OBOGraphNode>;
  zpByZFA: Map<string, OBOGraphNode[]>;
  /** How many times ZFIN curated each ZP term, by term URI. */
  zfinCounts: Map<string, number>;
};

// Loading / Loaded discriminated union
type GraphsLoading = {
  loading: true;
  reload: () => void
};

type GraphsLoaded = {
  loading: false;
  reload: () => void;
} & ZPData;

export type GraphsResult = GraphsLoading | GraphsLoaded;

// The ontology files come from the app's extdata bundle (extdata/README.md).
// They are served under the bundle's hash, which the unversioned manifest
// names.
async function getDataBase(): Promise<string> {
  const resp = await fetch("/extdata/manifest.json");
  if (!resp.ok) {
    throw Error(`Error requesting /extdata/manifest.json: ${resp.status} ${resp.statusText}`);
  }
  const { hash } = await resp.json();
  return `/extdata/${hash}`;
}

// zfin_counts.tsv has a header row, then one `ZP:0000041<TAB>12` per term.
async function loadZfinCounts(uri: string): Promise<Map<string, number>> {
  const resp = await fetch(uri);
  if (!resp.ok) {
    throw Error(`Error requesting ${uri}: ${resp.status} ${resp.statusText}`);
  }
  const counts = new Map<string, number>();
  for (const line of (await resp.text()).split("\n").slice(1)) {
    const [curie, count] = line.split("\t");
    if (!curie || !count) continue;
    counts.set(`http://purl.obolibrary.org/obo/${curie.replace(":", "_")}`, Number(count));
  }
  return counts;
}

async function loadZPData(): Promise<ZPData> {
  const loader = new OBOGraphLoader();
  const DATA_BASE = await getDataBase();

  const [zfaGraph, zpGraph, zfinCounts] = await Promise.all([
    loader.fromURI(`${DATA_BASE}/zfa.json`),
    loader.fromURI(`${DATA_BASE}/zp.json`),
    loadZfinCounts(`${DATA_BASE}/zfin_counts.tsv`),
  ]);

  const zfaHierarchy = zfaGraph.getHierarchy(ZFA_ROOT);
  const zpHierarchy = zpGraph.getHierarchy(ZP_ROOT);
  const zpItems = zpGraph.findAllChildren(zpGraph.getItem(ZP_ROOT));

  const zpByZFA = new Map<string, OBOGraphNode[]>();

  for (const node of zpItems) {
    for (const edge of node.edges || []) {
      if (edge.pred === UPHENO_ASSOCIATED_WITH) {
        if (!zpByZFA.has(edge.obj)) zpByZFA.set(edge.obj, []);
        zpByZFA.get(edge.obj)!.push(node);
      }
    }
  }


  return { zfaHierarchy, zpHierarchy, zpByZFA, zfinCounts };
}

export function useZPGraph(): GraphsResult {
  const queryClient = useQueryClient();
  const { data } = useQuery({
    queryKey: keys.zpGraph,
    queryFn: loadZPData,
    // Loaded once per session: a bundle's files never change, and building
    // the hierarchies is not cheap, so keep the result even while nothing
    // is showing it.
    staleTime: Infinity,
    gcTime: Infinity,
  });

  // Clear cache and re-trigger loading hook
  const reload = () => {
    queryClient.resetQueries({ queryKey: keys.zpGraph });
  };

  if (!data) {
    return {
      loading: true,
      reload,
    };
  }

  return {
    loading: false,
    reload,
    ...data,
  };
}
