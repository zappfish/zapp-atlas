const OBO = "http://purl.obolibrary.org/obo/";

/** http://purl.obolibrary.org/obo/ZP_0000055 -> ZP:0000055 */
export const curieOf = (uri: string) => uri.replace(OBO, "").replace("_", ":");
