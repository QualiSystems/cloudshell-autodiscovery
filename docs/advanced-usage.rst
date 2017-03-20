Advanced usage
===============


Generate input data
~~~~~~~~~~~~~~~~~~~
Run command to generate input data file::

  autodiscovery echo-input-template --save-to-file input.yml


Now, edit your generated `input.yml` file with devices info and CloudShell server credentials

Generate additional vendors configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Run command to generate additional vendors configuration data file::

  autodiscovery echo-vendors-configuration-template --save-to-file extented_vendors.json


Now, edit your generated `extented_vendors.json` file with additional Vendors information

Discover devices
~~~~~~~~~~~~~~~~
Run command to generate input data file::

  autodiscovery run --input-file input.yml --config-file extented_vendors.json --offline


Now, check/edit your generated `report.xlsx` file with discovered devices info

Upload discovered devices into the CloudShell
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Run command to upload discovered devices from the report into the CloudShell server::

   autodiscovery run-from-report --input-file input.yml --config-file extented_vendors.json --report-file report.xlsx

After this command discovered devices will be added into the CloudShell
