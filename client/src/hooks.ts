import { useEffect, useRef, useState } from "react";
import {
  Hierarchy,
  OBOGraphLoader,
  type OBOGraphNode,
} from 'frogpot';

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

// Global cache
const zpCache: {
  promise: Promise<ZPData> | null;
  data: ZPData | null;
} = {
  promise: null,
  data: null,
};

const DATA_BASE = import.meta.env.VITE_DATA_BASE_URL || "data";

async function loadZPData(): Promise<ZPData> {
  const loader = new OBOGraphLoader();

  const [zfaGraph, zpGraph] = await Promise.all([
    loader.fromURI(`${DATA_BASE}/zfa.json`),
    loader.fromURI(`${DATA_BASE}/zp-zapp.json`),
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
  const [data, setData] = useState(zpCache.data);
  const [loadCounter, setLoadCounter] = useState(0)
  const cancelledRef = useRef(false);

  // Clear cache and re-trigger loading hook
  const reload = () => {
    zpCache.data = null;
    zpCache.promise = null;
    setData(null);
    setLoadCounter(prev => prev + 1)
  };

  useEffect(() => {
    cancelledRef.current = false;

    if (zpCache.data) {
      setData(zpCache.data);
      return;
    }

    // Data is already loading-- just subscribe to that promise
    if (zpCache.promise) {
      zpCache.promise.then((data) => {
        if (!cancelledRef.current) setData(data);
      });

      return;
    }

    // Otherwise, start loading data from scratch
    zpCache.promise = loadZPData().then((data) => {
      zpCache.data = data;

      if (!cancelledRef.current) setData(data);

      return data;
    });

    return () => {
      cancelledRef.current = true;
    };
  }, [loadCounter]);

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

