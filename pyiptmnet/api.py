import json
import requests
import csv
import builtins
from io import StringIO
import pandas as pd
import urllib3
from pyiptmnet.enums import API_VERSION

__host_url = "https://research.bioinformatics.udel.edu/iptmnet/api"
urllib3.disable_warnings()
__selected_version = None

def set_host_url(url):
    """
    Sets the base URL for the iPTMnet API.

    Args:
        url (str): The new URL for the API host.
    """
    global __host_url
    __host_url = url

def set_api_version(version):
    """
    Sets the API version to use in requests.

    Args:
        version (API_VERSION): Enum value of the API version.
    """
    global __selected_version
    __selected_version = version

def _to_dataframe_from_json(text):
    """
    Helper function to convert text in CSV format to a pandas DataFrame.

    Args:
        text (str): String with data in CSV format.

    Returns:
        pandas.DataFrame: A DataFrame representing the data from the CSV.
    """
    data = StringIO(text)
    dataframe = pd.read_csv(data, sep=",")
    return dataframe

def search(search_term, term_type, role, ptm_list=None, organism_list=None, dict=None):
    """
    Performs a search in the iPTMnet database.

    Args:
        search_term (str): The search query (e.g., 'SMAD2', 'Q15796').
        term_type (TermType): The type of the search query (e.g., TermType.GENE, TermType.UNIPROT_AC).
        role (Role): The role of the protein (e.g., Role.ENZYME, Role.SUBSTRATE).
        ptm_list (list[PTM_TYPE], optional): A list of post-translational modification (PTM) types for filtering.
        organism_list (list[str], optional): A list of organism taxon codes for filtering.
        dict (bool, optional): If True, returns the raw JSON response as a dictionary. Otherwise,
                               returns a pandas DataFrame converted to a dictionary. Defaults to None.

    Returns:
        dict: A dictionary with the search results.
              If nothing is found, returns {'id': 'No data found for the given ID.'}.

    Raises:
        requests.exceptions.HTTPError: If the API returns an HTTP error code.
    """
    if ptm_list is None:
        ptm_list = []
    else:
        # iterate the original list to create a new list with values
        ptm_value_list = []
        for ptm in ptm_list:
            ptm_value_list.append(ptm.value)

        # ptm_list = ptm_value_list
        ptm_list = ptm_value_list

    if organism_list is None:
        organism_list = []

    data = {
        "search_term": search_term,
        "term_type": term_type.value,
        "ptm_type": ptm_list,
        "role": role.value,
        "organism": organism_list
    }

    base_url = __get_base_url()
    url = f"{base_url}/search"

    if dict is True:
        headers = {"Accept": "application/json"}
    else:
        headers = {"Accept": "text/plain"}

    result = requests.get(url, params=data, verify=False, headers=headers)

    if result.status_code == 200:
        # read the result
        if result.text == "":
            return {id: "No data found for the given ID."}
        elif dict is True:
            search_results = json.loads(result.text)
        else:
            search_results = _to_dataframe_from_json(result.text)
        return search_results
    else:
        # raise the error
        result.raise_for_status()


def get_info(id, dict=None):
    """
    Gets general information about a protein by its UniProt AC.

    Args:
        id (str): The UniProt Accession Number (AC) of the protein (e.g., 'Q15796').
        dict (bool, optional): This parameter is present for consistency but is not used. The response is always JSON.

    Returns:
        dict: A dictionary with information about the protein (name, gene, organism, etc.).
              If no information is found, returns {'id': 'No info found for the given ID.'}.

    Raises:
        requests.exceptions.HTTPError: If the API returns an HTTP error code.
    """
    base_url = __get_base_url()
    url = f"{base_url}/{id}/info"
    result = requests.get(url, verify=False)

    if result.status_code == 200:
        # read the result
        if result.text == "":
            return {id: "No info found for the given ID."}
        info = json.loads(result.text)
        return info
    else:
        # raise the error
        result.raise_for_status()


def get_msa(id, dict=None):
    """
    Gets multiple sequence alignment (MSA) data for a protein.

    Args:
        id (str): The UniProt Accession Number (AC) of the protein (e.g., 'Q15796').
        dict (bool, optional): If True, returns JSON as a dictionary. Otherwise, also returns
                               JSON as a dictionary. The response format is always JSON.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary represents one sequence
                    in the alignment with details about each site.
                    If no MSA is found, returns {'id': 'No msa found for the given ID.'}.

    Raises:
        requests.exceptions.HTTPError: If the API returns an HTTP error code.
    """
    base_url = __get_base_url()
    url = f"{base_url}/{id}/msa"
    if dict is True:
        headers = {"Accept": "application/json"}
    else:
        headers = {"Accept": "text/plain"}

    result = requests.get(url, verify=False, headers=headers)

    if result.status_code == 200:
        # read the result
        if result.text == "":
            return {id: "No msa found for the given ID."}
        elif dict is True:
            data = json.loads(result.text)
        else:
            data = json.loads(result.text)
        return data
    else:
        # raise the error
        result.raise_for_status()


def get_substrates(id, dict=None):
    """
    Gets substrates for a given protein (which acts as an enzyme).

    Args:
        id (str): The UniProt Accession Number (AC) of the enzyme protein (e.g., 'Q15796').
        dict (bool, optional): If True, returns the raw JSON response as a dictionary.
                               Otherwise, returns a pandas DataFrame converted to a dictionary.

    Returns:
        dict: A dictionary with information about the substrates.
              If no substrates are found, returns {'id': 'No substrate found for the given ID.'}.

    Raises:
        requests.exceptions.HTTPError: If the API returns an HTTP error code.
    """
    base_url = __get_base_url()
    url = f"{base_url}/{id}/substrate"

    if dict is True:
        headers = {"Accept": "application/json"}
    else:
        headers = {"Accept": "text/plain"}

    result = requests.get(url, verify=False, headers=headers)

    if result.status_code == 200:
        # read the result
        if result.text == "":
            return {id: "No substrate found for the given ID."}
        elif dict is True:
            data = json.loads(result.text)
        else:
            data = _to_dataframe_from_json(result.text)
        return data
    else:
        # raise the error
        result.raise_for_status()


def get_proteoforms(id, dict=None):
    """
    Gets proteoforms for a given protein.

    Args:
        id (str): The UniProt Accession Number (AC) of the protein (e.g., 'Q15796').
        dict (bool, optional): If True, returns the raw JSON response as a dictionary.
                               Otherwise, returns a pandas DataFrame converted to a dictionary.

    Returns:
        dict: A dictionary with information about the proteoforms.
              If no proteoforms are found, returns {'id': 'No proteoforms found for the given ID.'}.

    Raises:
        requests.exceptions.HTTPError: If the API returns an HTTP error code.
    """
    base_url = __get_base_url()
    url = f"{base_url}/{id}/proteoforms"

    if dict is True:
        headers = {"Accept": "application/json"}
    else:
        headers = {"Accept": "text/plain"}

    result = requests.get(url, verify=False, headers=headers)


    if result.status_code == 200:
        # read the result
        if result.text == "" or result.text == "[]":
            return {id: "No proteoforms found for the given ID."}
        elif dict is True:
            data = json.loads(result.text)
        else:
            data = _to_dataframe_from_json(result.text)
        return data
    else:
        # raise the error
        result.raise_for_status()


def get_ptm_dependent_ppi(id, dict=None):
    """
    Gets PTM-dependent protein-protein interactions (PPIs) for a given protein.

    Args:
        id (str): The UniProt Accession Number (AC) of the protein (e.g., 'Q15796').
        dict (bool, optional): If True, returns the raw JSON response as a dictionary.
                               Otherwise, returns a pandas DataFrame converted to a dictionary.

    Returns:
        dict: A dictionary with information about PTM-dependent interactions.
              If no interactions are found, returns {'id': 'No ptmppi found for the given ID.'}.

    Raises:
        requests.exceptions.HTTPError: If the API returns an HTTP error code.
    """
    base_url = __get_base_url()
    url = f"{base_url}/{id}/ptmppi"

    if dict is True:
        headers = {"Accept": "application/json"}
    else:
        headers = {"Accept": "text/plain"}

    result = requests.get(url, verify=False, headers=headers)

    if result.status_code == 200:
        # read the result
        if result.text == "" or result.text == "[]":
            return {id: "No ptmppi found for the given ID."}
        elif dict is True:
            data = json.loads(result.text)
        else:
            data = _to_dataframe_from_json(result.text)
        return data
    else:
        result.raise_for_status()


def get_ppi_for_proteoforms(id, dict=None):
    """
    Gets protein-protein interactions (PPIs) for the proteoforms of a given protein.

    Args:
        id (str): The UniProt Accession Number (AC) of the protein (e.g., 'Q15796').
        dict (bool, optional): If True, returns the raw JSON response as a dictionary.
                               Otherwise, returns a pandas DataFrame converted to a dictionary.

    Returns:
        dict: A dictionary with information about the interactions of proteoforms.
              If no interactions are found, returns {'id': 'No proteoformsppi found for the given ID.'}.

    Raises:
        requests.exceptions.HTTPError: If the API returns an HTTP error code.
    """
    base_url = __get_base_url()
    url = f"{base_url}/{id}/proteoformsppi"
    if dict is True:
        headers = {"Accept": "application/json"}
    else:
        headers = {"Accept": "text/plain"}

    result = requests.get(url, verify=False, headers=headers)

    if result.status_code == 200:
        # read the result
        if result.text == "" or result.text == "[]":
            return {id: "No proteoformsppi found for the given ID."}
        elif dict is True:
            data = json.loads(result.text)
        else:
            data = _to_dataframe_from_json(result.text)
        return data
    else:
        # raise the error
        result.raise_for_status()


def get_ptm_enzymes_from_file(file_name, dict=None):
    """
    Gets PTM enzymes for sites listed in a file.

    The file must be in TSV (tab-separated values) format with three columns:
    Substrate UniProt AC, amino acid residue, and site position.

    Args:
        file_name (str): The path to the file with sites.
        dict (bool, optional): If True, returns the raw JSON response as a dictionary.
                               Otherwise, returns a pandas DataFrame converted to a dictionary.

    Returns:
        dict: A dictionary with information about enzymes for each site.
    """
    sites = __get_sites_from_files(file_name)

    return __get_data(sites,get_ptm_enzymes_from_list, dict=dict)


def get_ptm_enzymes_from_list(items,dict=None):
    """
    Gets PTM enzymes for a list of sites.

    Args:
        items (list[dict]): A list of dictionaries, where each dictionary describes a site.
                            Example: {'substrate_ac': 'P27361', 'site_residue': 'Y', 'site_position': '187'}
        dict (bool, optional): If True, returns the raw JSON response as a dictionary.
                               Otherwise, returns a pandas DataFrame converted to a dictionary.

    Returns:
        dict: A dictionary with information about the enzymes.
              If no enzymes are found, returns {'id': 'No ptm enzymes found for the given ID.'}.

    Raises:
        requests.exceptions.HTTPError: If the API returns an HTTP error code.
    """
    base_url = __get_base_url()
    url = f"{base_url}/batch_ptm_enzymes"
    json_data = json.dumps(items, indent=4)

    if dict is True:
        headers = {"Accept": "application/json"}
    else:
        headers = {"Accept": "text/plain"}

    result = requests.post(url, data=json_data, verify=False, headers=headers)

    if result.status_code == 200:
        # read the result
        if result.text == "" or result.text == "[]":
            return {id: "No ptm enzymes found for the given ID."}
        elif dict is True:
            data = json.loads(result.text)
        else:
            data = _to_dataframe_from_json(result.text)
        return data
    else:
        # raise the error
        result.raise_for_status()


def get_ptm_ppi_from_file(file_name,dict=None):
    """
    Gets PTM-dependent PPIs for sites listed in a file.

    The file must be in TSV (tab-separated values) format with three columns:
    Substrate UniProt AC, amino acid residue, and site position.

    Args:
        file_name (str): The path to the file with sites.
        dict (bool, optional): If True, returns the raw JSON response as a dictionary.
                               Otherwise, returns a pandas DataFrame converted to a dictionary.

    Returns:
        dict: A dictionary with information about PTM-dependent PPIs.
    """
    sites = __get_sites_from_files(file_name)
    return __get_data(sites,get_ptm_ppi_from_list,dict=dict)


def get_ptm_ppi_from_list(items, dict=None):
    """
    Gets PTM-dependent PPIs for a list of sites.

    Args:
        items (list[dict]): A list of dictionaries, where each dictionary describes a site.
                            Example: {'substrate_ac': 'P27361', 'site_residue': 'Y', 'site_position': '187'}
        dict (bool, optional): If True, returns the raw JSON response as a dictionary.
                               Otherwise, returns a pandas DataFrame converted to a dictionary.

    Returns:
        dict: A dictionary with information about PTM-dependent PPIs.
              If no PPIs are found, returns {'id': 'No ptmppi found for the given ID.'}.

    Raises:
        requests.exceptions.HTTPError: If the API returns an HTTP error code.
    """
    base_url = __get_base_url()
    url = f"{base_url}/batch_ptm_ppi"
    json_data = json.dumps(items, indent=4)

    if dict is True:
        headers = {"Accept": "application/json"}
    else:
        headers = {"Accept": "text/plain"}

    result = requests.post(url, data=json_data, verify=False,headers=headers)

    if result.status_code == 200:
        # read the result
        if result.text == "" or result.text == "[]":
            return {id: "No ptmppi found for the given ID."}
        elif dict is True:
            data = json.loads(result.text)
        else:
            data = _to_dataframe_from_json(result.text)
        return data
    else:
        # raise the error
        result.raise_for_status()

def get_stats():
    """
    Gets statistics of the iPTMnet database. This function is not yet implemented.
    """
    raise NotImplementedError


def __get_sites_from_files(file_name):
    """
    Internal helper function to read sites from a TSV file.

    Args:
        file_name (str): The path to the file.

    Returns:
        list[dict]: A list of dictionaries representing the sites.
    """
    sites = []
    with open(file_name) as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for substrate_ac, site_residue, site_position in reader:
            site = {
                "substrate_ac": substrate_ac,
                "site_residue": site_residue,
                "site_position": site_position
            }
            sites.append(site)
    return sites

def __get_data(sites, get_data_func, dict=None):
    """
    Split *sites* into ≤1000‑item chunks, call *get_data_func* on each chunk,
    and stitch the pieces back together.

    Parameters
    ----------
    sites : list[dict]
    get_data_func : callable
        Called as ``get_data_func(chunk, dict=dict)``.
    dict : bool, optional
        • True  → caller wants JSON‑style output (lists/dicts).  
        • False/None → caller expects tabular data (DataFrame) **or** a CSV‑
          derived dict (legacy behaviour).

    Returns
    -------
    pandas.DataFrame | dict | list
        Combined data from all chunks, matching the single‑chunk shape.
    """
    # ─── no batching needed
    if len(sites) <= 1000:
        return get_data_func(sites, dict=dict)

    # ─── batch requests
    all_chunks = []
    for i in range(0, len(sites), 1000):
        chunk = sites[i : i + 1000]
        chunk_result = get_data_func(chunk, dict=dict)
        if chunk_result:
            all_chunks.append(chunk_result)

    if not all_chunks:
        return [] if dict else pd.DataFrame()

    # ─── merge results
    if dict is True:
        # Expecting JSON‑style results
        flattened = []
        for chunk in all_chunks:
            if isinstance(chunk, list):
                flattened.extend(chunk)
            elif isinstance(chunk, builtins.dict):  # ← use built‑in dict type
                flattened.append(chunk)
            else:
                flattened.append(chunk)  # fallback
        return flattened

    # dict is False/None → caller thinks they're getting a DataFrame
    first = all_chunks[0]

    if isinstance(first, pd.DataFrame):
        return pd.concat(all_chunks, ignore_index=True)

    elif isinstance(first, builtins.dict):  # ← built‑in dict type
        merged = {}
        for chunk in all_chunks:
            merged.update(chunk)
        return merged

    # Unexpected – return raw list to avoid crashing
    return all_chunks

def __get_base_url():
    """
    Internal helper function to build the base URL based on the host and version.

    Returns:
        str: The full base URL for an API request.
    """
    if __selected_version == None:
        return __host_url
    else:
        return f"{__host_url}/{__selected_version}"

