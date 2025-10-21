# bulk_es_load.py

import os
import sys
import logging

from aced_submission.meta_flat_load import delete as meta_flat_delete
from aced_submission.grip_load import get_project_data
from opensearchpy import OpenSearchException

# Set up logging to see output
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logging.getLogger().setLevel(logging.INFO)

# --- START REQUIRED NEW HELPER FUNCTIONS ---

def get_all_projects_to_load():
    """
    In a real scenario, this function would query Gen3 Fence/Arborist
    or Indexd to get a full list of all active projects in the data commons.
    
    For your local test environment, hardcode the projects you know exist 
    and were restored from Production.
    """
    # Based on your PostgreSQL DB names (which align with Production projects)
    # The common Gen3 project format is PROGRAM-PROJECT
    return [
        "CALYPR-arborist_cbds",
        "CALYPR-fence_cbds",
        "CALYPR-requestor_cbds",
        "CALYPR-indexd_cbds",
        "CALYPR-wts_cbds",
        # ... add any other projects as needed
    ]

def bulk_load_project(project_id: str):
    """
    Re-implements the core ES loading logic from _load_all for a single project.
    """
    # For a bulk load, assume we are not dealing with local files (no FHIR import)
    # just data already in GRIP.
    
    program, project = project_id.split('-', 1) # Assumes 'CALYPR-arborist_cbds'

    output = {'logs': []} # Capture internal logs

    try:
        # Step 1: Fetch and flatten the data into the local SQLite DB
        work_path = pathlib.Path("work")
        db_path = (work_path / f"{project_id}_fhir.db")
        db_path.unlink(missing_ok=True) # Ensure a fresh database

        db = LocalFHIRDatabase(db_name=db_path)
        
        logging.info(f"Fetching data from GRIP for project {project_id}...")
        # Note: 'CALIPER' is the GRIP graph name from fhir_import_export.py
        db.bulk_insert_data(
            resources=get_project_data(_get_grip_service(), "CALIPER", project_id, output, _get_token())
        )
        
        # Step 2: Define generators for flattened data (same as original script)
        index_generator_dict = {
            'researchsubject': db.flattened_research_subjects,
            'specimen': db.flattened_specimens,
            'file': db.flattened_document_references,
            "medicationadministration": db.flattened_medication_administrations,
            "groupmember": db.flattened_group_members,
        }

        # Step 3: Clear and Reload Elasticsearch/OpenSearch indices
        for index in index_generator_dict.keys():
            logging.info(f"Clearing old ES index for {project_id}:{index}")
            meta_flat_delete(project_id=project_id, index=index)

        for index, generator in index_generator_dict.items():
            logging.info(f"Loading new data into ES index for {project_id}:{index}")
            load_flat(project_id=project_id, index=index,
                      generator=generator(),
                      limit=None, elastic_url=DEFAULT_ELASTIC,
                      output_path=None)

        logging.info(f"SUCCESS: Loaded {project_id} into Elasticsearch.")
        
    except OpenSearchException as e:
        logging.error(f"OpenSearch Error on project {project_id}: {str(e)}")
    except Exception as e:
        logging.error(f"General Error on project {project_id}: {str(e)}")

# --- END REQUIRED NEW HELPER FUNCTIONS ---


def main_bulk():
    """Main function to run bulk load across all projects."""
    projects_to_load = get_all_projects_to_load()
    
    if not projects_to_load:
        logging.warning("No projects defined in get_all_projects_to_load. Nothing to do.")
        return

    # Check for required environment variables used by the helper functions
    if not os.environ.get('GRIP_SERVICE_NAME') or not os.environ.get('ACCESS_TOKEN'):
        logging.error("Missing required environment variables (GRIP_SERVICE_NAME or ACCESS_TOKEN).")
        logging.error("Please set GRIP_SERVICE_NAME and ACCESS_TOKEN (a Gen3 token with appropriate permissions).")
        return

    # Create the work directory if it doesn't exist (it is ignored by git)
    pathlib.Path("work").mkdir(parents=True, exist_ok=True)
    
    logging.info(f"Starting bulk Elasticsearch load for {len(projects_to_load)} projects.")
    
    for project_id in projects_to_load:
        bulk_load_project(project_id)
        
    logging.info("Bulk Elasticsearch load process complete.")


if __name__ == '__main__':
    # Ensure you are running this script from the same directory as fhir_import_export.py 
    # to maintain imports and file paths.
    main_bulk()