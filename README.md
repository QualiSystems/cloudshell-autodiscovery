[![Build Status](https://travis-ci.org/QualiSystems/cloudshell-autodiscovery.svg?branch=master)](https://travis-ci.org/QualiSystems/cloudshell-autodiscovery)
[![codecov](https://codecov.io/gh/QualiSystems/cloudshell-autodiscovery/branch/master/graph/badge.svg)](https://codecov.io/gh/QualiSystems/cloudshell-autodiscovery)
[![PyPI version](https://badge.fury.io/py/cloudshell-autodiscovery.svg)](https://badge.fury.io/py/cloudshell-autodiscovery)
[![Dependency Status](https://dependencyci.com/github/QualiSystems/cloudshell-autodiscovery/badge)](https://tidelift.com/subscriber/github/QualiSystems/repositories/cloudshell-autodiscovery)

---

# **CloudShell Autodiscovery Tool**  

Release date: January 2019

Document version: 1.0

# In This Guide

* [Introduction](#introduction)
    * [Workflow](#workflow)
* [Installation](#installation)
    * [Installation Prerequisites](#installation-prerequisites)
    * [Installing the Autodiscovery tool](#installing-the-autodiscovery-tool)
* [Using the Autodiscovery Tool](#using-the-autodiscovery-tool)
    * [Help Commands](#help-commands)
* [Autodiscovering Devices in CloudShell](#autodiscovering-devices-in-cloudshell)
    * [Autodiscovering devices modeled in CloudShell](#autodiscovering-devices-modeled-in-cloudshell)
    * [Autodiscovering devices not modeled in CloudShell](#autodiscovering-devices-not-modeled-in-cloudshell)
        * [Offline Mode](#offline-mode)
        * [Online Mode](#online-mode)
        * [Additional vendors configuration file editable parameters](#additional-vendors-configuration-file-editable-parameters)
* [Creating Connections on Discovered Devices](#creating-connections-on-discovered-devices)
    * [Automatic Mode](#automatic-mode)
    * [Manual Mode](#manual-mode)
* [Input Data Files](#input-data-files)
    * [Input file in YAML format](#input-file-in-yaml-format)
    * [Input file in JSON format](#input-file-in-json-format)
    * [Additional vendors configuration file in JSON format](#additional-vendors-configuration-file-in-JSON-format)

# Introduction
The Autodiscovery tool enables CloudShell admins to discover a large number of devices at once “into” CloudShell, instead of having to manually create them one by one in CloudShell Portal. 

Since the tool performs a bulk discovery of devices, the relevant shells must be imported into CloudShell prior to running the tool. 

The tool supports devices that are modeled in CloudShell, but can also be customized to discover devices that are not modeled in CloudShell, see [Autodiscovering devices not modeled in CloudShell](#autodiscovering-devices-not-modeled-in-cloudshell). 

## Workflow

The basic flow for autodiscovering resources is as follows:

1.	Create a list of the devices you want to discover, by providing specific IPs and/or IP ranges.
2.	Make sure you have an appropriate shell for each device you wish to discover. 
3.	We recommend to first search for the shells in the [Quali Community Integrations](https://community.quali.com/integrations) page. Note that you can also extend existing shells to match the device’s specifications or create new shells from scratch - see the [CloudShell Dev guide](https://devguide.quali.com/) for more information.
4.	Import the shells into CloudShell - see [Importing Shells](https://help.quali.com/Online%20Help/9.1/Portal/Content/CSP/MNG/Mng-Shells.htm#Adding) in the CloudShell online help.
5.	Run the Autodiscovery tool. When the process completes, the discovered device resources are included in the **Inventory** dashboard in CloudShell Portal.

# Installation
## Installation Prerequisites
*	Windows, Linux, or Mac OS versions that support Python v2
*	Network access to the devices you want to discover
*	SNMP enabled on all devices
*	CloudShell version 8.0 and above
*	Python 2.7.x

    **Important:** If you have another version of Python installed on the autodiscovery machine, this may cause unexpected behavior.
*	pip

## Installing the Autodiscovery tool

There are two ways to install the Autodiscovery tool:
* Install via pip (public PyPi repository): 

   ```pip install cloudshell-autodiscovery```
   
* Install from the tool’s GitHub repository source:  

   ```
   git clone git@github.com:QualiSystems/cloudshell-autodiscovery.git
   
   cd cloudshell-autodiscovery
   
   pip install -r requirements.txt 
   
   python setup.py install
   ```
   If git is not installed, replace the first line with the following: 
         
      git clone https://github.com/QualiSystems/cloudshell-autodiscovery.git
      
# Using the Autodiscovery Tool
The tool is installed in the machine’s default Python27 folder. For example: *c:\Python27\Scripts folder*. 

 ![](https://github.com/QualiSystems/cloudshell-autodiscovery/blob/master/autodiscovery-install-files.png)

To use the tool, navigate to this folder in command-line, unless you have set these folders as env variables which will allow you to run the tool from anywhere on the machine. To do so, add the python/pip installation folder paths to your local environment variables. For example *C:\Python27 and C:\Python27\Scripts*.

You can perform these procedures in either offline or online mode. In online mode, you generate the autodiscovered device configurations and create them as is, while in offline mode, you can optionally modify the autodiscovered device configurations before creating and discovering them into CloudShell. 

## Help Commands

To list the commands available in this tool, run the following command-line: 

```autodiscovery --help```

To learn what version of the Autodiscovery tool you are using, run the following command-line: 

```autodiscovery version --help```

To view specific options associated with any autodiscovery command, type the command and add --help. For example:

```autodiscovery <echo-input-template> --help```

# Autodiscovering Devices in CloudShell

This chapter explains how to discover devices in CloudShell using the Autodiscovery tool. The tool supports devices that are modeled by Quali-published shells and devices for which you have a new or extended shell. 

   * [Autodiscovering devices modeled in CloudShell](#autodiscovering-devices-modeled-in-cloudShell)
   * [Autodiscovering devices not modeled in CloudShell](#autodiscovering-devices-not-modeled-in-cloudShell)
   
## Autodiscovering devices modeled in CloudShell  

**To autodiscover devices modeled in CloudShell:**

1. Open command line and navigate to the autodiscovery tool’s installation folder. 

2. To generate the input file, run the following command-line:

   ```autodiscovery echo-input-template --save-to-file input.yml```
   
   The input file is created in the folder where you ran the command. If you want the file to be created in a different location, specify the full path to this location.
   
    * *To generate the file in json format, change “yml” to “json”. For reference, see sample input files: [Input file in YAML format](#input-file-in-yaml-format) or [Input file in JSON format](#input-file-in-json-format).*
      
    * *To rename the input file, use:* ```autodiscovery echo-input-template --save-to-file <input filename>.[yml|json]```

3. Open the *input* file in your preferred editor and update the device info and CloudShell server credentials.

   1. Update the fields to include the details of the devices you want to discover as follows:
   
      |Field|Description|
      |:---|:---|
      |IP of devices to discover|**devices-ips:** Add a single device ip or a range of device ips and the domain in which to create them.<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;• **range:** If you want to add a string of devices, it must follow this format: xxx.xxx.xx.100-110. You can have a range within the IP address in any segment of the address, for example xxx.xxx.9.1-10.xxx.<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;• **domain:** Specify the CloudShell domain. If you want the devices to be created in the Global domain (default), omit this line.|
      |IP and credentials for the CloudShell API|**cloudshell:**<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;• **ip:** Address of the CloudShell API<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;• **user:** Admin user on CloudShell<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;• **password:** Admin user's password|
      |Possible SNMP community strings|**community-strings:** Add possible SNMP read community strings for the devices, such as public, public2 etc.|
      |Additional settings per Vendor|**vendor-settings:** <br>      **Default:**<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;• **cli-credentials**: (mandatory) Add default values to be used if all devices have the same CLI credentials, including user, password, enable password etc.<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;• **folder-path:** Add the folder path as it appears in CloudShell Resource Manager Client.<br>**Cisco/Juniper:** (vendor specific information) Add other device credentials as required for specific vendors.<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;• **cli-credentials:** Add user and password<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;• **folder-path:** Add the folder path as it appears in CloudShell Resource Manager Client.|
   
   2. Save your changes. Make sure you do not save the file to a different folder.
   
4. At this point, you can choose to immediately discover the devices as resources into CloudShell or make modifications to the device settings before discovering them. Perform the appropriate procedure:

   **To immediately discover the devices in CloudShell:**
   
   * Run the following command-line from the folder containing the input file:
   
      ```autodiscovery run --input-file input.yml```
         
      **If you changed the file name, make sure you replace “input.yml” with the new name.**

      The devices are discovered in CloudShell. A *discovery_report.xlsx* file is produced in the input file’s containing folder, providing the following information about the discovered devices:
   
      |Field|Description|
      |:---|:---|
      |IP|Device IP|
      |Vendor|Device vendor, for example: Cisco|
      |sysObjectID|OID unique name for each device|
      |Description|Device description|
      |SNMP Read Community|SNMP Read Community string, for example: Public|
      |Model Type|Device model type, for example: router, switch, etc.|
      |Device Name|Resource’s display name in CloudShell| 
      |Domain|**Global** (default) or other domain assigned in the input file in CloudShell|
      |Folder|Containing folder of the resource, as displayed in CloudShell Portal’s **Inventory** dashboard and the Resource catalog in the blueprint and sandbox diagrams.|
      |Attributes|Resource attributes, for example: Enable SNMP=False, SNMP Read Community=Public. User can add any attribute defined in the shell model. 
      |Added to CloudShell|Indicates the devices that were added to CloudShell as resources. Possible values are: Skipped, Failed, and Success.|
      |Comment|Any issues related to the processing of a specific device|
        
      * *To generate a log file, add the tag:* ```--log-file <log filename>```
      
      * *To run this command-line without discovering the resources on CloudShell, i.e. only create the resources in CloudShell but do not discover them, add the tag:* ```--no-autoload```. <br><br>*Note that if you use* ```--no-autoload```*, after the tool creates the resources in CloudShell, you will have to manually discover each individual resource in CloudShell.*
      
    **To edit device details before discovery:**
   
   1. To generate an Excel report, run the following command-line from the folder containing the input file:
   
      ```autodiscovery run --input-file input.yml --report-file <report filename> --offline```
    
      By default, the report file is saved to the current user’s *C: drive* folder. However, you can save the file in a different existing folder, for example: 
    
      ```autodiscovery run --input-file input.yml --report-file C:\Users\Administrator\temp\<report filename> --offline```
    
   2. Update the report file as appropriate.
  
   3. To discover the devices into CloudShell from the report, run the following command-line:
  
      ```autodiscovery run-from-report --input-file input.yml --report-file <report filename>.xlsx```
   
      You must run this command from the same folder where the report file is saved. By default, the file is saved to the location where you ran the command.  
            
      * *To generate the report in console format instead of .xlsx (default), add the tag:* ```--report-type console```
              
      * *To generate a log file, add the tag:* ```--log-file <log filename>```

## Autodiscovering devices not modeled in CloudShell 

When autodiscovering unmodeled devices, you must ensure that:

1. You have created or extended shells for these devices and loaded them into CloudShell. 

2. You created a vendor configuration input file called *extended_vendors.json*. The *extended_vendors.json* file provides the device details (device name, model etc.), see [Offline Mode](#offline-mode). 

   **Note:** For assistance using the *extended_vendors.json* file, contact customer support. 
   
   The autodiscovery tool attempts to recognize the devices, using the *extended_vendors.json*, and associate each one with the relevant loaded shell. 

   The additional vendor configuration input file does not override the *input* file but is added to it. This process, therefore, requires two configuration files: an “input” file and an “extended vendors configuration” file. 

You can autodiscover devices, for which you created or extended your own shell(s), in two modes: 

•	[Offline mode](#offline-mode) – should be used when you want to verify the information before creating and discovering the devices in CloudShell. This is the recommended mode when you want to autodiscover devices for which you created or extended your own shell (s) or when running the tool for the first time. 

•	[Online mode](#online-mode) – should be used when you do not need to verify the information before creating and discovering the devices in CloudShell.

### Offline Mode

In offline mode, the Autodiscovery tool gives you an opportunity to verify the information before creating the devices in CloudShell. 

**To autodiscover devices not modeled in CloudShell in offline mode:**

1.	To generate the input file, run the following command-line: 

    ```autodiscovery echo-input-template --save-to-file input.yml```
    
    The input file is created in the folder where you ran the command. If you want the file to be created in a different location, specify the full path to this location.
      
    * *To generate the file in json format, change “yml” to “json”. For reference, see sample input files: [Input file in YAML format](#input-file-in-yaml-format) or [Input file in JSON format](#input-file-in-json-format).*
   
    * *To rename the input file, use* ```autodiscovery echo-input-template <input filename>.[yml|json]```

2.	Open the *input* file in your preferred editor and update the device info and CloudShell server credentials as explained in [Autodiscovering devices modeled in CloudShell](#autodiscovering-devices-modeled-in-cloudshell).

3.	Create and update the extended vendors configuration file. 

    1.	Run the following command-line: 
   
         ```autodiscovery echo-vendors-configuration-template --save-to-file extended_vendors.json```

         The *extended_vendors.json* file is created and saved to the folder where you ran the command. 
      
         This data file is generated only in JSON format. In the future, you will be able to generate the file in YAML format as well. For reference, see a sample input file: [Additional vendors configuration file in JSON format](#additional-vendors-configuration-file-in-json-format).
                  
         * *If you want the file to be created in a different location, specify the full path to this location.* 

         * *To rename the *extended_vendors.json* file, use:* ```autodiscovery echo-vendors-configuration-template --save-to-file <extended_vendors filename>.json```

    2.	Edit the *extended_vendors.json* file with additional vendor information. See the [Additional vendors configuration file editable parameters](#additional-vendors-configuration-file-editable-parameters) table for details.
   
4.	Generate the *discovery_report.xlsx* Excel file that combines the information from the input file with the information in the additional vendors configuration file - *extended_vendors.json*. This file is used to discover the devices in CloudShell.

    1.	Run the following command-line:
   
         ```autodiscovery run --input-file input.yml --config-file extended_vendors.json --offline```

         **If you changed the file names, you need to replace “input.yml” and/or “extended_vendors.json” with the new name(s) here.**

         You must run this command from the same folder where the *input* file and the *extended_vendors.json* files are saved.
 
         A *discovery_report.xlsx* Excel file is saved to the folder where you ran the command.
  
    2.	Review the *discovery_report.xlsx* file and update the configurations accordingly. 
 
    3.	Save your changes.
   
    4.	Create CloudShell resources for the devices by running the following command-line:
   
         ```autodiscovery run-from-report --input-file input.yml --report-file discovery_report.xlsx```

         You must run this command from the folder containing the *input* file and the *discovery_report.xlsx* files.
    
         CloudShell discovers the devices and generates a *discovery_report.xlsx file*, containing the autodiscovery details, in the folder where you ran the command. Use this file to troubleshoot any issues.
 
         * *To generate the report in console format instead of .xlsx (default), add the tag:* ```--report-type console```

         * *To generate a log file, add the tag:* ```--log-file <log filename>```

### Online Mode

In online mode, the Autodiscovery tool immediately attempts to create and discover the resources in CloudShell. 

1. To generate the input file, run the following command-line:

   ```autodiscovery echo-input-template --save-to-file input.yml```
   
   The input file is created in the folder where you ran the command. If you want the file to be created in a different location, specify the full path to this location.
     
   * *To generate the file in json format, change “yml” to “json”. For reference, see sample input files: [Input file in YAML format](#input-file-in-yaml-format) or [Input file in JSON format](#input-file-in-json-format).*

   * *To rename the input file, use:* ```autodiscovery echo-input-template <input filename>.[yml|json]```

2.	Open the *input* file in your preferred editor and update the device info and CloudShell server credentials, as explained in [Autodiscovering devices modeled in CloudShell](#Autodiscovering-devices-modeled-in-cloudshell).

3.	Generate the vendor configurations data file. 

    1. Run the following command-line: 
   
         ```autodiscovery echo-vendors-configuration-template --save-to-file extended_vendors.json```
         
         * *The extended_vendors.json file is saved in the folder where you ran the command. If you want the file to be created in a different location, specify the full path to this location. For reference, see a sample input file: [Additional vendors configuration file in JSON format](#additional-vendors-configuration-file-in-json-format).*

         * *To rename the *extended_vendors.json* file, use:* ```autodiscovery echo-vendors-configuration-template --save-to-file <extended_vendors filename>.json```
      
    2. Edit the generated *extended_vendors.json* file with additional vendor information. See the [Additional vendors configuration file editable parameters](#additional-vendors-configuration-file-editable-parameters) table for details.
   
4.	Generate the input file that combines the information from the *input* file with the information in the additional vendors configuration file (*extended_vendors.json*).

    * Run the following command-line: 
   
         ```autodiscovery run --input-file input.yml --config-file extended_vendors.json```

         **If you changed the file names, you need to replace “input.yml” and/or “extended_vendors.json” with the new name(s) here.**

         You must run this command from the same folder where the *input* file and the *extended_vendors.json* files are saved.
 
         CloudShell discovers the devices and generates an Excel file *discovery_report.xlsx* in the folder where you ran the command,  containing the autodiscovery details. Use this file to troubleshoot any issues.
         
         * *To generate a log file, add the tag:* ```--log-file <log filename>```

         * *To run this command-line without discovering the resources on CloudShell, i.e. only creating the resources in CloudShell without discovering them, add the tag:* ```--no-autoload``` <br><br>*Note that if you use* ```--no-autoload```*, after the tool creates the resources in CloudShell, you will have to manually discover each individual resource in CloudShell.*
      
### Additional vendors configuration file editable parameters

|Field|Description|
|:---|:---|
|name|Name of the vendor|
|aliases|Regex string which is an alias for the vendor name. You can include a single alias or a list of aliases.|
|type|Device type<br>Currently, the tool only supports “networking” devices. A “networking” device is any device whose device statistics are accessed via SNMP.|
|default_os|(Optional) If the OS on the device cannot be identified, this OS is used.| 
|default_prompt|Regexp string for the default prompt|
|enable_prompt|Regexp string for the enable prompt|
|operation_systems|•	name: Name of the operating system<br>• aliases: Regex string which is an alias for the OS name. You can include a single alias or a list of aliases.<br>• default_model: Model type of the device (switch, router, etc.)<br>• models_map: Add the aliases that will be used to refer to “switch” or “router”. If Autodiscovery cannot identify the model, the tool will use the default.<br>• families: Resource family names for the device on CloudShell.<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;o	Switch<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;	first_gen<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•	family_name<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•	model_name<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•	driver_name<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;	second_gen<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•	family_name<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•	model_name<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•	driver_name<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;o	router<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;	first_gen<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•	family_name<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•	model_name<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•	driver_name<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;	second_gen<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•	family_name<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•	model_name<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•	driver_name|

# Creating Connections on Discovered Devices

This section describes how to connect the discovered resources to your physical network. 

There are two ways to create these connections: [automatic](#automatic-mode) and [manual](#manual-mode).

## Automatic Mode

In automatic mode, the Autodiscovery tool discovers all the ports on the specified resources and creates physical network connections based on their "Adjacent" attributes.

* To discover and create resource connections, run the following command-line from the folder containing the input file:

    ```autodiscovery connect-ports --<input filename>.[yml|json] --resources-names <resources name> --domain <domain>```

     * *Replace* ```<resources name>``` *with the comma-separated names of the resources you want to discover and connect*
     * *Replace* ```<domain>``` *with the CloudShell domain of the resources*
     * *To generate a log file, add the tag:* ```--log-file <log filename>```
     * *To generate the report in console format instead of .xlsx (default), add the tag:* ```--connections-report-type console```
     * *To only generate the report without creating any connections in CloudShell, add the tag:* ```--offline```. *This report can be used later with the* ```autodiscovery connect-ports-from-report``` *command*.
      
    The tool generates a *connect_ports_report.xlsx* file containing the discovered connections in the folder where you ran the command. Use this file to troubleshoot any issues.

## Manual Mode

Manual mode is a three-step process. First, generate a “device connections” Excel file, then edit the file with the required connections, and finally run it using the Autodiscovery tool. You can also use the *connect_ports_report.xlsx* report that is generated with the ```autodiscovery connect-ports --offline``` command as a “device connections” Excel file.

1.	Create the resource connections Excel file. 

2. In the following command-line, replace <connections filename> with a name for the file and run this command-line:
   
      ```autodiscovery echo-excel-connections-report-template --save-to-file <connections filename>```

      An Excel file *<connections filename>.xlsx* is generated in the folder where you ran the command. If you want the file to be created in a different location, specify the full path to this location.
   
3. Specify the physical port connections between the devices. 
   
   **Note:** For sub-resources, you must include the full address of each port in CloudShell.
   
   |Field|Description|
   |:---|:---|
   |Resource Name|(Optional) Name of the resource where port is located.|
   |Source Port Full Name|Full path to the resource’s port on CloudShell.<br>For example:  DUT 1/Chassis 1/Module 1/Port 1|
   |Adjacent|(Optional) "Adjacent" port's attribute value.|
   |Target Port Full Name|Full path to the resource’s port on CloudShell.<br>For example: Switch 2/Chassis 1/Module 1/Port 1|
   |Domain|CloudShell domain of the resources|
   |Connection Status|Read-only field indicating the status after running the **connect-ports** command.<br>•	**Success** - Ports were successfully connected<br>•	**Skipped** - Connections were discovered but not added to the CloudShell<br>•	**Failed** - Ports were not successfully connected|
   |Comment|Read-only field indicating any additional information/error messages returned in case of a connection failure.|

4. Save your changes. Do not change the file name.
   
5. To apply the resource connections, run the following command-line from the folder containing the input file and the *extended_vendors.json* file: 

    ```autodiscovery connect-ports-from-report --<input filename>.[yml|json] --connections-report-file <connections filename>```
   
      * *To generate a log file, add the tag:* ```--log-file <log filename>```

# Input Data Files

This section provides the files you will receive when you run the command to produce the input file in YAML and JSON format as well as the additional vendors configuration file in JSON format. 

•	[Input file in YAML format](#input-file-in-yaml-format)

•	[Input file in JSON format](#input-file-in-json-format)

•	[Additional vendors configuration file in JSON format](#additional-vendors-configuration-file-in-json-format)

## Input file in YAML format

```
# IP of devices to discover (could be a range or single one)
devices-ips:
    -   range: 192.168.10.3-45
        domain: Some Domain
    -   range: 192.168.8.1-9.10
        domain: Some other Domain
    -   192.168.42.235

# IP and credentials for the CloudShell API
cloudshell:
    ip: 192.168.85.9
    user: admin
    password: admin

# Possible SNMP community strings
community-strings:
    -   public
    -   public2

# Additional settings per Vendor (Possible CLI credentials (user/password), resource folder)
vendor-settings:
    default:
        cli-credentials:
            -   user: root
                password: Password1
                enable password: Password2we
            -   user: root1
                password: Password2
        folder-path: autodiscovery
    Cisco:
        cli-credentials:
            -   user: cisco
                password: Password1
            -   user: cisco2
                password: Password2
        folder-path: cisco
    Juniper:
        cli-credentials:
            -   user: juniper
                password: Password1
            -   user: juniper2
                password: Password2
                enable_password: Password2
```

## Input file in JSON format

```
{
    "cloudshell": {
        "ip": "192.168.85.9", 
        "password": "admin", 
        "user": "admin"
    }, 
    "community-strings": [
        "public", 
        "public2"
    ], 
    "devices-ips": [
        {
            "domain": "Some Domain", 
            "range": "192.168.10.3-45"
        }, 
        {
            "domain": "Some other Domain", 
            "range": "192.168.8.1-9.10"
        }, 
        "192.168.42.235"
    ], 
    "vendor-settings": {
        "Cisco": {
            "cli-credentials": [
                {
                    "password": "Password1", 
                    "user": "cisco"
                }, 
                {
                    "password": "Password2", 
                    "user": "cisco2"
                }
            ], 
            "folder-path": "cisco"
        }, 
        "Juniper": {
            "cli-credentials": [
                {
                    "password": "Password1", 
                    "user": "juniper"
                }, 
                {
                    "enable_password": "Password2", 
                    "password": "Password2", 
                    "user": "juniper2"
                }
            ]
        }, 
        "default": {
            "cli-credentials": [
                {
                    "enable password": "Password2we", 
                    "password": "Password1", 
                    "user": "root"
                }, 
                {
                    "password": "Password2", 
                    "user": "root1"
                }
            ], 
            "folder-path": "autodiscovery"
        }
    }
}
```

## Additional vendors configuration file in JSON format

```
[
   {
      "name": "Cisco",
      "aliases": [
         "[Cc]iscoSystems"
      ],
      "type": "networking",
      "default_os": "IOS",
      "default_prompt": ">\\s*$",
      "enable_prompt": "(?:(?!\\)).)#\\s*$",
      "operation_systems": [
         {
            "name": "IOS",
            "aliases": [
               "CAT[ -]?OS",
               "IOS[ -]?X?[E]?"
            ],
            "default_model": "switch",
            "models_map": [
               {
                  "model": "switch",
                  "aliases": [
                     "[Cc]atalyst",
                     "C2950"
                  ]
               },
               {
                  "model": "router",
                  "aliases": [
                     "IOS[ -]?X?[E]?"
                  ]
               }
            ],
            "families": {
               "switch": {
                  "first_gen": {
                     "family_name": "Switch",
                     "model_name": "Cisco IOS Switch",
                     "driver_name": "Generic Cisco IOS Driver Version3"
                  },
                  "second_gen": {
                     "family_name": "CS_Switch",
                     "model_name": "Cisco IOS Switch 2G",
                     "driver_name": "Cisco IOS Switch 2G"
                  }
               },
               "router": {
                  "first_gen": {
                     "family_name": "Router",
                     "model_name": "Cisco IOS Router",
                     "driver_name": "Generic Cisco IOS Driver Version3"
                  },
                  "second_gen": {
                     "family_name": "CS_Router",
                     "model_name": "Cisco IOS Router 2G",
                     "driver_name": "Cisco IOS Router 2G"
                  }
               }
            }
         }
      ]
   }
]
```


