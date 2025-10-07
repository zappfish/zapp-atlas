###############
### Imports ###
import os
import gzip
import re
import json
import argparse
from collections import Counter


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


def read_compounds_to_chebi_cas(pubchem_cid_synonym_filepath: str):
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
    with gzip.open(pubchem_cid_synonym_filepath, 'rt') as infile:

        for line in infile:

            cid, alias = line.strip('\r').strip('\n').split('\t')

            # Map chebi ids to cids
            if alias.startswith("CHEBI:"):

                # chebi-->cid
                if alias not in chebi2cid:
                    chebi2cid.update({alias:{}})

                chebi2cid[alias].update({cid:''})

                # cid-->chebi
                if cid not in cid2chebi:
                    cid2chebi.update({cid:{}})

                cid2chebi[cid].update({alias:''})



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
        parser.add_argument("-i", "--input_file", help="path/to/CID-Synonym-unfiltered.gz file to read in data from", required=True, type=str)
        parser.add_argument("-o", "--output_file", help="path/to/output.json file to write data to", required=True, type=str)
        ###parser.add_argument("-m", "--mapping_type", help="Type of cas-->chebi mapping to include in output json file. Options are 'all' (default), 'one2one', 'one2many', 'one2none'", required=False, type=str, default="all", choices=["all", "one2one", "one2many", "one2none"])
        return parser.parse_args()

    args = parse_input_command()
    ############################

    ###############
    ### PROGRAM ###

    # Input / output files
    pubchem_filepath = args.input_file
    json_outfile = args.output_file

    # Make sure all our data/directories exists before hand
    if not os.path.isfile(pubchem_filepath):
        raise FileNotFoundError("Input file {} not found!".format(pubchem_filepath))

    if not os.path.isdir(os.path.dirname(json_outfile)):
        raise NotADirectoryError("Output directory {} for file not found!".format(os.path.dirname(json_outfile)))

    # For the "unfiltered" pubchem cid-synonym file, we want to create four different mapping tables...
    # cas2chebi --> {cas_id:chebi_id}   1:1 mappings
    # chebi2cas --> {chebi_id:{cas_id:'', ...}}   1:>=1 mappings (For only cas numbers found in cas2chebi)
    # multi_chebi_cas --> {cas_id:{chebi_id:'', ...}}   1:>1 mappings 
    # zero_chebi_cas --> {cas_id:''}   1:0 mappings

    # Create initial mappings from pubchem cid-synonym file
    print("- Reading in pubchem cid-synonym file, creating initial mapping tables...")
    chebi2cid, cas2cid, cid2chebi, cid2cas = read_compounds_to_chebi_cas(pubchem_filepath)

    # Figure out which cas numbers map to a unique chebi ids, and which do not
    cas2chebi, chebi2cas, zero_chebi_cas, multi_chebi_cas = map_cas_to_chebi(chebi2cid, cas2cid, cid2chebi, cid2cas)

    # For all cas numbers that map to a unique chebi id, we want to bring in all the other "alias's" this compound can go by (within pubchems database at least)
    # So we loop back through the original file, and pull in all the alias's for the cids that map to our cas numbers of interest
    print("- Looping back through pubchem cid-synonym file, pulling in all alias's for cas numbers of interest...")
    select_cids = set([cid for k in cas2chebi for cid in cas2cid[k]])
    cas2alias = read_compounds_to_select_cas_alias(pubchem_filepath, select_cids, cid2chebi)

    # Create json data structure, write to file, and return
    json_data = mapping_tables_to_json(cas2chebi, 
                                       multi_chebi_cas, 
                                       zero_chebi_cas, 
                                       cas2cid, 
                                       cas2alias,
                                       outfile_path=json_outfile)
    
    print("- Finished!")