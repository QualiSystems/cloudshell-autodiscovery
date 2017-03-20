Basic usage
===============

Run command to generate input data file::

  autodiscovery echo-input-template --save-to-file input.yml


Now, edit your generated `input.yml` file with devices info and CloudShell server credentials


Run command to discover devices from input file and load them into the CloudShell server::

  autodiscovery run --input-file input.yml

After this command discovered devices will be added into the CloudShell. Yo can find information about the uploaded
devices in the generated `report.xlsx` file