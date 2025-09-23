# General imports
import os
import argparse
import requests
import tarfile
import pickle


def download_file_url(url: str, outdir: str, overwrite: bool = False):
    """
    Will download file from url to outdir/filename
    filename is generated from the last portion of the url split by "/"
    """
    
    # Download and write file
    filename = os.path.join(outdir, url.split("/")[-1])

    if overwrite != True:
        if os.path.isfile(filename):
            print("- Warning, file {} already exists... Set overwrite to True to download and replace".format(filename))
            return

    print("- Downloading file from {} to {}...".format(url, filename))
    with open(filename, "wb") as f:
        r = requests.get(url)
        f.write(r.content)


if __name__ == '__main__':
    ################
	## ARG PARSE ###
    def parse_input_command():
        parser = argparse.ArgumentParser(description='Downloads pubchem cid_synonym file to specified directory')
        parser.add_argument("-d", "--download_dir", help="path/to/directory to write file(s) to", required=True, type=str)
        return parser.parse_args()

    args = parse_input_command()
    ############################

    ###############
    ### PROGRAM ###

    pubchem_unfiltered_url = "https://ftp.ncbi.nlm.nih.gov/pubchem/Compound/Extras/CID-Synonym-filtered.gz"
    download_file_url(pubchem_unfiltered_url, args.download_dir, overwrite=False)