# Objective

This library creates a python wrapper over Konker API to allow easier usage and integration 
with Konker REST API

# Sample Usage

import * as konker from pykonker

konker = konker.Client()
konker.login(username='', password='')
applications = konker.getApplications()
devices = konker.getAllDevicesForApplication('default')
data = konker.readData(guid=devices[0]['guid'])

# References

https://www.konkerlabs.com/developers/developers-en.html
https://konker.atlassian.net/wiki/spaces/DEV/pages/28180518/Guia+de+Uso+da+Plataforma+Konker
https://api.demo.konkerlabs.net/v1/swagger-ui.html
