#/bin/bash

python3 auto_documentation/main.py  --run-type=DOX_GENERATE --ticket-source=JIRA --ticket-tree-src=tests/test_data/example_config.yaml --parent-ticket-id=MBA-15 --output-file-path=example.docx --document-type=word --test-folder=tests/test_data/example_test_folder/test_MBA-14.py