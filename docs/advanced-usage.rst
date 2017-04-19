Advanced usage
===============


Generate input data
~~~~~~~~~~~~~~~~~~~
Run the following command to generate input data file::

  autodiscovery echo-input-template --save-to-file input.yml


Now, edit your generated `input.yml` file with the device’s information and CloudShell server credentials

Generate an additional vendors configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Run the following command to generate an additional vendors configuration data file::

  autodiscovery echo-vendors-configuration-template --save-to-file extented_vendors.json


Now, edit your generated `extented_vendors.json` file with additional Vendors information

Discover devices
~~~~~~~~~~~~~~~~
Run the following command to generate input data file::

  autodiscovery run --input-file input.yml --config-file extented_vendors.json --offline


Now, review your generated `report.xlsx` file with the discovered device’s information

Upload discovered devices into the CloudShell
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Run the following command to upload discovered devices from the report into the CloudShell server::

   autodiscovery run-from-report --input-file input.yml --config-file extented_vendors.json --report-file report.xlsx

Resources for the discovered devices are added to CloudShell
