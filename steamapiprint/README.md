## **SteamApiPrint**
Simple Python script that uses some HTML magic to generate
JSON files for Steam Api points.\
Not only makes your work easier, but a little bit faster.

### **Usage**
Get all available API sections\
`./steamapiprint.py --sections`\
Get all available API point names for a section\
`./steamapiprint.py --section <section> --point-names`\
Get all available API points for a section\
`./steamapiprint.py --section <section> --points`\
Get an API point for a section\
`./steamapiprint.py --section <section> --point <point>`\
\
Export to JSON format\
example: Export all API points for a section to JSON array\
`./steamapiprint.py --section ISteamUser --points --export ISteamUser.json`


@TheNoiselessNoise