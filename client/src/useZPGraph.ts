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

async function loadZPData(): Promise<ZPData> {
  const loader = new OBOGraphLoader();
  const DATA_BASE = await getDataBase();

  const [zfaGraph, zpGraph] = await Promise.all([
    loader.fromURI(`${DATA_BASE}/zfa.json`),
    loader.fromURI(`${DATA_BASE}/zp.json`),
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


  return { zfaHierarchy, zpHierarchy, zpByZFA };
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
