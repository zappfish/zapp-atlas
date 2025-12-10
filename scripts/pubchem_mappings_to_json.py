###############
### Imports ###
import os
import gzip
import re
import json
import argparse
from collections import Counter

# For ontology data
import pronto


#######################
### Chebi functions ###

# Chebiv2 ontology preload (Part 1)
def read_obo_to_mapping_tables(input_obo_path):
    
    # First read ontology data into memory
    obo_data = pronto.Ontology(input_obo_path)
    print("- {} read into memory...".format(input_obo_path))
    
    # Identify chebi terms (ids) that have been replaced, and or are obsolete
    obsolete_terms = {} # keys = obsolete terms, values = None
    replaced_terms = {} # keys = terms, values = replacement term
    term_mappings = {} # keys = chebi term (primary or secondary), value = primary chebi term
    term_synoynyms = {}

    for term in obo_data.terms():

        # Primary (canonical) ID
        primary_id = term.id

        # replaced_terms will have key as the term that is replaced. And the value is the term that is replacing it 
        if term.replaced_by and term.obsolete:
            replaced_terms[primary_id] = term.replaced_by
            chebi_term_mappings.update({primary_id:term.replaced_by})
            chebi_term_mappings.update({term.replaced_by:term.replaced_by})

        # obsolete_terms will have no replacements, and are just obsolete
        elif term.obsolete:
            obsolete_terms[primary_id] = None

        # Update chebi mapping terms, where the values are the primary chebi ids
        elif primary_id not in term_mappings:
            term_mappings.update({primary_id:primary_id})
        else:
            print("- ERROR, Multiple terms found with same primary id {}...".format(primary_id))

        # Map any secondary IDs to this primary
        for alt_id in term.alternate_ids:
            if alt_id not in term_mappings:
                term_mappings.update({alt_id:primary_id})
            else:
                print("- ERROR, Multiple terms found with same alternate id {}...".format(alt_id))

    print("- Primary terms found {}".format(format(len([1 for k,v in term_mappings.items() if k == v]), ',')))
    print("- Secondary terms found {}".format(format(len([1 for k,v in term_mappings.items() if k != v]), ',')))
    print("- Obsolete terms found {}".format(format(len(obsolete_terms), ',')))
    print("- Replaced terms found {}".format(format(len(replaced_terms), ',')))
    
    return term_mappings, term_synoynyms, replaced_terms, obsolete_terms


# This allows us to loop through chebiv2 names flat file to obtain a set of synoyms to use for each chebi term
def read_chebi_flatnames_to_alias(chebi_names_filepath:str):
    
    # Our cas --> "synonyms" (more human readable names presumably)
    chebi2alias = {}
    c1,c2 = "compound_id", "name"
    
    # We assume gz file
    processed = 0
    
    # Handle gz and unzipped data
    opener = gzip.open if chebi_names_filepath.endswith(".gz") else open
    with opener(chebi_names_filepath, "rt") as infile:
        
        # Our header should look something like this
        header_map = {h:i for i,h in enumerate(infile.readline().split('\t'))}
        
        # Check to see if header is what we need
        if (c1 not in header_map) or (c2 not in header_map):
            raise ValueError("- Necessary header information of {} and or {} not present. Exiting".format(c1, c2))
        
        #id	compound_id	name	type	status_id	adapted	language_code	ascii_name
        chebi_ind, name_ind = header_map["compound_id"], header_map["name"]
        for line in infile:
            
            # Progress statement at the beginning here 
            processed += 1
            if processed % 10_000_000 == 0:
                print("- Processed {}...".format(format(processed, ',')))
            
            # Grab cid and selct for only the ones we're interested in
            cols = line.strip('\r').strip('\n').split('\t')
            chebi_id, name = cols[chebi_ind], cols[name_ind]
            
            # Format to CHEBI:...
            chebi_id = "CHEBI:{}".format(chebi_id)
            
            if chebi_id not in chebi2alias:
                chebi2alias.update({chebi_id:{}})
            chebi2alias[chebi_id].update({name:''})
    
    tot_chebs = len(chebi2alias)
    tot_syns = sum([len(v) for v in chebi2alias.values()])
    print("- Total chebi terms found {} with {} synonyms/names describing them".format(format(tot_chebs, ','),
                                                                                       format(tot_syns, ',')))
    return chebi2alias


#########################
### Pubchem functions ###

def is_cas_number(text: str):
    """
    Returns True if the input string is a CAS registery number
    https://en.wikipedia.org/wiki/CAS_Registry_Number
    """
    
    # between 2 and 7 characters in lenght - 2 characters in length - 1 character in length
    return_val = False
    pattern = r'^\d{2,7}-\d{2}-\d$'
    if re.match(pattern, text):
        return_val = True
    
    return return_val


def read_compounds_to_chebi_cas(pubchem_cid_synonym_filepath: str, chebi_mapping_terms: dict):
    """
    TSV file where first column is the pubchem CID number, and the second column is an alternate alias for that CID.
    Multiple alias are/can be present for each unique CID.
    
    In this script, we are only interested in compounds with a ChEBI identifier and or CAS-RN.
    Because there are 100+ million lines in this file, we only want to bring in data we are interested in.
    So we make four different mapping "tables" we can parse through in a later script
    """
    
    # Four datastructures we return
    chebi2cid = {}
    cas2cid = {}

    cid2chebi = {}
    cid2cas = {}
    
    # We assume gz file
    processed = 0
    chebi_map_failed = 0
    with gzip.open(pubchem_cid_synonym_filepath, 'rt') as infile:

        for line in infile:

            cid, alias = line.strip('\r').strip('\n').split('\t')

            # Map chebi ids to cids
            if alias.startswith("CHEBI:"):
                
                # Now we select for terms that are within our preloaded ontology
                if alias in chebi_mapping_terms:
                    
                    # Map any given term --> primary term (removes the need to perform this step downstream)
                    mapped_alias = chebi_mapping_terms[alias]

                    # chebi-->cid
                    if mapped_alias not in chebi2cid:
                        chebi2cid.update({mapped_alias:{}})

                    chebi2cid[mapped_alias].update({cid:''})

                    # cid-->chebi
                    if cid not in cid2chebi:
                        cid2chebi.update({cid:{}})

                    cid2chebi[cid].update({mapped_alias:''})
                else:
                    chebi_map_failed += 1



            # Map cas numbers to cids
            elif is_cas_number(alias):

                # cas-->cid
                if alias not in cas2cid:
                    cas2cid.update({alias:{}})

                cas2cid[alias].update({cid:''})

                # cid-->cas
                if cid not in cid2cas:
                    cid2cas.update({cid:{}})

                cid2cas[cid].update({alias:''})

            processed += 1
            if processed % 10_000_000 == 0:
                print("- Processed {}...".format(format(processed, ',')))
    
    print("- {} chebi terms found".format(format(len(chebi2cid), ',')))
    print("- {} cas terms found".format(format(len(cas2cid), ',')))
    print("- {} cid terms found (with chebi mapping)".format(format(len(cid2chebi), ',')))
    print("- {} cid terms found (with cas mapping)".format(format(len(cid2cas), ',')))
    print('- {} chebi terms/entries identified within pubchem data, but failed to map to chebi_v2 ontology'.format(format(chebi_map_failed, ',')))
    return chebi2cid, cas2cid, cid2chebi, cid2cas


def map_cas_to_chebi(chebi2cid: dict, cas2cid: dict, cid2chebi: dict, cid2cas: dict):
    """
    The common "mapping" term between the cas-rns and the chebi ids is the pubchem compound id (cid).
    We want to figure our which cas-rns map to a compound (cid) that also has a chebi term(s).
    """
    
    # Loop through our cas numbers, and figure out the chebi id we can map them to
    # If multiple chebi id's are available, we do not want to include these as they are unreliable
    
    cas2chebi = {}
    chebi2cas = {}
    zero_chebi_cas = {}
    multi_chebi_cas = {}
    
    for cas_num, cids in cas2cid.items():
        
        
        
        # Identify all chebi ids that this cas number could map to, based on the cids it maps to
        chebs = set()
        for cid in cids:
            if cid in cid2chebi:
                chebs = chebs | set(cid2chebi[cid])
        
        # If only one chebi id is found, this means it is a reliable mapping and we can include it
        tot_chebs = len(chebs)
        if tot_chebs == 1:
            chebi_id = list(chebs)[0]
            cas2chebi.update({cas_num:chebi_id})
            if chebi_id not in chebi2cas:
                chebi2cas.update({chebi_id:{}})

            chebi2cas[chebi_id].update({cas_num:''})
        
        # Means there is no chebi id we can map to from this cas number
        elif tot_chebs == 0:
            zero_chebi_cas.update({cas_num:''})
        
        # Means there are multiple chebi ids we could map to from this cas number (unreliable mapping)
        elif tot_chebs > 1:
            multi_chebi_cas.update({cas_num:chebs})


    print("- {} Chebi ids found with >= 1 cas number".format(format(len(chebi2cas), ',')))
    print("- {} Cas-numbers mapped to unique ChEBI id".format(format(len(cas2chebi), ',')))
    print("- {} Cas-numbers found mapping to zero ChEBI ids".format(format(len(zero_chebi_cas), ',')))
    print("- {} Cas-numbers found mapping to multiple ChEBI ids".format(format(len(multi_chebi_cas), ',')))
    
    return cas2chebi, chebi2cas, zero_chebi_cas, multi_chebi_cas


def read_compounds_to_select_cas_alias(pubchem_cid_synonym_filepath: str, select_cids: dict, cid2chebi: dict):
    """
    TSV file where first column is the pubchem CID number, and the second column is an alternate alias for that CID.
    Multiple alias are/can be present for each unique CID.
    
    In this script, we are only interested in compounds where we know there is a one:one cas--> ChEBI mapping.
    We want to bring in all the other "alias's" this compound can go by (within pubchems database at least)
    """
    
    # Our cas --> "synonyms" (more human readable names presumably)
    cas2alias = {}
    
    # We assume gz file
    processed = 0
    with gzip.open(pubchem_cid_synonym_filepath, 'rt') as infile:

        for line in infile:
            
            # Progress statement at the beginning here 
            processed += 1
            if processed % 10_000_000 == 0:
                print("- Processed {}...".format(format(processed, ',')))
            
            # Grab cid and selct for only the ones we're interested in
            cid, alias = line.strip('\r').strip('\n').split('\t')
            if cid not in select_cids:
                continue
            
            elif cid not in cid2chebi:
                continue
            
            cas_nums = cid2cas[cid]
            for c in cas_nums:
                if c not in cas2alias:
                    cas2alias.update({c:{}})
                cas2alias[c].update({alias:''})
                
    print("- {} Cas-numbers mapped to {} synonyms...".format(format(len(cas2alias), ','),
                                                             format(sum([len(v) for v in cas2alias.values()]), ',')))
    return cas2alias


################################################################################
### Functions to bring data tables together into final output structure json ###
def map_cas_to_chebialias(cas_to_chebi_map: dict, chebi_name_map: dict):
    """
    Step where we take each cas_rn chebi mapping term(s) and pull in the alternate names 
    presumably preformated from chebi names flat file as a {"CHEBI:123":{alt_nameXYZ:'', ...}
    """
    
    cas2alias = {}
    mapped_chebi = {}
    for cas_n,v in cas_to_chebi_map.items():
        
        cas_names = set()
        
        # Allows for multiple entries or single string
        # (1:>1 cas-->chebi mapping)
        if type(v) == type(set()):
            for chebi_id in v:
                if not chebi_id.startswith("CHEBI:"):
                    raise ValueError("- Invalid term found for input chebi_name_map")
                cas_names = cas_names | set(list(chebi_name_map.get(chebi_id, {}).keys()))
                mapped_chebi.update({chebi_id:''})
        
        # Single entry (1:1 cas-->chebi mapping)
        elif type(v) == type('empty_string'):
            chebi_id = v
            if not chebi_id.startswith("CHEBI:"):
                raise ValueError("- Invalid term found for input chebi_name_map")
            cas_names = cas_names | set(list(chebi_name_map.get(chebi_id, {}).keys()))
            mapped_chebi.update({chebi_id:''})
        
        # Doesn't match what we expect
        else:
            raise ValueError("- Improper input format for cas_to_chebi_map argument...")
        
        cas2alias.update({cas_n:{ccc:'' for ccc in cas_names}}) # Convert data to dict() instead of set()
    
    tot_cas = len(cas2alias)
    tot_syns = sum([len(v) for v in cas2alias.values()])
    print("- Total unique CHEBI terms mapped to {} from {} CAS-numbers".format(format(len(mapped_chebi), ','),
                                                                               format(tot_cas, ',')))
    
    print("- Total cas numbers found {} with {} synonyms/names describing them".format(format(tot_cas, ','),
                                                                                       format(tot_syns, ',')))
    return cas2alias


def mapping_tables_to_json(cas2chebi: dict, 
                           multi_chebi_cas: dict, 
                           zero_chebi_cas: dict,
                           cas2cid: dict, 
                           cas2alias: dict,
                           outfile_path=False):
    """
    We produce three cas number --> chebi_id(s) dictionaries...
    - cas2chebi is simply a 1:1 mapping of cas_number key --> chebi_id value
    - multi_chebi_cas is 1:many mapping of cas_number key --> {chebi_idx:'', chebi_idy:'', ...}
    - zero_chebi_cas is 1:none mapping of cas_number key --> none (our cas numbers with no available chebi ids)
    We need to loop through all three of these, and create json entries for the cas numbers
    """
    
    # Our preliminary output datastructures
    json_dict = {}
    json_entries = []
    
    #####################################
    ### 1:1 cas--chebi mapping tables ###
    for k, v in cas2chebi.items():
        
        alias_data = list(cas2alias.get(k, []))
        cas_num = str(k)
        chbs = [str(v)]
        cids = list(cas2cid[k].keys())
        
        json_entry = {"cas_number":cas_num,
                      "chebi_ids":chbs,
                      "synonyms":alias_data,
                      "pubchem_cids":cids}
        
        json_entries.append(json_entry)
    print("- {} json entries created for 1:1 cas-chebi mappings...".format(format(len(cas2chebi), ',')))
    
    
    ########################################
    ### 1:many cas--chebi mapping tables ###
    for k, v in multi_chebi_cas.items():
                
        alias_data = list(cas2alias.get(k, []))
        cas_num = str(k)
        chbs = list(v)
        cids = list(cas2cid[k].keys())
        
        json_entry = {"cas_number":cas_num,
                      "chebi_ids":chbs,
                      "synonyms":alias_data,
                      "pubchem_cids":cids}
        
        json_entries.append(json_entry)
    print("- {} json entries created for 1:many cas-chebi mappings...".format(format(len(multi_chebi_cas), ',')))
    
    
    #####################################
    ### 1:0 cas--chebi mapping tables ###
    for k, v in zero_chebi_cas.items():
        
        alias_data = list(cas2alias.get(k, []))
        cas_num = str(k)
        chbs = []
        cids = list(cas2cid[k].keys())
        
        json_entry = {"cas_number":cas_num,
                      "chebi_ids":chbs,
                      "synonyms":alias_data,
                      "pubchem_cids":cids}
        
        json_entries.append(json_entry)
    print("- {} json entries created for 1:0 cas-chebi mappings...".format(format(len(zero_chebi_cas), ',')))
    
    
    # Convert our data to json, write, and return
    json_out = json.dumps(json_entries, indent=4)

    # Write to file
    print("- Writing data to {}...".format(outfile_path))
    with open(outfile_path, "w") as outfile:
        json.dump(json_out, outfile, indent=4)
    
    print("- Loading data as json...")
    with open(outfile_path, "r") as infile:
        json_out = json.load(infile)
    print("- Done!")
    
    return json_out



if __name__ == '__main__':
    ################
	## ARG PARSE ###
    def parse_input_command():
        parser = argparse.ArgumentParser(description='Reads through PubChem CID-Synonym file, creates cas-->chebi mapping tables, and writes to json file')
        parser.add_argument("-i", "--input_directory", help="Input directory containing PubChem, chebi obo, and chebi flat names files", required=True, type=str)
        parser.add_argument("-o", "--output_file", help="path/to/output.json file to write data to", required=True, type=str)
        ###parser.add_argument("-m", "--mapping_type", help="Type of cas-->chebi mapping to include in output json file. Options are 'all' (default), 'one2one', 'one2many', 'one2none'", required=False, type=str, default="all", choices=["all", "one2one", "one2many", "one2none"])
        return parser.parse_args()

    args = parse_input_command()
    ############################

    ###############
    ### PROGRAM ###

    # Input / output files
    pubchem_filepath = os.path.join(args.input_directory, "CID-Synonym-unfiltered.gz")
    chebi_obopath = os.path.join(args.input_directory, "chebi.obo")
    chebi_flatnamespath = os.path.join(args.input_directory, "names.tsv.gz")
    json_outfile = args.output_file

    # Make sure all our data/directories exists before hand
    for inpath in [pubchem_filepath, chebi_obopath, chebi_flatnamespath]:
        if not os.path.isfile(inpath):
            raise FileNotFoundError("Input file {} not found!".format(inpath))

    if not os.path.isdir(os.path.dirname(json_outfile)):
        raise NotADirectoryError("Output directory {} for file not found!".format(os.path.dirname(json_outfile)))

    # Read chebi obo into memory, and upack data into individual datastructures
    chebi_term_data = read_obo_to_mapping_tables(chebi_obopath)
    chebi_mappings, chebi_synonyms, chebi_replaced, chebi_obsolete = chebi_term_data

    # Read chebi flatnames file into memory in the form of {"CHEBI:123":{name123:'', ...}}
    chebi_names = read_chebi_flatnames_to_alias(chebi_flatnamespath)

    # For the "unfiltered" pubchem cid-synonym file, we want to create four different mapping tables...
    # cas2chebi --> {cas_id:chebi_id}   1:1 mappings
    # chebi2cas --> {chebi_id:{cas_id:'', ...}}   1:>=1 mappings (For only cas numbers found in cas2chebi)
    # multi_chebi_cas --> {cas_id:{chebi_id:'', ...}}   1:>1 mappings 
    # zero_chebi_cas --> {cas_id:''}   1:0 mappings

    # Create initial mappings from pubchem cid-synonym file
    print("- Reading in pubchem cid-synonym file, creating initial mapping tables...")
    chebi2cid, cas2cid, cid2chebi, cid2cas = read_compounds_to_chebi_cas(pubchem_filepath, chebi_mappings)

    # Figure out which cas numbers map to a unique chebi ids, and which do not
    cas2chebi, chebi2cas, zero_chebi_cas, multi_chebi_cas = map_cas_to_chebi(chebi2cid, cas2cid, cid2chebi, cid2cas)

    # V1 - Pubchem synonyms (If we wanted to use pubchem synonyms instead of chebi names)
    # For all cas numbers that map to a unique chebi id, we want to bring in all the other "alias's" this compound can go by (within pubchems database at least)
    # So we loop back through the original file, and pull in all the alias's for the cids that map to our cas numbers of interest
    ##print("- Looping back through pubchem cid-synonym file, pulling in all alias's for cas numbers of interest...")
    ##select_cids = set([cid for k in cas2chebi for cid in cas2cid[k]])
    ##cas2alias = read_compounds_to_select_cas_alias(pubchem_filepath, select_cids, cid2chebi)

    # V2 - Chebi synonyms (Preferred way for now)
    print("- Pulling in names for 1:1 cas-->chebi mappings via chebi_v2 ontology flat names file...")
    cas2alias = map_cas_to_chebialias(cas_to_chebi_map=cas2chebi, chebi_name_map=chebi_names)

    print("- Pulling in names for 1:>1 cas-->chebi mappings via chebi_v2 ontology flat names file...")
    cas2alias.update(map_cas_to_chebialias(cas_to_chebi_map=multi_chebi_cas, chebi_name_map=chebi_names))

    # Last summary statistics
    tot_cas = len(cas2alias)
    tot_syns = sum([len(v) for v in cas2alias.values()])
    tot_chebi = len(set(list(cas2chebi.keys())) | set([vv for v in multi_chebi_cas.values() for vv in v]))
    print("- Total unique CHEBI ids mapped to {}".format(format(tot_chebi, ',')))
    print("- Total cas numbers found {} with {} synonyms/names describing them".format(format(tot_cas, ','),
                                                                                    format(tot_syns, ',')))

    # Create json data structure, write to file, and return
    json_data = mapping_tables_to_json(cas2chebi, 
                                       multi_chebi_cas, 
                                       zero_chebi_cas, 
                                       cas2cid, 
                                       cas2alias,
                                       outfile_path=json_outfile)
    
    print("- Finished!")