Basic usage
===============

Run the following command to generate input data file::

  autodiscovery echo-input-template --save-to-file input.yml


Now, edit your generated `input.yml` file with the device’s information and CloudShell server credentials


Run the following command to discover devices from input file and load them into the CloudShell server::

  autodiscovery run --input-file input.yml

Resources for the discovered devices are added to CloudShell. Yo can find information about the uploaded
devices in the generated `report.xlsx` file